# Basic example

```clj
; $ allows you to join multiple elements under one root node
($
    ((h 1)
        "Hello, world!"
    )
    "Welcome to " (bf "my") " blog! It is:"
    (list-unordered
        (it "cool")
        ($ (bf "super") " awesome")
        ((style "color: red; font-size: 100%") "amazing")
    )
)
```
Compiles to (approximately):
```html
<h1>Hello, world!</h1>
Welcome to <b>my</b> blog! It is:
<ul>
    <li><i>cool</i></li>
    <li><b>super</b> awesome</li>
    <li><span style="color: red; font-size: 100%">amazing</span></li>
</ul>
```


# Syntax

```clj
; comment

"Hello, world!" ; string
1               ; integer
(f arg1 arg2)   ; function call: f(arg1, arg2)
(f a, b, c)     ; commas are whitespace
```



# Data types

## String (`str`)
```clj
"Hello, world!" : str
```

## Integer (`int`)
```clj
42 : int
```

## Renderable (`Ren`)
It's something you can render as HTML.
```clj
"Hello, world!"   : str < Ren
42                : int < Ren
(bf "Bold text")  : inline < Ren
(div "Something") : block < Ren
```

## Inlinable (`Inl`)
It's something that can be turned into an inline HTML element.
```clj
"Hello, world"   : str < Inl
42               : int < Inl
(bf "Bold text") : inline < Inl

Inl < Ren
```

## Blockable (`Blk`)
It's something that can be turned into a block HTML element.
```clj
(div "Something") : block < Blk

Blk < Ren
```

## Function (`(λ ...)`)
A function `(λ a b c . r)` is something you can call with
arguments being of type `a`, `b`, `c` etc. respectively and get a value
of type `r`.
```clj
+     : (λ int int . int)

; a function can take a variable number of arguments:
div   : (λ ...Ren . block)

; a function can take different forms:
$     : (λ ...Inl . inline)
      : (λ ...Ren . Ren)

; a function can return another function:
h     : (λ int . (λ ...Inl . inline))
style : (λ str . (λ ...Inl . inline))
```
