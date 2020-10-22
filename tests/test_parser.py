import fnl
import fnl.entity_types as et
import fnl.entities as e


def test_parser():
    SOURCE = """
        ; this is a comment
        ($
            ((h 1)
                "Hello, world!"
            )
            "Welcome to " (bf "my") " blog! It is:"
            (list-unordered
                (it "cool")
                ($ (bf "super") " awesome") ; this is a comment as well
                ((style "color: red; font-size: 100%") "amazing")
            )
        )
    """

    ast = fnl.parse(SOURCE)

    assert ast == e.Sexpr(
        e.Name("$"),
        (
            e.Sexpr(
                e.Sexpr(e.Name("h"), (e.Integer(1),)),
                (e.String("Hello, world!"),)
            ),
            e.String("Welcome to "), e.Sexpr(e.Name("bf"), (e.String("my"),)), e.String(" blog! It is:"),
            e.Sexpr(
                e.Name("list-unordered"),
                (
                    e.Sexpr(e.Name("it"), (e.String("cool"),)),
                    e.Sexpr(e.Name("$"),
                        (
                            e.Sexpr(e.Name("bf"), (e.String("super"),)),
                            e.String(" awesome")
                        )
                    ),
                    e.Sexpr(
                        e.Sexpr(e.Name("style"), (e.String("color: red; font-size: 100%"),)),
                        (e.String("amazing"),)
                    )
                )
            )
        )
    )