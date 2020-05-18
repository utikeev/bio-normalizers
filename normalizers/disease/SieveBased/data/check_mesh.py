import argparse
from pathlib import Path


def setup_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument('--mesh_terminology', type=lambda x: Path(x), required=True)
    return parser


def main(mesh: Path):
    print(mesh.name)


if __name__ == '__main__':
    parser = setup_argparser()
    args_ = parser.parse_args()
    main(args_.mesh_terminology)
