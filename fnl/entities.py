from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, Sequence, TypeVar, Optional, Tuple
from fnl import entity_types as et
import html


R = TypeVar("R", bound="HtmlRender")


class HtmlRender:
    """Represents a value that can be rendered as HTML."""

    def as_text(self) -> str:
        """Render as HTML"""
        raise NotImplementedError

    def fmap(self: R, fn: Callable[[str], str]) -> R:
        """Apply a transformation to the textual part of HTML"""
        raise NotImplementedError


@dataclass
class RawHtml(HtmlRender):
    """Renders `content` as is (without escaping)"""
    content: str

    def as_text(self) -> str:
        return self.content

    def fmap(self, fn: Callable[[str], str]):
        # We can't know what parts of raw HTML are text, so do nothing
        return self


@dataclass
class SafeHtml(HtmlRender):
    """Renders the escaped version of `unsafe_content`."""
    unsafe_content: str
    _after_escape: Callable[[str], str] = staticmethod(lambda s: s)  # type: ignore

    def as_text(self) -> str:
        return self._after_escape(html.escape(self.unsafe_content, quote=True))

    def fmap(self, fn: Callable[[str], str]):
        return SafeHtml(
            self.unsafe_content,
            _after_escape=lambda s: fn(self._after_escape(s))
        )


@dataclass
class HtmlTag(HtmlRender):
    """
    Renders an HTML tag named `tag` with options being `options`.
    `options` is not sanitized -- make sure it's right.

    >>> HtmlTag("b", 'class="c"', [RawHtml("hello"), RawHtml(" world")]).as_text()
    '<b class="c">hello world</b>'
    """
    tag: str
    options: str
    content: Sequence[HtmlRender]

    def as_text(self) -> str:
        options = "" if self.options == "" else " " + self.options
        return (
             f"<{self.tag}{options}>"
            + "".join(r.as_text() for r in self.content)
            +f"</{self.tag}>"
        )

    def fmap(self, fn: Callable[[str], str]):
        return HtmlTag(
            self.tag,
            self.options,
            [r.fmap(fn) for r in self.content]
        )

@dataclass
class Concat(HtmlRender):
    """
    Renders multiple elements in order.

    >>> Concat([RawHtml("hello"), RawHtml(" world")]).as_text()
    'hello world'
    """
    children: Sequence[HtmlRender]

    def as_text(self) -> str:
        return "".join(r.as_text() for r in self.children)

    def fmap(self, fn: Callable[[str], str]):
        return Concat([r.fmap(fn) for r in self.children])


class Entity:
    """
    Base class for all expressions

    An entity is renderable as an inline element if it has a `render_inline`
    method, and renderable as a block element if it has a `render_block`
    method.
    """
    @property
    def ty(self) -> et.EntityType:
        """Return the type to which the entity belongs"""
        return et.TAny()

    def render(self, runtime) -> HtmlRender:
        """Render the entity as an HTML tree"""
        e = self.evaluate(runtime)
        if hasattr(e, "render_inline"):
            return e.render_inline(runtime) # type: ignore
        if hasattr(e, "render_block"):
            return e.render_block(runtime) # type: ignore
        raise TypeError(f"Cannot render {e}")

    def evaluate(self, runtime) -> Entity:
        """Evaluate an expression until it settles on a final value"""
        return self


@dataclass(eq=True)
class Name(Entity):
    """Represents getting a global variable by its name"""
    name: str

    _cached: Optional[Entity] = None

    @property
    def ty(self):
        if self._cached is None:
            return et.TAny()
        else:
            return self._cached.ty

    def evaluate(self, runtime) -> Entity:
        self._cached = runtime[self.name]
        if self._cached is None:
            raise KeyError(f"Name {self.name} not found")
        return self._cached


class CallError(Exception):
    """Error that occurs when evaluating an s-expression"""
    def __init__(self, msg: str, propagate: bool):
        self.msg = msg
        self.propagate = propagate
        self.args = (msg, propagate)


@dataclass
class Sexpr(Entity):
    """Represents a function call"""
    fn: Entity
    args: Tuple[Entity, ...]

    _position: Optional[Tuple[int, int]] = None # (line, column)
    _cached: Optional[Entity] = None

    def __eq__(self, other):
        if not isinstance(other, Sexpr):
            return NotImplemented

        return (self.fn, self.args) == (other.fn, other.args)

    @property
    def ty(self):
        if self._cached is None:
            return et.TAny()
        return self._cached.ty

    def _type_mismatch(self, msg: str):
        # If we know where this s-expression is located, we need to stop
        # propagating the error and abort. Otherwise, the line and column
        # are known upstream
        if self._position is None:
            raise CallError(msg, propagate=True)
        else:
            line, column = self._position
            raise CallError(msg.format(line=line, column=column), propagate=False)

    def evaluate(self, runtime):
        self.fn = self.fn.evaluate(runtime)
        if not hasattr(self.fn, "call"):
            self._type_mismatch(
                f"Trying to call {self.fn.ty.signature()}"
                " (line {line}, column {column})"
            )
        self.args = tuple(e.evaluate(runtime) for e in self.args)

        error = None
        try:
            self._cached = self.fn.call(*self.args).evaluate(runtime) # type: ignore
        except TypeError as e:
            error = "".join(e.args) + " (line {line}, column {column})"
        # raise the exception without the long traceback:
        if error is not None:
            self._type_mismatch(error)

        assert self._cached is not None
        return self._cached


@dataclass(frozen=True, eq=True)
class Integer(Entity):
    value: int

    ty = et.TInt()

    def render_inline(self, runtime) -> HtmlRender:
        return RawHtml(str(self.value))


@dataclass(frozen=True, eq=True)
class String(Entity):
    value: str

    ty = et.TStr()

    def render_inline(self, runtime):
        return SafeHtml(self.value)


@dataclass(frozen=True, eq=True)
class InlineTag(Entity):
    """Represents an inline HTML tag"""
    tag: str
    options: str
    children: Tuple[Entity, ...]

    ty = et.TInline()

    def render_inline(self, runtime):
        return HtmlTag(
            self.tag,
            self.options,
            [c.render_inline(runtime) for c in self.children]  # type: ignore
        )


@dataclass(frozen=True, eq=True)
class BlockTag(Entity):
    """Represents a block HTML tag"""
    tag: str
    options: str
    children: Tuple[Entity, ...]

    ty = et.TBlock()

    def render_block(self, runtime):
        return HtmlTag(
            self.tag,
            self.options,
            [c.render(runtime) for c in self.children]  # type: ignore
        )


@dataclass(frozen=True, eq=True)
class InlineRaw(Entity):
    """Represents raw HTML source code which is rendered inline"""
    html: str

    ty = et.TInline()

    def render_inline(self, runtime):
        return RawHtml(self.html)


@dataclass(frozen=True, eq=True)
class BlockRaw(Entity):
    """Represents raw HTML source code which is rendered as a block"""
    html: str

    ty = et.TInline()

    def render_block(self, runtime):
        return RawHtml(self.html)


@dataclass(frozen=True, eq=True)
class InlineConcat(Entity):
    """Represents a concatenation of multiple inline entities"""
    children: Tuple[Entity, ...]

    ty = et.TInline()

    def render_inline(self, runtime):
        return Concat([e.render_inline(runtime) for e in self.children])  # type: ignore


@dataclass(frozen=True, eq=True)
class BlockConcat(Entity):
    """Represents a concatenation of multiple entities of mixed kinds"""
    children: Tuple[Entity, ...]

    ty = et.TBlock()

    def render_block(self, runtime):
        return Concat([e.render(runtime) for e in self.children])  # type: ignore


@dataclass(frozen=True, eq=True)
class Function(Entity):
    """
    Represents a function.

    `overloads` is a mapping between a particular function signature and the
    callable that should be called when that signature is matched.

    For concrete examples, see `tests/test_entities.py`
    """
    overloads: Dict[et.TFunction, Callable]

    @property
    def ty(self):
        return et.TUnion(tuple(self.overloads.keys()))

    def call(self, *args):
        """
        Call the function with the given arguments.

        If no overload matches the function, a TypeError is thrown.
        """
        for (o, f) in self.overloads.items():
            if o.rest_type is None:
                same_length = len(o.arg_types) == len(args)
                types_match = all(
                    expected_type.match(arg)
                    for arg, expected_type in zip(args, o.arg_types)
                )
                if same_length and types_match:
                    return f(*args)
            else:
                for i in range(len(args) + 1):
                    positional_args, rest_args = args[:i], args[i:]

                    # check if the rest_args are the same
                    assert o.rest_type is not None
                    if not all(o.rest_type.match(r) for r in rest_args):
                        break

                    for arg, expected_type in zip(positional_args, o.arg_types):
                        if not expected_type.match(arg):
                            break

                    return f(*positional_args, *rest_args)
        arg_types_repr = "(" + ", ".join(e.ty.signature() for e in args) + ")"
        raise TypeError(f"Cannot call {self.ty.signature()} with {arg_types_repr}")


    def return_type_when_called_with(self, *, args, rest):
        # TODO: implement these cases:
        # (λ x ...y . z) can be called as (λ x y y y . z)
        # (λ x y ...y . z) can be called as (λ x y y y . z)
        # (λ x y y y y ...y . z) can't be called as (λ x y y y . z)
        for o in self.overloads.keys():
            if o.arg_types == args and o.rest_type == rest:
                return o.return_type
        return None


@dataclass(eq=True)
class AfterRender(Entity):
    """
    Apply the function to the rendered content of an element.
    For example, the `nobr` function replaces every ` ` with `&nbsp;`
    """
    subexpr: Entity
    fn: Callable[[str], str]

    @property
    def ty(self):
        return self.subexpr.ty

    def evaluate(self, runtime):
        self.subexpr = self.subexpr.evaluate(runtime)
        return self

    def render(self, runtime):
        return self.subexpr.render(runtime).fmap(self.fn)

    # whether an Entity is renderable as inline or as block is determined
    # by it having a render_inline or render_block attribute, so this is
    # necessary to preserve strong typing:
    def __getattr__(self, attr):
        if attr == "render_inline":
            if hasattr(self.subexpr, "render_inline"):
                return self.subexpr.render_inline  # type: ignore
        elif attr == "render_block":
            if hasattr(self.subexpr, "render_block"):
                return self.subexpr.render_block  # type: ignore
        else:
            raise AttributeError(attr)

    def _render_inline(self, runtime):
        return self.subexpr.render_inline(runtime).fmap(self.fn)  # type: ignore

    def _render_block(self, runtime):
        return self.subexpr.render_block(runtime).fmap(self.fn)  # type: ignore
