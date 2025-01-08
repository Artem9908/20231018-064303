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

def test_specific_max_len_boundaries():
    with open('tests/test_data/source.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Test with max_len = 4396
    fragments_4396 = list(split_message(html, max_len=4396))
    assert '</div></span>' in fragments_4396[0]
    assert '<span><div>' in fragments_4396[1]
    
    # Test with max_len = 4296
    fragments_4296 = list(split_message(html, max_len=4296))
    assert '</div></span>' in fragments_4296[0]
    assert any('<div></div>' in f for f in fragments_4296)

def test_whitespace_handling():
    html = """
    <div>
        <p>   Some text   </p>
        <p>   More text   </p>
    </div>
    """
    fragments = list(split_message(html, max_len=30))
    assert all(f.strip() for f in fragments)  # No empty fragments

def test_invalid_html():
    html = "<div>Unclosed div"
    fragments = list(split_message(html, max_len=30))
    assert all('<div>' in f for f in fragments)
    assert all('</div>' in f for f in fragments)

def test_empty_input():
    html = ""
    fragments = list(split_message(html, max_len=30))
    assert len(fragments) == 0

def test_only_whitespace():
    html = "   \n   \t   "
    fragments = list(split_message(html, max_len=30))
    assert len(fragments) == 0