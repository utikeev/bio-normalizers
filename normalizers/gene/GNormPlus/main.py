from common.models.bio_entities import GeneMention
from common.models.paper import Passage, Paper
from common.models.util import Location
from normalizers.gene.GNormPlus.config import TEST_CONFIG
from normalizers.gene.GNormPlus.normalizer import GNormPlus

if __name__ == '__main__':
    title = Passage('title', 'rCNT1', genes=[GeneMention(Location(0, 5), 'rCNT1')])
    paper = Paper('0', [title], [])
    normalizer = GNormPlus(TEST_CONFIG)
    normalizer.load_data(verbose=True)
    normalizer.normalize(paper)
    print(paper)

    print('Hello, world!')
