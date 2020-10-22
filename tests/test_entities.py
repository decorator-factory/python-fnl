import fnl.entity_types as et
import fnl.entities as e


def test_function_with_fixed_signature():
    add = e.Function({
        et.TFunction(
            (et.TInt(), et.TInt()),
            None,
            et.TInt()
        ): lambda x, y: e.Integer(x.value + y.value)
    })

    assert add.call(e.Integer(5), e.Integer(4)) == e.Integer(9)


def test_function_with_varargs_signature():
    add = e.Function({
        et.TFunction(
            (),
            et.TInt(),
            et.TInt()
        ): lambda *args: e.Integer(sum(e.value for e in args))
    })

    assert add.call() == e.Integer(0)
    assert add.call(e.Integer(5)) == e.Integer(5)
    assert add.call(e.Integer(5), e.Integer(4)) == e.Integer(9)
    assert add.call(e.Integer(5), e.Integer(4), e.Integer(1)) == e.Integer(10)


def test_overloaded_function():
    add = e.Function({
        et.TFunction(
            (et.TInt(), et.TInt()),
            None,
            et.TInt()
        ): lambda x, y: e.Integer(x.value + y.value),

        et.TFunction(
            (et.TStr(), et.TStr()),
            None,
            et.TStr()
        ): lambda x, y: e.String(x.value + y.value)
    })

    assert add.call(e.Integer(5), e.Integer(4)) == e.Integer(9)
    assert add.call(e.String("ab"), e.String("cd")) == e.String("abcd")


def test_sexpr():
    add = e.Function({
        et.TFunction(
            (et.TInt(), et.TInt()),
            None,
            et.TInt()
        ): lambda x, y: e.Integer(x.value + y.value)
    })

    runtime = {"+": add}

    sexpr = e.Sexpr(
        e.Name("+"),
        (e.Integer(5), e.Integer(4))
    )

    # before evaluation, Sexpr doesn't have a definite type
    assert sexpr.ty == et.TAny()
    assert sexpr.evaluate(runtime) == e.Integer(9)
    # .evaluate mutates a Sexpr and assigns a type to it
    assert sexpr.ty == et.TInt()