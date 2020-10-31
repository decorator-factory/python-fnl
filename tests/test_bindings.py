import fnl


def test_let_multibinding():
    assert (
        fnl.html(
            """
            ((let
              &(x "foo"))
              &($
                (var &x)
                ; nested scope can temporarily shadow names:
                ((let
                  &(x "bar") &(y "baz"))
                  &($
                    (var &x)
                      (var &y)))
                    ; and then `x` is still available
                (var &x)))
            """,
            fnl.bindings()
        )
        == "foobarbazfoo"
    )


def test_let_single_binding():
    assert (
        fnl.html(
            """
            (let
              &x "foo"
              &($
                (var &x)
                (let
                  &x "bar"
                  &(let
                    &y "baz"
                    &($
                      (var &x)
                      (var &y))))
                (var &x)))
            """,
            fnl.bindings()
        )
        == "foobarbazfoo"
    )