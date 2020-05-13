import argparse
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple, Optional, Dict, List

from tqdm import tqdm


def setup_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--dump", type=lambda x: Path(x), required=True)
    parser.add_argument("--out", type=lambda x: Path(x), required=True)
    return parser


class SpeciesEntry(NamedTuple):
    id: str
    name: str
    unique_name: Optional[str]
    s_type: str


def main(dump: Path, out: Path):
    same_name: Dict[str, List[SpeciesEntry]] = defaultdict(list)
    with dump.open('r') as f:
        lines = f.readlines()
        for line in tqdm(lines, 'Processing lines'):  # type: str
            parts = line.split('|')
            s_id = parts[0].strip()
            s_name = parts[1].strip()
            unique_name: Optional[str] = parts[2].strip()
            unique_name = None if unique_name == '' else unique_name
            s_type = parts[3].strip()
            entry = SpeciesEntry(s_id, s_name, unique_name, s_type)
            if entry.unique_name:
                same_name[entry.name].append(entry)

        same_name = {k: v for k, v in same_name.items() if len(v) > 1}

    number = 0
    with out.open('w') as f:
        for name, items in same_name.items():  # type: str, List[SpeciesEntry]
            f.write(name + '\n')
            for item in items:
                number += 1
                f.write(f'\t{item}\n')
            f.write('\n')
    print(f'Total {len(lines)} names processed.')
    print(f'Found {number} conflicting names grouped into {len(same_name)} chunks.')


if __name__ == '__main__':
    argparser = setup_argparser()
    args_ = argparser.parse_args()
    main(args_.dump, args_.out)
