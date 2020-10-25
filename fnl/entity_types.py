from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from . import entities as e


class EntityType:
    """
    Represents the type of `fnl.entities.Entity`.

    Used primarily for typechecking and dispatching functions.

    Note that an `EntityType` represents an FNL type, not the concrete Python
    type of an object. For example, a value of type `inline` can be one of
    many different objects in `fnl.entities`.
    """
    def match(self, value: "e.Entity") -> bool:
        """Can a value be interpreted (casted into) this type?"""
        return value.ty == self or value.ty == TAny()

    def signature(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True, eq=True)
class TAny(EntityType):
    """
    The `any` type:

    - can be casted from any type
    - can be casted into any type
    """
    def match(self, value: "e.Entity") -> bool:
        return True

    def signature(self) -> str:
        return "any"


@dataclass(frozen=True, eq=True)
class TSexpr(EntityType):
    """The `(fn x y z)` type. Makes sense only inside TQuoted."""
    function_type: EntityType
    arg_types: Tuple[EntityType, ...]

    def match(self, value: "e.Entity") -> bool:
        return (
            isinstance(value, e.Sexpr)
            and self.function_type.match(value.fn)
            and len(self.arg_types) == len(value.args)
            and all(
                t.match(arg) for (t, arg) in zip(self.arg_types, value.args)
            )
        )


@dataclass(frozen=True, eq=True)
class TName(EntityType):
    """
    The `name` type. Makes sense only inside TQuoted.

    The optional `pattern` attribute may be used to only match a particular name.
    """
    pattern: Optional[Callable[[str], bool]] = None

    def match(self, value: "e.Entity") -> bool:
        if not isinstance(value, e.Name):
            return False

        return self.pattern is None or self.pattern(value.name)


@dataclass(frozen=True, eq=True)
class TQuoted(EntityType):
    """The `&[T]` type"""
    parameter: EntityType

    def match(self, value: "e.Entity") -> bool:
        if super().match(value):
            return True
        return isinstance(value, e.Quoted) and self.parameter.match(value.subexpression)

    def signature(self) -> str:
        return f"&[{self.parameter.signature()}]"


@dataclass(frozen=True, eq=True)
class TInt(EntityType):
    """The `int` type"""
    def signature(self) -> str:
        return "int"


@dataclass(frozen=True, eq=True)
class TStr(EntityType):
    """The `str` type"""
    def signature(self) -> str:
        return "str"


@dataclass(frozen=True, eq=True)
class TInline(EntityType):
    """The `inline` type -- an inline HTML element"""
    def match(self, value: "e.Entity") -> bool:
        if super().match(value):
            return True
        return hasattr(value, "render_inline")

    def signature(self) -> str:
        return "inline"


@dataclass(frozen=True, eq=True)
class TBlock(EntityType):
    """The `block` type -- a block HTML element"""
    def match(self, value: "e.Entity") -> bool:
        if super().match(value):
            return True
        return hasattr(value, "render_block")

    def signature(self) -> str:
        return "block"


@dataclass(frozen=True, eq=True)
class TFunction(EntityType):
    """The function type"""
    arg_types: Tuple[EntityType, ...]
    rest_type: Optional[EntityType]
    return_type: EntityType

    def match(self, value: "e.Entity") -> bool:
        if super().match(value):
            return True
        return (
            hasattr(value, "call")
            and value.return_type_when_called_with(  # type: ignore
                args=self.arg_types,
                rest=self.rest_type,
            ) == self.return_type
        )

    def signature(self) -> str:
        args_repr = " ".join(t.signature() for t in self.arg_types)
        if self.rest_type is not None:
            args_repr += " ..." + self.rest_type.signature()
        return_repr = self.return_type.signature()
        return f"(λ {args_repr} . {return_repr})"


@dataclass(frozen=True)
class TUnion(EntityType):
    """
    Union type.

    Used when one out of multiple types is expected or can be produced.
    """
    variants: Tuple[EntityType, ...]

    def __eq__(self, other):
        if not isinstance(other, TUnion):
            return NotImplemented
        return set(self.variants) == set(other.variants)

    def __hash__(self):
        return hash(("union", frozenset(self.variants)))

    def match(self, value: "e.Entity") -> bool:
        if super().match(value):
            return True
        return any(t.match(value) for t in self.variants)

    def signature(self) -> str:
        return "|".join(t.signature() for t in self.variants)
