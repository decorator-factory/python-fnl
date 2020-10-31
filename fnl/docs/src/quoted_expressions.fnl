($docs $filename $source "Quoted expressions"
  ((h 2)
    "Strict evaluation")
  (p
    "Suppose that you want to render some content conditionally. For example,
    you might want to add notes that are only visible to the editors; or
    you might want to temporarily disable some part of the tree. It's not very
    hard to implement, right?")

  (pre """
  extensions = {}

  is_debug = True

  @fn(extensions, 'if-debug')
  def if_debug():
      def _if_debug(subtree):
          if is_debug:
              return subtree
          else:
              return e.BlockConcat(())
      yield ('(λ inline|block . block)', _if_debug)
  """)

  (p
    "Let's see if it works.")

  (pre """
  >>> is_debug = True
  >>> fnl.html('(if-debug (bf \"hi\"))', extensions)
  '<b>hi</b>'
  >>> is_debug = False
  >>> fnl.html('(if-debug (bf \"hi\"))', extensions)
  ''
  """)

  (p
    "It works, but there are some issues. The subtree is evaluated
    even if it doesn't get rendered. It might waste some resources if it's
    a really large tree (or if it requies reading from a file, which is probably
    not a good idea, but you might want to read a config, for instance). More
    importantly, under certain conditions, it might throw an error because
    something about this tree requires " (tt "is_debug") " to be true.")

  (p
    "FNL is a " (it "strict") " language. It means that function arguments are
    fully evaluated first, and only then are passed to the function. So, alas,
    we're out of luck.")

  ((h 2)
    "Quoted expression to the rescue")

  (p
    "...unless we use quoted expressions! A quoted expression represents an expression
    that doesn't get immediately evaluated. You can create a quoted expression
    by prefixing it with " (tt "&") ", for example, " (mono "&1024") " is a
    deferred integer, and " (mono "&(hello \"world\")") " is a deferred call.")

  (pre """
  extensions = {}

  is_debug = True

  @fn(extensions, 'if-debug')
  def if_debug():
      def _if_debug(quoted):
          if is_debug:
              return quoted.subexpression
          else:
              return e.BlockConcat(())
      yield ('(λ &[any] . block)', _if_debug)
  """)

  (p
    (mono "&[any]") " is a type of a quoted expession. The type of an expesssion
    isn't known until it's fully evaluated, so we will use " (tt "any") "as the
    type parameter. Other examples of quoted types: "
    (list-unordered
      ($ (tt "&[str] ") (--) " quoted string (like " (tt "&\"hi\"") ")" )
      ($ (tt "&[int] ") (--) " quoted integer (like " (tt "&10") ")" )
      ($ (tt "&[name] ") (--) " quoted name (like " (tt "&a-name") ")" )
      ($ (tt "&[name[a|b]] ") (--) " bounded quoted name (only " (tt "&a") " or " (tt "&b") " )" )
      ($ (tt "&[(name int)] ") (--) " s-expression (like " (tt "&(version 7)") ")" )))

  ((h 2)
    "Examples of using quoted expressions in " (tt "fnl.x"))

  (p
    (tt "fnl.x") " is a standard extension that helps you construct arbitrary HTML.")

  (pre """
    import fnl

    source = ...

    print(fnl.html(source, fnl.x))
    # or:
    print(fnl.html(source, {**your, **extensions, **fnl.x}))
    # or, in 3.9+:
    print(fnl.html(source, your | extensions | fnl.x))
  """)

  (p
    (tt "fnl.x")  " exports three function: " ((sepmap ", " tt) "b" "i" "+") ". "
    (tt "b") " creates a block element, " (tt "i") " creates an inline element,
    and " (tt "+") " is a shortcut for the " (tt "div") " element.")

  (pre """
  ($
    (b\"!DOCTYPE\" &html &.)
    (b&html &(lang \"en\")
      (b&head
        (b&meta &(charset \"UTF-8\") &.)
        (b&meta &(name \"viewport\") &(content \"width=device-width, initial-scale=1.0\") &.)
        (b&title \"My blog\")
        (b&link &(rel \"stylesheet\") &(href \"style.css\") &/))
      (b&body
        (b&main &#app
          (+ &.greeting
            ((h 1) \"Hello, world!\")
          (+ &.content
            (i&a &(href \"pay.html\") \"Give me your money\")))))))
  """)

  (p "This is going to render the following HTML code:")

  (pre """
  <!DOCTYPE html>
  <html lang=\"en\">
    <head>
      <meta charset=\"UTF-8\">
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
      <title>My blog</title>
      <link rel=\"stylesheet\" href=\"style.css\" />
    </head>
    <body>
      <main id=\"app\">
        <div class=\"greeting\">
          <h1>Hello, world!</h1>
          <div class=\"content\">
            <a href=\"pay.html\">Give me your money</a>
          </div>
        </div>
      </main>
    </body>
  </html>""")

  (p
    "As you can see, there aren't that many rules:"
    (list-unordered
      ($ "You can use plain old FNL functions (like " (tt "h") ")")
      ($ (tt "(b&tag ...)") " creates a block element")
      ($ (tt "(b\"tag!?!&\" ...)") " creates a block element with a name which is
        not a valid identifier")
      ($ (tt "(i&tag ...)") " creates an inline element")
      ($ (tt "&.class") " adds a class")
      ($ (tt "&#id") " adds an ID")
      ($ (tt "&html") " adds an attribute without an argument")
      ($ (tt "&(attr \"value\")") " adds an attribute")
      ($ (tt "&.") " makes the tag closed without making a " (tt "<tag></tag>")
        " pair")
      ($ (tt "&/") " makes the tag closed without making a " (tt "<tag></tag>")
        " pair and adds a slash ( / ) at the end.")))

  (p
    (tt "fnlx") " takes advantage of quoted expressions: an expression like "
    (mono "(lang \"en\")") " or " (tt "&#id") " would fail at runtime.")

  (p
    "With this tool, you can write pretty much any HTML you want. If you're
    feeling adventurous, you can even write markup for Vue.js like that.")

  (horizontal-rule)
  ((h 2) "Source:")
  (pre $source)
)