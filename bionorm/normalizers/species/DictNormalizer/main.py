from bionorm.common.models import Passage, Paper, SpeciesMention, Location
from bionorm.normalizers.species.DictNormalizer import DictNormalizer

if __name__ == '__main__':
    normalizer = DictNormalizer.default()
    normalizer.load_data(verbose=True)
    title = Passage('title', 'mice', species=[SpeciesMention(Location(0, 5), 'human')])
    paper = Paper('0', [title], [])
    normalizer.normalize(paper)
    print(paper)
