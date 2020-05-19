"""
Script to build terminology dictionary from MeSH® dump in RDF format, which can be downloaded here:
ftp://nlmpubs.nlm.nih.gov/online/mesh/rdf/
Downloaded data is the courtesy of the U.S. National Library of Medicine.
"""

import argparse
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set

from tqdm import tqdm

ID_PREFIX = '<http://id.nlm.nih.gov/mesh/2020/'
DISEASE_TYPE = '<http://id.nlm.nih.gov/mesh/vocab#SCR_Disease>'


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


def setup_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("--mesh_dump", type=lambda x: Path(x), required=True)
    parser.add_argument("--out_file", type=lambda x: Path(x), required=True)
    return parser


def get_id(id_str: str) -> str:
    return id_str[len(ID_PREFIX):-1]


def strip_label(label: str) -> str:
    # "Hyperandrogenism"@en -> Hyperandrogenism
    return label[1:-4]


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


def main(mesh_dump: Path, out_file: Path):
    entities: Dict[str, Dict[EntityType, List[str]]] = {}
    with mesh_dump.open('r') as mesh:
        lines = mesh.readlines()
        for line in tqdm(lines):
            id_str, field_str, value_str = line.split(' ', maxsplit=2)
            ent_id = get_id(id_str)  # Omit last > and prefix
            if ent_id not in entities:
                entities[ent_id] = defaultdict(list)
            try:
                ent_type = EntityType(field_str)
                entities[ent_id][ent_type].append(value_str[:-3])
            except ValueError:
                continue

    diseases: Dict[str, Set[str]] = {}

    def add_topical_descriptor(t_id: str):
        if t_id not in diseases:
            diseases[t_id] = set(get_terms_from_concepts(entities, t_id))
            if EntityType.BROADER_DESCRIPTOR in entities[t_id]:
                for broader in entities[t_id][EntityType.BROADER_DESCRIPTOR]:
                    broader_id = get_id(broader)
                    add_topical_descriptor(broader_id)

    for ent, d in entities.items():
        if EntityType.TYPE in d and d[EntityType.TYPE][0] == DISEASE_TYPE:
            diseases[ent] = set(get_terms_from_concepts(entities, ent))
            for disease in d[EntityType.PREFERRED_MAPPED_TO]:
                disease_id = get_id(disease)
                add_topical_descriptor(disease_id)
        if EntityType.TREE_NUMBER in d and get_id(d[EntityType.TREE_NUMBER][0]).startswith('C'):
            add_topical_descriptor(ent)
    
    with out_file.open('w') as out:
        for d_id, aliases in diseases.items():
            aliases_str = '|'.join(aliases)
            out.write(f'{d_id}||{aliases_str}\n')


if __name__ == '__main__':
    parser = setup_argparser()
    args_ = parser.parse_args()
    main(args_.mesh_dump, args_.out_file)
