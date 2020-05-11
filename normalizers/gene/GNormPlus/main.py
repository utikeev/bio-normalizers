from normalizers.gene.GNormPlus.models.paper import Paper, Passage, Annotation, Location, AnnotationType
from normalizers.gene.GNormPlus.normalizer import GNormPlus

if __name__ == '__main__':

    title = Passage('title', 'p53', [Annotation(Location(0, 3), 'p53', AnnotationType.GENE)])
    paper = Paper('0', [title], [])
    normalizer = GNormPlus.default()
    normalizer.load_data(verbose=True)
    normalizer.normalize(paper)
    print(paper)

    print('Hello, world!')
