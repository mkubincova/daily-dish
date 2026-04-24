import random
import re
import string


def slugify(text: str, suffix_length: int = 6) -> str:
    """Convert text to URL slug with a random suffix to avoid collisions."""
    slug = text.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = slug.strip("-")
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=suffix_length))
    return f"{slug}-{suffix}"
