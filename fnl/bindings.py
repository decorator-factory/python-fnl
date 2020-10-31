from dataclasses import dataclass
from typing import Callable, Dict, Optional, Any
from fnl.type_parser import parse_fn
from . import e
from .definitions import fn
from context_manager_patma import match


@dataclass
class EvaluateInContext(e.Entity):
    before_evaluation: Callable[[Dict[str, e.Entity]], Any]
    after_evaluation: Callable[[Dict[str, e.Entity]], Any]
    subexpression: e.Entity

    def evaluate(self, runtime) -> e.Entity:
        self.before_evaluation(runtime)
        result = self.subexpression.evaluate(runtime)
        self.after_evaluation(runtime)
        return result


def bindings() -> Dict[str, e.Entity]:
    extensions = {}

    parent_loops = []
    bindings = {}

    def get_name(name: str) -> Optional[e.Entity]:
        if name in bindings:
            return bindings[name]

        for parent_bindings in reversed(parent_loops):
            if name in parent_bindings:
                return parent_bindings[name]

        return None

    @fn(extensions, "var")
    def var():
        def _var(quoted_name):
            name = quoted_name.subexpression.name
            if (value := get_name(name)) is not None:
                return value
            else:
                raise TypeError(f"Binding {name} not found")
        yield ("(λ &[name] . any)", _var)

    @fn(extensions, "let")
    def let():
        def push_subscope_with(new_scope):
            def push_subscope(runtime):
                nonlocal bindings
                parent_loops.append(bindings)
                bindings = {
                    name: expr.evaluate(runtime)
                    for name, expr in new_scope.items()
                }
            return push_subscope

        def pop_subscope(_runtime):
            nonlocal bindings
            bindings = parent_loops.pop()

        def from_many(*kv_pairs):
            new_bindings = {}
            for entry in kv_pairs:
                with match(entry) as case:
                    with case('Quoted(Sexpr(Name(name), expr))') as [m]:
                        new_bindings[m.name] = m.expr

            def _from_many(quoted_body):
                return EvaluateInContext(
                    push_subscope_with(new_bindings),
                    pop_subscope,
                    quoted_body.subexpression
                )

            return e.Function({parse_fn("(λ &[any] . any)"): _from_many})
        yield ("(λ ...&[(name any)] . (λ &[any] . any))", from_many)

        def from_one(key, value, quoted_body):
            return EvaluateInContext(
                push_subscope_with({key.subexpression.name: value}),
                pop_subscope,
                quoted_body.subexpression
            )
        yield ("(λ &[name] any &[any] . any)", from_one)

    return extensions
