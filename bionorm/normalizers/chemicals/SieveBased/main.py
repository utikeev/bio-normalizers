from bionorm.common.models import ChemicalMention, Location, Passage, Paper
from bionorm.normalizers.chemicals import ChemicalsSieveBasedNormalizer


def main():
    normalizer = ChemicalsSieveBasedNormalizer.default()
    normalizer.load_data(verbose=True)

    passage = Passage('abstract', '', chemicals=[
        ChemicalMention(Location(19, 54), '2,3,7,8-tetrachlorodibenzo-p-dioxin'),
        ChemicalMention(Location(133, 168), '2,3,7,8-Tetrachlorodibenzo-p-dioxin'),
        ChemicalMention(Location(170, 174), 'TCDD'),
        ChemicalMention(Location(763, 779), 'aryl hydrocarbon'),
        ChemicalMention(Location(1396, 1408), 'testosterone'),
    ])
    paper = Paper('1036571', [passage], [])
    normalizer.normalize(paper, verbose=True)


if __name__ == '__main__':
    main()
