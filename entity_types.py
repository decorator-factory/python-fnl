from dataclasses import dataclass
from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
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
        return "Any"


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
    def signature(self) -> str:
        return "inline"


@dataclass(frozen=True, eq=True)
class TBlock(EntityType):
    """The `block` type -- a block HTML element"""
    def signature(self) -> str:
        return "block"


@dataclass(frozen=True, eq=True)
class IInl(EntityType):
    """
    The `Inl` pseudotype

    - can be `str`, `int`, or `inline`
    - can be casted to `inline`
    """
    def match(self, value: "e.Entity") -> bool:
        if super().match(value):
            return True
        return hasattr(value, "render_inline")

    def signature(self) -> str:
        return "Inl"


@dataclass(frozen=True, eq=True)
class IBlk(EntityType):
    """
    The `Blk` pseudotype

    - can be casted to `block`
    """
    def match(self, value: "e.Entity") -> bool:
        if super().match(value):
            return True
        return hasattr(value, "render_block")

    def signature(self) -> str:
        return "Blk"


@dataclass(frozen=True, eq=True)
class IRen(EntityType):
    """
    The `Ren` pseudotype

    - something you can render as HTML
    - can be `Inl` or `Blk`
    """
    def match(self, value: "e.Entity") -> bool:
        if super().match(value):
            return True
        return IInl().match(value) or IBlk().match(value)

    def signature(self) -> str:
        return "Ren"


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


@dataclass(frozen=True, eq=True)
class TUnion(EntityType):
    """
    Union type.

    Used when one out of multiple types is expected or can be produced.
    """
    variants: Tuple[EntityType, ...]

    def match(self, value: "e.Entity") -> bool:
        if super().match(value):
            return True
        return any(t.match(value) for t in self.variants)

    def signature(self) -> str:
        return "|".join(t.signature() for t in self.variants)