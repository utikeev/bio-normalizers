from typing import Callable

from tqdm import tqdm


def process_file(path: str, process_fn: Callable[[str], None], *, verbose: bool = False, message: str = ''):
    with open(path, 'r') as f:
        lines = f.readlines()
        if verbose:
            lines = tqdm(lines, message)
        for line in lines:
            stripped = line.strip()
            if stripped:
                process_fn(stripped)
