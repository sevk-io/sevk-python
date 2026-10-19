from sevk.markup import render


def test_renders_markup_into_an_html_email_document() -> None:
    html = render("<section><paragraph>Hello world</paragraph></section>")
    assert html.startswith("<!DOCTYPE html PUBLIC")
    assert "Hello world" in html
    assert "<paragraph>" not in html
