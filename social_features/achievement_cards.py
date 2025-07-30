from typing import List


def create_card(title: str, lines: List[str]) -> str:
    """Return a simple ascii card summarizing achievements."""
    content_width = max([len(title)] + [len(l) for l in lines])
    border = '+' + '-' * (content_width + 2) + '+'
    result = [border]
    result.append(f"| {title.ljust(content_width)} |")
    result.append(border)
    for line in lines:
        result.append(f"| {line.ljust(content_width)} |")
    result.append(border)
    return '\n'.join(result)