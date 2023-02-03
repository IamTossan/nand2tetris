#!/usr/bin/env python

from functools import reduce
from itertools import tee
import re
import sys
import os

def compose(*fns):
    return reduce(
        lambda f, g: lambda x: f(g(x)),
        fns,
        lambda x: x,
    )

dest_map = {
    "M": "001",
    "D": "010",
    "DM": "011",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "ADM": "111",
}

comp_map = {
    "0": "101010",
    "1": "111111",
    "-1": "111010",
    "D": "001100",
    "A": "110000",
    "M": "110000",
    "!D": "001101",
    "!A": "110001",
    "!M": "110001",
    "-D": "001111",
    "-A": "110011",
    "-M": "110011",
    "D+1": "011111",
    "A+1": "110111",
    "M+1": "110111",
    "D-1": "001110",
    "A-1": "110010",
    "M-1": "110010",
    "D+A": "000010",
    "D+M": "000010",
    "D-A": "010011",
    "D-M": "010011",
    "A-D": "000111",
    "M-D": "000111",
    "D&A": "000000",
    "D&M": "000000",
    "D|A": "010101",
    "D|M": "010101",
}

jump_map = {
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

symbol_table = {
    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
    "R4": 4,
    "R5": 5,
    "R6": 6,
    "R7": 7,
    "R8": 8,
    "R9": 9,
    "R10": 10,
    "R11": 11,
    "R12": 12,
    "R13": 13,
    "R14": 14,
    "R15": 15,
    "SCREEN": 16384,
    "KBD": 24576,
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
}

def next_addr():
    num = 16
    while True:
        yield num
        num += 1

def translate_a_instruction(op):
    if not op.startswith('@'):
        return op

    a = op[1:]
    if a.isnumeric():
        return bin(int(a))[2:].zfill(16)
    elif a in symbol_table:
        return bin(int(symbol_table[a]))[2:].zfill(16)
    else:
        return op

def translate_c_instruction(op):
    if op.startswith('@'):
        return op

    instruction = re.split(r"[=;]", op)

    dest = "000"
    if "=" in op:
        dest = dest_map[instruction[0]]
        a = "1" if "M" in instruction[1] else "0"
        comp = comp_map[instruction[1]]
    else:
        a = "1" if "M" in instruction[0] else "0"
        comp = comp_map[instruction[0]]


    jump = "000"
    if ";" in op:
        jump = jump_map[instruction[-1]]

    return "111" + a + comp + dest + jump

def load_symbols(l):
    xs, out = tee(l)
    count = 0
    addr = next_addr()
    for idx, x in enumerate(xs):
        if x.startswith("("):
            symbol_table[x[1:-1]] = idx - count
            count += 1
        if x.startswith("@") and x[1].islower():
            if x[1:] not in symbol_table:
                symbol_table[x[1:]] = next(addr)
                print(x[1:], symbol_table[x[1:]])

    return filter(lambda x: not x.startswith("("), out)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <FILENAME>")
        exit()

    filename = sys.argv[1].split("/")[-1].split(".")[0]

    with open(sys.argv[1]) as f:
        a = compose(
            lambda l: map(translate_a_instruction, l),
            lambda l: map(translate_c_instruction, l),
            lambda l: load_symbols(l),
            lambda l: filter(lambda x: x, l),
            lambda l: filter(lambda x: not x.startswith('//'), l),
            lambda l: map(lambda x: x.strip(), l),
            lambda l: map(lambda x: x.split("//")[0], l),
        )(f.readlines())

        # print(list(a))

        file_path = f"dist/{filename}.hack"
        if not os.path.exists(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))

        with open(file_path, "w") as d:

            for l in list(a):
                d.write(f"{l}\n")

