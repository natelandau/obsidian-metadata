# type: ignore
"""Test the parsers module."""

import re

import pytest

from obsidian_metadata.models.enums import Wrapping
from obsidian_metadata.models.parsers import Parser

P = Parser()


def test_identify_internal_link_1():
    """Test the internal_link attribute.

    GIVEN a string with an external link
    WHEN the internal_link attribute is called within a regex
    THEN the external link is not found
    """
    assert re.findall(P.internal_link, "[link](https://example.com/somepage.html)") == []


def test_identify_internal_link_2():
    """Test the internal_link attribute.

    GIVEN a string with out any links
    WHEN the internal_link attribute is called within a regex
    THEN no links are found
    """
    assert re.findall(P.internal_link, "foo bar baz") == []


def test_identify_internal_link_3():
    """Test the internal_link attribute.

    GIVEN a string with an internal link
    WHEN the internal_link attribute is called within a regex
    THEN the internal link is found
    """
    assert re.findall(P.internal_link, "[[internal_link]]") == ["[[internal_link]]"]
    assert re.findall(P.internal_link, "[[internal_link|text]]") == ["[[internal_link|text]]"]
    assert re.findall(P.internal_link, "[[test/Main.md]]") == ["[[test/Main.md]]"]
    assert re.findall(P.internal_link, "[[%Man &Machine + Mind%]]") == ["[[%Man &Machine + Mind%]]"]
    assert re.findall(P.internal_link, "[[Hello \\| There]]") == ["[[Hello \\| There]]"]
    assert re.findall(P.internal_link, "[[\\||Yes]]") == ["[[\\||Yes]]"]
    assert re.findall(P.internal_link, "[[test/Main|Yes]]") == ["[[test/Main|Yes]]"]
    assert re.findall(P.internal_link, "[[2020#^14df]]") == ["[[2020#^14df]]"]
    assert re.findall(P.internal_link, "!foo[[bar]]baz") == ["[[bar]]"]
    assert re.findall(P.internal_link, "[[]]") == ["[[]]"]


def test_return_frontmatter_1():
    """Test the return_frontmatter method.

    GIVEN a string with frontmatter
    WHEN the return_frontmatter method is called
    THEN the frontmatter is returned
    """
    content = """
---
key: value
---
# Hello World
"""
    assert P.return_frontmatter(content) == "---\nkey: value\n---"


def test_return_frontmatter_2():
    """Test the return_frontmatter method.

    GIVEN a string without frontmatter
    WHEN the return_frontmatter method is called
    THEN None is returned
    """
    content = """
# Hello World
---
key: value
---
"""
    assert P.return_frontmatter(content) is None


def test_return_frontmatter_3():
    """Test the return_frontmatter method.

    GIVEN a string with frontmatter
    WHEN the return_frontmatter method is called with data_only=True
    THEN the frontmatter is returned
    """
    content = """
---
key: value
key2: value2
---
# Hello World
"""
    assert P.return_frontmatter(content, data_only=True) == "key: value\nkey2: value2"


def test_return_frontmatter_4():
    """Test the return_frontmatter method.

    GIVEN a string without frontmatter
    WHEN the return_frontmatter method is called with data_only=True
    THEN None is returned
    """
    content = """
# Hello World
---
key: value
---
"""
    assert P.return_frontmatter(content, data_only=True) is None


def test_return_inline_metadata_1():
    """Test the return_inline_metadata method.

    GIVEN a string with no inline metadata
    WHEN the return_inline_metadata method is called
    THEN return None
    """
    assert P.return_inline_metadata("foo bar baz") is None
    assert P.return_inline_metadata("foo:bar baz") is None
    assert P.return_inline_metadata("foo:::bar baz") is None
    assert P.return_inline_metadata("[foo:::bar] baz") is None


@pytest.mark.parametrize(
    ("string", "returned"),
    [
        ("[k1:: v1]", [("k1", " v1", Wrapping.BRACKETS)]),
        ("(k/1::  v/1)", [("k/1", "  v/1", Wrapping.PARENS)]),
        (
            "[k1::v1] and (k2:: v2)",
            [("k1", "v1", Wrapping.BRACKETS), ("k2", " v2", Wrapping.PARENS)],
        ),
        ("(début::début)", [("début", "début", Wrapping.PARENS)]),
        ("[😉::🚀]", [("😉", "🚀", Wrapping.BRACKETS)]),
        (
            "(🛸rocket🚀ship:: a 🎅 [console] game)",
            [("🛸rocket🚀ship", " a 🎅 [console] game", Wrapping.PARENS)],
        ),
    ],
)
def test_return_inline_metadata_2(string, returned):
    """Test the return_inline_metadata method.

    GIVEN a string with inline metadata within a wrapping
    WHEN the return_inline_metadata method is called
    THEN return the wrapped inline metadata
    """
    assert P.return_inline_metadata(string) == returned


@pytest.mark.parametrize(
    ("string", "returned"),
    [
        ("k1::v1", [("k1", "v1", Wrapping.NONE)]),
        ("😉::🚀", [("😉", "🚀", Wrapping.NONE)]),
        ("k1::  w/ !@#$|  ", [("k1", "  w/ !@#$|  ", Wrapping.NONE)]),
        ("クリスマス:: 家庭用ゲーム機", [("クリスマス", " 家庭用ゲ\u30fcム機", Wrapping.NONE)]),
        ("Noël:: Un jeu de console", [("Noël", " Un jeu de console", Wrapping.NONE)]),
        ("🎅:: a console game", [("🎅", " a console game", Wrapping.NONE)]),
        ("🛸rocket🚀ship:: a 🎅 console game", [("🛸rocket🚀ship", " a 🎅 console game", Wrapping.NONE)]),
        (">flag::irish flag 🇮🇪", [("flag", "irish flag 🇮🇪", Wrapping.NONE)]),
        ("foo::[bar] baz", [("foo", "[bar] baz", Wrapping.NONE)]),
        ("foo::bar) baz", [("foo", "bar) baz", Wrapping.NONE)]),
        ("[foo::bar baz", [("foo", "bar baz", Wrapping.NONE)]),
        ("_foo_::bar baz", [("_foo_", "bar baz", Wrapping.NONE)]),
        ("**foo**::bar_baz", [("**foo**", "bar_baz", Wrapping.NONE)]),
        ("`foo`::`bar baz`", [("`foo`", "`bar baz`", Wrapping.NONE)]),
    ],
)
def test_return_inline_metadata_3(string, returned):
    """Test the return_inline_metadata method.

    GIVEN a string with inline metadata without a wrapping
    WHEN the return_inline_metadata method is called
    THEN return the wrapped inline metadata
    """
    assert P.return_inline_metadata(string) == returned


@pytest.mark.parametrize(
    ("string", "returned"),
    [
        ("#foo", ["#foo"]),
        ("#tag1 #tag2 #tag3", ["#tag1", "#tag2", "#tag3"]),
        ("#foo.bar", ["#foo"]),
        ("#foo-bar_baz#", ["#foo-bar_baz"]),
        ("#daily/2021/20/08", ["#daily/2021/20/08"]),
        ("#🌱/🌿", ["#🌱/🌿"]),
        ("#début", ["#début"]),
        ("#/some/🚀/tag", ["#/some/🚀/tag"]),
        (r"\\#foo", ["#foo"]),
        ("#f#oo", ["#f", "#oo"]),
        ("#foo#bar#baz", ["#foo", "#bar", "#baz"]),
    ],
)
def test_return_tags_1(string, returned):
    """Test the return_tags method.

    GIVEN a string with tags
    WHEN the return_tags method is called
    THEN the valid tags are returned
    """
    assert P.return_tags(string) == returned


@pytest.mark.parametrize(
    ("string"),
    [
        ("##foo# ##bar # baz ##"),
        ("##foo"),
        ("foo##bar"),
        ("#1123"),
        ("foo bar"),
        ("aa#foo"),
        ("$#foo"),
    ],
)
def test_return_tags_2(string):
    """Test the return_tags method.

    GIVEN a string without valid tags
    WHEN the return_tags method is called
    THEN None is returned
    """
    assert P.return_tags(string) == []


def test_return_top_with_header_1():
    """Test the return_top_with_header method.

    GIVEN a string with frontmatter above a first markdown header
    WHEN return_top_with_header is called
    THEN return the content up to the end of the first header
    """
    content = """
---
key: value
---
# Hello World

foo bar baz
"""
    assert P.return_top_with_header(content) == "---\nkey: value\n---\n# Hello World\n"


def test_return_top_with_header_2():
    """Test the return_top_with_header method.

    GIVEN a string with content above a first markdown header on the first line
    WHEN return_top_with_header is called
    THEN return the content up to the end of the first header
    """
    content = "\n\n### Hello World\nfoo bar\nfoo bar"
    assert P.return_top_with_header(content) == "### Hello World\n"


def test_return_top_with_header_3():
    """Test the return_top_with_header method.

    GIVEN a string with no markdown headers
    WHEN return_top_with_header is called
    THEN return None
    """
    content = "Hello World\nfoo bar\nfoo bar"
    assert not P.return_top_with_header(content)


def test_return_top_with_header_4():
    """Test the return_top_with_header method.

    GIVEN a string with no markdown headers
    WHEN return_top_with_header is called
    THEN return None
    """
    content = "qux bar baz\nbaz\nfoo\n### bar\n# baz foo bar"
    assert P.return_top_with_header(content) == "qux bar baz\nbaz\nfoo\n### bar\n"


def test_strip_frontmatter_1():
    """Test the strip_frontmatter method.

    GIVEN a string with frontmatter
    WHEN the strip_frontmatter method is called
    THEN the frontmatter is removed
    """
    content = """
---
key: value
---
# Hello World
"""
    assert P.strip_frontmatter(content).strip() == "# Hello World"


def test_strip_frontmatter_2():
    """Test the strip_frontmatter method.

    GIVEN a string without frontmatter
    WHEN the strip_frontmatter method is called
    THEN nothing is removed
    """
    content = """
# Hello World
---
key: value
---
"""
    assert P.strip_frontmatter(content) == content


def test_strip_frontmatter_3():
    """Test the strip_frontmatter method.

    GIVEN a string with frontmatter
    WHEN the strip_frontmatter method is called with data_only=True
    THEN the frontmatter is removed
    """
    content = """
---
key: value
---
# Hello World
"""
    assert P.strip_frontmatter(content, data_only=True).strip() == "---\n---\n# Hello World"


def test_strip_frontmatter_4():
    """Test the strip_frontmatter method.

    GIVEN a string without frontmatter
    WHEN the strip_frontmatter method is called with data_only=True
    THEN nothing is removed
    """
    content = """
# Hello World
---
key: value
---
"""
    assert P.strip_frontmatter(content, data_only=True) == content


def test_strip_inline_code_1():
    """Test the strip_inline_code method.

    GIVEN a string with inline code
    WHEN the strip_inline_code method is called
    THEN the inline code is removed
    """
    assert P.strip_inline_code("Foo `bar` baz `Qux` ```bar\n```") == "Foo baz ```bar\n```"
    assert P.strip_inline_code("Foo `bar` baz `Qux` ```bar\n```") == "Foo baz ```bar\n```"


def test_validators():
    """Test validators."""
    assert P.validate_tag_text.search("test_tag") is None
    assert P.validate_tag_text.search("#asdf").group(0) == "#"
