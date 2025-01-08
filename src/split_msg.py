import click
from pathlib import Path
from msg_split import split_message

@click.command()
@click.option('--max-len', default=4096, help='Maximum length of each fragment')
@click.argument('input_file', type=click.Path(exists=True))
def main(max_len: int, input_file: str):
    """Split HTML message into fragments."""
    input_path = Path(input_file)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    try:
        for i, fragment in enumerate(split_message(source, max_len), 1):
            print(f"-- fragment #{i}: {len(fragment)} chars --")
            print(fragment)
            print()
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    main()