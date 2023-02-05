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
                self.static[v["name"]] = v
            else:
                v = {
                    "name": ls.pop(0)["label"],
                    "type": _type,
                    "index": len(self.field),
                }
                self.field[v["name"]] = v
            if ls[0]["label"] == ",":
                ls.pop(0)
        ls.pop(0)
        ls.pop(0)

    def get_args(self, ls):
        args = {}
        ls.pop(0)
        while ls[0]["kind"] != "parameterList" and ls[0]["type"] != "close":
            _type = ls.pop(0)["label"]
            name = ls.pop(0)["label"]
            args[name] = {
                "name": name,
                "type": _type,
                "index": len(args),
            }
            if ls[0]["kind"] != "parameterList":
                ls.pop(0)
        ls.pop(0)
        return args

    def get_local(self, ls):
        local = {}
        while ls[0]["kind"] == "varDec" and ls[0]["type"] == "open":
            ls.pop(0)
            ls.pop(0)
            _type = ls.pop(0)["label"]
            while ls[0]["kind"] == "identifier":
                name = ls.pop(0)["label"]
                local[name] = {
                    "name": name,
                    "type": _type,
                    "index": len(local),
                }
                ls.pop(0)
            ls.pop(0)
        return local

    def compile_term(self, ls, acc, vars):
        ls.pop(0)
        term = ls.pop(0)
        if term["kind"] == "integerConstant":
            acc.append(f"push constant {term['label']}")
        elif term["label"] == "(":
            self.compile_expression(ls, acc, vars)
            ls.pop(0)
        ls.pop(0)

    def compile_op(self, ls, acc, vars):
        op = ls.pop(0)["label"]
        if op == "+":
            return "add"
        if op == "-":
            return "sub"
        if op == "*":
            return "call Math.multiply 2"

    def compile_expression(self, ls, acc, vars):
        ls.pop(0)
        self.compile_term(ls, acc, vars)
        while ls[0]["kind"] != "expression":
            op = self.compile_op(ls, acc, vars)
            self.compile_term(ls, acc, vars)
            acc.append(op)
        ls.pop(0)
        return 0

    def compile_expression_list(self, ls, acc, vars):
        ls.pop(0)
        expressions = []
        while ls[0]["kind"] != "expressionList":
            expressions.append(self.compile_expression(ls, acc, vars))
        ls.pop(0)
        return expressions

    def compile_do_statement(self, ls, acc, vars):
        ls.pop(0)
        ls.pop(0)
        func_name = "{}{}{}".format(
            ls.pop(0)["label"], ls.pop(0)["label"], ls.pop(0)["label"]
        )
        ls.pop(0)
        expressions = self.compile_expression_list(ls, acc, vars)
        ls.pop(0)
        ls.pop(0)
        ls.pop(0)
        acc.append(f"call {func_name} {len(expressions)}")
        acc.append("pop temp 0")

    def compile_return_statement(self, ls, acc, vars):
        ls.pop(0)
        ls.pop(0)
        ls.pop(0)
        ls.pop(0)
        acc.append("push constant 0")
        acc.append("return")

    def compile_subroutine_body(self, ls, acc, args):
        ls.pop(0)
        ls.pop(0)

        local = {}
        if ls[0]["kind"] == "varDec":
            local = self.get_local(ls)

        ls.pop(0)
        vars = {
            "static": self.static,
            "field": self.field,
            "args": args,
            "local": local,
        }
        while ls[0]["kind"] != "statements":
            if ls[0]["kind"] == "doStatement":
                self.compile_do_statement(ls, acc, vars)
            elif ls[0]["kind"] == "returnStatement":
                self.compile_return_statement(ls, acc, vars)
            else:
                ls.pop(0)
        ls.pop(0)
        ls.pop(0)

    def compile_subroutine(self, ls, acc):
        ls.pop(0)
        kind = ls.pop(0)["label"]
        return_type = ls.pop(0)["label"]
        subroutine_name = ls.pop(0)["label"]

        ls.pop(0)
        args = self.get_args(ls)
        ls.pop(0)

        acc.append(f"function {self.class_name}.{subroutine_name} {len(args)}")
        self.compile_subroutine_body(ls, acc, args)
        ls.pop(0)

    def compile(self, ls):
        acc = []
        while not (ls[0]["depth"] == 1 and ls[0]["kind"] == "identifier"):
            ls.pop(0)
        self.class_name = ls.pop(0)["label"]
        ls.pop(0)

        if ls[0]["kind"] == "classVarDec":
            self.set_class_vars(ls)

        self.compile_subroutine(ls, acc)
        ls.pop(0)
        ls.pop(0)

        pprint.pprint(acc)

        return acc
