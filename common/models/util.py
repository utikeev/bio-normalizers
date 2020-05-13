class Location:
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def __str__(self):
        return f'[{self.start}, {self.end}]'

    def __repr__(self):
        return str(self)


class Abbreviation:
    def __init__(self, long_form: str, short_form: str):
        self.long_form = long_form
        self.short_form = short_form

    def __str__(self):
        return f'{self.short_form} -> {self.long_form}'

    def __repr__(self):
        return str(self)
