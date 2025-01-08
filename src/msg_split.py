from typing import Generator
from bs4 import BeautifulSoup, Tag

MAX_LEN = 4096

class HTMLFragmentationError(Exception):
    """Exception raised when HTML fragmentation fails."""
    pass

def split_message(source: str, max_len=MAX_LEN) -> Generator[str, None, None]:
    """Splits the original message into fragments of the specified length."""
    soup = BeautifulSoup(source, 'html.parser')
    
    def get_parent_tags(element):
        """Returns all parent tags that need to be preserved."""
        tags = []
        for parent in element.parents:
            if parent.name in ['p', 'b', 'strong', 'i', 'ul', 'ol', 'div', 'span']:
                tags.append(parent)
        return tags[::-1]
    
    def create_wrapper_start(tags):
        """Creates opening tags for a fragment."""
        result = []
        for tag in tags:
            attrs = ''
            if tag.attrs:
                attrs = ' ' + ' '.join(f'{k}="{v}"' for k, v in tag.attrs.items())
            result.append(f'<{tag.name}{attrs}>')
        return ''.join(result)
    
    def create_wrapper_end(tags):
        """Creates closing tags for a fragment."""
        return ''.join(f'</{tag.name}>' for tag in reversed(tags))

    def is_unsplittable(element):
        """Check if element is unsplittable."""
        if isinstance(element, Tag):
            if element.name in ['a', 'code', 'b', 'i', 'strong', 'em']:
                content = str(element)
                if len(content) > max_len:
                    raise HTMLFragmentationError("Unsplittable element exceeds max_len")
                return True
        return False

    def process_element(element, parent_tags=None):
        """Process an HTML element."""
        if parent_tags is None:
            parent_tags = []

        # Handle unsplittable elements
        if is_unsplittable(element):
            content = str(element)
            if len(content) > max_len:
                raise HTMLFragmentationError("Unsplittable element exceeds max_len")
            return [content]

        if isinstance(element, Tag):
            # Try to keep the entire element together first
            content = str(element)
            if len(content) <= max_len:
                return [content]

            # If we need to split, preserve parent structure
            current_tags = parent_tags + [element]
            wrapper_start = create_wrapper_start(current_tags)
            wrapper_end = create_wrapper_end(current_tags)
            available_len = max_len - len(wrapper_start) - len(wrapper_end)

            fragments = []
            current = ''

            for child in element.children:
                child_str = str(child).strip()
                if not child_str:
                    continue

                # Try to add child to current fragment
                if len(current + child_str) <= available_len:
                    current += child_str
                else:
                    # Store current fragment if it exists
                    if current:
                        fragments.append(wrapper_start + current + wrapper_end)
                    
                    # Handle child content
                    if isinstance(child, Tag):
                        for child_fragment in process_element(child, current_tags):
                            if len(wrapper_start + child_fragment + wrapper_end) <= max_len:
                                fragments.append(wrapper_start + child_fragment + wrapper_end)
                            else:
                                # Split child content if needed
                                child_parts = process_element(child, current_tags)
                                fragments.extend(wrapper_start + part + wrapper_end for part in child_parts)
                    else:
                        # Split text at word boundaries
                        words = child_str.split()
                        current = ''
                        for word in words:
                            if len(current + word + ' ') <= available_len:
                                current += word + ' '
                            else:
                                if current:
                                    fragments.append(wrapper_start + current.rstrip() + wrapper_end)
                                current = word + ' '
                    current = ''

            if current:
                fragments.append(wrapper_start + current.rstrip() + wrapper_end)

            return fragments

        # Handle text nodes
        text = str(element).strip()
        if not text:
            return []
        
        if len(text) <= max_len:
            return [text]
        
        # Split text at word boundaries
        words = text.split()
        fragments = []
        current = ''
        
        for word in words:
            if len(current + word + ' ') <= max_len:
                current += word + ' '
            else:
                if current:
                    fragments.append(current.rstrip())
                current = word + ' '
        
        if current:
            fragments.append(current.rstrip())
            
        return fragments

    # Process root elements
    current_fragment = ''
    root_tags = []
    
    for element in soup.children:
        if not str(element).strip():
            continue
            
        if isinstance(element, Tag):
            root_tags = [element]
        
        for fragment in process_element(element, root_tags):
            if len(current_fragment + fragment) <= max_len:
                current_fragment += fragment
            else:
                if current_fragment:
                    yield current_fragment
                current_fragment = fragment
    
    if current_fragment:
        yield current_fragment