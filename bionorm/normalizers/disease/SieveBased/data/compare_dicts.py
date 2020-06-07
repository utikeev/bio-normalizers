"""
Compare default sieve-based terminology with the one mined from MeSH dump.
"""

import argparse
from pathlib import Path
from typing import Set


def setup_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("--mesh_dump", type=lambda x: Path(x), required=True)
    parser.add_argument("--terminology", type=lambda x: Path(x), required=True)
    return parser


def main(mesh_dump: Path, terminology: Path):
    print(mesh_dump.name)
    print(terminology.name)
    mesh_ids: Set[str] = set()
    with mesh_dump.open('r') as mesh:
        lines = mesh.readlines()
        for line in lines:
            mesh_ids.add(line.split('||')[0])
    with terminology.open('r') as terminology:
        lines = terminology.readlines()
        for line in lines:
            term_id = line.split('||')[0].split('|')[0]
            if term_id not in mesh_ids and not term_id[0].isdigit():
                print(term_id)


if __name__ == '__main__':
    parser = setup_argparser()
    args_ = parser.parse_args()
    main(args_.mesh_dump, args_.terminology)