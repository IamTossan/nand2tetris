import pathlib

class CodeGenerator:
    def __init__(self, file_name, tokens):
        self.file_name = file_name
        self.tokens = tokens

    def write(self, ls):
        with open(f"dist/{self.file_name}.vm", "w") as f:
            for l in ls:
                f.write(f"{l}\n")

    def run(self):
        a = self.compile(self.tokens)
        # pprint.pprint(list(a))

        self.write(list(a))

    def get_identifier(self, name):
        pass

    def set_identifier(self, name, kind):
        pass

    def compile(self, ls):
        self.class_name = next(x for x in ls if x['kind'] == "identifier")['label']

        return ls