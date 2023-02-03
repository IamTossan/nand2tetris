import pathlib
from utils import compose

class CodeGenerator:
    def __init__(self, file_path):
        self.file_path = file_path

    def open(self):
        file_name = pathlib.PurePath(self.file_path).name
        return open(f"dist/{file_name.split('.')[0][:-1]}.xml")

    def write(self, ls):
        file_name = pathlib.PurePath(self.file_path).name.split(".")[0][:-1]

        with open(f"dist/{file_name}.vm", "w") as f:
            for l in ls:
                f.write(f"{l}\n")

    def run(self):
        with self.open() as f:
            a = compose(
                lambda l: self.compile(l),
                lambda l: map(lambda x: x.strip(), l),
            )(f.readlines())
        # pprint.pprint(list(a))

        self.write(list(a))

    def get_identifier(self, name):
        pass

    def set_identifier(self, name, kind):
        pass

    def compile(self, ls):
        class_name = next(x for x in ls if x.startswith("<identifier>"))

        return ls