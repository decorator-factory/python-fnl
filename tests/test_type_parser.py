import fnl


def test_primitive_types():
    assert fnl.type_parser.parse("int") == fnl.et.TInt()
    assert fnl.type_parser.parse("str") == fnl.et.TStr()
    assert fnl.type_parser.parse("inline") == fnl.et.TInline()
    assert fnl.type_parser.parse("block") == fnl.et.TBlock()
    assert fnl.type_parser.parse("Inl") == fnl.et.IInl()
    assert fnl.type_parser.parse("Blk") == fnl.et.IBlk()
    assert fnl.type_parser.parse("Ren") == fnl.et.IRen()


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
        fnl.type_parser.parse("(λ str Blk . int)")
        == fnl.type_parser.parse("(^ str Blk . int)")
        == fnl.et.TFunction((fnl.et.TStr(), fnl.et.IBlk()), None, fnl.et.TInt())
    )


def test_function_type_with_rest():
    assert (
        fnl.type_parser.parse("(λ ...str . int)")
        == fnl.type_parser.parse("(^ ...str . int)")
        == fnl.et.TFunction((), fnl.et.TStr(), fnl.et.TInt())
    )


def test_function_type_full():
    assert (
        fnl.type_parser.parse("(λ int Blk ...str . int)")
        == fnl.type_parser.parse("(^ int Blk ...str . int)")
        == fnl.et.TFunction((fnl.et.TInt(), fnl.et.IBlk()), fnl.et.TStr(), fnl.et.TInt())
    )
