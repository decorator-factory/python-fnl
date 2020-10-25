from . import entity_types as et
from lark import Lark, v_args, Transformer


@v_args(inline=True)
class TypeTransformer(Transformer):
    @staticmethod
    def primitive_type(token):
        return {
            "any": et.TAny,
            "never": lambda: et.TUnion(()),
            "str": et.TStr,
            "int": et.TInt,
            "inline": et.TInline,
            "block": et.TBlock,
        }[str(token)]()

    @staticmethod
    def union_type(*types):
        return et.TUnion(types)

    @staticmethod
    def function_type(*types):
        *required_types, rest_type, return_type = types
        # rest_type can be None
        # NOTE: Bug in Pyright -------V
        return et.TFunction(tuple(required_types), rest_type, return_type)  # type: ignore


parser = Lark.open(
    "types.lark",
    rel_to=__file__,
    parser="lalr",
    transformer=TypeTransformer(),
    propagate_positions=True,
    maybe_placeholders=True,
)


def parse(source: str) -> et.EntityType:
    return parser.parse(source)  # type: ignore


def parse_fn(source: str) -> et.TFunction:
    """Utility function for cases where a function type is expected"""
    parsed = parse(source)
    if not isinstance(parsed, et.TFunction):
        raise ValueError(f"{source} should've been a function")
    return parsed
