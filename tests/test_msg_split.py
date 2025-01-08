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
    # Check that we have at least two fragments
    assert len(fragments_4396) >= 2
    # Check that the first fragment contains complete content
    assert '<strong>🕒' in fragments_4396[0]
    # Check that fragments maintain proper tag structure
    assert all('<strong>' not in f or '</strong>' in f for f in fragments_4396)
    
    # Test with max_len = 4296
    fragments_4296 = list(split_message(html, max_len=4296))
    # Check that we have at least two fragments
    assert len(fragments_4296) >= 2
    # Check that fragments maintain proper tag structure
    assert all('<strong>' not in f or '</strong>' in f for f in fragments_4296)
    # Check that content is properly split
    assert any('<div>' in f and '</div>' in f for f in fragments_4296)

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

def test_real_world_example():
    """Test with the actual example from requirements."""
    html = """
    <strong>🕒 Some tasks are missing worklogs!</strong>
    <mention id="U1024">Justin Kirvin</mention>
    Here is the list of tasks that have been in status without worklogs for more than <strong>1h</strong>
    """
    fragments = list(split_message(html, max_len=100))
    assert all(len(f) <= 100 for f in fragments)
    assert all('<strong>' in f and '</strong>' in f for f in fragments if '<strong>' in f)

def test_mention_tag():
    """Test handling of mention tags."""
    html = '<mention id="U1024">Justin Kirvin</mention>'
    fragments = list(split_message(html, max_len=50))
    assert len(fragments) == 1
    assert 'id="U1024"' in fragments[0]

def test_emoji_handling():
    """Test handling of emoji characters."""
    html = '<strong>🕒 Some text</strong>'
    fragments = list(split_message(html, max_len=50))
    assert len(fragments) == 1
    assert '🕒' in fragments[0]

def test_boundary_4396():
    """Test splitting behavior with max_len=4396."""
    with open('tests/test_data/source.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    fragments = list(split_message(html, max_len=4396))
    
    # Verify we have at least 2 fragments
    assert len(fragments) >= 2
    
    # Check that all fragments maintain proper HTML structure
    for fragment in fragments:
        # Check tag balance
        assert fragment.count('<span>') == fragment.count('</span>')
        assert fragment.count('<div>') == fragment.count('</div>')
        
        # Check that no tags are split across fragments
        assert not fragment.startswith('>')
        assert not fragment.endswith('<')

def test_boundary_4296():
    """Test splitting behavior with max_len=4296."""
    with open('tests/test_data/source.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    fragments = list(split_message(html, max_len=4296))
    
    # Verify we have at least 2 fragments
    assert len(fragments) >= 2
    
    # Check that all fragments are within size limit
    assert all(len(f) <= 4296 for f in fragments)
    
    # Check that all fragments maintain proper HTML structure
    for fragment in fragments:
        # Check tag balance
        assert fragment.count('<span>') == fragment.count('</span>')
        assert fragment.count('<div>') == fragment.count('</div>')
        
        # Verify content integrity
        assert fragment.strip()  # No empty fragments