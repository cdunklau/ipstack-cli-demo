"""
Given an IPv4 or IPv6 address, use the ipstack.com API to find the
address's associated latitude and longitude. Output in human-readable
or JSON formats.
"""
import argparse
import configparser
import dataclasses
import ipaddress
import json
import os
import sys
import urllib.parse
from typing import Tuple

import requests


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()

    try:
        validated_ip = validate_input_ip(args.ip)
    except ValueError as err:
        fatal(f"Invalid IP address {args.ip}: {err.args[0]}")

    # FIXME: Validate base_url and access_key.
    client = IPStackAPIClient(args.base_url, args.access_key)
    try:
        lat, long = client.request_latlong(validated_ip)
    except IPStackAPIClientError as err:
        fatal(f"Error querying IPStack API: {err.code} {err.type}: {err.info}")

    output = format_output(lat, long, args.output)

    print(output)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Look up an IP address's latitude and longitude using the IPStack API."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # FIXME: This is insecure (for simplicity's sake)! For a "real"
    #        application, we would instead pull the access key from a
    #        config file and/or from env vars.
    parser.add_argument(
        "--access-key",
        "-k",
        help="API access key. Required.",
        required=True,
    )
    parser.add_argument(
        "--base-url",
        "-u",
        help="Base URL for the IPStack API.",
        default="https://api.ipstack.com",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output format.",
        choices=["plain", "json"],
        default="plain",
    )
    parser.add_argument(
        "ip",
        metavar="IP_ADDR",
        help="IPv4 or IPv6 address to look up.",
    )
    return parser


def validate_input_ip(input_ip: str) -> str:
    ipobj = ipaddress.ip_address(input_ip.strip())
    return str(ipobj)


class IPStackAPIClient:
    def __init__(self, baseurl: str, access_key: str) -> None:
        self._baseurl = baseurl.rstrip("/") + "/"
        self._access_key = access_key
        self._session = requests.Session()

    def request_latlong(self, ip: str) -> Tuple[float, float]:
        url = self._baseurl + urllib.parse.quote(ip, safe="")
        res = self._session.get(
            url,
            params={
                # XXX: This is pretty insecure since GET requests might
                #      be cached... would rather put the API key in a
                #      header, but IPStack doesn't appear to support that.
                "access_key": self._access_key,
                "fields": "latitude,longitude",
            },
        )
        struct = res.json()
        if not struct.get("success", True):
            raise IPStackAPIClientError(struct["error"])
        return struct["latitude"], struct["longitude"]


class IPStackAPIClientError(Exception):
    def __init__(self, error_struct: dict) -> None:
        self.code = error_struct["code"]
        self.type = error_struct["type"]
        self.info = error_struct.get("info", "(no detail)")


def format_output(lat: float, long: float, output_format: str) -> str:
    if output_format == "json":
        return json.dumps({"latitude": lat, "longitude": long})

    if output_format == "plain":
        ns = "N" if lat >= 0 else "S"
        ew = "E" if long >= 0 else "W"
        return f"{abs(lat):g} {ns}, {abs(long):g} {ew}"

    raise ValueError(f"Unexpected output format: {output_format}")


def fatal(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
