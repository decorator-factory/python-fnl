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


  ((h 2)
    "Using the " (tt "foreach") " function to express a repeating pattern")

  (bf "foreach : ") (tt (type foreach))
  (pre ($fnl
    """
      ($
        (bf "Questions: ")
        (b&ul
          (foreach
            &question
            &("What... is your name?"
              "What... is your quest?"
              "What... is the air-speed velocity of an unladen swallow?")
            &(b&li (var &question)))))
    """
  ))
  ($box ($
    (bf "Questions: ")
    (b&ul
      (foreach
        &question
        &("What... is your name?"
          "What... is your quest?"
          "What... is the air-speed velocity of an unladen swallow?")
        &(b&li (var &question))))))


  ((h 2)
    "Iterating over pairs of values")
  (p
    "There are no built-in tuples or associative arrays in FNL.
    But those data structures can be emulated with " (tt "let") ".")
  (p
    "After all, what is a pair of values, for example, a pair containing
    a question and an answer to that question? One way to frame it is to say
    that a pair " (mono "(question, answer)") " is a function that accepts
    another function " (mono "(λ q a . t)") " and calls it with some
    arguments " (tt "q") " and " (tt "a") ".")

  (p
    "This is how it can be implemented in Python:")
  (pre """
    entries = [
        lambda f: f("What... is your name?", "It is 'Arthur', King of the Britons."),
        lambda f: f("What... is your quest?", "To seek the Holy Grail."),
        lambda f: f("What... is the air-speed velocity of an unladen swallow?",
                    "What do you mean? An African or European swallow?"),
    ]
    for entry in entries:
        entry(
            lambda q, a: (print("Q:", q), print("A:", a))
        )
  """)

  (p
    "And this is how you could implement it in FNL:")
  (pre ($fnl """
    (foreach
      &entry
      &(&((let
          &(q "What... is your name?")
          &(a "It is 'Arthur', King of the Britons.")) (var &fn))
        &((let
          &(q "What... is your quest?")
          &(a "To seek the Holy Grail.")) (var &fn))
        &((let
          &(q "What... is the air-speed velocity of an unladen swallow?")
          &(a "What do you mean? An African or European swallow?")) (var &fn)))

      &(list-unordered
        (let &fn &($ (bf "Q: ") (var &q)) (var &entry))
        (let &fn &($ (bf "A: ") (var &a)) (var &entry))))
  """))
  ($box
    (foreach
      &entry
      &(&((let
          &(q "What... is your name?")
          &(a "It is 'Arthur', King of the Britons.")) (var &fn))
        &((let
          &(q "What... is your quest?")
          &(a "To seek the Holy Grail.")) (var &fn))
        &((let
          &(q "What... is the air-speed velocity of an unladen swallow?")
          &(a "What do you mean? An African or European swallow?")) (var &fn)))

      &(list-unordered
        (let &fn &($ (bf "Q: ") (var &q)) (var &entry))
        (let &fn &($ (bf "A: ") (var &a)) (var &entry)))))

  (p
    "This is a pretty effective emulation of an associative array, but I'm
    not sure about the effects of ampersand soup on your health. There must
    be a better way!")

  ((h 2)
    "Associative arrays: the " (tt "obj") " function")
  (bf "obj : ") (tt (type obj))
  (p
    "The " (tt "obj") " function is just a shorthand for creating an entry like those
    in the last example. The only difference is that it uses " (tt "@")
    " instead of " (tt "fn") " (yes, " (tt "@") " is a valid in identifiers).")
  (pre ($fnl """
    (foreach
        &entry
        &((obj
            &(q "What... is your name?")
            &(a "It is 'Arthur', King of the Britons."))
          (obj
            &(q "What... is your quest?")
            &(a "To seek the Holy Grail."))
          (obj
            &(q "What... is the air-speed velocity of an unladen swallow?")
            &(a "What do you mean? An African or European swallow?")))

        &(list-unordered
          (let &@ &($ (bf "Q: ") (var &q)) (var &entry))
          (let &@ &($ (bf "A: ") (var &a)) (var &entry))))))
  """))
  ($box
    (foreach
      &entry
      &((obj
          &(q "What... is your name?")
          &(a "It is 'Arthur', King of the Britons."))
        (obj
          &(q "What... is your quest?")
          &(a "To seek the Holy Grail."))
        (obj
          &(q "What... is the air-speed velocity of an unladen swallow?")
          &(a "What do you mean? An African or European swallow?")))

      &(list-unordered
        (let &@ &($ (bf "Q: ") (var &q)) (var &entry))
        (let &@ &($ (bf "A: ") (var &a)) (var &entry)))))



  (horizontal-rule)
  ((h 2) "Source:")
  (pre ($fnl $source)))