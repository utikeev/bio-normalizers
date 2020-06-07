from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Optional

from tqdm import tqdm

ID_PREFIX = '<http://id.nlm.nih.gov/mesh/2020/'
DISEASE_TYPE = '<http://id.nlm.nih.gov/mesh/vocab#SCR_Disease>'
CHEMICAL_TYPE = '<http://id.nlm.nih.gov/mesh/vocab#SCR_Chemical>'


class EntityType(Enum):
    PREFERRED_MAPPED_TO = '<http://id.nlm.nih.gov/mesh/vocab#preferredMappedTo>'
    PREFERRED_CONCEPT = '<http://id.nlm.nih.gov/mesh/vocab#preferredConcept>'
    PREFERRED_TERM = '<http://id.nlm.nih.gov/mesh/vocab#preferredTerm>'
    TYPE = '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>'
    LABEL = '<http://www.w3.org/2000/01/rdf-schema#label>'
    TERM = '<http://id.nlm.nih.gov/mesh/vocab#term>'
    CONCEPT = '<http://id.nlm.nih.gov/mesh/vocab#concept>'
    PREFERRED_LABEL = '<http://id.nlm.nih.gov/mesh/vocab#prefLabel>'
    ALT_LABEL = '<http://id.nlm.nih.gov/mesh/vocab#altLabel>'
    BROADER_DESCRIPTOR = '<http://id.nlm.nih.gov/mesh/vocab#broaderDescriptor>'
    TREE_NUMBER = '<http://id.nlm.nih.gov/mesh/vocab#treeNumber>'


def get_id(id_str: str) -> str:
    return id_str[len(ID_PREFIX):-1]


def get_labels_from_dict(term_dict: Dict[EntityType, List[str]]) -> List[str]:
    labels = []

    if EntityType.LABEL in term_dict:
        label = term_dict[EntityType.LABEL][0]
        labels.append(strip_label(label))
    if EntityType.ALT_LABEL in term_dict:
        for label in term_dict[EntityType.ALT_LABEL]:
            labels.append(strip_label(label))
    if EntityType.PREFERRED_LABEL in term_dict:
        for label in term_dict[EntityType.PREFERRED_LABEL]:
            labels.append(strip_label(label))
    return labels


def get_terms_from_single_concept(entities: Dict[str, Dict[EntityType, List[str]]], concept_id: str) -> List[str]:
    concept = entities[concept_id] if concept_id in entities else {}
    terms = get_labels_from_dict(concept)

    if EntityType.PREFERRED_TERM in concept:
        term_id = get_id(concept[EntityType.PREFERRED_TERM][0])
        if term_id in entities:
            term_dict = entities[term_id]
            terms += get_labels_from_dict(term_dict)

    if EntityType.TERM in concept:
        preferred_terms = concept[EntityType.TERM]
        for term in preferred_terms:
            term_id = get_id(term)
            if term_id in entities:
                term_dict = entities[term_id]
                terms += get_labels_from_dict(term_dict)
    return terms


def get_terms_from_concepts(entities: Dict[str, Dict[EntityType, List[str]]], entity_id: str) -> List[str]:
    entity_dict = entities[entity_id] if entity_id in entities else {}
    terms = get_labels_from_dict(entity_dict)

    if EntityType.PREFERRED_CONCEPT in entity_dict:
        concept_id = get_id(entity_dict[EntityType.PREFERRED_CONCEPT][0])
        terms += get_terms_from_single_concept(entities, concept_id)
    if EntityType.CONCEPT in entity_dict:
        for concept in entity_dict[EntityType.CONCEPT]:
            concept_id = get_id(concept)
            terms += get_terms_from_single_concept(entities, concept_id)
    return terms


def strip_label(label: str) -> str:
    # "Hyperandrogenism"@en -> Hyperandrogenism
    return label[1:-4]


def collect_entities(mesh_file: Path, tree_prefix: str, scr_type: Optional[str] = None) -> Dict[str, Set[str]]:
    entities: Dict[str, Dict[EntityType, List[str]]] = {}
    with mesh_file.open('r') as mesh:
        lines = mesh.readlines()
        for line in tqdm(lines, 'Reading MeSH dump...'):  # type: str
            id_str, field_str, value_str = line.split(' ', maxsplit=2)
            ent_id = get_id(id_str)  # Omit last > and prefix
            if ent_id not in entities:
                entities[ent_id] = defaultdict(list)
            try:
                entity_type = EntityType(field_str)
                entities[ent_id][entity_type].append(value_str[:-3])
            except ValueError:
                continue

    result: Dict[str, Set[str]] = {}

    def add_topical_descriptor(t_id: str):
        if t_id not in result and t_id in entities:
            result[t_id] = set(get_terms_from_concepts(entities, t_id))
            if EntityType.BROADER_DESCRIPTOR in entities[t_id]:
                for broader in entities[t_id][EntityType.BROADER_DESCRIPTOR]:
                    broader_id = get_id(broader)
                    add_topical_descriptor(broader_id)

    for ent, d in tqdm(entities.items(), 'Processing entities...'):  # type: str, Dict[EntityType, List[str]]
        if scr_type and EntityType.TYPE in d and d[EntityType.TYPE][0] == scr_type:
            result[ent] = set(get_terms_from_concepts(entities, ent))
        if EntityType.TREE_NUMBER in d and get_id(d[EntityType.TREE_NUMBER][0]).startswith(tree_prefix):
            add_topical_descriptor(ent)

    return result
