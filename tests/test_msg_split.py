import pytest
from src.msg_split import split_message, HTMLFragmentationError

def test_simple_split():
    html = """
    <p>First paragraph</p>
    <p>Second paragraph</p>
    """
    fragments = list(split_message(html, max_len=20))
    assert len(fragments) == 2
    assert all(len(f) <= 20 for f in fragments)

def test_nested_tags():
    html = """
    <div>
        <p><b>Bold text</b></p>
        <p>Normal text</p>
    </div>
    """
    fragments = list(split_message(html, max_len=30))
    assert all('<div>' in f for f in fragments)
    assert all('</div>' in f for f in fragments)

def test_unsplittable():
    html = '<p><a href="very-long-url-that-exceeds-max-len">Link</a></p>'
    with pytest.raises(HTMLFragmentationError):
        list(split_message(html, max_len=20))