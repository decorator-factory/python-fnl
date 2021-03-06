import re
import json  # json is needed to decode a string
from textwrap import dedent
from typing import Iterable, Tuple, Mapping, Union
from lark import Lark, Transformer, v_args

from . import patma_utils as _patma_utils  # imported for the side effects

from . import entities as e
from . import entity_types as et
from . import definitions
from .bindings import bindings
from . import type_parser
from . import fnlx as _fnlx
x = _fnlx.exports


@v_args(inline=True)
class LanguageTransformer(Transformer):
    @staticmethod
    def integer(token):
        return e.Integer(int(token))

    @staticmethod
    def string(token):
        return e.String(json.loads(
            re.sub(r"\s+", " ", token)
        ))

    @staticmethod
    def raw_string(token):
        s = str(token)[3:-3].replace(R'\"""', '"""')
        return e.String(dedent(s))

    @staticmethod
    def sexpr(left_paren, fn, *args):
        return e.Sexpr(fn, args, _position=(left_paren.line, left_paren.column))

    name = e.Name
    quoted = e.Quoted


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
    runtime.update(extensions)  # type: ignore -- Pyright, issue 1119

    error = None
    try:
        expr = parse(source).evaluate(runtime)
        return expr.render(runtime).as_text()
    except e.CallError as call_error:
        error = call_error.msg

    # raise the exception without the internal traceback:
    raise FnlTypeError(error)
