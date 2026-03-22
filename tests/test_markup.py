"""
Sevk Markup Block/Template Engine Tests
"""

import pytest

from sevk.markup.renderer import _render_template, _process_block_tag, render


# ---------------------------------------------------------------------------
# _render_template tests
# ---------------------------------------------------------------------------

class TestRenderTemplateSimpleVariables:
    """Test simple variable substitution in _render_template"""

    def test_simple_variable(self):
        result = _render_template("{%name%}", {"name": "Alice"})
        assert result == "Alice"

    def test_missing_variable(self):
        result = _render_template("{%name%}", {})
        assert result == ""

    def test_multiple_variables(self):
        result = _render_template("{%first%} {%last%}", {"first": "John", "last": "Doe"})
        assert result == "John Doe"


class TestRenderTemplateFallback:
    """Test fallback syntax {%variable ?? fallback%}"""

    def test_fallback_value_present(self):
        result = _render_template("{%name ?? Guest%}", {"name": "Alice"})
        assert result == "Alice"

    def test_fallback_value_missing(self):
        result = _render_template("{%name ?? Guest%}", {})
        assert result == "Guest"

    def test_fallback_value_empty_string(self):
        result = _render_template("{%name ?? Guest%}", {"name": ""})
        assert result == "Guest"

    def test_fallback_value_null(self):
        result = _render_template("{%name ?? Guest%}", {"name": None})
        assert result == "Guest"


class TestRenderTemplateEachLoop:
    """Test {%#each ...%} loop processing"""

    def test_each_with_alias(self):
        template = "{%#each items as item%}{%item.name%}{%/each%}"
        config = {"items": [{"name": "A"}, {"name": "B"}]}
        result = _render_template(template, config)
        assert result == "AB"

    def test_each_default_this(self):
        template = "{%#each items%}{%this.name%}{%/each%}"
        config = {"items": [{"name": "X"}, {"name": "Y"}]}
        result = _render_template(template, config)
        assert result == "XY"

    def test_each_empty_array(self):
        template = "{%#each items as item%}{%item.name%}{%/each%}"
        config = {"items": []}
        result = _render_template(template, config)
        assert result == ""

    def test_each_parent_scope(self):
        template = "{%#each items as item%}{%item.name%}-{%color%}{%/each%}"
        config = {"items": [{"name": "A"}], "color": "red"}
        result = _render_template(template, config)
        assert result == "A-red"

    def test_each_multiple_props(self):
        template = "{%#each items as item%}{%item.first%} {%item.last%},{%/each%}"
        config = {"items": [{"first": "John", "last": "Doe"}, {"first": "Jane", "last": "Smith"}]}
        result = _render_template(template, config)
        assert result == "John Doe,Jane Smith,"


class TestRenderTemplateIfElse:
    """Test {%#if ...%} conditional processing"""

    def test_if_true(self):
        result = _render_template("{%#if show%}visible{%/if%}", {"show": True})
        assert result == "visible"

    def test_if_false(self):
        result = _render_template("{%#if show%}visible{%/if%}", {"show": False})
        assert result == ""

    def test_if_else_true(self):
        result = _render_template("{%#if show%}yes{%else%}no{%/if%}", {"show": True})
        assert result == "yes"

    def test_if_else_false(self):
        result = _render_template("{%#if show%}yes{%else%}no{%/if%}", {"show": False})
        assert result == "no"

    def test_if_no_else_false(self):
        result = _render_template("{%#if show%}content{%/if%}", {"show": False})
        assert result == ""


class TestRenderTemplateTruthiness:
    """Test truthiness evaluation for if conditionals"""

    def test_none_is_falsy(self):
        result = _render_template("{%#if val%}yes{%else%}no{%/if%}", {"val": None})
        assert result == "no"

    def test_empty_string_is_falsy(self):
        result = _render_template("{%#if val%}yes{%else%}no{%/if%}", {"val": ""})
        assert result == "no"

    def test_false_is_falsy(self):
        result = _render_template("{%#if val%}yes{%else%}no{%/if%}", {"val": False})
        assert result == "no"

    def test_zero_is_falsy(self):
        result = _render_template("{%#if val%}yes{%else%}no{%/if%}", {"val": 0})
        assert result == "no"

    def test_empty_list_is_falsy(self):
        result = _render_template("{%#if val%}yes{%else%}no{%/if%}", {"val": []})
        assert result == "no"

    def test_non_empty_string_is_truthy(self):
        result = _render_template("{%#if val%}yes{%else%}no{%/if%}", {"val": "hello"})
        assert result == "yes"

    def test_non_empty_list_is_truthy(self):
        result = _render_template("{%#if val%}yes{%else%}no{%/if%}", {"val": [1]})
        assert result == "yes"

    def test_number_is_truthy(self):
        result = _render_template("{%#if val%}yes{%else%}no{%/if%}", {"val": 42})
        assert result == "yes"


class TestRenderTemplateNestedIfs:
    """Test nested if conditionals"""

    def test_nested_both_true(self):
        template = "{%#if outer%}{%#if inner%}both{%/if%}{%/if%}"
        result = _render_template(template, {"outer": True, "inner": True})
        assert result == "both"

    def test_nested_outer_true_inner_false(self):
        template = "{%#if outer%}A{%#if inner%}B{%/if%}C{%/if%}"
        result = _render_template(template, {"outer": True, "inner": False})
        assert result == "AC"

    def test_nested_outer_false(self):
        template = "{%#if outer%}{%#if inner%}both{%/if%}{%/if%}"
        result = _render_template(template, {"outer": False, "inner": True})
        assert result == ""


class TestRenderTemplateDoublebracePreservation:
    """Test that {{variable}} syntax is preserved untouched"""

    def test_double_brace_preserved(self):
        result = _render_template("Hello {{name}}", {"name": "Alice"})
        assert "{{name}}" in result

    def test_double_brace_with_single_brace_variable(self):
        result = _render_template("{%greeting%} {{name}}", {"greeting": "Hi"})
        assert result == "Hi {{name}}"


class TestRenderTemplateCombined:
    """Test combinations of if, each, and variables"""

    def test_combined_if_each_variables(self):
        template = "{%#if showList%}{%#each items as item%}{%item.name%}-{%/each%}{%else%}empty{%/if%}"
        config = {"showList": True, "items": [{"name": "A"}, {"name": "B"}]}
        result = _render_template(template, config)
        assert result == "A-B-"

    def test_combined_if_false_skips_each(self):
        template = "{%#if showList%}{%#each items as item%}{%item.name%}{%/each%}{%else%}empty{%/if%}"
        config = {"showList": False, "items": [{"name": "A"}]}
        result = _render_template(template, config)
        assert result == "empty"


# ---------------------------------------------------------------------------
# _process_block_tag tests
# ---------------------------------------------------------------------------

class TestProcessBlockTagConfigParsing:
    """Test config parsing in _process_block_tag"""

    def test_config_with_single_quotes(self):
        attrs = {"config": "{'name':'Alice'}"}
        result = _process_block_tag(attrs, "{%name%}")
        assert result == "Alice"

    def test_config_with_entities(self):
        attrs = {"config": '{"name":&quot;Bob&quot;}'}
        result = _process_block_tag(attrs, "{%name%}")
        assert result == "Bob"

    def test_empty_config(self):
        attrs = {"config": "{}"}
        result = _process_block_tag(attrs, "{%name%}")
        assert result == ""

    def test_invalid_json_config(self):
        attrs = {"config": "not json"}
        result = _process_block_tag(attrs, "{%name%}")
        assert result == ""


class TestProcessBlockTagTemplate:
    """Test template resolution in _process_block_tag"""

    def test_template_from_inner_content(self):
        attrs = {"config": '{"name":"World"}'}
        result = _process_block_tag(attrs, "Hello {%name%}")
        assert result == "Hello World"

    def test_missing_template(self):
        attrs = {"config": '{"name":"World"}'}
        result = _process_block_tag(attrs, "")
        assert result == ""


# ---------------------------------------------------------------------------
# Full render pipeline tests (using the render function)
# ---------------------------------------------------------------------------

class TestFullRenderPipelineBlocks:
    """Test full render pipeline with block tags producing sevk markup"""

    def _body(self, html):
        """Extract content between the body div tags for assertion."""
        import re
        m = re.search(r'<div aria-roledescription="email" role="article">\n([\s\S]*?)\n</div>', html)
        return m.group(1).strip() if m else html

    def test_block_with_paragraph(self):
        markup = '<block config=\'{"text":"Hello"}\'><paragraph>{%text%}</paragraph></block>'
        result = self._body(render(markup))
        assert "<p" in result
        assert "Hello" in result

    def test_block_with_heading(self):
        markup = '<block config=\'{"title":"Welcome"}\'><heading level="2">{%title%}</heading></block>'
        result = self._body(render(markup))
        assert "<h2" in result
        assert "Welcome" in result

    def test_block_with_button(self):
        markup = '<block config=\'{"label":"Click","url":"https://example.com"}\'><button href="{%url%}">{%label%}</button></block>'
        result = self._body(render(markup))
        assert "Click" in result
        assert "https://example.com" in result
        assert "<a " in result

    def test_block_with_image(self):
        markup = '<block config=\'{"src":"https://img.test/photo.png","alt":"Photo"}\'><image src="{%src%}" alt="{%alt%}" /></block>'
        result = self._body(render(markup))
        assert "<img " in result
        assert "https://img.test/photo.png" in result
        assert 'alt="Photo"' in result

    def test_block_with_section(self):
        markup = '<block config=\'{"content":"Inside section"}\'><section padding="20px"><paragraph>{%content%}</paragraph></section></block>'
        result = self._body(render(markup))
        assert "Inside section" in result
        assert "<table" in result

    def test_block_with_link(self):
        markup = '<block config=\'{"url":"https://example.com","text":"click here"}\'><link href="{%url%}">{%text%}</link></block>'
        result = self._body(render(markup))
        assert "<a " in result
        assert "https://example.com" in result
        assert "click here" in result

    def test_block_with_row_column(self):
        markup = '<block config=\'{"left":"L","right":"R"}\'><row><column><paragraph>{%left%}</paragraph></column><column><paragraph>{%right%}</paragraph></column></row></block>'
        result = self._body(render(markup))
        assert "L" in result
        assert "R" in result
        assert "sevk-column" in result

    def test_block_with_each_loop(self):
        markup = '<block config=\'{"items":[{"name":"A"},{"name":"B"}]}\'>{%#each items as item%}<paragraph>{%item.name%}</paragraph>{%/each%}</block>'
        result = self._body(render(markup))
        assert "<p" in result
        assert "A" in result
        assert "B" in result

    def test_block_with_if_else(self):
        markup = '<block config=\'{"show":true}\'>{%#if show%}<paragraph>Visible</paragraph>{%else%}<paragraph>Hidden</paragraph>{%/if%}</block>'
        result = self._body(render(markup))
        assert "Visible" in result
        assert "Hidden" not in result

    def test_block_with_if_else_false(self):
        markup = '<block config=\'{"show":false}\'>{%#if show%}<paragraph>Visible</paragraph>{%else%}<paragraph>Hidden</paragraph>{%/if%}</block>'
        result = self._body(render(markup))
        assert "Hidden" in result
        assert "Visible" not in result

    def test_double_brace_preserved_in_block(self):
        markup = '<block config=\'{"greeting":"Hi"}\'><paragraph>{%greeting%} {{username}}</paragraph></block>'
        result = self._body(render(markup))
        assert "Hi" in result
        assert "{{username}}" in result

    def test_multiple_blocks(self):
        markup = (
            '<block config=\'{"title":"Header"}\'><heading level="1">{%title%}</heading></block>'
            '<block config=\'{"text":"Body text"}\'><paragraph>{%text%}</paragraph></block>'
        )
        result = self._body(render(markup))
        assert "Header" in result
        assert "Body text" in result

    def test_block_with_fallback_values(self):
        markup = '<block config=\'{}\'><paragraph>{%name ?? Subscriber%}</paragraph></block>'
        result = self._body(render(markup))
        assert "Subscriber" in result

    def test_social_links_template(self):
        markup = (
            '<block config=\'{"links":[{"url":"https://twitter.com","label":"Twitter"},{"url":"https://github.com","label":"GitHub"}]}\'>'
            '{%#each links as link%}<link href="{%link.url%}">{%link.label%}</link> {%/each%}'
            '</block>'
        )
        result = self._body(render(markup))
        assert "Twitter" in result
        assert "GitHub" in result
        assert "https://twitter.com" in result
        assert "https://github.com" in result

    def test_header_template_with_nested_if(self):
        markup = (
            '<block config=\'{"title":"Welcome","showSubtitle":true,"subtitle":"To our app"}\'>'
            '<heading level="1">{%title%}</heading>'
            '{%#if showSubtitle%}<paragraph>{%subtitle%}</paragraph>{%/if%}'
            '</block>'
        )
        result = self._body(render(markup))
        assert "Welcome" in result
        assert "To our app" in result

    def test_header_template_nested_if_hidden(self):
        markup = (
            '<block config=\'{"title":"Welcome","showSubtitle":false,"subtitle":"To our app"}\'>'
            '<heading level="1">{%title%}</heading>'
            '{%#if showSubtitle%}<paragraph>{%subtitle%}</paragraph>{%/if%}'
            '</block>'
        )
        result = self._body(render(markup))
        assert "Welcome" in result
        assert "To our app" not in result

    def test_unsubscribe_footer_template(self):
        markup = (
            '<block config=\'{"company":"Acme Inc","unsubscribeUrl":"https://example.com/unsub"}\'>'
            '<section padding="20px" text-align="center">'
            '<paragraph font-size="12px">{%company%}</paragraph>'
            '<link href="{%unsubscribeUrl%}">Unsubscribe</link>'
            '</section>'
            '</block>'
        )
        result = self._body(render(markup))
        assert "Acme Inc" in result
        assert "https://example.com/unsub" in result
        assert "Unsubscribe" in result


# ---------------------------------------------------------------------------
# Lang and Dir attribute tests
# ---------------------------------------------------------------------------

class TestLangAndDirAttributes:
    """Test lang and dir attribute parsing from root mail/email tag"""

    def test_lang_attribute(self):
        markup = '<mail lang="tr"><body><paragraph>Merhaba</paragraph></body></mail>'
        result = render(markup)
        assert 'lang="tr"' in result

    def test_dir_attribute(self):
        markup = '<mail dir="rtl"><body><paragraph>Hello</paragraph></body></mail>'
        result = render(markup)
        assert 'dir="rtl"' in result

    def test_lang_and_dir_attributes(self):
        markup = '<mail lang="ar" dir="rtl"><body><paragraph>مرحبا</paragraph></body></mail>'
        result = render(markup)
        assert 'lang="ar"' in result
        assert 'dir="rtl"' in result

    def test_default_lang_and_dir(self):
        markup = '<mail><body><paragraph>Hello</paragraph></body></mail>'
        result = render(markup)
        assert 'lang="en"' in result
        assert 'dir="ltr"' in result
