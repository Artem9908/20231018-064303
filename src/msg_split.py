from typing import Generator, List, Optional, Union
from bs4 import BeautifulSoup, Tag, NavigableString

MAX_LEN = 4096

class HTMLFragmentationError(Exception):
    """Base exception for HTML fragmentation errors."""
    pass

class UnsplittableElementError(HTMLFragmentationError):
    """Raised when an unsplittable element exceeds max_len."""
    pass

def split_message(source: str, max_len: int = MAX_LEN) -> Generator[str, None, None]:
    """Splits HTML message into fragments while preserving tag structure."""
    if not source.strip():
        return
        
    soup = BeautifulSoup(source, 'html.parser')
    
    def is_unsplittable(tag: Tag) -> bool:
        return tag.name in ['a', 'code', 'mention']
    
    def is_block_tag(tag: Tag) -> bool:
        return tag.name in ['p', 'b', 'strong', 'i', 'ul', 'ol', 'div', 'span']
    
    def create_fragment(content: str, wrapper_tags: List[Tag] = None) -> str:
        """Creates a fragment with proper wrapper tags."""
        if not wrapper_tags:
            return content.strip()
            
        result = content
        for tag in wrapper_tags:
            attrs = ' '.join(f'{k}="{v}"' for k, v in tag.attrs.items())
            result = f'<{tag.name}{" " + attrs if attrs else ""}>{result}</{tag.name}>'
        return result.strip()

    def get_content_length(content: str, wrapper_tags: List[Tag] = None) -> int:
        """Calculate total length including wrapper tags."""
        return len(create_fragment(content, wrapper_tags))

    def process_tag(tag: Tag, current_wrappers: List[Tag] = None) -> Generator[str, None, None]:
        if current_wrappers is None:
            current_wrappers = []
            
        # Handle unsplittable tags
        if is_unsplittable(tag):
            content = str(tag)
            if len(content) > max_len:
                raise UnsplittableElementError(f"Element {tag.name} exceeds max_len")
            yield content
            return

        # Update wrappers for block tags
        if is_block_tag(tag):
            current_wrappers = current_wrappers + [tag]

        # Calculate wrapper overhead
        wrapper_overhead = len(create_fragment('', current_wrappers))
        available_len = max_len - wrapper_overhead

        # Process tag contents
        current_fragment = ''
        
        for child in tag.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if not text:
                    continue
                    
                potential_text = current_fragment + (' ' if current_fragment else '') + text
                if len(potential_text) <= available_len:
                    current_fragment = potential_text
                else:
                    if current_fragment:
                        yield create_fragment(current_fragment, current_wrappers)
                    current_fragment = text if len(text) <= available_len else text[:available_len]
                    if len(text) > available_len:
                        for i in range(available_len, len(text), available_len):
                            yield create_fragment(text[i:i + available_len], current_wrappers)
                        current_fragment = ''
            else:
                # Process nested tag
                if current_fragment:
                    yield create_fragment(current_fragment, current_wrappers)
                    current_fragment = ''
                
                for fragment in process_tag(child, current_wrappers):
                    yield fragment

        if current_fragment:
            yield create_fragment(current_fragment, current_wrappers)

    # Process each top-level element
    for element in soup.children:
        if isinstance(element, NavigableString):
            text = str(element).strip()
            if not text:
                continue
                
            yield text
        elif isinstance(element, Tag):
            for fragment in process_tag(element):
                yield fragment