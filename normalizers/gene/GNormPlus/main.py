from normalizers.gene.GNormPlus.models.paper import Passage, Annotation, Location, AnnotationType, Paper, Abbreviation
from normalizers.gene.GNormPlus.normalizer import GNormPlus

if __name__ == '__main__':
    normalizer = GNormPlus.default()
    normalizer.load_data(verbose=True)
    # for entry in normalizer.gene_without_sp_prefix:
    #     print(entry)

    title = 'Amphibians as a model to study endocrine disruptors: II. Estrogenic activity of environmental chemicals in vitro and in vivo.'
    title_passage = Passage('title', title, [])
    abstract = 'Several environmental chemicals are known to have estrogenic activity by interacting with development and functions of ' \
               'endocrine systems in nearly all classes of vertebrates. In order to get a better insight of potential estrogenic effects ' \
               'on amphibians caused by environmental pollution this study aims to develop a model for investigating endocrine disruptors ' \
               'using the amphibian Xenopus laevis. In that model the potential estrogenic activity of endocrine disruptors is determined ' \
               'at several levels of investigation: (I) binding to liver estrogen receptor; (II) estrogenicity in vitro by inducing ' \
               'vitellogenin synthesis in primary cultured hepatocytes; and (III) in vivo effects on sexual development. Here we deal ' \
               'with establishing methods to assay estrogenic activity of environmental chemicals in vitro and in vivo. In vitro we used ' \
               'a semiquantitative reverse transcriptase-polymerase chain reaction (RT-PCR) technique to determine mRNA-induction of the ' \
               'estrogenic biomarker vitellogenin in primary cultured hepatocytes of male Xenopus laevis. Time courses of ' \
               'vitellogenin-mRNA in the presence and absence of 10(-6) M 17 beta-estradiol (E2) resulted in a marked loss of mRNA from ' \
               'controls after 2 days while E2 treatment kept vitellogenin-mRNA at a relatively stable level. After 36 h of incubation ' \
               'estrogenic activities of E2, 4-nonylphenol (NP), and 2,2-bis-(4-hydroxyphenyl)-propan (bisphenol A) at concentrations ' \
               'ranging from 10(-10) to 10(-5) M were assayed by RT-PCR of vitellogenin-mRNA and showed the following ranking of ' \
               'dose-dependent potency: E2 &gt; NP &gt; bisphenol A. These in vitro results were confirmed further by in vivo experiments ' \
               'determining sexual differentiation of Xenopus laevis after exposure to E2 and environmental chemicals during larval ' \
               'development. Concentrations of 10(-7) and 10(-8) M E2 as well as 10(-7) M of NP or bisphenol A caused a significant ' \
               'higher number of female phenotypes compared to controls indicating a similar ranking of estrogenic potencies in vivo as ' \
               'in vitro. In addition, butylhydroxyanisol and octylphenol, both showed feminization at 10(-7) M while octylphenol was ' \
               'also effective at 10(-8) M. In summary these results demonstrate for the first time the use of a semiquantitative RT-PCR ' \
               'technique for screening estrogenicity by assaying mRNA induction of the estrogenic biomarker vitellogenin in vitro. The ' \
               'combination of this newly developed method with classical exposure experiments is necessary for determination of the ' \
               'biological significance of estrogenic chemicals. '
    abstract_passage = Passage('abstract', abstract, [])

    mentions = """
    GENE vitellogenin 726 738
    GENE reverse transcriptase 984 1005
    GENE RT 1033 1035
    GENE vitellogenin 1107 1119
    GENE vitellogenin-mRNA 1192 1209
    GENE mRNA 1302 1306
    GENE vitellogenin-mRNA 1358 1375
    GENE vitellogenin-mRNA 1608 1625
    GENE vitellogenin 2468 2480
    """

    for mention in mentions.split('\n'):
        mention = mention.strip()
        if mention == '':
            continue
        parts = mention.split()
        mention = ' '.join(parts[1:-2])
        start = int(parts[-2])
        end = int(parts[-1])
        abstract_passage.annotations.append(Annotation(Location(start - len(title), end - len(title)), mention, AnnotationType.GENE))

    paper = Paper('0', [title_passage, abstract_passage], [])
    paper.abbreviations.append(Abbreviation('reverse transcriptase', 'RT'))

    normalizer.normalize(paper)
    print([p.annotations for p in paper.passages])

    #     tree = PrefixTree(normalizer.suffix_translation_map)
    #     lines = """1	aaronsohnia
    # 1-1	pubescens	99022
    # 1-1-1	desf
    # 1-1-1-1	k
    # 1-1-1-1-1	bremer
    # 1-1-1-1-1-1	humphries	99022
    # 1-2	factorovskyi	314051
    # 1-2-1	warburg
    # 1-2-1-1	eig	314051
    # 2	aaroniella
    # 2-1	sp
    # 2-1-1	bioug
    # 2-1-1-1	31029
    # 2-1-1-1-1	e
    # 2-1-1-1-1-1	03	2086899
    # 2-1-1-1-1-2	08	2086897
    # 2-1-1-2	02071
    # 2-1-1-2-1	a
    # 2-1-1-2-1-1	12	2086895
    # 2-1-1-3	25742
    # 2-1-1-3-1	a
    # 2-1-1-3-1-1	05	2086898""".split('\n')
    #     print(lines)
    #     tree.load_from_lines(lines)
    #     print(tree.pretty_print())

    print('Hello, world!')
