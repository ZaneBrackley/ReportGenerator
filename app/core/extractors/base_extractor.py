class BaseExtractor:
    def __init__(self, tables):
        self.tables = tables

    def parse(self):
        raise NotImplementedError("Subclasses must implement the parse() method")
