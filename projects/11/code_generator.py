import pathlib

import pprint


class CodeGenerator:
    def __init__(self, file_name, tokens):
        self.file_name = file_name
        self.tokens = tokens
        self.static = {}
        self.field = {}

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

    def set_class_vars(self, ls):
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
                self.static[v['name']] = v
            else:
                v = {
                    "name": ls.pop(0)["label"],
                    "type": _type,
                    "index": len(self.field),
                }
                self.field[v['name']] = v
            if ls[0]["label"] == ",":
                ls.pop(0)
        ls.pop(0)
        ls.pop(0)

    def get_args(self, ls):
        args = {}
        ls.pop(0)
        while ls[0]['kind'] != 'parameterList' and ls[0]['type'] != 'close':
            _type = ls.pop(0)["label"]
            name = ls.pop(0)["label"]
            args[name] = {
                "name": name,
                "type": _type,
                "index": len(args),
            }
            if ls[0]['kind'] != 'parameterList':
                ls.pop(0)
        ls.pop(0)
        return args

    def get_local(self, ls):
        local = {}
        while ls[0]['kind'] == 'varDec' and ls[0]['type'] == 'open':
            ls.pop(0)
            ls.pop(0)
            _type = ls.pop(0)['label']
            while ls[0]['kind'] == 'identifier':
                name = ls.pop(0)['label']
                local[name] = {
                    "name": name,
                    "type": _type,
                    "index": len(local),
                }
                ls.pop(0)
            ls.pop(0)
        return local

    def compile_subroutine_body(self, ls, args):
        ls.pop(0)
        ls.pop(0)
        while ls[0]['kind'] != 'subroutineBody':
            if ls[0]['kind'] == 'varDec':
                local = self.get_local(ls)
            else:
                ls.pop(0)
        print(args)

    def compile_subroutine(self, ls):
        ls.pop(0)
        kind = ls.pop(0)['label']
        return_type = ls.pop(0)['label']
        subroutine_name = ls.pop(0)['label']

        ls.pop(0)
        args = self.get_args(ls)
        ls.pop(0)

        self.compile_subroutine_body(ls, args)


    def compile(self, ls):
        pprint.pprint(ls[:20])
        while not (ls[0]["depth"] == 1 and ls[0]["kind"] == "identifier"):
            ls.pop(0)
        self.class_name = ls.pop(0)["label"]
        ls.pop(0)
        while ls[0]["kind"] == "classVarDec":
            self.set_class_vars(ls)
        while ls[0]["kind"] == "subroutineDec":
            self.compile_subroutine(ls)

        pprint.pprint(ls[:10])

        return ls
