import sys
import time
from dataclasses import dataclass
from typing import Dict, Tuple
import fnl
from pathlib import Path
import string

try:
    import watchgod
except ImportError:
    watchgod = None


@dataclass
class Template(fnl.e.Entity):
    template_html: str
    parts: Dict[str, fnl.e.Entity]

    def render_block(self, runtime: Dict[str, fnl.e.Entity]) -> fnl.e.HtmlRender:
        rendered_parts = {name: part.render(runtime).as_text() for name, part in self.parts.items()}
        template = string.Template(self.template_html)
        return fnl.e.RawHtml(template.substitute(rendered_parts))


extensions: Dict[str, fnl.e.Entity] = {}
store: Dict[str, Tuple[str, str]] = {}  # filename -> (title, source)


@fnl.definitions.fn(extensions, "$docs")
def make_docs():
    def _make_docs(
        filename: fnl.e.String,
        source: fnl.e.String,
        title: fnl.e.String,
        *elements: fnl.e.Entity
    ):
        store[filename.value] = (title.value, source.value)
        return Template(
            template_html,
            {
                "title": title,
                "mount": fnl.e.BlockConcat(elements),
            }
        )
    yield ("(λ str str str ...inline|block . block)", _make_docs)


@fnl.definitions.fn(extensions, "$link-to")
def link_to():
    def _link_to(filename: fnl.e.String):
        (title, _source) = store.get(filename.value, ("title?", "source?"))
        return fnl.e.InlineTag("a", f'href="{filename.value}"', (fnl.e.String(title),))
    yield ("(λ str . inline)", _link_to)


@fnl.definitions.fn(extensions, "$source-of")
def source_of():
    def _source_of(filename: fnl.e.String):
        (_title, source) = store.get(filename.value, ("title?", "source?"))
        return fnl.e.String(source)
    yield ("(λ str . str)", _source_of)


@fnl.definitions.fn(extensions, "$box")
def box():
    def _box(*elements: fnl.e.Entity):
        return fnl.e.BlockTag("div", 'class="fnl--box"', elements)
    yield ("(λ inline|block . block)", _box)


@fnl.definitions.fn(extensions, "$fnl")
def fnl_highlight():
    # Wrap FNL source code tokens in <span>s with appropriate CSS classes
    # so that a CSS stylesheet can style the tokens.
    def _fnl_highlight(s: fnl.e.String):
        code = s.value
        last_pos = 0
        highlighted_tokens = []
        for token in fnl.parser.lex(code):
            # the lexer ignores comments and whitespace, so we need to collect them:
            whitespace = code[last_pos:token.pos_in_stream]
            if whitespace != "":
                highlighted_tokens.append(("code--fnl--ws", whitespace))
            last_pos = token.pos_in_stream + len(token)
            kind = token.type.lower().replace("_", "-")
            highlighted_tokens.append((f"code--fnl--{kind}", token.value))

        # TODO: TODO: TODO: TODO: refactor this in the next commit!
        return fnl.e.InlineConcat(tuple(
            fnl.e.InlineTag(
                "span", f'class="{css_class}"', (fnl.e.String(content),)
            ) if content not in {"(", ")"}
            else {
                "(": fnl.e.InlineRaw(f'<span class="code--fnl--sexpr"><span class="{css_class}">(</span>'),
                ")": fnl.e.InlineRaw(f'<span class="{css_class}">)</span></span>'),
            }[content]
            for (css_class, content) in highlighted_tokens
        ))
    yield ("(λ str . inline)", _fnl_highlight)


def compile_fnl(source: str, target_filename: str):
    t1 = time.time()
    html = fnl.html(source, {
            **extensions,
            **fnl.x,
            **fnl.bindings(),
            "$filename": fnl.e.String(target_filename),
            "$source": fnl.e.String(source),
        })
    t2 = time.time()
    return html, t2 - t1


if __name__ == "__main__":
    if len(sys.argv) not in (1, 2) or sys.argv[1:] not in ([], ["--watch"]):
        print("Usage: python -m fnl.docs [--watch]")
        sys.exit(1)

    template_html = (Path(__file__).parent / "template.html").read_text()

    src_dir = Path(__file__).parent / "src"
    html_dir = Path(__file__).parent / "html"

    for source_path in src_dir.glob("*.fnl"):
        source = source_path.read_text()

        target_filename = source_path.with_suffix(".html").name
        target_path = html_dir / target_filename

        html, delta_time = compile_fnl(source, target_filename)
        target_path.write_text(html)
        print(f"Compiled {target_filename:30} in {delta_time:.3f} s")

    index_source = (src_dir / "index.fnl").read_text()
    target_path = html_dir / "index.html"

    html, delta_time = compile_fnl(index_source, "index.html")
    target_path.write_text(html)

    # Watching handler

    if sys.argv[1:] == ["--watch"]:
        if watchgod is None:
            print("You must install the `watchgod` library to watch for files")
            sys.exit(1)

        for changes in watchgod.watch(src_dir):
            for (kind, path) in changes:
                if kind in (watchgod.Change.added, watchgod.Change.modified):
                    source_path = Path(path)
                    source = source_path.read_text()
                    target_filename = source_path.with_suffix(".html").name
                    target_path = html_dir / target_filename

                    html, delta_time = compile_fnl(source, target_filename)
                    target_path.write_text(html)
                    print(f"Compiled {target_filename:30} in {delta_time:.3f} s")
