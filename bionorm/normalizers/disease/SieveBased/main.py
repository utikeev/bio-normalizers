from bionorm.common.models import DiseaseMention, Location, Passage, Paper, Abbreviation
from bionorm.normalizers.disease.SieveBased import DiseaseSieveBasedNormalizer


def main():
    normalizer = DiseaseSieveBasedNormalizer.default()
    normalizer.load_data(verbose=True)

    passage = Passage('abstract', '', diseases=[
        DiseaseMention(Location(86, 107), 'dysrhythmias'),
    ])
    paper = Paper('1036571', [passage], [Abbreviation('scleroderma renal crisis', 'SRC')])
    normalizer.normalize(paper, verbose=True)


if __name__ == '__main__':
    main()
