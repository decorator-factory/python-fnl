($docs $filename $source "Language tutorial"
  (p
    "The language is not meant to be a replacement for HTML,
    it's just a tool for rendering HTML to style a blog post. There's still a
    lot of work to do, but it's already pretty useful, at least in my view.")

  (horizontal-rule)

  (p
    "The syntax of the language is based on S-expressions in lisp: to call
    a function " (mono "f") " with arguments " ((sepmap ", " mono) "x" "y" "z")
    ", you write " (mono "(f x y z)") ". For example, " (mono "2 + (3 * 5)")
    " would be written as " (mono "(+ 2 (* 3 5))") ". Apart from that, you have
    names (like " (mono "p") "or" (mono "list-unordered") "), strings ( like "
    (mono "\"hello\"") ") and integers (like " (mono "42") ").")

  (p
    "The entire document is just one big expression.")

  (p
    "Some examples of markup, just to give you an idea:")

  (horizontal-rule)
  ((h 3)
    "A string is a valid document:")
  (p (mono "\"Hello, world\""))
  ($box
    "Hello, world")

  (horizontal-rule)
  ((h 3)
    "You can concatenate things with the " (mono "$") " function:")
  (p (mono "($ \"Hello, \" \"world!\")"))
  ($box
    ($ "Hello, " "world!"))

  (horizontal-rule)
  ((h 3)
    "Some functions represent HTML tags:")
  (pre ($fnl """
    (p              ; paragraph
      (bf "Hello")  ; boldface
      (it "World")  ; italics
      (tt "Aaaaa")  ; monospaces text

      ; heading:
      ((h 3) "To do:")
      (list-unordered
        "Buy milk"
        "Submit a pull request"
        "Solve fizzbuzz"))
  """))
  ($box
    (p
        (bf "Hello")
        (it "World")
        (tt "Aaaaa")

        ((h 3) "To do:")
        (list-unordered
          "Buy milk"
          "Submit a pull request"
          "Solve fizzbuzz")))

  (horizontal-rule)
  ((h 3)
    "Strong typing")
  (p
    "Some languages are powerful not because of something you can do with them,
    but rather because of something you " (it "can't") ". Strict languages like
    Haskell or Rust are a good example of that.")
  (p (pre ($fnl """
    (b (p "text"))
  """)))
  (p
    "This results in an error: "
    (bf (mono "Cannot call (λ  ...inline . inline) with (block) (line 71, column 3)")))
  (p
    "Why can't you do that? It seems perfectly fine, but it isn't: "
    (tt "p") " is a 'block' element, while " (tt "b") " is an 'inline' element,
    and you can't put a 'block' element inside an 'inline' element.
    You can go to " (a "https://validator.w3.org/" "the W3C validator")
    " and see for yourself that " (mono "<b><p>text</p></b>") " is a no-no.")

  (horizontal-rule)
  ((h 3)
    "Inspecting types")
  (p
    "You can inspect the type of an object by using the " (tt "type")
    " function:")
  (pre ($fnl
  """
  (list-unordered
    (tt "\"hello\": " (type "hello"))
    (tt "5: " (type 5))
    (tt "p: " (type p))
    (tt "$: " (type $))
    (tt "h: " (type h))
    (tt "nobr: " (type nobr))
    (tt "horizontal-rule: " (type nobr))
  )
  """
  ))
  ($box
    (list-unordered
      (tt "\"hello\": " (type "hello"))
      (tt "5: " (type 5))
      (tt "p: " (type p))
      (tt "$: " (type $))
      (tt "h: " (type h))
      (tt "nobr: " (type nobr))
      (tt "horizontal-rule: " (type horizontal-rule))))

  (p
    "Let's break down the function types:"
    (list-unordered
      "The lambda (λ) just means that it's a function"
      ($ (tt "(λ a . b)") " is a function from type 'a' to type 'b'")
      ($ (tt "(λ ...a . b)") " is a function that accepts any number of 'a's an returns a 'b'")
      ($ (tt "a | b") " means \"either an 'a' or a 'b'\"")
      ($ (tt "inline") " is an inline HTML element, which also includes strings and ints.")
      ($ (tt "block") " is a block HTML element")
    )
  )

  (horizontal-rule)
  ((h 3)
    "Higher-order functions")

  (p
    "There's a type that seems strange: " (mono "h: (λ int . (λ ...Inl . block))"))
  (p
    "Just like in Python or in many other computer languages, functions are
    first-class values: they can be created, returned, and passed as arguments
    to other functions. So " (tt "h") " is a function that takes an integer
    and returns a new function, which in turn accepts any number of inline-ish
    elements and returns a block HTML element.")

  (p
    (tt "map") " is another example of a higher-order function. its type
    is " (mono (type map)) ". That's a very long type, but basically, "
    (tt "map") " allows you to apply a function to a list of values.")
  (pre ($fnl """
    ((map p) "First paragraph" "Second paragraph" "Third paragraph")
  """))
  ((map p) "First paragraph" "Second paragraph" "Third paragraph")

  (p
    (tt "sep") " allows you to separate a list of values with a separator
    you give it.")
  (pre ($fnl """
    (p
      ((sep ", ") "int" "str" "list"))
  """))
  ($box
    (p
      ((sep ", ") "int" "str" "list")))

  (p
    "Ah, but what if you need to " (mono "sep") (it " and ") (mono "map") "?
    In that case you can use " (mono "sepmap") "!")
  (pre ($fnl """
    (p
      ((sepmap ", " tt) "int" "str" "list"))
  """))
  ($box
    (p
      ((sepmap ", " tt) "int" "str" "list")))

  (horizontal-rule)
  ((h 2)
    "Documentation for all built-in functions")
  (foreach &name (documented-names)
    &($
      ((h 3) (tt (bf (extract-name (var &name))) " : " (type (unquote (var &name)))))
      (doc (unquote (var &name)))
    ))

  (horizontal-rule)
  ((h 2) "Source:")
  (pre ($fnl $source))
)