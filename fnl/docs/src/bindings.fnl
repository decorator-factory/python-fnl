($docs $filename $source "Name bindings"

  (p
    "As you have already seen, quoted expressions are very powerful: they
    allow you to compute an expression conditionally, or not compute it at all
    and use it as a data structure instead.")
  (p
    "The " (mono "fnl.bindings") " module provides even more useful functions
    that rely on quoted expressions. The module has to maintain some internal
    state, so you have to call " (mono "fnl.bindings") " to get a new mapping.")
  (pre """
    import fnl

    source = ...

    html = fnl.html(source, fnl.bindings())
    # or:
    html = fnl.html(source, {**some, **other, **stuff, **fnl.bindings()})
  """)

  ((h 2)
    "Using the " (tt "let") " and " (tt "var") " functions")

  (p
    "The " (tt "let") " and " (tt "var") " functions allow you to bind an
    expression to a name and then refer to it by that name:")

  (pre ($fnl """
    (let
      &title "Name bindings"
      &($ "The title is: " (var &title)))
    """))
  ($box
    (let
      &title "Name bindings"
      &($ "The title is: " (var &title))))

  (p
    "Note that the 'body' (the last argument to " (tt "let") ") is quoted
    because it can't be evaluated before calling the function.")

  (horizontal-rule)

  (p
    (tt "let") " is not an assignment operator from imperative languages like C, Java,
    or Python. It's a subsitution of a name within a scope. So when you leave
    the " (tt "let") "'s 'scope', so to speak, all of its bindings disappear:")

  (pre ($fnl """
    (let
      &answer "I do"
      &($
        (var &answer)
        " "
        (let
          &answer 42
          &(var &answer))
        " "
        (var &answer)))
    """))
  ($box
    (let
      &answer "I do"
      &($
        (var &answer)
        " "
        (let
          &answer 42
          &(var &answer))
        " "
        (var &answer))))

  (horizontal-rule)

  (p
    "You can also do it the other way around: you can name a quoted expression!")

  (pre ($fnl """
    (let
      &bf+it &(bf (it (var &text)))
      &($
        "Now you can make text which is bold "
        (let &text "and" (var &bf+it))
        " italic!"))
  """))
  ($box
    (let
      &bf+it &(bf (it (var &text)))
      &($
        "Now you can make text which is bold "
        (let &text "and" (var &bf+it))
        " italic!")))

  (p "Explanation:")
  (pre ($fnl """
    ; this line:
    (let &text "and" (var &bf+it))

    ; gets expanded as:
    (let &text "and" &(bf (it (var &text))))

    ; ...because in the outer 'let', 'bf+it' is defined as:
    &(bf (it (var &text)))
  """))

  (p
    "You can compare this pattern to calling a Python function with named (keyword)
    arguments; or passing an 'options object' to a function in JavaScript.")

  (horizontal-rule)
  (p
    "The " (tt "let") " function has the following type signature:")
  (pre (type let))

  (p
    "So, as you may infer, there's an overload that allows you to make multiple
    bindings at one:")
  (pre ($fnl """
    ((let
      &(question "What... is your quest?")
      &(answer "To seek the Holy Grail."))
      &(list-unordered
        ($ (bf "Q: ") (var &question))
        ($ (bf "A: ") (var &answer))))
  """))
  ($box
    ((let
      &(question "What... is your quest?")
      &(answer "To seek the Holy Grail."))
      &(list-unordered
        ($ (bf "Q: ") (var &question))
        ($ (bf "A: ") (var &answer)))))

  (p
    "As before, you can reverse this relation:")
  (pre ($fnl """
    (let
      &qa-entry &(list-unordered
            ($ (bf "Q: ") (var &q))
            ($ (bf "A: ") (var &a)))

      &($
        ((let
          &(q "What... is your name?")
          &(a "It is 'Arthur', King of the Britons."))
          (var &qa-entry))

        ((let
          &(q "What... is your quest?")
          &(a "To seek the Holy Grail."))
          (var &qa-entry))

        ((let
          &(q "What... is the air-speed velocity of an unladen swallow?")
          &(a "What do you mean? An African or European swallow?"))
          (var &qa-entry))))
  """))
  ($box
    (let
      &qa-entry &(list-unordered
            ($ (bf "Q: ") (var &q))
            ($ (bf "A: ") (var &a)))

      &($
        ((let
          &(q "What... is your name?")
          &(a "It is 'Arthur', King of the Britons."))
          (var &qa-entry))

        ((let
          &(q "What... is your quest?")
          &(a "To seek the Holy Grail."))
          (var &qa-entry))

        ((let
          &(q "What... is the air-speed velocity of an unladen swallow?")
          &(a "What do you mean? An African or European swallow?"))
          (var &qa-entry)))))

  (horizontal-rule)
  ((h 2) "Source:")
  (pre ($fnl $source)))