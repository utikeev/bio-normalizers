from normalizers.disease.SieveBased.config.config import SieveBasedConfig
from normalizers.disease.SieveBased.processing.text_processor import TextProcessor


def main():
    processor = TextProcessor(SieveBasedConfig())
    processor.load_data(verbose=True)

    initial = 'Three grey geese on the green grass grazing grey were the geese and green was the grazing'
    print(processor.get_stemmed_phrase(initial))


if __name__ == '__main__':
    main()
