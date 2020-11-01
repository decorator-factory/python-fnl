import json
from typing import Dict
import fnl
import re
from . import entity_types as et
from . import entities as e
from . import type_parser


BUILTINS: Dict[str, e.Entity] = {}


# we need to parse the docstrings of built-in functions
# to equip them with a documentation Entity
def _parse_docstring(docstring: str) -> e.Entity:
    docstring = docstring.strip()
    parts = []
    last_stop = 0
    for match in re.finditer(r"%%([^%]+|%(?!%))+%%", docstring):
        (start, stop) = match.span()
        if last_stop != start:
            parts.append(e.String(docstring[last_stop:start]))
        last_stop = stop
        parts.append(fnl.parse(match[1]))
    if last_stop != len(docstring):
        parts.append(e.String(docstring[last_stop:]))
    return e.InlineConcat(tuple(parts))


def fn(target: Dict[str, e.Entity], name: str):
    """
    Helper decorator for defining functions with overloads

    >>> @fn(extensions, "identity")
    ... def identity():
    ...     def _str(s):
    ...         return s
    ...     yield ("(λ str . str)", _str)
    ...
    ...     def _int(n):
    ...         return n
    ...     yield ("(λ int . int)", _int)
    ...
    """
    def _add_fn(f):
        overloads = {}
        for declaration in f():
            if len(declaration) == 2:
                # ("(λ int ...str . str)", fn)
                (type_string, fn) = declaration
                function_type = type_parser.parse_fn(type_string)
            elif len(declaration) == 4:
                # ((TInt(),), TStr(), TStr(), fn)
                arg_types, rest_types, return_type, fn = declaration
                function_type = et.TFunction(arg_types, rest_types, return_type)
            else:
                raise ValueError(declaration)
            overloads[function_type] = fn

        target[name] = e.Function(overloads, _docstring_source=f.__doc__)
        return target[name]
    return _add_fn


@fn(BUILTINS, "bf")
def boldface():
    """
    Boldface text. Represents the %%(tt "<b>")%% HTML tag.
    """
    def from_inline(*args):
        return e.InlineTag("b", "", args)
    yield ("(λ ...inline . inline)", from_inline)


@fn(BUILTINS, "it")
def italics():
    """
    Italic text. Represents the %%(tt "<i>")%% HTML tag.
    """
    def from_inline(*args):
        return e.InlineTag("i", "", args)
    yield ("(λ ...inline . inline)", from_inline)


@fn(BUILTINS, "tt")
def tt():
    """
    Monospace text. Represents the %%(tt "<tt>")%% HTML tag.
    """
    def from_inline(*args):
        return e.InlineTag("tt", "", args)
    yield ("(λ ...inline . inline)", from_inline)


@fn(BUILTINS, "mono")
def monospace():
    """
    Like %%(tt "tt")%%, but prevents text inside from line-wrapping.
    """
    def from_inline(*args):
        # (mono ...args) = (nobr (tt ...args))
        return e.Sexpr(nobr, (e.Sexpr(tt, args),))
    yield ("(λ ...inline . inline)", from_inline)


@fn(BUILTINS, "e")
def entity():
    r"""
    Creates an HTML entity. %%(tt "(e \"mdash\")")%% renders as %%(tt "&mdash;")%%.
    """
    def from_str(s):
        return e.InlineRaw(f"&{s.value};")
    yield ("(λ str . inline)", from_str)


@fn(BUILTINS, "$")
def concat():
    """
    Concatenate multiple elements.
    """
    def from_inline(*args):
        return e.InlineConcat(args)
    yield ("(λ ...inline . inline)", from_inline)

    def from_mixed(*args):
        return e.BlockConcat(args)
    yield ("(λ ...inline|block . inline|block)", from_mixed)


@fn(BUILTINS, "h")
def heading():
    """
    Heading. Represents the %%(tt "<h1>..<h6>")%% HTML tags.
    """
    FN_TYPE = type_parser.parse_fn("(λ ...inline . block)")

    def from_int(n: e.Integer):
        def from_inline(*args):
            return e.BlockTag(f"h{n.value}", "", args)
        return e.Function({FN_TYPE: from_inline})
    yield ("(λ int . (λ ...inline . block))", from_int)


@fn(BUILTINS, "style")
def style_inline():
    """
    Applies CSS styling to an inline element. Use sparingly.
    """
    FN_TYPE = type_parser.parse_fn("(λ ...inline . inline)")

    def from_str(s: e.String):
        def from_inline(*args):
            return e.InlineTag("span", "style=" + json.dumps(s.value), args)
        return e.Function({FN_TYPE: from_inline})
    yield ("(λ str . (λ ...inline . inline))", from_str)


@fn(BUILTINS, "list-unordered")
def list_unordered():
    """
    Represents the %%(tt "<ul>")%% HTML tag.
    """
    def from_inline(*args):
        return e.BlockTag(
            "ul",
            "",
            # NOTE Pyright heisenbug:
            tuple(e.BlockTag("li", "", (arg,)) for arg in args)
        )
    yield ("(λ ...inline . block)", from_inline)


@fn(BUILTINS, "list-ordered")
def list_ordered():
    """
    Represents the %%(tt "<ol>")%% HTML tag.
    """
    def from_inline(*args):
        return e.BlockTag(
            "ol",
            "",
            # NOTE Pyright heisenbug:
            tuple(e.BlockTag("li", "", (arg,)) for arg in args)
        )
    yield ("(λ ...inline . block)", from_inline)


@fn(BUILTINS, "p")
def paragraph():
    """
    Represents the %%(tt "<p>")%% HTML tag.
    """
    def from_inline(*args):
        return e.BlockTag("p", "", args)
    yield ("(λ ...inline|block . block)", from_inline)


@fn(BUILTINS, "a")
def link():
    """
    Represents the %%(tt "<a>")%% HTML tag.
    """
    def from_str_inline(adr, text):
        return e.InlineTag("a", f"href={json.dumps(adr.value)}", (text,))
    yield ("(λ str inline . inline)", from_str_inline)


@fn(BUILTINS, "horizontal-rule")
def horizontal_rule():
    """
    Represents the %%(tt "<hr/>")%% HTML tag.
    """
    def from_void():
        return e.ClosedBlockTag("hr", "", include_slash=True)
    yield ("(λ . block)", from_void)


@fn(BUILTINS, "--")
def emdash():
    """
    The "em dash" (&mdash;).
    """
    def from_void():
        return e.InlineRaw("&mdash;")
    yield ("(λ . inline)", from_void)


@fn(BUILTINS, "pre")
def pre():
    """
    Represents the %%(tt "<pre>")%% HTML tag.

    Make sure to use a multiline (\"\"\"...\"\"\") string here.
    """
    def from_inline(*args):
        elements = []
        for arg in args:
            elements.append(arg)
            elements.append(e.InlineRaw("\n"))
        return e.BlockTag("pre", "", tuple(elements))
    yield ("(λ ...str . block)", from_inline)


@fn(BUILTINS, "map")
def map_function():
    """
    Map a function onto a list of values.

    The overloads are messy and will soon be refactored.
    """
    INPUT_FN_INLINE = et.TFunction((et.TInline(),), None, et.TInline())
    # HACK... `(λ ...a . t)` fits everywhere `(λ a . t)` fits,
    # but my type system doesn't know that yet
    INPUT_FN_INLINE2 = et.TFunction((), et.TInline(), et.TInline())  # HACK
    FN_TYPE_INLINE = et.TFunction((), et.TInline(), et.TInline())

    INPUT_FN_STR = et.TFunction((et.TStr(),), None, et.TInline())
    INPUT_FN_STR2 = et.TFunction((), et.TStr(), et.TInline())
    FN_TYPE_STR = et.TFunction((), et.TStr(), et.TInline())

    def from_fn_inline(fn):
        def from_inl(*args):
            return e.InlineConcat(tuple(e.Sexpr(fn, (arg,)) for arg in args))
        return e.Function({FN_TYPE_INLINE: from_inl})
    yield ((INPUT_FN_INLINE,), None, FN_TYPE_INLINE, from_fn_inline)
    yield ((INPUT_FN_INLINE2,), None, FN_TYPE_INLINE, from_fn_inline)  # HACK
    yield ((INPUT_FN_STR,), None, FN_TYPE_STR, from_fn_inline)
    yield ((INPUT_FN_STR2,), None, FN_TYPE_STR, from_fn_inline)

    INPUT_FN_BLOCK = et.TFunction((et.TUnion((et.TBlock(), et.TInline())),), None, et.TBlock())
    INPUT_FN_BLOCK2 = et.TFunction((), et.TUnion((et.TBlock(), et.TInline())), et.TBlock())  # HACK
    FN_TYPE_BLOCK = et.TFunction((), et.TUnion((et.TBlock(), et.TInline())), et.TBlock())

    def from_fn_block(fn):
        def from_ren(*args):
            return e.BlockConcat(tuple(e.Sexpr(fn, (arg,)) for arg in args))  # type: ignore
        return e.Function({FN_TYPE_BLOCK: from_ren})
    yield ((INPUT_FN_BLOCK,), None, FN_TYPE_BLOCK, from_fn_block)
    yield ((INPUT_FN_BLOCK2,), None, FN_TYPE_BLOCK, from_fn_block)  # HACK


@fn(BUILTINS, "sepmap")
def sepmap():
    """
    Combination of %%(tt "sep")%% and %%(tt "map")%%.
    """
    # HACK: see `@fn(BUILTINS, map)`
    INPUT_FN_INLINE = et.TFunction((et.TInline(),), None, et.TInline())
    INPUT_FN_INLINE2 = et.TFunction((), et.TInline(), et.TInline())
    INPUT_FN_STR = et.TFunction((et.TStr(),), None, et.TInline())
    INPUT_FN_STR2 = et.TFunction((), et.TStr(), et.TInline())
    FN_TYPE_INL = et.TFunction((), et.TInline(), et.TInline())
    FN_TYPE_STR = et.TFunction((), et.TStr(), et.TInline())

    def from_inl_fn(sep, fn):
        def from_inl(*args):
            #    ((sepmap ", " e) "sub" "sup" "sube")
            # == ((sep ", ") (e "sub") (e "sup") (e "sube"))
            return e.Sexpr(
                e.Sexpr(separated, (sep,)),
                tuple(e.Sexpr(fn, (arg,)) for arg in args)
            )
        return e.Function({FN_TYPE_INL: from_inl, FN_TYPE_STR: from_inl})
    yield ((et.TInline(), INPUT_FN_INLINE), None, FN_TYPE_INL, from_inl_fn)
    yield ((et.TInline(), INPUT_FN_INLINE2), None, FN_TYPE_INL, from_inl_fn)
    yield ((et.TStr(), INPUT_FN_STR), None, FN_TYPE_STR, from_inl_fn)
    yield ((et.TStr(), INPUT_FN_STR2), None, FN_TYPE_STR, from_inl_fn)


@fn(BUILTINS, "sep")
def separated():
    """
    Concatenate inline elements, separating them with a given string.
    """
    FN_TYPE = type_parser.parse_fn("(λ ...inline . inline)")

    def from_str(separator):
        def from_inline(*args):
            elements = []
            for arg in args:
                elements.append(arg)
                elements.append(separator)
            if elements != []:
                elements.pop()
            return e.InlineConcat(tuple(elements))
        return e.Function({FN_TYPE: from_inline})
    yield ((et.TInline(),), None, FN_TYPE, from_str)


@fn(BUILTINS, "nobr")
def nobr():
    """
    Replaces spaces in text with &nbsp; so that it's not subject to text wrapping.

    Does %%(bf "not")%% represent the %%(tt "nobr")%% HTML TAG.
    """
    def from_ren(ren: e.Entity):
        return e.AfterRender(ren, lambda s: s.replace(" ", "&nbsp;"))
    yield ("(λ inline . inline)", from_ren)
    yield ("(λ block . block)", from_ren)


@fn(BUILTINS, "type")
def debug_type():
    """
    Renders the type of a value as a string.
    """
    def from_any(obj: e.Entity):
        return e.String(obj.ty.signature())
    yield("(λ any . inline)", from_any)


@fn(BUILTINS, "doc")
def document_function():
    """
    Render the documentation for a function.
    """
    def from_function(fn: e.Function):
        if not isinstance(fn, e.Function):
            raise TypeError(f"Expected function, got {fn}")
        if fn._docstring_source is None:
            return e.String("(no documentation available)")
        else:
            return _parse_docstring(fn._docstring_source)
    yield("(λ any . inline)", from_function)
