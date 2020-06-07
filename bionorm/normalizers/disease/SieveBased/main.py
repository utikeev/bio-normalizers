from bionorm.common.models import DiseaseMention, Location, Passage, Paper, Abbreviation
from bionorm.normalizers.disease.SieveBased import DiseaseSieveBasedNormalizer


def main():
    normalizer = DiseaseSieveBasedNormalizer.default()
    normalizer.load_data(verbose=True)

    passage = Passage('abstract', 'Scleroderma renal crisis (SRC) is a rare complication of systemic sclerosis (SSc) but can be severe '
                                  'enough to require temporary or permanent renal replacement therapy. Moderate to high dose '
                                  'corticosteroid use is recognized as a major risk factor for SRC. Furthermore, there have been reports '
                                  'of thrombotic microangiopathy precipitated by cyclosporine in patients with SSc. In this article, '
                                  'we report a patient with SRC induced by tacrolimus and corticosteroids. The aim of this work is to '
                                  'call attention to the risk of tacrolimus use in patients with SSc', diseases=[
        DiseaseMention(Location(11, 35), 'scleroderma renal crisis'),
        DiseaseMention(Location(117, 120), 'SRC'),
    ])
    paper = Paper('1036571', [passage], [Abbreviation('scleroderma renal crisis', 'SRC')])
    normalizer.normalize(paper, verbose=True)


if __name__ == '__main__':
    main()
