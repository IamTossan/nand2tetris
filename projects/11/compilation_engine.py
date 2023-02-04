import pathlib
from utils import compose


def tab(depth):
    return depth * "  "


def make_node(depth, token, token_type="token"):
    return {
        "depth": depth,
        "label": token["label"] if "label" in token else "",
        "kind": token["kind"],
        "type": token_type,
    }


def to_xml(node):
    if node["type"] == "open":
        return f"{tab(node['depth'])}<{node['kind']}>"
    elif node["type"] == "close":
        return f"{tab(node['depth'])}</{node['kind']}>"
    else:
        return f"{tab(node['depth'])}<{node['kind']}> {node['label']} </{node['kind']}>"


class CompilationEngine:
    def __init__(self, file_name):
        self.file_name = file_name

    def open(self):
        return open(f"dist/{self.file_name}T.xml")

    def write(self, ls):
        with open(f"dist/{self.file_name}.xml", "w") as f:
            for l in ls:
                f.write(f"{to_xml(l)}\n")

    def run(self):
        with self.open() as f:
            a, t = compose(
                lambda l: CompilationEngine.compile(l),
                lambda l: CompilationEngine.parse(l),
                lambda l: list(l)[1:-1],
                lambda l: map(lambda x: x.strip(), l),
            )(f.readlines())

        self.write(a)
        return a

    @staticmethod
    def parse(raw_tokens):
        tokens = []
        for t in raw_tokens:
            raw_kind = t.split(">")
            raw_name = raw_kind[1].split("<")
            tokens.append(
                {
                    "kind": raw_kind[0][1:],
                    "label": raw_name[0][1:-1],
                }
            )
        return tokens

    @staticmethod
    def makeVarDec(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "varDec"}, "open"))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        while tokens[0]["label"] == ",":
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth, {"kind": "varDec"}, "close"))
        return acc, tokens

    @staticmethod
    def makeClassVarDec(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "classVarDec"}, "open"))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        while tokens[0]["label"] == ",":
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth, {"kind": "classVarDec"}, "close"))
        return acc, tokens

    @staticmethod
    def makeExpressionList(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "expressionList"}, "open"))
        if not tokens[0]["label"] == ")":
            acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
            while tokens[0]["label"] == ",":
                acc.append(make_node(depth + 1, tokens.pop(0)))
                acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
        acc.append(make_node(depth, {"kind": "expressionList"}, "close"))
        return acc, tokens

    @staticmethod
    def makeTerm(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "term"}, "open"))
        if tokens[0]["kind"] == "<identifier>" and tokens[1]["label"] == "(":
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc, tokens = CompilationEngine.makeExpressionList(tokens, acc, depth + 1)
            acc.append(make_node(depth + 1, tokens.pop(0)))
        elif tokens[0]["kind"] == "<identifier>" and tokens[1]["label"] == ".":
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc, tokens = CompilationEngine.makeExpressionList(tokens, acc, depth + 1)
            acc.append(make_node(depth + 1, tokens.pop(0)))
        elif tokens[1]["label"] == ")":
            acc.append(make_node(depth + 1, tokens.pop(0)))
        elif tokens[0]["label"] in ("~", "-"):
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc, tokens = CompilationEngine.makeTerm(tokens, acc, depth + 1)
        elif tokens[0]["label"] == "(":
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
            acc.append(make_node(depth + 1, tokens.pop(0)))
        elif tokens[0]["kind"] == "stringConstant":
            acc.append(make_node(depth + 1, tokens.pop(0)))
        elif tokens[0]["kind"] == "integerConstant":
            acc.append(make_node(depth + 1, tokens.pop(0)))
        elif tokens[1]["label"] == "[":
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
            acc.append(make_node(depth + 1, tokens.pop(0)))
        elif tokens[0]["kind"] == "identifier":
            acc.append(make_node(depth + 1, tokens.pop(0)))
        elif tokens[0]["label"] in ("true", "false", "null", "this"):
            acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth, {"kind": "term"}, "close"))
        return acc, tokens

    @staticmethod
    def makeExpression(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "expression"}, "open"))
        acc, tokens = CompilationEngine.makeTerm(tokens, acc, depth + 1)

        while tokens[0]["label"] in (
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
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc, tokens = CompilationEngine.makeTerm(tokens, acc, depth + 1)
        acc.append(make_node(depth, {"kind": "expression"}, "close"))
        return acc, tokens

    @staticmethod
    def makeLetStatement(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "letStatement"}, "open"))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))

        if tokens[0]["label"] == "[":
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
            acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth, {"kind": "letStatement"}, "close"))
        return acc, tokens

    @staticmethod
    def makeIfStatement(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "ifStatement"}, "open"))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc, tokens = CompilationEngine.makeStatements(tokens, acc, depth + 1)
        acc.append(make_node(depth + 1, tokens.pop(0)))

        if tokens[0]["label"] == "else":
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc, tokens = CompilationEngine.makeStatements(tokens, acc, depth + 1)
            acc.append(make_node(depth + 1, tokens.pop(0)))

        acc.append(make_node(depth, {"kind": "ifStatement"}, "close"))

        return acc, tokens

    @staticmethod
    def makeWhileStatement(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "whileStatement"}, "open"))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc, tokens = CompilationEngine.makeStatements(tokens, acc, depth + 1)
        acc.append(make_node(depth, tokens.pop(0)))
        acc.append(make_node(depth, {"kind": "whileStatement"}, "close"))

        return acc, tokens

    @staticmethod
    def makeDoStatement(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "doStatement"}, "open"))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        if tokens[0]["kind"] == "identifier" and tokens[1]["label"] == "(":
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc, tokens = CompilationEngine.makeExpressionList(tokens, acc, depth + 1)
            acc.append(make_node(depth + 1, tokens.pop(0)))
        elif tokens[0]["kind"] == "identifier" and tokens[1]["label"] == ".":
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc.append(make_node(depth + 1, tokens.pop(0)))
            acc, tokens = CompilationEngine.makeExpressionList(tokens, acc, depth + 1)
            acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth, {"kind": "doStatement"}, "close"))

        return acc, tokens

    @staticmethod
    def makeReturnStatement(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "returnStatement"}, "open"))
        acc.append(make_node(depth, tokens.pop(0)))
        if not tokens[0]["label"] == ";":
            acc, tokens = CompilationEngine.makeExpression(tokens, acc, depth + 1)
        acc.append(make_node(depth, tokens.pop(0)))
        acc.append(make_node(depth, {"kind": "returnStatement"}, "close"))

        return acc, tokens

    @staticmethod
    def makeStatements(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "statements"}, "open"))
        while tokens[0]["kind"] == "keyword" and tokens[0]["label"] in (
            "let",
            "if",
            "while",
            "do",
            "return",
        ):
            if tokens[0]["label"] == "let":
                acc, tokens = CompilationEngine.makeLetStatement(tokens, acc, depth + 1)
            elif tokens[0]["label"] == "if":
                acc, tokens = CompilationEngine.makeIfStatement(tokens, acc, depth + 1)
            elif tokens[0]["label"] == "while":
                acc, tokens = CompilationEngine.makeWhileStatement(
                    tokens, acc, depth + 1
                )
            elif tokens[0]["label"] == "do":
                acc, tokens = CompilationEngine.makeDoStatement(tokens, acc, depth + 1)
            elif tokens[0]["label"] == "return":
                acc, tokens = CompilationEngine.makeReturnStatement(
                    tokens, acc, depth + 1
                )
        acc.append(make_node(depth, {"kind": "statements"}, "close"))
        return acc, tokens

    @staticmethod
    def makeSubroutineBody(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "subroutineBody"}, "open"))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        while tokens[0]["label"] == "var":
            acc, tokens = CompilationEngine.makeVarDec(tokens, acc, depth + 1)
        if not tokens[0]["label"] == "}":
            acc, tokens = CompilationEngine.makeStatements(tokens, acc, depth + 1)
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth, {"kind": "subroutineBody"}, "close"))
        return acc, tokens

    @staticmethod
    def makeParameterList(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "parameterList"}, "open"))
        while not tokens[0]["label"] == ")":
            acc.append(make_node(depth, tokens.pop(0)))
        acc.append(make_node(depth, {"kind": "parameterList"}, "close"))
        return acc, tokens

    @staticmethod
    def makeSubroutineDec(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "subroutineDec"}, "open"))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc, tokens = CompilationEngine.makeParameterList(tokens, acc, depth + 1)
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc, tokens = CompilationEngine.makeSubroutineBody(tokens, acc, depth + 1)
        acc.append(make_node(depth, {"kind": "subroutineDec"}, "close"))
        return acc, tokens

    @staticmethod
    def makeClass(tokens, acc, depth):
        acc.append(make_node(depth, {"kind": "class"}, "open"))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth + 1, tokens.pop(0)))
        while tokens[0]["label"] in ("static", "field"):
            acc, tokens = CompilationEngine.makeClassVarDec(tokens, acc, depth + 1)
        while tokens[0]["label"] in ("constructor", "function", "method"):
            acc, tokens = CompilationEngine.makeSubroutineDec(tokens, acc, depth + 1)
        acc.append(make_node(depth + 1, tokens.pop(0)))
        acc.append(make_node(depth, {"kind": "class"}, "close"))
        return acc, tokens

    @staticmethod
    def compile(tokens):
        if tokens[0]["label"] == "class":
            return CompilationEngine.makeClass(tokens, [], 0)
        return acc, tokens
