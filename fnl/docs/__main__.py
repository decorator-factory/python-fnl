from dataclasses import dataclass
from typing import Dict, Tuple
import fnl
from pathlib import Path
import string


# Language extension:


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


template_html = (Path(__file__).parent / "template.html").read_text()

src_dir = Path(__file__).parent / "src"
html_dir = Path(__file__).parent / "html"

for source_path in src_dir.glob("*.fnl"):
    # if source_path.name == "index.fnl":  # index.fnl is special
    #     continue
    source = source_path.read_text()

    target_filename = source_path.with_suffix(".html").name
    target_path = html_dir / target_filename

    target_path.write_text(
        fnl.html(source, {
            **extensions,
            **fnl.x,
            "$filename": fnl.e.String(target_filename),
            "$source": fnl.e.String(source),
        })
    )
    print(f"{source_path} -> {target_path}")


index_source = (src_dir / "index.fnl").read_text()
target_path = html_dir / "index.html"
target_path.write_text(
    fnl.html(index_source, {
        **extensions,
        **fnl.x,
        "$filename": fnl.e.String("index.html"),
        "$source": fnl.e.String(index_source),
    })
)
