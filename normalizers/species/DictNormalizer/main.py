from common.models import Passage, Paper, SpeciesMention, Location
from normalizers.species.DictNormalizer.normalizer import DictNormalizer

if __name__ == '__main__':
    normalizer = DictNormalizer.default()
    normalizer.load_data(verbose=True)
    title = Passage('title', 'mice', species=[SpeciesMention(Location(0, 5), 'human')])
    paper = Paper('0', [title], [])
    normalizer.normalize(paper)
    print(paper)
