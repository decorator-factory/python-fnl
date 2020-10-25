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


def test_block_element():
    assert (
        fnl.html('(b&p "a paragraph")', fnl.x)
        == '<p>a paragraph</p>'
    )


def test_block_element_with_parameters():
    assert (
        fnl.html('(b&p &.box &#mybox &defer "a paragraph")', fnl.x)
        == '<p class="box" id="mybox" defer>a paragraph</p>'
    )


def test_inline_element():
    assert (
        fnl.html('(i&span "a paragraph")', fnl.x)
        == '<span>a paragraph</span>'
    )


def test_inline_element_with_parameters():
    assert (
        fnl.html('(i&span &.box &#mybox &defer "a paragraph")', fnl.x)
        == '<span class="box" id="mybox" defer>a paragraph</span>'
    )


def test_named_attributes():
    assert (
        fnl.html('(i&span &(hello "world") "a paragraph")', fnl.x)
        == '<span hello="world">a paragraph</span>'
    )
