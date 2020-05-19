from common.models.bio_entities import DiseaseMention
from common.models.paper import Passage, Paper
from common.models.util import Location
from normalizers.disease.SieveBased.normalizer import DiseaseSieveBasedNormalizer


def main():
    normalizer = DiseaseSieveBasedNormalizer.default()
    normalizer.load_data(verbose=True)

    passage = Passage('abstract', '', diseases=[
        DiseaseMention(Location(11, 24), 'renal failure'),
        DiseaseMention(Location(11, 24), 'renal failure'),
        DiseaseMention(Location(29, 37), 'myositis'),
        DiseaseMention(Location(48, 74), 'phenytoin hypersensitivity'),
        DiseaseMention(Location(144, 166), 'maculopapular erythema'),
        DiseaseMention(Location(228, 241), 'renal failure'),
        DiseaseMention(Location(246, 254), 'myositis'),
        DiseaseMention(Location(270, 275), 'fever'),
        DiseaseMention(Location(277, 292), 'lymphadenopathy'),
        DiseaseMention(Location(294, 316), 'exfoliative dermatitis'),
        DiseaseMention(Location(322, 331), 'hepatitis'),
        DiseaseMention(Location(452, 471), 'renal insufficiency'),
        DiseaseMention(Location(491, 504), 'renal failure'),
        DiseaseMention(Location(509, 517), 'myositis'),
        DiseaseMention(Location(537, 573), 'phenytoin hypersensitivity reactions'),
        DiseaseMention(Location(612, 629), 'morbilliform rash'),
    ])
    paper = Paper('1036571', [passage], [])
    normalizer.normalize(paper, verbose=True)


if __name__ == '__main__':
    main()
