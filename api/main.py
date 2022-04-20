from typing import Dict
from datetime import datetime
from fastapi import FastAPI, Query, HTTPException
from api.helper import validate, generate_encoding
from api.models import LongURL, UrlObject, ShortLinkSettings

app = FastAPI()

urls: Dict[str, UrlObject] = {}
settings: ShortLinkSettings = {"domain_prefix": "https://shor.ty/"}


@app.post("/encode/")
def encode(url: LongURL) -> UrlObject:
    """**Encodes a provided url to a corresponding shorter version of itself**

    The returned object contains the encoded version as well as additional
    parameters about the creation.

    The creational parameters (created_at, last_accessed) in the object
    can be used on the client-side to evaluate if an encoding for a provided
    URL is already existing or not. If both timestamps are equal, the encoding
    is created at time of the API call. If they do not match, the API call
    accessed the stored/cached object.

    **Args:**
        _url (LongURL)_: specifies long version of an url which should be encoded

    **Raises:**
        _HTTPException_: for url argument which is not a valid URL

    **Returns:**
        _UrlObject_: url object with all information about the encoded url.
    """

    if not validate(url=url.longurl):
        raise HTTPException(
            status_code=400,
            detail=f"the provided url '{url.longurl}' is not a valid URL. please conform to a valid URL format with preceeding http or https schemas, see https://www.w3.org/Addressing/URL/url-spec.txt",
        )

    # get current time for generating timestamped response
    dt = datetime.now()

    # strips trailing space from url
    longurl = url.longurl.rstrip()

    # check if url is already encoded and stored in memory
    for url in urls.values():
        if url["longurl"] == longurl:
            # if url is found in memory return it and
            # change last_accessed property to dt
            url["last_accessed"] = dt
            return url

    # if url is not already encoded, proceed with encoding process
    existing_encodings = [url["shorturl"].lstrip(settings["domain_prefix"]) for url in urls.values()]
    shorturl = settings["domain_prefix"] + generate_encoding(existing_encodings)

    # add UrlObject to the stored urls dict with shorturl as key
    urls[shorturl] = {
        "longurl": longurl,
        "shorturl": shorturl,
        "created_at": dt,
        "last_accessed": dt,
    }

    return urls[shorturl]


@app.get("/decode/")
def decode(
    shorturl: str = Query(
        None, alias="shorturl", title="short version of the encoded url that will be decoded to its original url"
    )
) -> UrlObject:
    """**Decodes a provided url in short format into its respective longer version**

    **Args:**
        shorturl (str): query parameter which specifies the short version of an URL

    **Raises:**
        _HTTPException_: for shorturl argument which is not a valid URL
        _HTTPException_: for shorturl which is currently not stored and hence cannot be decoded

    **Returns:**
        _UrlObject_: full url object for a provided shorturl
    """

    if not validate(url=shorturl):
        raise HTTPException(
            status_code=400,
            detail=f"the provided shorturl '{shorturl}' is not a valid URL. please conform to a valid URL format with preceeding http or https schemas, see https://www.w3.org/Addressing/URL/url-spec.txt",
        )

    try:
        urls[shorturl]["last_accessed"] = datetime.now()
        return urls[shorturl]
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"the requested shorturl '{shorturl}' cannot be found and is not encoded yet. please first encode to decode.",
        )


@app.put("/update-prefix/")
def update_prefix(domain_prefix: str) -> Dict:
    """**Updates a static domain prefix variable which alters the final shortened url by changing its domain prefix**

    This endpoint can be used to alter the existing domain_prefix of
    "https://shor.ty/" to a customized domain_prefix.

    Providing a valid domain_prefix will encode all URLs so that they
    conform to the following format: "<domain_prefix>/<short_encoding>"

    **Args:**
        _domain_prefix (str)_: specifies a new domain prefix.
            has to be a valid url with less than 20 characters

    **Raises:**
        _HTTPException_: for invalid url format of domain_prefix argument
        _HTTPException_: for domain_prefix arg which is longer than 20 chars

    **Returns:**
        _Dict_: old and new domain_prefix value as Dict
    """

    if not validate(url=domain_prefix):
        raise HTTPException(
            status_code=400,
            detail=f"the provided domain prefix '{domain_prefix}' is not a valid URL. please conform to a valid URL format with preceeding http or https schemas, see https://www.w3.org/Addressing/URL/url-spec.txt",
        )

    if len(domain_prefix) > 20:
        raise HTTPException(
            status_code=400,
            detail=f"the provided domain prefix '{domain_prefix}' seems to be longer than the maximum of 20 characters.",
        )

    # adding last slash
    domain_prefix = domain_prefix if domain_prefix.endswith("/") else f"{domain_prefix}/"

    # changing short url to https://
    domain_prefix = domain_prefix if domain_prefix.startswith("https://") else f"https{domain_prefix[4:]}"

    old_prefix = settings["domain_prefix"]
    settings["domain_prefix"] = domain_prefix.replace("http:", "https:", 1)

    return {"old_prefix": old_prefix, "new_prefix": settings["domain_prefix"]}
