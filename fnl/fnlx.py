'''
Here's the idea:

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title</title>
    <link rel="stylesheet" href="style.css"/>
</head>
<body>
    <main>
        <div class="title">
            <h1>$title</h1>
            <a href="index.html">Go to the index</a>
        </div>
        <div class="mount">
            $mount
        </div>
    </main>
</body>
</html>

x("""
($
    (b"!DOCTYPE" &html)
    (b&html &(lang "en"))
    (b&head
        (b&meta &(charset "UTF-8") &/)
        (b&meta &(name "viewport") &(content "width=device-width, initial-scale=1.0") &/)
        (b&title ($var &title))
        (b&link &(rel "stylesheet") &(href "style.css) &/))
    (b&body
        (b&main
            (+ &.title
                ((h 1) ($var &title))
                (a "index.html" "Go to the index"))
            (+ &.mount
                ($var &mount))))

)


""")

'''

# λ

from fnl.entities import BlockTag
import fnl
from . import entities as e
from . import entity_types as et
from .definitions import fn

from typing import Dict


exports: Dict[str, e.Entity] = {}


@fn(exports, "+")
def div():
    def _div(*args: e.Entity):
        classes = []
        options = []
        body = []
        for arg in args:
            if isinstance(arg, e.Quoted):
                if isinstance(arg.subexpression, e.Name):
                    name = arg.subexpression.name
                    if name.startswith("."):  # class, like: &.danger
                        classes.append(name[1:])

                    elif name.startswith("#"):  # id, like: &#app
                        options.append(f'id="{name[1:]}"')

                    else:  # no-argument option, like &defer
                        options.append(name)

                elif isinstance(arg.subexpression, e.Sexpr):
                    if not isinstance(arg.subexpression.fn, e.Name):
                        raise TypeError(f"Expected name, got {arg.subexpression.fn}")

                    if len(arg.subexpression.args) != 2:
                        raise ValueError("Expected 2 values in quoted S-expression")

                    if not isinstance(arg.subexpression.args[1], e.String):
                        raise TypeError(f"Expected string, got {arg.subexpression.args[1]}")

                    name = arg.subexpression.fn.name
                    value: str = arg.subexpression.args[1].value  # type: ignore
                    options.append(f"{name}={value}")

                else:
                    raise TypeError(f"Expected name or call, got {arg.subexpression}")
            else:
                body.append(arg)

        class_str = "" if classes == [] else 'class="' + " ".join(classes) + '"'
        option_string = " ".join([class_str, *options])
        return BlockTag("div", option_string, tuple(body))  # type: ignore # NOTE: Pyright heisenbug

    yield ("(λ ...any . block)", _div)
