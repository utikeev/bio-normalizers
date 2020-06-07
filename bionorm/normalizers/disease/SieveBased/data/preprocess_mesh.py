"""
Script to build terminology dictionary from MeSH® dump in RDF format, which can be downloaded here:
ftp://nlmpubs.nlm.nih.gov/online/mesh/rdf/
Downloaded data is the courtesy of the U.S. National Library of Medicine.
"""

import argparse
from pathlib import Path

from bionorm.common.util import DISEASE_TYPE, collect_entities


def setup_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("--mesh_dump", type=lambda x: Path(x), required=True)
    parser.add_argument("--out_file", type=lambda x: Path(x), required=True)
    return parser


def main(mesh_dump: Path, out_file: Path):
    diseases = collect_entities(mesh_dump, 'C', DISEASE_TYPE)
    
    with out_file.open('w') as out:
        for d_id, aliases in diseases.items():
            aliases_str = '|'.join(aliases)
            out.write(f'{d_id}||{aliases_str}\n')


if __name__ == '__main__':
    parser = setup_argparser()
    args_ = parser.parse_args()
    main(args_.mesh_dump, args_.out_file)
