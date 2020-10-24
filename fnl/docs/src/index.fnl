($docs $filename $source "Index"
  ($box
    (list-unordered
      ($link-to "index.html")
      ($link-to "language_tutorial.html")
      ($link-to "using_fnl.html")))


  (horizontal-rule)
  ((h 1)
    "FNL")
  ((h 2)
    "FNL is Not Lisp")


  (horizontal-rule)
  (p
    "FNL is a markup language for your blog. It's...")

  ((h 3) "...terse")
  (pre """
    ($
      ((h 1)
        \"Hello, world!\")
      \"Welcome to \" (bf \"my\") \" blog! It is:\"
      (list-unordered
        (it \"cool\")
        ($ (bf \"super\") \" awesome\")
        ((style \"color: red; font-size: 100%\") \"amazing\")
        ((sepmap \", \" tt) \"modern\" \"striking\" \"inspiring\")))
  """)
  ($box
    ($
    ((h 1)
      "Hello, world!")
    "Welcome to " (bf "my") " blog! It is:"
    (list-unordered
      (it "cool")
      ($ (bf "super") " awesome")
      ((style "color: red; font-size: 100%") "amazing")
      ((sepmap ", " tt) "modern" "striking" "inspiring"))))


  (horizontal-rule)
  ((h 3) "...easy to use")
  (pre """
      import fnl

      print(fnl.html('($ (bf \"Hello, \") (it \"world!\"))'))
  """)
  (pre """
      <b>Hello, </b><i>world!</i>
  """)


  (horizontal-rule)
  ((h 3) "...easy to extend")

  (pre """
      import fnl
      extensions = {}

      @fnl.definitions.fn(extensions, 'box')
      def box():
          def _box(*elements: fnl.e.Entity):
              # <div class=\"box\">...</div>
              return fnl.e.BlockTag('div', 'class=\"box\"', elements)
          yield (\"(λ ...Ren . block)\", _box)

      html = fnl.html(
          '(box \"This is how this box was made!\")',
          extensions
      )
  """)
  ($box
    "This is how this box was made!")
  ; ...except for the $, of course


  (horizontal-rule)
  ((h 3) "...strongly typed")

  (pre """
      (bf (p \"I'm putting a <p> inside a <b>. It's my foot. And my gun.\"))
  """)
  (pre """
    fnl.FnlTypeError: Cannot call (λ  ...Inl . inline) with (block) (line 1, column 1)
  """)


  (horizontal-rule)
  ((h 3) "Convinced?")
  (pre """
    $ pip install git+https://github.com/decorator-factory/python-fnl
  """)


  (horizontal-rule)
  ((h 2) "Source:")
  (pre $source)

)