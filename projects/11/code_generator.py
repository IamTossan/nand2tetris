import pathlib
import uuid

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
                    "kind": "static",
                    "index": len(self.static),
                }
                self.static[v["name"]] = v
            else:
                v = {
                    "name": ls.pop(0)["label"],
                    "type": _type,
                    "kind": "this",
                    "index": len(self.field),
                }
                self.field[v["name"]] = v
            if ls[0]["label"] == ",":
                ls.pop(0)
        ls.pop(0)
        ls.pop(0)

    def get_args(self, ls, subroutine_kind):
        args = {}
        if subroutine_kind == "method":
            args["this"] = {
                "name": "this",
                "type": self.class_name,
                "kind": "argument",
                "index": len(args),
            }
        ls.pop(0)
        while ls[0]["kind"] != "parameterList" and ls[0]["type"] != "close":
            _type = ls.pop(0)["label"]
            name = ls.pop(0)["label"]
            args[name] = {
                "name": name,
                "type": _type,
                "kind": "argument",
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
                    "kind": "local",
                    "index": len(local),
                }
                ls.pop(0)
            ls.pop(0)
        return local

    def compile_term(self, ls, acc, vars):
        ls.pop(0)
        if ls[0]["kind"] == "integerConstant":
            acc.append(f"push constant {ls[0]['label']}")
            ls.pop(0)
        elif ls[0]["label"] == "(":
            ls.pop(0)
            self.compile_expression(ls, acc, vars)
            ls.pop(0)
        elif ls[1]["label"] == ".":
            o = ls.pop(0)["label"]
            ls.pop(0)
            f = ls.pop(0)

            if o in vars:
                acc.append(f"push {vars[o]['kind']} {vars[o]['index']}")

            print(o, vars)
            func_name = "{}.{}".format(o, f["label"])
            ls.pop(0)
            expressions = self.compile_expression_list(ls, acc, vars)
            ls.pop(0)
            acc.append(f"call {func_name} {len(expressions)}")
        elif ls[0]["label"] == "-":
            ls.pop(0)
            self.compile_term(ls, acc, vars)
            acc.append("neg")
        elif ls[0]["label"] == "~":
            ls.pop(0)
            self.compile_term(ls, acc, vars)
            acc.append("not")
        elif ls[0]["kind"] == "identifier":
            v = vars[ls.pop(0)["label"]]
            acc.append(f"push {v['kind']} {v['index']}")
        elif ls[0]["label"] == "true":
            ls.pop(0)
            acc.append("push constant 0")
            acc.append("not")
        elif ls[0]["label"] == "false":
            ls.pop(0)
            acc.append("push constant 0")
        elif ls[0]["label"] == "this":
            ls.pop(0)
            acc.append("push pointer 0")
        else:
            print("else term", ls[0])
            # pprint.pprint(ls[:10])
        ls.pop(0)

    def compile_op(self, ls, acc, vars):
        op = ls.pop(0)["label"]
        if op == "+":
            return "add"
        if op == "-":
            return "sub"
        if op == "=":
            return "eq"
        if op == "&amp;":
            return "and"
        if op == "&gt;":
            return "gt"
        if op == "&lt;":
            return "lt"
        if op == "*":
            return "call Math.multiply 2"
        if op == "/":
            return "call Math.divide 2"

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
            if ls[0]["kind"] != "expressionList":
                ls.pop(0)
        ls.pop(0)
        return expressions

    def compile_do_statement(self, ls, acc, vars):
        ls.pop(0)
        ls.pop(0)
        o = ls.pop(0)["label"]
        s = ls.pop(0)["label"]

        if o in vars:
            acc.append(f"push {vars[o]['kind']} {vars[o]['index']}")

        if s == "(":
            func_name = f"{self.class_name}.{o}"
            acc.append("push pointer 0")
        else:
            func_name = "{}.{}".format(
                vars[o]["type"] if o in vars else o, ls.pop(0)["label"]
            )
            ls.pop(0)

        expressions = self.compile_expression_list(ls, acc, vars)
        ls.pop(0)
        ls.pop(0)
        ls.pop(0)
        acc.append(
            f"call {func_name} {len(expressions) + (1 if o in vars or s == '(' else 0)}"
        )
        acc.append("pop temp 0")

    def compile_return_statement(self, ls, acc, vars):
        ls.pop(0)
        ls.pop(0)
        if ls[0]["label"] != ";":
            self.compile_expression(ls, acc, vars)
        else:
            acc.append("push constant 0")
        ls.pop(0)
        ls.pop(0)
        acc.append("return")

    def compile_let_statement(self, ls, acc, vars):
        ls.pop(0)
        ls.pop(0)
        target = vars[ls.pop(0)["label"]]
        ls.pop(0)
        self.compile_expression(ls, acc, vars)
        acc.append(f"pop {target['kind']} {target['index']}")
        ls.pop(0)
        ls.pop(0)

    def compile_if_statement(self, ls, acc, vars):
        ls.pop(0)
        ls.pop(0)
        ls.pop(0)
        self.compile_expression(ls, acc, vars)
        acc.append("not")
        end_if_label = uuid.uuid4()
        else_label = uuid.uuid4()
        acc.append(f"if-goto {else_label}")
        ls.pop(0)
        ls.pop(0)

        self.compile_statements(ls, acc, vars)
        ls.pop(0)
        if ls[0]["label"] == "else":
            acc.append(f"goto {end_if_label}")
            acc.append(f"label {else_label}")
            ls.pop(0)
            ls.pop(0)
            self.compile_statements(ls, acc, vars)
            ls.pop(0)
        else:
            acc.append(f"label {else_label}")
        acc.append(f"label {end_if_label}")
        ls.pop(0)

    def compile_while_statement(self, ls, acc, vars):
        while_start = uuid.uuid4()
        while_end = uuid.uuid4()

        ls.pop(0)
        ls.pop(0)
        acc.append(f"label {while_start}")
        ls.pop(0)
        self.compile_expression(ls, acc, vars)
        acc.append("not")
        acc.append(f"if-goto {while_end}")
        ls.pop(0)
        ls.pop(0)
        self.compile_statements(ls, acc, vars)
        acc.append(f"goto {while_start}")
        acc.append(f"label {while_end}")
        ls.pop(0)
        ls.pop(0)

    def compile_statements(self, ls, acc, vars):
        ls.pop(0)
        while ls[0]["kind"] != "statements":
            if ls[0]["kind"] == "doStatement":
                self.compile_do_statement(ls, acc, vars)
            elif ls[0]["kind"] == "returnStatement":
                self.compile_return_statement(ls, acc, vars)
            elif ls[0]["kind"] == "letStatement":
                self.compile_let_statement(ls, acc, vars)
            elif ls[0]["kind"] == "ifStatement":
                self.compile_if_statement(ls, acc, vars)
            elif ls[0]["kind"] == "whileStatement":
                self.compile_while_statement(ls, acc, vars)
            else:
                ls.pop(0)
        ls.pop(0)

    def compile_subroutine_body(self, ls, acc, args, subroutine_name, subroutine_kind):
        ls.pop(0)
        ls.pop(0)

        local = {}
        if ls[0]["kind"] == "varDec":
            local = self.get_local(ls)

        vars = {
            **self.static,
            **self.field,
            **args,
            **local,
        }
        acc.append(f"function {self.class_name}.{subroutine_name} {len(local)}")
        if subroutine_kind == "constructor":
            acc.append(f"push constant {len(self.field)}")
            acc.append("call Memory.alloc 1")
            acc.append("pop pointer 0")
        elif subroutine_kind == "method":
            acc.append("push argument 0")
            acc.append("pop pointer 0")
        self.compile_statements(ls, acc, vars)
        ls.pop(0)

    def compile_subroutine(self, ls, acc):
        ls.pop(0)
        kind = ls.pop(0)["label"]
        return_type = ls.pop(0)["label"]
        subroutine_name = ls.pop(0)["label"]

        ls.pop(0)
        args = self.get_args(ls, kind)
        ls.pop(0)

        acc.append("")
        self.compile_subroutine_body(ls, acc, args, subroutine_name, kind)
        ls.pop(0)
        ls.pop(0)

    def compile(self, ls):
        acc = []
        while not (ls[0]["depth"] == 1 and ls[0]["kind"] == "identifier"):
            ls.pop(0)
        self.class_name = ls.pop(0)["label"]
        ls.pop(0)

        while ls[0]["kind"] == "classVarDec":
            self.set_class_vars(ls)

        while ls[0]["kind"] == "subroutineDec":
            self.compile_subroutine(ls, acc)
        ls.pop(0)
        ls.pop(0)

        pprint.pprint(acc)

        return acc
