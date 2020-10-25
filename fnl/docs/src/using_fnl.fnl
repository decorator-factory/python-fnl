($docs $filename $source "Using FNL"
  ((h 2)
    "Basic usage")
  (p
    "Using FNL is pretty straight-forward. You give it source code, and it
    gives you HTML.")

  (pre """
  import fnl

  source_code = \"\"\"
    ($
      ((h 1)
        \"Hello, world!\")
      (p \"Lorem ipsum dolor sit amet\"))
  \"\"\"

  html: str = fnl.html()
  """)


  ((h 2)
    "Extending FNL")

  (p
    "To extend FNL, you'll need to learn a bit about its internals.
    The two most important modules are " (tt "fnl.entities") " and "
    (tt "fnl.entity_types") ".")

  (p
    (tt "fnl.entity_types") " defines the " (tt "EntityType") " class and all
    of its subclasses; they represent the types that are defined 'in the
    language spec', if I may say so. You'll need them to define the signatures
    of your own functions.")

  (p
    (tt "fnl.entities") " defines the " (tt "Entity") " class and all
    of its subclasses; they represent the expressions and values that appear
    in the program. Here are some of them:")

  (list-unordered
    ($ (tt "Name ") (--) " represents an expression that accesses a global
      value, like " (tt "bf") " or " (tt "$") ".")

    ($ (tt "Integer ") (--) " represents... well, an integer")

    ($ (tt "String ") (--) " as you might expect, it's a string")

    ($ (tt "InlineTag ") (--) " inline HTML tag, such as <b>")

    ($ (tt "BlockTag ") (--) " block HTML tag, such as <p>")

    ($ (tt "InlineConcat ") (--) " concatenation of inline elements")

    ($ (tt "BlockConcat ") (--) " concatenation of mixed elements; the
      result is a block element. The name might be confusing, but
      the relevant part here is that this value cannot be used as an inline
      element, but can be used as a block element.")
  )


  ((h 2)
    "Providing custom symbols")
  (p
    "If you take a look at the signature of " (tt "fnl.html") ", you can see
    that it accepts an optional " (tt "extensions") " argument. It's a mapping
    from strings (names) to " (tt "Entity") " objects. For example, you can
    define some constants like that:")

  (pre """
  import fnl
  import fnl.entities as e

  source = \"\"\"
    (p
      \"From basic mathematics we know that \" (e \"pi\") \" = \" PI \" and e = \" E \".\")
  \"\"\"

  print(fnl.html(source, {'PI': e.Integer(3), 'E': e.Integer(3)}))
  """)

  (p
    "You should get: " (mono "<p>From basic mathematics we know that &pi; = 3 and e = 3.</p>"))

  (p
    "In that mapping, you can provide any expression you want.")

  (pre """
  print(fnl.html(source, {'PI': e.Integer(3), 'E': e.Name('PI')}))
  """)


  ((h 2)
    "Creating functions")

  (p
    "Let's create a very simple function: it should take a string as an argument
    and return it unchanged. First, let's import all the necessary modules.")

  (pre """
    >>> import fnl
    >>> import fnl.entities as e
    >>> import fnl.entity_types as et
  """)

  (p
    "Then we'll need to create a " (bf "signature") " for our function so that
    the type system knows what the function accepts and returns. As you may
    remember, a function can take a few required arguments and (possibly)
    varargs of one type, like " (mono "(λ a b ...c . d)") ".")

  (pre """
    >>> function_type = et.TFunction(
    ...    arg_types = ( et.TStr(), )
    ...    rest = None,
    ...    return_type =  et.TStr()
    ... )
    ...
    >>> function_type.signature()
    '(λ str . str)'
  """)

  (p
    "Now we have to create a callable (basically, a Python function) that takes
    a " (mono "e.String()") " and returns a " (mono "e.String()") ".")

  (pre """
    >>> def identity(s: e.String) -> e.String:
    ...     return s
    ...
    >>>
  """)

  (p
    "The type annotations are completely optional, they only serve as documentation.")

  (p
    "Now we can combine the two to create a FNL function:")

  (pre """
    >>> function = e.Function({function_type: identity})
    >>>
  """)

  (p
    (mono "e.Function") " is a subclass of " (mono "e.Entity ") (--)
    "it's the type that all the built-in functions in FNL have. Let's test our function.")

  (pre """
    >>> fnl.html('(id \"hello\")', {'id': function})
    'hello'
    >>> fnl.html('(p (id \"hello, \") (id \"world!\"))', {'id': function})
    '<p>hello, world!</p>'
  """)

  (p
    "Congratulations, it works! Now let's try to break our function.")
  (pre """
    >>> fnl.html('(id 42)', {'id': function})
    FnlTypeError: Cannot call (λ str . str) with (int) (line 1, column 1)
  """)


  ((h 2)
    "Using string-based function annotations")

  (p
    "Creating a function type is so verbose, why can't I just write (λ str . str)?
    Actually, you can! " (mono "fnl.type_parser.parse_fn") " converts a function
    type as a string into a " (tt "TFunction") ".")

  (pre """
    from fnl.type_parser import parse_fn

    def identity(s):
        return s

    function = e.Function({parse_fn('(λ str . str)'): identity})
  """)


  ((h 2)
    "Examples and more advanced features")

  (p
    "Let's create a " (tt "dup") " function that repeats a string twice using
    the same steps.")

  (pre """
    def _dup(s: e.String) -> e.String:
        return e.String(s.value + s.value)

    fnl.html('(dup \"py\")', {parse_fn('(λ str . str)'): dup})
    #=> 'pypy'
  """)

  (p
    "Let's create a function " (tt "-") " that accepts any number of strings
    and puts hyphens between them.")

  (pre """
    def _hyphenate(*strings: e.String) -> e.String:
        return e.String(\"-\".join(s.value for s in strings))
    hyphenate = e.Function({parse_fn('(λ ...str . str)'): _hyphenate})

    fnl.html('(- \"lorem\" \"ipsum\" \"dolor\" \"sit\" \"amet\")', {'-': hyphenate})
    #=> 'lorem-ipsum-dolor-sit-amet'

    fnl.html('(type -)', {'-': hyphenate})
    #=> '(λ  ...str . str)'
  """)

  (p
    "Remember that a function can have multiple overloads. Let's modify our
    function so that it accepts integers as well.")

  (pre """
    def _hyphenate_str(*strings: e.String) -> e.String:
        return e.String(\"-\".join(s.value for s in strings))

    def _hyphenate_int(*ints: e.Integer) -> e.String:
        return e.String(\"-\".join(str(n.value) for n in ints))

    hyphenate = e.Function({
        parse_fn('(λ ...str . str)'): _hyphenate_str,
        parse_fn('(λ ...int . str)'): _hyphenate_int,
    })

    fnl.html('(- \"lorem\" \"ipsum\" \"dolor\" \"sit\" \"amet\")', {'-': hyphenate})
    #=> 'lorem-ipsum-dolor-sit-amet'

    fnl.html('(- 1 2 3 4 5)', {'-': hyphenate})
    #=> '1-2-3-4-5'

    fnl.html('(type -)', {'-': hyphenate})
    #=> '(λ  ...str . str)|(λ  ...int . str)'
  """)


  ((h 2)
    "Using the " (mono "fnl.definitions.fn") " shortcut")
  (p
    "If you look at the source code of " (mono "fnl/definitions.py")
    ", you'll see declarations like this:")

  (pre """
    @fn(BUILTINS, \"$\")
    def concat():
        def from_inline(*args):
            return e.InlineConcat(args)
        yield (\"(λ  ...inline . inline)\", from_inline)

        def from_mixed(*args):
            return e.BlockConcat(args)
        yield (\"(λ  ...inline|block . inline|block)\", from_mixed)
  """)

  (p
    (mono "fn") "is a helper decorator for creating FNL function. It accepts
    a dictionary and the function name as argument, and it can be applied to a
    generator function that yields " (mono "(signature, function)") " tuples:")


  (p
    "For example, our " (tt "-") " function could've been written as this:")

  (pre """
    extensions = {}

    @fn(extensions, \"-\")
    def hyphenate():
        def from_strings(*strings):
            return e.String(\"-\".join(s.value for s in strings))
        yield (\"(λ ...str . str)\", from_strings)

        def from_ints(*ints):
            return e.String(\"-\".join(str(n.value) for n in ints))
        yield (\"(λ ...int . str)\", from_ints)

    fnl.html('(- 1 2 3 4 5)', extensions  )
    #=> '1-2-3-4-5'
  """)

  (horizontal-rule)
  ((h 2) "Source:")
  (pre $source)
)