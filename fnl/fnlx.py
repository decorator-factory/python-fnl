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

$0:Quoted(Name($name))
$1:Quoted(Sexpr(Name($name), String($value)))
$2:Quoted($other)
$3:$unquoted

'''

import json
import fnl
from . import entities as e
from . import entity_types as et
from .definitions import fn

from typing import Dict, List, NamedTuple, Iterable


exports: Dict[str, e.Entity] = {}


class TagInfo(NamedTuple):
    classes: List[str]
    options: List[str]
    body: List[e.Entity]
    is_closed: bool

    @property
    def as_option_string(self):
        if self.classes == []:
            return " ".join(self.options)
        else:
            class_str = 'class="' + " ".join(self.classes) + '"'
            return " ".join([class_str, *self.options])


def parse_html_options(args: Iterable[e.Entity]):
    """Separates actual elements from HTML options: class names, ID names etc."""
    classes = []
    options = []
    body = []
    is_closed = False
    for arg in args:
        if isinstance(arg, e.Quoted):
            if isinstance(arg.subexpression, e.Name):
                name = arg.subexpression.name
                if name.startswith("."):  # class, like: &.danger
                    classes.append(name[1:])

                elif name.startswith("#"):  # id, like: &#app
                    options.append(f'id="{name[1:]}"')

                elif name == "/":
                    is_closed = True

                else:  # no-argument option, like &defer

                    options.append(name)

            elif isinstance(arg.subexpression, e.Sexpr):
                if not isinstance(arg.subexpression.fn, e.Name):
                    raise TypeError(f"Expected name, got {arg.subexpression.fn}")

                if len(arg.subexpression.args) != 1:
                    raise ValueError("Expected 2 values in quoted S-expression")

                if not isinstance(arg.subexpression.args[0], e.String):
                    raise TypeError(f"Expected string, got {arg.subexpression.args[0]}")

                name = arg.subexpression.fn.name
                value: str = arg.subexpression.args[0].value  # type: ignore
                options.append(f"{name}={json.dumps(value)}")

            else:
                raise TypeError(f"Expected name or call, got {arg.subexpression}")
        else:
            body.append(arg)
    return TagInfo(classes, options, body, is_closed)


@fn(exports, "+")
def div():
    def _div(*args: e.Entity):
        info = parse_html_options(args)
        return e.BlockTag("div", info.as_option_string, tuple(info.body))  # type: ignore

    yield ("(λ ...any . block)", _div)


@fn(exports, "b")
def block_tag():
    def _block_tag(*args: e.Entity):
        name_arg = args[0]
        if isinstance(name_arg, e.Quoted):
            assert isinstance(name_arg.subexpression, e.Name)
            name = name_arg.subexpression.name
        elif isinstance(name_arg, e.String):
            name = name_arg.value
        else:
            raise TypeError(f"Expected quoted name or string, got {name_arg}")

        info = parse_html_options(args[1:])
        if info.is_closed:
            return e.ClosedBlockTag(name, info.as_option_string, include_slash=True)
        else:
            return e.BlockTag(name, info.as_option_string, tuple(info.body))  # type: ignore

    yield ("(λ ...any . block)", _block_tag)


@fn(exports, "i")
def inline_tag():
    def _inline_tag(*args: e.Entity):
        name_arg = args[0]
        if isinstance(name_arg, e.Quoted):
            assert isinstance(name_arg.subexpression, e.Name)
            name = name_arg.subexpression.name
        elif isinstance(name_arg, e.String):
            name = name_arg.value
        else:
            raise TypeError(f"Expected quoted name or string, got {name_arg}")

        info = parse_html_options(args[1:])

        if info.is_closed:
            return e.ClosedInlineTag(name, info.as_option_string, include_slash=True)
        else:
            return e.InlineTag(name, info.as_option_string, tuple(info.body))  # type: ignore

    yield ("(λ ...any . inline)", _inline_tag)
