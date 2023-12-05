# GeoIP Latitude and Longitude lookup

This program demonstrates interacting with a simple REST API (ipstack.com),
and allows the user to retrieve the latitude and longitude associated with a
particular IPv4 or IPv6 address. Supported output formats are human-readable
(the default) or JSON.

As this is merely a demonstration, it is rudimentary and carries security
risks. See the Security Concerns section below for details.

## Local Installation

You will need Python 3.8 or later. Create a virtualenv and upgrade the
packaging tools:

    python3 -m venv venv
    venv/bin/python -m pip install --upgrade pip setuptools wheel

Install the requests library:

    venv/bin/python -m pip install requests

You can then run the program with:

    venv/bin/python ipstack_latlong.py --help


## Running with Docker

The program is packaged as a Docker image:

    docker run -i --rm cdunklau/ipstack-cli --help


## Usage

You must sign up for an account with ipstack.com to receive the required API
access key. The [free account tier](https://ipstack.com/signup/free)
has no cost, but offers only a limited number of lookups per month, and is
less secure as it does not support encryption via HTTPS.

If you use the free tier, you need to specify the `--base-url` as
`http://api.ipstack.com` (note http, not https).


    usage: ipstack_latlong.py [-h] --access-key ACCESS_KEY [--base-url BASE_URL]
			      [--output {plain,json}]
			      IP_ADDR

    Look up an IP address's latitude and longitude using the IPStack API.

    positional arguments:
      IP_ADDR               IPv4 or IPv6 address to look up.

    optional arguments:
      -h, --help            show this help message and exit
      --access-key ACCESS_KEY, -k ACCESS_KEY
			    API access key. Required. (default: None)
      --base-url BASE_URL, -u BASE_URL
			    Base URL for the IPStack API. (default:
			    https://api.ipstack.com)
      --output {plain,json}, -o {plain,json}
			    Output format. (default: plain)

## Security Concerns

The program receives the API access key through command line arguments. This
exposes the key in shell history and system process list (e.g. the output of
the `ps` command). To mitigate this, the program should be updated to instead
pull the access key from a config file and/or environment variables.

The program sends the API access key in a GET request through query string
variables in the URL. Since GET requests may be cached and the free tier only
supports plaintext HTTP, this may expose the API access key to an attacker.
As the ipstack.com API does not appear to support other authentication
methods, the only feasible way to mitigate this threat is to use the paid
subscription and use HTTPS.

The free tier does not support encrypted HTTP (HTTPS), so the API access key
may be exposed to an attacker in general, even if the ipstack.com API were
updated to support other authentication methods.
