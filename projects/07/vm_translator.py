#!/usr/bin/env python

from functools import reduce
from itertools import tee
import re
import sys
import os
import glob
import pathlib


def compose(*fns):
    return reduce(
        lambda f, g: lambda x: f(g(x)),
        fns,
        lambda x: x,
    )


def counter_generator():
    num = 0
    while True:
        yield num
        num += 1


counter = counter_generator()
pointer_map = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
}


def get_value(xs, file_name):
    if xs[1] == "constant":
        return ["@" + xs[2], "D=A"]
    elif xs[1] == "temp":
        return [f"@{int(xs[2]) + 5}", "D=M"]
    elif xs[1] == "static":
        return [f"@{file_name}.{xs[2]}", "D=M"]
    elif xs[1] == "pointer":
        target = "THIS" if xs[2] == "0" else "THAT"
        return [f"@{target}", "D=M"]
    elif xs[1] in ("this", "that") and xs[2] != 0:
        return [
            f"@{xs[2]}",
            "D=A",
            f"@{xs[1].upper()}",
            "D=M+D",
            "A=D",
            "D=M",
        ]
    elif xs[1] in pointer_map:
        return [
            f"@{xs[2]}",
            "D=A",
            f"@{pointer_map[xs[1]]}",
            "D=M+D",
            "A=D",
            "D=M",
        ]


def make_translate_instruction(file_name):
    def translate_instruction(l):
        instruction = l.split(" ")
        if instruction[0] == "push":
            return [
                "// " + l,
                *get_value(instruction, file_name),
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                "",
            ]
        elif instruction[0] == "pop":
            if instruction[1] in pointer_map:
                return [
                    "// " + l,
                    "@SP",
                    "M=M-1",
                    f"@{instruction[2]}",
                    "D=A",
                    f"@{pointer_map[instruction[1]]}",
                    "D=M+D",
                    "@R13",
                    "M=D",
                    "@SP",
                    "A=M",
                    "D=M",
                    "@R13",
                    "A=M",
                    "M=D",
                    "",
                ]
            elif instruction[1] == "temp":
                return [
                    "// " + l,
                    "@SP",
                    "M=M-1",
                    "@SP",
                    "A=M",
                    "D=M",
                    f"@{int(instruction[2]) + 5}",
                    "M=D",
                    "",
                ]
            elif instruction[1] == "static":
                return [
                    "// " + l,
                    "@SP",
                    "M=M-1",
                    "@SP",
                    "A=M",
                    "D=M",
                    f"@{file_name}.{instruction[2]}",
                    "M=D",
                    "",
                ]
            elif l in ("pop pointer 0", "pop pointer 1", "pop this 0", "pop that 0"):
                target = "THIS" if l in ("pop pointer 0", "pop this 0") else "THAT"
                return [
                    "// " + l,
                    "@SP",
                    "M=M-1",
                    "A=M",
                    "D=M",
                    f"@{target}",
                    "M=D",
                    "",
                ]
            elif instruction[1] in ("this", "that"):
                return [
                    "// " + l,
                    "@SP",
                    "M=M-1",
                    f"@{instruction[2]}",
                    "D=M",
                    f"@{instruction[1].upper()}",
                    "D=M+D",
                    "@R13",
                    "M=D",
                    "@SP",
                    "A=M",
                    "D=M",
                    "@R13",
                    "A=M",
                    "M=D",
                    "",
                ]
            else:
                raise Exception(f"{l} could not be parsed")
        elif instruction[0] == "add":
            return [
                "// " + l,
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@SP",
                "A=M-1",
                "M=M+D",
                "",
            ]
        elif instruction[0] == "sub":
            return [
                "// " + l,
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@SP",
                "A=M-1",
                "M=M-D",
                "",
            ]
        elif instruction[0] == "eq":
            idx = next(counter)
            return [
                "// " + l,
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@SP",
                "A=M-1",
                "M=M-D",
                "D=M",
                f"@JEQ.{idx}",
                "D;JEQ",
                "@SP",
                "A=M-1",
                "M=0",
                f"@END.JEQ.{idx}",
                "0;JMP",
                f"(JEQ.{idx})",
                "@SP",
                "A=M-1",
                "M=-1",
                f"(END.JEQ.{idx})",
                "",
            ]
        elif instruction[0] == "lt":
            idx = next(counter)
            return [
                "// " + l,
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@SP",
                "A=M-1",
                "M=M-D",
                "D=M",
                f"@LT.{idx}",
                "D;JGE",
                "@SP",
                "A=M-1",
                "M=-1",
                f"@END.LT.{idx}",
                "0;JMP",
                f"(LT.{idx})",
                "@SP",
                "A=M-1",
                "M=0",
                f"(END.LT.{idx})",
                "",
            ]
        elif instruction[0] == "gt":
            idx = next(counter)
            return [
                "// " + l,
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@SP",
                "A=M-1",
                "M=M-D",
                "D=M",
                f"@GLE.{idx}",
                "D;JLE",
                "@SP",
                "A=M-1",
                "M=-1",
                f"@END.GLE.{idx}",
                "0;JMP",
                f"(GLE.{idx})",
                "@SP",
                "A=M-1",
                "M=0",
                f"(END.GLE.{idx})",
                "",
            ]
        elif instruction[0] == "neg":
            return ["// " + l, "@SP", "A=M-1", "M=-M", ""]
        elif instruction[0] == "and":
            return [
                "// " + l,
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@SP",
                "A=M-1",
                "M=D&M",
                "",
            ]
        elif instruction[0] == "or":
            return [
                "// " + l,
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@SP",
                "A=M-1",
                "M=D|M",
                "",
            ]
        elif instruction[0] == "not":
            return ["// " + l, "@SP", "A=M-1", "M=!M", ""]
        elif instruction[0] == "function":
            return [
                "// " + l,
                f"({instruction[1]})",
                *["@SP", "A=M", "M=0", "@SP", "M=M+1"] * int(instruction[2]),
                "",
            ]
        elif instruction[0] == "return":
            return [
                "// " + l,
                "@LCL",  # get endframe to R13
                "D=M",
                "@R13",
                "M=D",
                "@5",  # get return address to R14
                "A=D-A",
                "D=M",
                "@R14",
                "M=D",
                "@SP",  # get return value
                "A=M-1",
                "D=M",
                "@ARG",  # copy return value to arg.0
                "A=M",
                "M=D",
                "@ARG",
                "D=M+1",
                "@SP",  # update SP to arg.1
                "M=D",
                "@R13",  # restore THAT
                "D=M-1",
                "A=D",
                "D=M",
                "@THAT",
                "M=D",
                "@13",
                "M=M-1",
                "@R13",  # restore THIS
                "D=M-1",
                "A=D",
                "D=M",
                "@THIS",
                "M=D",
                "@13",
                "M=M-1",
                "@R13",  # restore ARG
                "D=M-1",
                "A=D",
                "D=M",
                "@ARG",
                "M=D",
                "@13",
                "M=M-1",
                "@R13",  # restore LCL
                "D=M-1",
                "A=D",
                "D=M",
                "@LCL",
                "M=D",
                "@R14",  # return
                "A=M",
                "0;JMP",
                "",
            ]
        elif instruction[0] == "call":
            idx = next(counter)
            return [
                "// " + l,
                f"@{instruction[1]}$ret.{idx}",
                "D=A",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                "@LCL",  # push caller LCL
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                "@ARG",  # push caller ARG
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                "@THIS",  # push caller THIS
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                "@THAT",  # push caller THAT
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                "@SP",  # set new ARG
                "D=M",
                "@5",
                "D=D-A",
                f"@{instruction[2]}",
                "D=D-A",
                "@ARG",
                "M=D",
                "@SP",  # set new LCL
                "D=M",
                "@LCL",
                "M=D",
                f"@{instruction[1]}",  # jump to func
                "0;JMP",
                f"({instruction[1]}$ret.{idx})",
                "",
            ]
        elif instruction[0] == "label":
            return ["// " + l, f"({instruction[1]})", ""]
        elif instruction[0] == "goto":
            return ["// " + l, f"@{instruction[1]}", "0;JMP", ""]
        elif instruction[0] == "if-goto":
            return [
                "// " + l,
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                f"@{instruction[1]}",
                "D;JNE",
                "",
            ]
        else:
            raise Exception(f"{l} could not be parsed")

    return translate_instruction


def translate_file(file_path, file_name):
    with open(file_path) as f:
        a = compose(
            lambda l: map(
                make_translate_instruction(file_name.lower().split(".")[0]), l
            ),
            # lambda l: load_symbols(l),
            lambda l: filter(lambda x: x, l),
            lambda l: filter(lambda x: not x.startswith("//"), l),
            lambda l: map(lambda x: x.strip(), l),
            lambda l: map(lambda x: x.split("//")[0], l),
        )(f.readlines())
    return a


def bootstrap_code():
    return [
        "// call sys.init",
        "@256",
        "D=A",
        "@SP",
        "M=D",
        "@end",
        "D=A",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        "@LCL",  # push caller LCL
        "M=0",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        "@ARG",  # push caller ARG
        "M=0",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        "@THIS",  # push caller THIS
        "M=0",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        "@THAT",  # push caller THAT
        "M=0",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        "@SP",  # set new ARG
        "D=M",
        "@5",
        "D=D-A",
        "@ARG",
        "M=D",
        "@SP",  # set new LCL
        "D=M",
        "@LCL",
        "M=D",
        f"@Sys.init",  # jump to func
        "0;JMP",
        "",
    ]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <FILENAME>")
        exit()

    target = sys.argv[1]
    if os.path.isfile(target):
        a = translate_file(target)
        file_path = target.split(".")[0] + ".asm"
        with open(file_path, "w") as d:
            for i in list(a):
                for l in i:
                    d.write(f"{l}\n")
    elif os.path.isdir(target):
        files = [x for x in os.listdir(target) if x.endswith(".vm")]

        if len(files) == 1:
            a = translate_file(target + files[0], files[0])
            file_path = target + pathlib.PurePath(target).name + ".asm"
            with open(file_path, "w") as d:
                for i in list(a):
                    for l in i:
                        d.write(f"{l}\n")
        else:
            a = [
                translate_file(target + f, f)
                for f in ["Sys.vm"] + list(filter(lambda x: x != "Sys.vm", files))
            ]
            file_path = target + pathlib.PurePath(target).name + ".asm"
            with open(file_path, "w") as d:
                for l in bootstrap_code():
                    d.write(f"{l}\n")
                for f in a:
                    for i in list(f):
                        for l in i:
                            d.write(f"{l}\n")
