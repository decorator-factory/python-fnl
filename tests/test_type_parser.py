import fnl


def test_primitive_types():
    assert fnl.type_parser.parse("int") == fnl.et.TInt()
    assert fnl.type_parser.parse("str") == fnl.et.TStr()
    assert fnl.type_parser.parse("inline") == fnl.et.TInline()
    assert fnl.type_parser.parse("block") == fnl.et.TBlock()
    assert fnl.type_parser.parse("any") == fnl.et.TAny()


def test_quoted_type():
    assert fnl.type_parser.parse("&[int]") == fnl.et.TQuoted(fnl.et.TInt())


def test_sexpr_type():
    assert (
        fnl.type_parser.parse("&[(int str str)]")
        == fnl.et.TQuoted(fnl.et.TSexpr(fnl.et.TInt(), (fnl.et.TStr(), fnl.et.TStr())))
    )


def test_unbounded_name_type():
    assert fnl.type_parser.parse("name") == fnl.et.TName()


def test_bounded_name_type():
    t = fnl.type_parser.parse("name[foo|bar]")
    assert isinstance(t, fnl.et.TName)
    assert t.match(fnl.e.Name("foo"))
    assert t.match(fnl.e.Name("bar"))
    assert not t.match(fnl.e.Name("baz"))


def test_union_type():
    assert (
        fnl.type_parser.parse("int | str")
        == fnl.et.TUnion((fnl.et.TInt(), fnl.et.TStr()))
    )
    assert (
        fnl.type_parser.parse("int | str | inline")
        == fnl.et.TUnion((fnl.et.TInt(), fnl.et.TStr(), fnl.et.TInline()))
    )


def test_function_type_with_no_args():
    assert (
        fnl.type_parser.parse("(λ . int)")
        == fnl.type_parser.parse("(^ . int)")
        == fnl.et.TFunction((), None, fnl.et.TInt())
    )


def test_function_type_with_required_args():
    assert (
        fnl.type_parser.parse("(λ str block . int)")
        == fnl.type_parser.parse("(^ str block . int)")
        == fnl.et.TFunction((fnl.et.TStr(), fnl.et.TBlock()), None, fnl.et.TInt())
    )


def test_function_type_with_rest():
    assert (
        fnl.type_parser.parse("(λ ...str . int)")
        == fnl.type_parser.parse("(^ ...str . int)")
        == fnl.et.TFunction((), fnl.et.TStr(), fnl.et.TInt())
    )


def test_function_type_full():
    assert (
        fnl.type_parser.parse("(λ int block ...str . int)")
        == fnl.type_parser.parse("(^ int block ...str . int)")
        == fnl.et.TFunction((fnl.et.TInt(), fnl.et.TBlock()), fnl.et.TStr(), fnl.et.TInt())
    )
