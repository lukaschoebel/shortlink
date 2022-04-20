import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_encode_valid_url():
    valid_url = "https://thisisaverylongurl.com/trustme/itisvery/verylong"
    response = client.post(
        "/encode/",
        json={"longurl": valid_url},
    )
    assert response.status_code == 200
    assert response.json()["shorturl"] is not None


def test_encode_valid_url_with_trailing_space():
    valid_url_without_space = "https://thisisaverylongurl.com/testinger"
    valid_url_trailing_space = "https://thisisaverylongurl.com/testinger       "

    response_without_space = client.post(
        "/encode/",
        json={"longurl": valid_url_without_space},
    )
    response_with_space = client.post(
        "/encode/",
        json={"longurl": valid_url_trailing_space},
    )

    assert response_without_space.status_code == 200
    assert response_with_space.status_code == 200

    assert response_without_space.json()["longurl"] == response_with_space.json()["longurl"]
    assert response_without_space.json()["shorturl"] == response_with_space.json()["shorturl"]
    assert response_without_space.json()["created_at"] == response_with_space.json()["created_at"]


def test_encode_changing_last_accessed():
    response_one = client.post(
        "/encode/",
        json={"longurl": "http://www.test123.de"},
    )

    response_two = client.post(
        "/encode/",
        json={"longurl": "http://www.test123.de"},
    )

    assert response_one.status_code == 200
    assert response_two.status_code == 200
    assert response_one.json()["last_accessed"] != response_two.json()["last_accessed"]


def test_encode_invalid_urls():
    invalid_urls = [
        42,
        42.42,
        "",
        "hi",
        "www.notvalid.com",
        "DROP TABLE users;",
        "https:/hi.com",
        "thisisaverylongurl.com/trustme/itisvery/verylong",
    ]

    responses = [
        client.post(
            "/encode/",
            json={"longurl": url},
        )
        for url in invalid_urls
    ]

    assert all([r.status_code == 400 for r in responses])


@pytest.fixture()
def encoded_valid_url():
    valid_long_url = "https://thisisaverylongurl.com/alalalala/longlong/lilonglilong"
    response = client.post(
        "/encode/",
        json={"longurl": valid_long_url},
    )

    yield response


def test_decode_valid_url(encoded_valid_url):
    response = client.get("/decode/", params={"shorturl": encoded_valid_url.json()["shorturl"]})
    print(encoded_valid_url.json())
    assert response.status_code == 200
    assert response.json()["longurl"] == "https://thisisaverylongurl.com/alalalala/longlong/lilonglilong"


def test_decode_url_not_found():
    invalid_short_url = "https://shor.ty/424242"

    response = client.get("/decode/", params={"shorturl": invalid_short_url})
    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == f"the requested shorturl '{invalid_short_url}' cannot be found and is not encoded yet. please first encode to decode."
    )


def test_decode_invalid_short_url():
    invalid_short_url = "4242"

    response = client.get("/decode/", params={"shorturl": invalid_short_url})
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == f"the provided shorturl '{invalid_short_url}' is not a valid URL. please conform to a valid URL format with preceeding http or https schemas, see https://www.w3.org/Addressing/URL/url-spec.txt"
    )


def test_update_prefix_with_valid_short_url_with_slash():
    valid_short_url = "http://shaw.ty/"

    response = client.put("/update-prefix/", params={"domain_prefix": valid_short_url})
    assert response.status_code == 200
    assert response.json()["new_prefix"] == "https://shaw.ty/"


def test_update_prefix_with_valid_short_url_without_slash():
    valid_short_url = "http://shaw.ty"

    response = client.put("/update-prefix/", params={"domain_prefix": valid_short_url})
    assert response.status_code == 200
    assert response.json()["new_prefix"] == "https://shaw.ty/"


def test_update_prefix_with_invalid_short_url():
    invalid_short_url = "4242"

    response = client.put("/update-prefix/", params={"domain_prefix": invalid_short_url})
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == f"the provided domain prefix '{invalid_short_url}' is not a valid URL. please conform to a valid URL format with preceeding http or https schemas, see https://www.w3.org/Addressing/URL/url-spec.txt"
    )


def test_all_endpoints():
    valid_urls = [
        "https://uno.es",
        "https://deux.it/",
        "http://trois.fr",
    ]

    encode_responses = [
        client.post(
            "/encode/",
            json={"longurl": url},
        )
        for url in valid_urls
    ]

    assert all([r.status_code == 200 for r in encode_responses])
    assert all([r.json()["shorturl"] is not None for r in encode_responses])

    decode_responses = [
        client.get(
            "/decode/",
            params={"shorturl": url.json()["shorturl"]},
        )
        for url in encode_responses
    ]

    assert all(
        [
            (p.json()["longurl"] == g.json()["longurl"] and p.json()["shorturl"] == g.json()["shorturl"])
            for p, g in zip(encode_responses, decode_responses)
        ]
    )

    new_domain_prefix = "http://brief.ly"
    expected_domain_prefix = "https://brief.ly/"

    update_prefix_response = client.put("/update-prefix/", params={"domain_prefix": new_domain_prefix})
    assert update_prefix_response.status_code == 200
    assert update_prefix_response.json()["new_prefix"] == expected_domain_prefix
    old_domain_prefix = update_prefix_response.json()["old_prefix"]

    responses_with_new_prefix = [
        client.post(
            "/encode/",
            json={"longurl": url},
        )
        for url in valid_urls
    ]

    # already encoded urls will start with old domain prefix since cached version is used
    assert all([r.json()["shorturl"].startswith(old_domain_prefix) for r in responses_with_new_prefix])

    responses_with_new_prefix = [
        client.post(
            "/encode/",
            json={"longurl": url},
        )
        for url in [
            "https://oans.de",
            "https://zwoa.de/",
            "http://drei.de",
        ]
    ]

    # new urls are encoded to the new domain prefix
    assert all([r.json()["shorturl"].startswith(expected_domain_prefix) for r in responses_with_new_prefix])
