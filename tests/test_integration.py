from fnl import html


def test_basic():
    assert html('"hello"') == "hello"


def test_boldface():
    assert html('(bf "hello")') == "<b>hello</b>"


def test_italics():
    assert html('(it "hello")') == "<i>hello</i>"


def test_concat():
    assert html('($ "abc" "def" "ghi")') == "abcdefghi"
    assert html('($ "abc" (bf "def") "ghi")') == "abc<b>def</b>ghi"


def test_heading():
    assert html('((h 2) "hello" " " "world")') == "<h2>hello world</h2>"


def test_style_inline():
    assert html('((style "color: red") "text")') == '<span style="color: red">text</span>'


def test_list_unordered():
    assert (
        html('(list-unordered "hello" ($ "a" "b") "c")')
        == '<ul><li>hello</li><li>ab</li><li>c</li></ul>'
    )


def test_list_ordered():
    assert (
        html('(list-ordered "hello" ($ "a" "b") "c")')
        == '<ol><li>hello</li><li>ab</li><li>c</li></ol>'
    )


def test_separator():
    assert(
        html('((sep ", ") "python" "js" "haskell")')
        == 'python, js, haskell'
    )


def test_map():
    assert(
        html('((map p) "hello" "world" "abc")')
        == '<p>hello</p><p>world</p><p>abc</p>'
    )


def test_sepmap():
    assert (
        html('((sepmap ", " bf) "a" "b" "c")')
        == html('($ (bf "a") ", " (bf "b") ", " (bf "c"))')
    )


def test_nobr():
    assert (
        html('(nobr (p "h e l l o" (bf "w o r l d")))')
        == '<p>h&nbsp;e&nbsp;l&nbsp;l&nbsp;o<b>w&nbsp;o&nbsp;r&nbsp;l&nbsp;d</b></p>'
    )


def test_readme_example():
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
    assert html(SOURCE) == (
        '<h1>Hello, world!</h1>'
        'Welcome to <b>my</b> blog! It is:'
        '<ul>'
            '<li><i>cool</i></li>'
            '<li><b>super</b> awesome</li>'
            '<li><span style="color: red; font-size: 100%">amazing</span></li>'
        '</ul>'
    )