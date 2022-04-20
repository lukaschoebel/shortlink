import pytest
from api.helper import validate, generate_encoding


def test_validate_url():
    test_urls = [
        "http://www.cwi.nl:80/guido/Python.html",
        "www.hithere.com/data/without/http/in/front",
        532,
        "hello-world",
        "https://www.avalidurl.com/sovalid/sowow",
        "https://avalidurl.com/sovalid/sowow",
        "https://shor.ty/",
        "    https://shor.ty/",  # leading space is forbidden
        "https://shor.ty/    ",  # trailing space is allowed
    ]

    result = [validate(url) for url in test_urls]
    expected = [True, False, False, False, True, True, True, False, True]

    assert len(result) == len(expected)
    assert all([r == e for r, e in zip(result, expected)])


def test_validate_url_missing_arg():
    with pytest.raises(TypeError):
        validate()


def test_generate_encoding():
    assert len(generate_encoding([])) == 6
    assert len(generate_encoding([], k=7)) == 7
    assert len(generate_encoding([], k=15)) == 15


def test_generate_encoding_missing_arg():
    with pytest.raises(TypeError):
        generate_encoding()


def test_generate_encoding_invalid_k():
    with pytest.raises(ValueError):
        generate_encoding([], k=0)
