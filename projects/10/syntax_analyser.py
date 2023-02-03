#!/usr/bin/env python3

from functools import reduce
import re
import sys
import os
import pathlib
import pprint


def compose(*fns):
    return reduce(
        lambda f, g: lambda x: f(g(x)),
        fns,
        lambda x: x,
    )


flat_map = lambda f, xs: (y for ys in xs for y in f(ys))


def counter_generator():
    num = 0
    while True:
        yield num
        num += 1


counter = counter_generator()


class Tokenizer:
    KEYWORDS = [
        "class",
        "constructor",
        "function",
        "method",
        "field",
        "static",
        "var",
        "int",
        "char",
        "boolean",
        "void",
        "true",
        "false",
        "null",
        "this",
        "let",
        "do",
        "if",
        "else",
        "while",
        "return",
    ]
    SYMBOLS = "{}()[].,;+-*/&|<>=~"

    @staticmethod
    def add_token(cur, acc):
        res = []
        c = cur.strip()
        if not c:
            return

        if c in Tokenizer.KEYWORDS:
            acc.append(f"<keyword> {c} </keyword>")
        elif c in Tokenizer.SYMBOLS:
            if c == "<":
                c = "&lt;"
            if c == ">":
                c = "&gt;"
            if c == "&":
                c = "&amp;"
            acc.append(f"<symbol> {c} </symbol>")
        elif c.isdecimal() and 0 <= int(c) <= 32767:
            acc.append(f"<integerConstant> {c} </integerConstant>")
        elif c.startswith('"') and c.endswith('"'):
            acc.append(f"<stringConstant> {c[1:-1]} </stringConstant>")
        elif c.isidentifier():
            acc.append(f"<identifier> {c} </identifier>")
        else:
            xs = re.split(r"([-~.,;()[\]])", c)
            for x in xs:
                Tokenizer.add_token(x, acc)

    @staticmethod
    def tokenize(l):
        acc = []
        cur = ""
        is_in_str = False

        for c in l:
            if c == '"':
                if is_in_str:
                    cur += c
                    Tokenizer.add_token(cur, acc)
                    cur = ""
                    is_in_str = not is_in_str
                    continue
                is_in_str = not is_in_str
            if c == " " and not is_in_str:
                Tokenizer.add_token(cur, acc)
                cur = ""
            cur += c
        Tokenizer.add_token(cur, acc)
        return acc

    @staticmethod
    def translate_file(file_path):
        with open(file_path) as f:
            a = compose(
                lambda l: flat_map(Tokenizer.tokenize, l),
                lambda l: filter(lambda x: x, l),
                lambda l: filter(
                    lambda x: not (
                        x.startswith("//") or x.startswith("/**") or x.startswith("*")
                    ),
                    l,
                ),
                lambda l: map(lambda x: x.strip(), l),
                lambda l: map(lambda x: x.split("//")[0], l),
            )(f.readlines())
        return ["<tokens>", *a, "</tokens>"]

    def __init__(self, file_path):
        self.file_path = file_path

    def run(self):
        a = Tokenizer.translate_file(self.file_path)
        self.write(a)

    def write(self, a):
        file_name = pathlib.PurePath(self.file_path).name
        file_path = f"dist/{file_name.split('.')[0]}T.xml"
        with open(file_path, "w") as f:
            for i in list(a):
                f.write(f"{i}\n")


def tab(depth):
    return depth * "  "

class CodeGenerator:
    def __init__(self, file_path):
        self.file_path = file_path

    def open(self):
        file_name = pathlib.PurePath(self.file_path).name
        return open(f"dist/{file_name.split('.')[0]}.xml")

    def write(self, ls):
        file_name = pathlib.PurePath(self.file_path).name.split(".")[0][:-1]

        with open(f"dist/{file_name}.vm", "w") as f:
            for l in ls:
                f.write(f"{l}\n")

    def run(self):
        with self.open() as f:
            a, t = compose(
                lambda l: CodeGenerator.compile(l),
            )(f.readlines())
        pprint.pprint(a)

        self.write(a)

    @staticmethod
    def compile(l):
        return l

class CompilationEngine:
    def __init__(self, file_path):
        self.file_path = file_path

    def open(self):
        file_name = pathlib.PurePath(self.file_path).name
        return open(f"dist/{file_name.split('.')[0]}.xml")

    def write(self, ls):
        file_name = pathlib.PurePath(self.file_path).name.split(".")[0][:-1]

        with open(f"dist/{file_name}.xml", "w") as f:
            for l in ls:
                f.write(f"{l}\n")

    def run(self):
        with self.open() as f:
            a, t = compose(
                lambda l: CompilationEngine.compile(l),
                lambda l: list(l)[1:-1],
                lambda l: map(lambda x: x.strip(), l),
            )(f.readlines())
        pprint.pprint(a)

        self.write(a)

    @staticmethod
    def makeVarDec(tokens, acc, depth):
        acc.append(tab(depth) + "<varDec>")
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        while tokens[0].startswith("<symbol> ,"):
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth) + "</varDec>")
        return acc, tokens

    @staticmethod
    def makeClassVarDec(tokens, acc, depth):
        acc.append(tab(depth) + "<classVarDec>")
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        while tokens[0].startswith("<symbol> ,"):
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth) + "</classVarDec>")
        return acc, tokens

    @staticmethod
    def makeExpressionList(tokens, acc, depth):
        acc.append(tab(depth) + "<expressionList>")
        if not tokens[0].startswith("<symbol> )"):
            acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
            while tokens[0].startswith("<symbol> ,"):
                acc.append(tab(depth + 1) + tokens.pop(0))
                acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
        acc.append(tab(depth) + "</expressionList>")
        return acc, tokens

    @staticmethod
    def makeTerm(tokens, acc, depth):
        acc.append(tab(depth) + "<term>")
        if tokens[0].startswith("<identifier>") and tokens[1].startswith("<symbol> ("):
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc, tokens = CompilationEngine.makeExpressionList(tokens, acc, depth + 1)
            acc.append(tab(depth + 1) + tokens.pop(0))
        elif tokens[0].startswith("<identifier>") and tokens[1].startswith(
            "<symbol> ."
        ):
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc, tokens = CompilationEngine.makeExpressionList(tokens, acc, depth + 1)
            acc.append(tab(depth + 1) + tokens.pop(0))
        elif tokens[1].startswith("<symbol> )"):
            acc.append(tab(depth + 1) + tokens.pop(0))
        elif tokens[0].split(" ")[1] in ("~", "-"):
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc, tokens = CompilationEngine.makeTerm(tokens, acc, depth + 1)
        elif tokens[0].startswith("<symbol> ("):
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
            acc.append(tab(depth + 1) + tokens.pop(0))
        elif tokens[0].startswith("<stringConstant>"):
            acc.append(tab(depth + 1) + tokens.pop(0))
        elif tokens[0].startswith("<integerConstant>"):
            acc.append(tab(depth + 1) + tokens.pop(0))
        elif tokens[1].startswith("<symbol> ["):
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
            acc.append(tab(depth + 1) + tokens.pop(0))
        elif tokens[0].startswith("<identifier>"):
            acc.append(tab(depth + 1) + tokens.pop(0))
        elif tokens[0].split(" ")[1] in ("true", "false", "null", "this"):
            acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth) + "</term>")
        return acc, tokens

    @staticmethod
    def makeExpression(tokens, acc, depth):
        acc.append(tab(depth) + "<expression>")
        acc, tokens = CompilationEngine.makeTerm(tokens, acc, depth + 1)

        while tokens[0].split(" ")[1] in (
            "+",
            "-",
            "/",
            "*",
            "&lt;",
            "&gt;",
            "&amp;",
            "|",
            "=",
        ):
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc, tokens = CompilationEngine.makeTerm(tokens, acc, depth + 1)
        acc.append(tab(depth) + "</expression>")
        return acc, tokens

    @staticmethod
    def makeLetStatement(tokens, acc, depth):
        acc.append(tab(depth) + "<letStatement>")
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))

        if tokens[0].startswith("<symbol> ["):
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
            acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth) + "</letStatement>")
        return acc, tokens

    @staticmethod
    def makeIfStatement(tokens, acc, depth):
        acc.append(tab(depth) + "<ifStatement>")
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc, tokens = CompilationEngine.makeStatements(tokens, acc, depth + 1)
        acc.append(tab(depth + 1) + tokens.pop(0))

        if tokens[0].startswith("<keyword> else"):
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc, tokens = CompilationEngine.makeStatements(tokens, acc, depth + 1)
            acc.append(tab(depth + 1) + tokens.pop(0))

        acc.append(tab(depth) + "</ifStatement>")

        return acc, tokens

    @staticmethod
    def makeWhileStatement(tokens, acc, depth):
        acc.append(tab(depth) + "<whileStatement>")
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc, tokens = CompilationEngine.makeStatements(tokens, acc, depth + 1)
        acc.append(tab(depth) + tokens.pop(0))
        acc.append(tab(depth) + "</whileStatement>")

        return acc, tokens

    @staticmethod
    def makeDoStatement(tokens, acc, depth):
        acc.append(tab(depth) + "<doStatement>")
        acc.append(tab(depth + 1) + tokens.pop(0))
        if tokens[0].startswith("<identifier>") and tokens[1].startswith("<symbol> ("):
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc, tokens = CompilationEngine.makeExpressionList(tokens, acc, depth + 1)
            acc.append(tab(depth + 1) + tokens.pop(0))
        elif tokens[0].startswith("<identifier>") and tokens[1].startswith(
            "<symbol> ."
        ):
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc.append(tab(depth + 1) + tokens.pop(0))
            acc, tokens = CompilationEngine.makeExpressionList(tokens, acc, depth + 1)
            acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth) + "</doStatement>")

        return acc, tokens

    @staticmethod
    def makeReturnStatement(tokens, acc, depth):
        acc.append(tab(depth) + "<returnStatement>")
        acc.append(tab(depth) + tokens.pop(0))
        if not tokens[0].startswith("<symbol> ;"):
            acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
        acc.append(tab(depth) + tokens.pop(0))
        acc.append(tab(depth) + "</returnStatement>")

        return acc, tokens

    @staticmethod
    def makeStatements(tokens, acc, depth):
        acc.append(tab(depth) + "<statements>")
        while tokens[0].startswith("<keyword>") and tokens[0].split(" ")[1] in (
            "let",
            "if",
            "while",
            "do",
            "return",
        ):
            if tokens[0].startswith("<keyword> let"):
                acc, tokens = CompilationEngine.makeLetStatement(tokens, acc, depth + 1)
            elif tokens[0].startswith("<keyword> if"):
                acc, tokens = CompilationEngine.makeIfStatement(tokens, acc, depth + 1)
            elif tokens[0].startswith("<keyword> while"):
                acc, tokens = CompilationEngine.makeWhileStatement(
                    tokens, acc, depth + 1
                )
            elif tokens[0].startswith("<keyword> do"):
                acc, tokens = CompilationEngine.makeDoStatement(tokens, acc, depth + 1)
            elif tokens[0].startswith("<keyword> return"):
                acc, tokens = CompilationEngine.makeReturnStatement(
                    tokens, acc, depth + 1
                )
        acc.append(tab(depth) + "</statements>")
        return acc, tokens

    @staticmethod
    def makeSubroutineBody(tokens, acc, depth):
        acc.append(tab(depth) + "<subroutineBody>")
        acc.append(tab(depth + 1) + tokens.pop(0))
        while tokens[0].startswith("<keyword> var"):
            acc, tokens = CompilationEngine.makeVarDec(tokens, acc, depth + 1)
        if not tokens[0].startswith("<symbol> }"):
            acc, tokens = CompilationEngine.makeStatements(tokens, acc, depth + 1)
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth) + "</subroutineBody>")
        return acc, tokens

    @staticmethod
    def makeParameterList(tokens, acc, depth):
        acc.append(tab(depth) + "<parameterList>")
        while not tokens[0].startswith("<symbol> )"):
            acc.append(tab(depth) + tokens.pop(0))
        acc.append(tab(depth) + "</parameterList>")
        return acc, tokens

    @staticmethod
    def makeSubroutineDec(tokens, acc, depth):
        acc.append(tab(depth) + "<subroutineDec>")
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc, tokens = CompilationEngine.makeParameterList(tokens, acc, depth + 1)
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc, tokens = CompilationEngine.makeSubroutineBody(tokens, acc, depth + 1)
        acc.append(tab(depth) + "</subroutineDec>")
        return acc, tokens

    @staticmethod
    def makeClass(tokens, acc, depth):
        acc.append(tab(depth) + "<class>")
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth + 1) + tokens.pop(0))
        while tokens[0].split(" ")[1] in ("static", "field"):
            acc, tokens = CompilationEngine.makeClassVarDec(tokens, acc, depth + 1)
        while tokens[0].split(" ")[1] in ("constructor", "function", "method"):
            acc, tokens = CompilationEngine.makeSubroutineDec(tokens, acc, depth + 1)
        acc.append(tab(depth + 1) + tokens.pop(0))
        acc.append(tab(depth) + "</class>")
        return acc, tokens

    @staticmethod
    def compile(tokens):
        if tokens[0].startswith("<keyword> class"):
            return CompilationEngine.makeClass(tokens, [], 0)
        return acc, tokens


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <TARGET>")
        exit()

    for f in os.listdir("dist"):
        os.remove(os.path.join("dist", f))

    target = sys.argv[1]
    if os.path.isfile(target):
        files = [target]
    elif os.path.isdir(target):
        files = [target + x for x in os.listdir(target) if x.endswith(".jack")]

    for f in files:
        print(f)
        t = Tokenizer(f)
        t.run()

        file_path = f"dist/{f.split('.')[0]}T.xml"
        c = CompilationEngine(file_path)
        c.run()

        g = CodeGenerator(file_path)
        g.run()
