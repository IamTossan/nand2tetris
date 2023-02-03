#!/usr/bin/env python3

import sys
import os
import pprint

from tokenizer import Tokenizer
from compilation_engine import CompilationEngine
from code_generator import CodeGenerator

def counter_generator():
    num = 0
    while True:
        yield num
        num += 1

counter = counter_generator()

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
