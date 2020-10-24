import json
from typing import Dict
from . import entity_types as et
from . import entities as e
from . import type_parser


BUILTINS: Dict[str, e.Entity] = {}


def fn(target: Dict[str, e.Entity], name: str):
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
        target[name] = e.Function(overloads)
        return target[name]
    return _add_fn


@fn(BUILTINS, "bf")
def boldface():
    def from_inline(*args):
        return e.InlineTag("b", "", args)
    yield ("(λ ...Inl . inline)", from_inline)


@fn(BUILTINS, "it")
def italics():
    def from_inline(*args):
        return e.InlineTag("i", "", args)
    yield ("(λ ...Inl . inline)", from_inline)


@fn(BUILTINS, "tt")
def tt():
    def from_inline(*args):
        return e.InlineTag("tt", "", args)
    yield ("(λ ...Inl . inline)", from_inline)


@fn(BUILTINS, "mono")
def monospace():
    def from_inline(*args):
        # (mono ...args) = (nobr (tt ...args))
        return e.Sexpr(nobr, (e.Sexpr(tt, args),))
    yield ("(λ ...Inl . inline)", from_inline)


@fn(BUILTINS, "e")
def entity():
    def from_str(s):
        return e.InlineRaw(f"&{s.value};")
    yield ("(λ str . inline)", from_str)


@fn(BUILTINS, "$")
def concat():
    def from_inline(*args):
        return e.InlineConcat(args)
    yield ("(λ ...Inl . inline)", from_inline)

    def from_mixed(*args):
        return e.BlockConcat(args)
    yield ("(λ ...Ren . Ren)", from_mixed)


@fn(BUILTINS, "h")
def heading():
    FN_TYPE = type_parser.parse_fn("(λ ...Inl . block)")

    def from_int(n: e.Integer):
        def from_inline(*args):
            return e.BlockTag(f"h{n.value}", "", args)
        return e.Function({FN_TYPE: from_inline})
    yield ("(λ int . (λ ...Inl . block))", from_int)


@fn(BUILTINS, "style")
def style_inline():
    FN_TYPE = type_parser.parse_fn("(λ ...Inl . inline)")

    def from_str(s: e.String):
        def from_inline(*args):
            return e.InlineTag("span", "style=" + json.dumps(s.value), args)
        return e.Function({FN_TYPE: from_inline})
    yield ("(λ str . (λ ...Inl . inline))", from_str)


@fn(BUILTINS, "list-unordered")
def list_unordered():
    def from_inline(*args):
        return e.BlockTag(
            "ul",
            "",
            tuple(e.BlockTag("li", "", (arg,)) for arg in args)  # type: ignore # NOTE Pyright bug
        )
    yield ("(λ ...Inl . block)", from_inline)


@fn(BUILTINS, "list-ordered")
def list_ordered():
    def from_inline(*args):
        return e.BlockTag(
            "ol",
            "",
            tuple(e.BlockTag("li", "", (arg,)) for arg in args)  # type: ignore # NOTE Pyright bug
        )
    yield ("(λ ...Inl . block)", from_inline)


@fn(BUILTINS, "p")
def paragraph():
    def from_inline(*args):
        return e.BlockTag("p", "", args)
    yield ("(λ ...Ren . block)", from_inline)


@fn(BUILTINS, "a")
def link():
    def from_str_inline(adr, text):
        return e.InlineTag("a", f"href={json.dumps(adr.value)}", (text,))
    yield ("(λ str Inl . inline)", from_str_inline)


@fn(BUILTINS, "horizontal-rule")
def horizontal_rule():
    def from_void():
        return e.BlockRaw("<hr/>")
    yield ("(λ . block)", from_void)


@fn(BUILTINS, "--")
def emdash():
    def from_void():
        return e.InlineRaw("&mdash;")
    yield ("(λ . inline)", from_void)


@fn(BUILTINS, "nl")
def newline():
    def from_void():
        return e.InlineRaw("\n")
    yield ("(λ . inline)", from_void)


@fn(BUILTINS, "pre")
def pre():
    def from_inline(*args):
        elements = []
        for arg in args:
            elements.append(arg)
            elements.append(e.InlineRaw("\n"))
        return e.BlockTag("pre", "", tuple(elements))  # type: ignore # NOTE Pyright bug
    yield ("(λ ...str . block)", from_inline)


@fn(BUILTINS, "map")
def map_function():
    INPUT_FN_INLINE = et.TFunction((et.IInl(),), None, et.TInline())
    # HACK... `(λ ...a . t)` fits everywhere `(λ a . t)` fits,
    # but my type system doesn't know that yet
    INPUT_FN_INLINE2 = et.TFunction((), et.IInl(), et.TInline())  # HACK
    FN_TYPE_INLINE = et.TFunction((), et.IInl(), et.TInline())

    INPUT_FN_STR = et.TFunction((et.TStr(),), None, et.TInline())
    INPUT_FN_STR2 = et.TFunction((), et.TStr(), et.TInline())
    FN_TYPE_STR = et.TFunction((), et.TStr(), et.TInline())

    def from_fn_inline(fn):
        def from_inl(*args):
            # NOTE Pyright bug
            return e.InlineConcat(tuple(e.Sexpr(fn, (arg,)) for arg in args))  # type: ignore
        return e.Function({FN_TYPE_INLINE: from_inl})
    yield ((INPUT_FN_INLINE,), None, FN_TYPE_INLINE, from_fn_inline)
    yield ((INPUT_FN_INLINE2,), None, FN_TYPE_INLINE, from_fn_inline)  # HACK
    yield ((INPUT_FN_STR,), None, FN_TYPE_STR, from_fn_inline)
    yield ((INPUT_FN_STR2,), None, FN_TYPE_STR, from_fn_inline)

    INPUT_FN_BLOCK = et.TFunction((et.IRen(),), None, et.TBlock())
    INPUT_FN_BLOCK2 = et.TFunction((), et.IRen(), et.TBlock())  # HACK
    FN_TYPE_BLOCK = et.TFunction((), et.IRen(), et.TBlock())

    def from_fn_block(fn):
        def from_ren(*args):
            # NOTE Pyright bug
            return e.BlockConcat(tuple(e.Sexpr(fn, (arg,)) for arg in args))  # type: ignore
        return e.Function({FN_TYPE_BLOCK: from_ren})
    yield ((INPUT_FN_BLOCK,), None, FN_TYPE_BLOCK, from_fn_block)
    yield ((INPUT_FN_BLOCK2,), None, FN_TYPE_BLOCK, from_fn_block)  # HACK


@fn(BUILTINS, "sepmap")
def sepmap():
    # HACK: see `@fn(BUILTINS, map)`
    INPUT_FN_INLINE = et.TFunction((et.IInl(),), None, et.TInline())
    INPUT_FN_INLINE2 = et.TFunction((), et.IInl(), et.TInline())
    INPUT_FN_STR = et.TFunction((et.TStr(),), None, et.TInline())
    INPUT_FN_STR2 = et.TFunction((), et.TStr(), et.TInline())
    FN_TYPE_INL = et.TFunction((), et.IInl(), et.TInline())
    FN_TYPE_STR = et.TFunction((), et.TStr(), et.TInline())

    def from_inl_fn(sep, fn):
        def from_inl(*args):
            #    ((sepmap ", " e) "sub" "sup" "sube")
            # == ((sep ", ") (e "sub") (e "sup") (e "sube"))
            return e.Sexpr(
                e.Sexpr(separated, (sep,)),
                tuple(e.Sexpr(fn, (arg,)) for arg in args)  # type: ignore # NOTE Pyright bug
            )
        return e.Function({FN_TYPE_INL: from_inl, FN_TYPE_STR: from_inl})
    yield ((et.IInl(), INPUT_FN_INLINE), None, FN_TYPE_INL, from_inl_fn)
    yield ((et.IInl(), INPUT_FN_INLINE2), None, FN_TYPE_INL, from_inl_fn)
    yield ((et.TStr(), INPUT_FN_STR), None, FN_TYPE_STR, from_inl_fn)
    yield ((et.TStr(), INPUT_FN_STR2), None, FN_TYPE_STR, from_inl_fn)


@fn(BUILTINS, "sep")
def separated():
    FN_TYPE = type_parser.parse_fn("(λ ...Inl . inline)")

    def from_str(separator):
        def from_inline(*args):
            elements = []
            for arg in args:
                elements.append(arg)
                elements.append(separator)
            if elements != []:
                elements.pop()
            return e.InlineConcat(tuple(elements))  # type: ignore # NOTE Pyright bug
        return e.Function({FN_TYPE: from_inline})
    yield ((et.IInl(),), None, FN_TYPE, from_str)


@fn(BUILTINS, "nobr")
def nobr():
    def from_ren(ren: e.Entity):
        return e.AfterRender(ren, lambda s: s.replace(" ", "&nbsp;"))
    yield ("(λ Inl . inline)", from_ren)
    yield ("(λ Blk . block)", from_ren)


@fn(BUILTINS, "type")
def debug_type():
    def from_any(obj: e.Entity):
        return e.String(obj.ty.signature())
    yield("(λ any . inline)", from_any)
