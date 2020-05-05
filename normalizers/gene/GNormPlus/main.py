from normalizers.gene.GNormPlus.util.trees import PrefixTree
from normalizers.gene.GNormPlus.normalizer import GNormPlus

if __name__ == '__main__':
    normalizer = GNormPlus.default()
    normalizer.load_data(verbose=True)
    for entry in normalizer.gene_without_sp_prefix:
        print(entry)

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
