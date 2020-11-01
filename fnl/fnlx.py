import json
import fnl
from . import entities as e
from . import entity_types as et
from .definitions import fn

from context_manager_patma import match

from typing import Dict, List, NamedTuple, Iterable
from enum import Enum


exports: Dict[str, e.Entity] = {}


class TagKind(Enum):
    Open = 0
    ClosedWithSlash = 1
    ClosedWithoutSlash = 2


class TagInfo(NamedTuple):
    classes: List[str]
    options: List[str]
    body: List[e.Entity]
    kind: TagKind

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
    tag_kind = TagKind.Open
    for arg in args:
        with match(arg) as case:
            with case('Quoted(Name("/"))') as [m]:
                tag_kind = TagKind.ClosedWithSlash

            with case('Quoted(Name("."))') as [m]:
                tag_kind = TagKind.ClosedWithoutSlash

            with case('Quoted(Name(Cons(".", class_name)))') as [m]:
                classes.append(m.class_name)

            with case('Quoted(Name(Cons("#", id_name)))') as [m]:
                options.append(f'id="{m.id_name}"')

            with case('Quoted(Name(name)|String(name))') as [m]:
                options.append(m.name)

            with case('Quoted(Sexpr(Name(name), String(value)))') as [m]:
                options.append(f"{m.name}={json.dumps(m.value)}")

            with case('Quoted(other)') as [m]:
                raise TypeError(f"Expected name or call, got {m.other}")

            with case('element') as [m]:
                body.append(m.element)
    return TagInfo(classes, options, body, tag_kind)


@fn(exports, "+")
def div():
    """
    Part of the 'fnl.x' module.

    Shortcut for %%(tt "b &div")%%
    """
    def _div(*args: e.Entity):
        info = parse_html_options(args)
        return e.BlockTag("div", info.as_option_string, tuple(info.body))  # type: ignore

    yield ("(λ ...&[name]|&[(name str)]|inline|block . block)", _div)


_BLOCK_TAGS = frozenset((
    "address", "article", "aside", "blockquote", "canvas", "dd", "div", "dl",
    "dt", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h6",
    "header", "hr", "li", "main", "nav", "noscript", "ol", "p", "pre", "section",
    "table", "tfoot", "ul", "video"
))

_INLINE_TAGS = frozenset((
    "a", "abbr", "acronym", "b", "bdo", "big", "br", "button", "cite", "code",
    "dfn", "em", "i", "img", "input", "kbd", "label", "map", "object", "output",
    "q", "samp", "script", "select", "small", "span", "strong", "sub", "sup",
    "textarea", "time", "tt", "var"
))


@fn(exports, "b")
def block_tag():
    """
    Part of the 'fnl.x' module.

    Creates a block element. See the 'Quoted expressions' tutorial for more info.
    """
    def _block_tag(name_arg: e.Entity, *options: e.Entity):
        with match(name_arg) as case:
            with case('Quoted(Name(name))|String(name)') as [m]:
                name: str = m.name

        if name in _INLINE_TAGS:
            raise TypeError(f"<{name}> is an inline tag")

        info = parse_html_options(options)
        if info.kind == TagKind.ClosedWithSlash:
            return e.ClosedBlockTag(name, info.as_option_string, include_slash=True)
        elif info.kind == TagKind.ClosedWithoutSlash:
            return e.ClosedBlockTag(name, info.as_option_string, include_slash=False)
        else:
            return e.BlockTag(name, info.as_option_string, tuple(info.body))  # type: ignore

    yield ("(λ str|&[name] ...&[str]|&[name]|&[(name str)]|inline|block . block)", _block_tag)


@fn(exports, "i")
def inline_tag():
    """
    Part of the 'fnl.x' module.

    Creates an inline element. See the 'Quoted expressions' tutorial for more info.
    """
    def _inline_tag(name_arg: e.Entity, *options: e.Entity):
        with match(name_arg) as case:
            with case('Quoted(Name(name))|String(name)') as [m]:
                name: str = m.name

        if name in _BLOCK_TAGS:
            raise TypeError(f"<{name}> is an inline tag")

        info = parse_html_options(options)

        if info.kind == TagKind.ClosedWithSlash:
            return e.ClosedInlineTag(name, info.as_option_string, include_slash=True)
        elif info.kind == TagKind.ClosedWithoutSlash:
            return e.ClosedInlineTag(name, info.as_option_string, include_slash=False)
        else:
            return e.InlineTag(name, info.as_option_string, tuple(info.body))  # type: ignore

    yield ("(λ str|&[name] ...&[name]|&[(name str)]|inline . inline)", _inline_tag)
