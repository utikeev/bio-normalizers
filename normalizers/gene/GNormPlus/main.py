from normalizers.gene.GNormPlus.models.paper import Paper, Passage, GeneAnnotation, Location
from normalizers.gene.GNormPlus.normalizer import GNormPlus

if __name__ == '__main__':

    title = Passage('title', 'rCNT1', [GeneAnnotation(Location(0, 5), 'rCNT1')])
    paper = Paper('0', [title], [])
    normalizer = GNormPlus.default()
    normalizer.load_data(verbose=True)
    normalizer.normalize(paper)
    print(paper)

    print('Hello, world!')
