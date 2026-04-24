from app.utils.slug import slugify


def test_slugify_basic():
    result = slugify("Chocolate Cake")
    assert result.startswith("chocolate-cake-")
    assert len(result) > len("chocolate-cake-")


def test_slugify_special_chars():
    result = slugify("Hello World!")
    assert "!" not in result
    assert result.startswith("hello-world-")


def test_slugify_suffix_length():
    result = slugify("Test", suffix_length=4)
    parts = result.rsplit("-", 1)
    assert len(parts[1]) == 4


def test_slugify_unique():
    s1 = slugify("Same Title")
    s2 = slugify("Same Title")
    # With random suffixes, two calls should produce different results with overwhelming probability
    assert s1 != s2
