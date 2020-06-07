import re

SPECIES_PATTERN = re.compile(r'\**(\d+)$')
SCORE_PATTERN = re.compile(r'\d+-(\d+)')
MULTI_GENE_PATTERN = re.compile(r'\*(\d+(-\d+))')
SINGLE_GENE_PATTERN = re.compile(r'\d+(-\d+)')
HOMO_GMT_PATTERN = re.compile(r'^(\d+)-(\d+)$')
GENE_GMT_PATTERN = re.compile(r'^(\d+)$')
NUMBER_PATTERN = re.compile(r'\d+')

PREPROCESS_PATTERN0 = re.compile(r'^(.*[0-9A-Z])\s*p$')
PREPROCESS_PATTERN1 = re.compile('^(.+)nu$')
PREPROCESS_PATTERN2 = re.compile('^(.*)alpha(.*)$')
PREPROCESS_PATTERN3 = re.compile('^(.*)beta(.*)$')
PREPROCESS_PATTERN4 = re.compile(r'^(.+\d)a$')
PREPROCESS_PATTERN5 = re.compile(r'^(.+\d)b$')
PREPROCESS_PATTERN6 = re.compile('^(.+)II([a-z])$')
PREPROCESS_PATTERN7 = re.compile('^(.+)III([a-z])$')
