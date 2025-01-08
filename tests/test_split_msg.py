import pytest
from click.testing import CliRunner
from src.split_msg import main
from pathlib import Path

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def sample_html(tmp_path):
    content = "<p>Test content</p>"
    file_path = tmp_path / "test.html"
    file_path.write_text(content)
    return str(file_path)

def test_cli_basic(runner, sample_html):
    result = runner.invoke(main, [sample_html])
    assert result.exit_code == 0
    assert "<p>Test content</p>" in result.output

def test_cli_max_len(runner, tmp_path):
    # Create a file with an unsplittable tag that exceeds max_len
    content = '<a href="https://very-long-url-that-exceeds-max-len">Link text</a>'
    file_path = tmp_path / "test.html"
    file_path.write_text(content)
    
    result = runner.invoke(main, ['--max-len', '10', str(file_path)])
    assert result.exit_code != 0  # Should fail due to unsplittable content
    assert "HTML Fragmentation Error" in result.output  # Verify error message

def test_cli_json_format(runner, sample_html):
    result = runner.invoke(main, ['--format', 'json', sample_html])
    assert result.exit_code == 0
    assert '"total_fragments":' in result.output
    assert '"fragments":' in result.output

def test_cli_verbose(runner, sample_html):
    result = runner.invoke(main, ['--verbose', sample_html])
    assert result.exit_code == 0
    assert "fragment #1:" in result.output

def test_cli_invalid_file(runner):
    result = runner.invoke(main, ['nonexistent.html'])
    assert result.exit_code != 0

def test_cli_non_utf8_file(runner, tmp_path):
    # Create a file with non-UTF8 content
    file_path = tmp_path / "non_utf8.html"
    with open(file_path, 'wb') as f:
        f.write(b'\xFF\xFE' + b'Invalid UTF-8')
    
    result = runner.invoke(main, [str(file_path)])
    assert result.exit_code != 0
    assert "Error: Input file must be UTF-8 encoded" in result.output 