import re
import json  # json is needed to decode a string
from textwrap import dedent
from typing import Iterable, Tuple, Mapping, Union
from lark import Lark, Transformer, v_args
from . import entities as e
from . import entity_types as et
from . import definitions
from . import type_parser


@v_args(inline=True)
class LanguageTransformer(Transformer):
    @staticmethod
    def integer(token):
        return e.Integer(int(token))

    @staticmethod
    def string(token):
        return e.String(json.loads(
            re.sub(r"\s+", " ", str(token))
        ))

    @staticmethod
    def raw_string(token):
        s = str(token)[2:-2].replace("\n", "\\n")
        return e.String(dedent(json.loads(s)))

    @staticmethod
    def name(token):
        return e.Name(str(token))

    @staticmethod
    def sexpr(left_paren, fn, *args):
        return e.Sexpr(fn, args, _position=(left_paren.line, left_paren.column))

    @staticmethod
    def quoted(expr):
        return e.Quoted(expr)


parser = Lark.open(
    "fnl.lark",
    rel_to=__file__,
    parser="lalr",
    transformer=LanguageTransformer(),
    propagate_positions=True,
)


def parse(source: str) -> e.Entity:
    return parser.parse(source)  # type: ignore


class FnlTypeError(TypeError):
    pass


def html(
        source: str,
        extensions: Union[Iterable[Tuple[str, e.Entity]], Mapping[str, e.Entity]] = ()
) -> str:
    runtime = {**definitions.BUILTINS}
    runtime.update(extensions)  # type: ignore -- bug in Pyright # NOTE

    error = None
    try:
        expr = parse(source).evaluate(runtime)
        return expr.render(runtime).as_text()
    except e.CallError as call_error:
        error = call_error.msg

    # raise the exception without the internal traceback:
    raise FnlTypeError(error)
