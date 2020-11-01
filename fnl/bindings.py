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


@dataclass
class RuntimeDependent(e.Entity):
    getter: Callable[[Dict[str, e.Entity]], e.Entity]

    def evaluate(self, runtime) -> e.Entity:
        return self.getter(runtime).evaluate(runtime)


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

    @fn(extensions, "var")
    def var():
        """
        Part of the 'bindings' module.

        %%(tt "(var &x)")%% is used to look up the binding %%(tt "x")%%
        defined in a 'let' or 'for' clause.
        """
        def _var(quoted_name):
            name = quoted_name.subexpression.name
            if (value := get_name(name)) is not None:
                return value
            else:
                raise TypeError(f"Binding {name} not found")
        yield ("(λ &[name] . any)", _var)

    @fn(extensions, "let")
    def let():
        r"""
        Part of the 'bindings' module.

        Defines a scope in which certain bindings refer to certain expressions.
        Examples:
            %%(tt "(let &answer 42 &(bf (var &answer)))")%%,
            %%(tt "((let &(answer 42) &(pi 3)) &(bf (var &answer) \"...\" (var &pi)))")%%
        """
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

    @fn(extensions, "foreach")
    def foreach():
        r"""
        Part of the 'bindings' module.

        For each element of a 'list', render some expression while binding
        the element to a specific name.
        %%(tt "(foreach &i &(1 2 3 4) &($ (bf (var &i)) \" \")")%% will render
        boldface numbers 1, 2, 3 and 4 separated by spaces.
        """
        def _foreach(name, seq, body):
            with match([name, seq, body]) as case:
                with case('Seq(Quoted(Name(name)), Quoted(Name("nil")), Quoted(body))') as [m]:
                    name, seq, body = m.name, (), m.body

                with case('Seq(Quoted(Name(name)), Quoted(seq), Quoted(body))') as [m]:
                    name, seq, body = m.name, (m.seq.fn, *m.seq.args), m.body

            results = []
            for element in seq:
                results.append(
                    EvaluateInContext(
                        push_subscope_with({name: element}),
                        pop_subscope,
                        body
                    )
                )
            return e.Sexpr(e.Name("$"), tuple(results))

        yield ("(λ &[name] &[any] &[any] . any)", _foreach)

    @fn(extensions, "unquote")
    def unquote():
        """
        Part of the 'bindings' module.

        Extract and evaluate the expression from under the %%(tt "&")%%
        """
        def _unquote(quoted):
            return quoted.subexpression
        yield ("(λ &[any] . any)", _unquote)

    @fn(extensions, "extract-name")
    def extract_name():
        """
        Part of the 'bindings' module.

        Convert a quoted name to a string
        """
        def _extract_name(quoted_name):
            return e.String(quoted_name.subexpression.name)
        yield ("(λ &[name] . str)", _extract_name)

    @fn(extensions, "documented-names")
    def documented_names():
        """
        Part of the 'bindings' module.

        Get a list of all the documented names as a quoted s-expression:
        %%(tt "&(&bf &it &tt ...)")%%
        """
        def _get_names(runtime: Dict[str, e.Entity]):
            fn, *args = (
                e.Quoted(e.Name(key)) for key, value in runtime.items()
                if isinstance(value, e.Function) and value._docstring_source is not None
            )
            return e.Quoted(e.Sexpr(fn, tuple(args)))

        def _documented_names():
            return RuntimeDependent(_get_names)
        yield ("(λ . &[any])", _documented_names)

    return extensions
