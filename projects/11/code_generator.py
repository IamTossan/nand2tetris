import pathlib

import pprint


class CodeGenerator:
    def __init__(self, file_name, tokens):
        self.file_name = file_name
        self.tokens = tokens
        self.static = []
        self.field = []

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

    def compile_class_vars(self, ls):
        ls.pop(0)
        kind = ls.pop(0)["label"]
        _type = ls.pop(0)["label"]
        while ls[0]["label"] != ";":
            if kind == "static":
                v = {
                    "name": ls.pop(0)["label"],
                    "type": _type,
                    "index": len(self.static),
                }
                self.static.append(v)
            else:
                v = {
                    "name": ls.pop(0)["label"],
                    "type": _type,
                    "index": len(self.field),
                }
                self.field.append(v)
            if ls[0]["label"] == ",":
                ls.pop(0)
        ls.pop(0)
        ls.pop(0)

    def compile(self, ls):
        pprint.pprint(ls[:20])
        while not (ls[0]["depth"] == 1 and ls[0]["kind"] == "identifier"):
            ls.pop(0)
        self.class_name = ls.pop(0)["label"]
        ls.pop(0)
        while ls[0]["kind"] == "classVarDec":
            self.compile_class_vars(ls)

        pprint.pprint(ls[:10])

        return ls
