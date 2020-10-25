import fnl


def test_div_empty():
    assert (
        fnl.html('(+)', fnl.x)
        == '<div></div>'
    )


def test_div_simple():
    assert (
        fnl.html('(+ "hello, " (bf "world!") (p "paragraph"))', fnl.x)
        == '<div>hello, <b>world!</b><p>paragraph</p></div>'
    )


def test_div_with_class():
    assert (
        fnl.html('(+ &.box "hello, " (bf "world!"))', fnl.x)
        == '<div class="box">hello, <b>world!</b></div>'
    )


def test_div_with_class_and_id():
    assert (
        fnl.html('(+ &.box &#mybox "hello, " (bf "world!"))', fnl.x)
        == '<div class="box" id="mybox">hello, <b>world!</b></div>'
    )


def test_div_with_class_and_id_and_defer():
    assert (
        fnl.html('(+ &.box &#mybox &defer "hello, " (bf "world!"))', fnl.x)
        == '<div class="box" id="mybox" defer>hello, <b>world!</b></div>'
    )