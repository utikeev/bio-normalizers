from bionorm.common.models import GeneMention, Location, Passage, Paper
from bionorm.normalizers.gene.GNormPlus import GNormPlus, TEST_CONFIG

if __name__ == '__main__':
    title = Passage('title', 'rCNT1', genes=[GeneMention(Location(0, 5), 'rCNT1')])
    paper = Paper('0', [title], [])
    normalizer = GNormPlus(TEST_CONFIG)
    normalizer.load_data(verbose=True)
    normalizer.normalize(paper)
    print(paper)

    print('Hello, world!')
