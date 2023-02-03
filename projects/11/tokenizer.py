import pathlib
import re
from utils import compose, flat_map

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
