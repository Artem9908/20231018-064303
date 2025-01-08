import pytest
from click.testing import CliRunner
from src.split_msg import main

def test_cli_basic():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('test.html', 'w') as f:
            f.write('<p>Test content</p>')
        
        result = runner.invoke(main, ['--max-len=20', 'test.html'])
        assert result.exit_code == 0
        assert '<p>Test content</p>' in result.output

def test_cli_json_output():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('test.html', 'w') as f:
            f.write('<p>Test content</p>')
        
        result = runner.invoke(main, ['--max-len=20', '--format=json', 'test.html'])
        assert result.exit_code == 0
        assert '"total_fragments":' in result.output

def test_cli_invalid_file():
    runner = CliRunner()
    result = runner.invoke(main, ['--max-len=20', 'nonexistent.html'])
    assert result.exit_code != 0 