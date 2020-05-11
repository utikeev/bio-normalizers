from normalizers.gene.GNormPlus.models.paper import Paper, Passage, Annotation, Location, AnnotationType
from normalizers.gene.GNormPlus.processing.species import assign_species

if __name__ == '__main__':
    title = Passage('title', 'mGENE-123', [Annotation(Location(0, 9), 'mGENE-123', AnnotationType.GENE)])
    paper = Paper('0', [title], [])
    assign_species(paper, {}, set(), set(), {'10090': 'm'})
    print(paper)

    print('Hello, world!')
