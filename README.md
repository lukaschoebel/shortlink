# ShortLink

ShortLink is a service to shorten your long URLs.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Framework Selection](#framework-selection)
- [HowTo](#howto)
- [API Functionality](#api-functionality)
  - [Interaction with the API](#interaction-with-the-api)
  - [Encode (POST)](#encode-post)
    - [Example: Request & Response](#example-request--response)
    - [Implementation Notes](#implementation-notes)
  - [Decode (GET)](#decode-get)
    - [Example: Request & Response](#example-request--response-1)
    - [Implementation Notes](#implementation-notes-1)
  - [Update Prefix (PUT)](#update-prefix-put)
    - [Example: Request & Response](#example-request--response-2)
    - [Implementation Notes](#implementation-notes-2)
- [Tests](#tests)
- [Backlog](#backlog)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

The service comes with a callable API that implements an [`encode/`](#encode-post) and a [`decode/`](#decode-get) endpoint.

## Framework Selection

In order to implement a simple API that shortens a given URL and provides two endpoints, I chose to build this service with [FastAPI](https://fastapi.tiangolo.com/).

Claiming to be one of the fastest available Python frameworks, FastAPI allows for fast functionality and very easy construction of an API. The resulting code is intuitive to understand and, hence, allows to create of a robust and maintainable codebase.

Another advantage of building an API with FastAPI, is that it is based on [OpenAPI](https://github.com/OAI/OpenAPI-Specification) a.k.a _Swagger_ standards which provides an intuitive user interface (_Swagger UI_) to visually interact with the created API. The usage of Swagger UI is briefly described in [API Functionality](#api-functionality).

## HowTo

It is recommended to launch the ShortLink service in a dedicated _virtual environment_ (venv). Such a venv can be created with the environment management package _Conda_.

The following steps walk through the main steps for setting up the venv with the required packages:

1. Install [Conda](https://docs.conda.io/en/latest/miniconda.html)
2. Create virtual environment with `conda create -n shortlink`
3. Activate venv with `conda activate shortlink`
4. Install requirements with `pip install -r requirements.txt`

After having successfully installed the requirements in the venv, the API server can be launched with `uvicorn` by executing the following command in the `api/` directory:

```bash
cd api && uvicorn main:app
```

The above command will start the API server on the localhost. The endpoints can now be reached by accessing `http://127.0.0.1:8000/` and sending valid requests to the main endpoints (`encode/` or `decode/`).

For a better overview of the respective functionalities, it is referred to the next chapter which provides an overview of the included endpoints. The section [Interaction with the API](#interaction-with-the-api) provides showcases how to interact with the provided endpoints.

## API Functionality

The ShortLink API includes in total three endpoints: `encode/`, `decode/,` and `update-prefix/` with the following main ideas:

|   **Endpoint**   | **Functionality**                                         |
| :--------------: | :-------------------------------------------------------- |
|    `encode/`     | Encodes a valid, long URL to a shorter version of itself  |
|    `decode/`     | Decodes a valid, short URL to its respective long version |
| `update-prefix/` | Changes the domain prefix                                 |

While the two main endpoints are implemented as different HTTP requests, they both return an identical JSON object. This so-called _UrlObject_ - which is defined in `api/models.py` - consists of four properties: `longurl`, `shorturl`, `created_at,` and `last_accessed`. This results from the idea to provide the user with a consistent data object.

Further, the timestamps are added to the response object to provide information about the creation of the encoded object. If these creational parameters differ from each other, it means that the requested URL has already existed in the (pseudo) database and does not need to be encoded or decoded again. In a real-world scenario, this information could inform the user that the query has already been processed or generally track the usage of a shortened link.

### Interaction with the API

There are multiple ways to call and request data from the ShortLink API. To trigger the endpoints third-party tools like [Insomnia](https://insomnia.rest/) or [Postman](https://www.postman.com/) can be very helpful.

Another neat option to interact with the API is to use the _Swagger UI_ which comes conveniently with FastAPI. The user interface can be reached via `http://127.0.0.1:8000/docs` and will display the three endpoints. To request data, it is necessary to choose an endpoint and click on the button `Try it out` which is located on the right side beneath the description of the endpoint functionality. Having clicked the button, the request body or parameters have to be filled in.

Each API endpoint first validates the provided URL input to prevent misuse or potential abuse of the ShortLink service. It is noted, that only valid URLs with preceding `http` or `https` schemas are currently allowed to be entered. The API follows the [original specification](https://www.w3.org/Addressing/URL/url-spec.txt) of the URL. This means that `http://url.com` is valid, while `www.url.com` is invalid and will **not** be accepted as a request parameter/body by the endpoints.

Lastly, the canonical way to trigger the API endpoints is to use the `curl` command from the terminal. As the API usage with this option is easy to showcase in this document, the following sections will briefly describe how data from the ShortLink API can be posted or requested with `curl`.

### Encode (POST)

To encode a long version of an URL, the `encode/` endpoint takes a string in its request body. Since the idea is to provide a variable that is processed and stored in a (pseudo) database a.k.a memory, it is implemented as a `POST` request.

#### Example: Request & Response

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/encode/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "longurl": "https://www.thisisaverylongurl.com/trustmeitis/very/very/verylong"
}'
```

A successful 200-response to this request returns a JSON object that contains an _UrlObject_ with the four main properties. To obtain the shortened URL, the client has to access the shorturl. It can be observed that the creational parameters are identical which indicates that the long URL was encoded at the time of the request.

```json
{
  "longurl": "https://www.thisisaverylongurl.com/trustmeitis/very/very/verylong",
  "shorturl": "https://shor.ty/soC00L",
  "created_at": "2022-01-11T11:11:11.111111",
  "last_accessed": "2022-01-11T11:11:11.111111"
}
```

#### Implementation Notes

In the encoding request, the provided URL is first validated to guarantee that the argument conforms to a valid and correct HTTP format. If an URL is valid, it is preprocessed by removing any trailing whitespace.

Before the actual encoding of a provided long URL, the request first iterates over all stored UrlObjects to check if the provided address is already encoded to a shorter version of itself. If the `longurl` of any stored object matches the argument of the request body, the object with an altered `last_accessed` property is returned to the client. Since the entire memory object has to be searched, the `encode/` functionality has linear `O(n)` time complexity.

Otherwise, the URL is encoded by concatenating the domain prefix with a generated short encoding. As the last step, the UrlObject is stored within the internal database (a.k.a memory).

### Decode (GET)

As this request is used to retrieve data from the (pseudo) database a.k.a memory, it is implemented as a `GET` request.
Therefore, the `decode/` endpoint needs to be provided with a short version of an URL. This short URL is a query parameter for the request.

#### Example: Request & Response

Example cURL request to decode the encoded short URL `https://shor.ty/soC00L`:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/decode/?shorturl=https%3A%2F%2Fshor.ty%2FsoC00L' \
  -H 'accept: application/json'
```

A successful 200-response to this request returns a JSON object that contains an _UrlObject_ with the four main properties. It is noted that a `decode` request searches the (pseudo-)database for a provided encoded, key URL and, hence, changes the `last_accessed` property.

```json
{
  "longurl": "https://www.thisisaverylongurl.com/trustmeitis/very/very/verylong",
  "shorturl": "https://shor.ty/soC00L",
  "created_at": "2022-01-11T11:11:11.111111",
  "last_accessed": "2022-01-11T22:22:22.222222"
}
```

#### Implementation Notes

Before decoding a given shorturl, this endpoint first checks if the provided argument follows a valid HTTP scheme. If the provided URL is not valid, a 400 Error is raised and informs the user to enter a valid string.

Otherwise, the function tries to access the UrlObject with the provided valid `shorturl` as the key. Since all previous URLs are stored in a hash map, the access or time complexity is constant with `O(1)`. If there is not any URL with an encoding that matches the argument, a `KeyError` will be raised internally by Python which then subsequently also raises an HTTP 404-Error that informs the user to first encode an URL before he is able to decode it.

### Update Prefix (PUT)

In the ShortLink service, all long URLs are encoded to a short version which concatenates a domain prefix (default: `https://shor.ty/`) and a randomized encoding of length six. As an additional feature, this endpoint lets a (super-)user change this domain prefix to a customized version. It is implemented as a `PUT` request since it is altering a default value in the (pseudo-)database.

In a realistic scenario, it might be smart to implement API authentication and only allow admins of the service to change a prefix to guarantee consistent short URLs.

On a side note, it is further remarked that the domain prefix is currently stored as the only variable within the internal `settings` object (see line 9, `api/main.py`). If the API will be extended and other variables might be stored within this object, a partial update with a `PATCH` request might be more suitable for the given use case

#### Example: Request & Response

A cURL request to update the existing domain prefix with `https://shaw.ty/` would look like this:

```bash
curl -X 'PUT' \
  'http://127.0.0.1:8000/update-prefix/?domain_prefix=https%3A%2F%2Fshaw.ty%2F' \
  -H 'accept: application/json'
```

A successful response returns a JSON object that contains the new and the old domain prefix to the user:

```json
{
  "old_prefix": "https://shor.ty/",
  "new_prefix": "https://shaw.ty/"
}
```

#### Implementation Notes

Before updating the domain prefix, the provided URL is first validated twice. First, the URL is checked for the correct HTTP format. Second, the entire URL has to be less than twenty characters since the entire idea behind ShortLink is to provide a short link to the client. If these requirements are not met, the endpoint will raise HTTP exceptions for the user.

Before updating the current domain prefix in the ShortLink settings, a slash is added and the HTTP scheme is always changed to HTTPS.

## Tests

The functionality of each API endpoint is thoroughly tested. The automated tests can be performed by executing `pytest` within the test folder:

```bash
cd tests && pytest
```

In total, it contains 16 tests and checks the functionality for the helper functions that validate and generate the encoding as well as for all API endpoints.

## Backlog

Here, some ideas for further development are collected:

- Integration of a database

- Add _tracking functionality_ to be able to return the count of clicked URLs to a super-user

- Implement API settings for more customized encodings

- Add API Authentication to differentiate between users

- Add CORS

- ...

---

Lukas Schöbel

hello@lukasschoebel.com

+49 157 52979101
