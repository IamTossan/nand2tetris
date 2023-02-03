import pathlib
from utils import compose

def tab(depth):
    return depth * "  "


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
                # lambda l: CompilationEngine.parse(l),
                lambda l: list(l)[1:-1],
                lambda l: map(lambda x: x.strip(), l),
            )(f.readlines())

        self.write(a)

    @staticmethod
    def parse(raw_tokens):
        tokens = []
        for t in raw_tokens:
            raw_kind, name, _ = t.split(" ")
            tokens.append({
                "name": name,
                "kind": raw_kind[1:-1]
            })

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
