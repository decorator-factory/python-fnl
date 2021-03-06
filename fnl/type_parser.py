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
    def name_type(*allowed_names):
        if allowed_names == ():
            return et.TName()
        else:
            _names = frozenset(allowed_names)
            return et.TName(_names.__contains__)

    @staticmethod
    def union_type(*types):
        return et.TUnion(types)

    @staticmethod
    def quoted_type(parameter):
        return et.TQuoted(parameter)

    @staticmethod
    def sexpr_type(fn_type, *arg_types):
        return et.TSexpr(fn_type, arg_types)

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
