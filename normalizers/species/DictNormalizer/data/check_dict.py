import argparse
from pathlib import Path


def setup_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--dict", type=lambda x: Path(x), required=True)
    return parser


def main(dict_path: Path):
    with dict_path.open('r') as f:
        lines = f.readlines()
        print(lines[0])


if __name__ == '__main__':
    argparser = setup_argparser()
    args_ = argparser.parse_args()
    main(args_.dict)
