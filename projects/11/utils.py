from functools import reduce


def compose(*fns):
    return reduce(
        lambda f, g: lambda x: f(g(x)),
        fns,
        lambda x: x,
    )


flat_map = lambda f, xs: (y for ys in xs for y in f(ys))
