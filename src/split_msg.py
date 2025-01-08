import click
from pathlib import Path
from src.msg_split import split_message, HTMLFragmentationError
import json

@click.command()
@click.option('--max-len', default=4096, help='Maximum length of each fragment')
@click.option('--format', type=click.Choice(['text', 'json']), default='text', help='Output format')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.argument('input_file', type=click.Path(exists=True))
def main(max_len: int, format: str, verbose: bool, input_file: str):
    """Split HTML message into fragments."""
    input_path = Path(input_file)
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source = f.read()
    except UnicodeDecodeError:
        click.echo("Error: Input file must be UTF-8 encoded", err=True)
        raise click.Abort()
    
    try:
        fragments = list(split_message(source, max_len))
        
        if format == 'json':
            result = {
                'total_fragments': len(fragments),
                'fragments': [
                    {
                        'number': i,
                        'length': len(f),
                        'content': f
                    } for i, f in enumerate(fragments, 1)
                ]
            }
            click.echo(json.dumps(result, indent=2))
        else:
            for i, fragment in enumerate(fragments, 1):
                if verbose:
                    click.echo(f"-- fragment #{i}: {len(fragment)} chars --")
                click.echo(fragment)
                click.echo()
                
    except HTMLFragmentationError as e:
        click.echo(f"HTML Fragmentation Error: {str(e)}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        raise click.Abort()

if __name__ == '__main__':
    main()