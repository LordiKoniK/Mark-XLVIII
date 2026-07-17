import hashlib
import hmac
import json
import time
import uuid
from urllib.parse import urlencode

import requests


EMPTY_BODY_SHA256 = (
    "e3b0c44298fc1c149afbf4c8996fb924"
    "27ae41e4649b934ca495991b7852b855"
)


class TuyaRequest:

    def __init__(self, client):
        self.client = client

    # ---------------------------------------------------------

    @staticmethod
    def timestamp():
        return str(int(time.time() * 1000))

    # ---------------------------------------------------------

    @staticmethod
    def nonce():
        return uuid.uuid4().hex

    # ---------------------------------------------------------

    @staticmethod
    def canonical_json(body):

        if body is None:
            return ""

        return json.dumps(
            body,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    # ---------------------------------------------------------

    @staticmethod
    def sha256(text: str):

        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    # ---------------------------------------------------------

    def content_hash(self, body):

        if body is None:
            return EMPTY_BODY_SHA256

        return self.sha256(
            self.canonical_json(body)
        )

    # ---------------------------------------------------------

    @staticmethod
    def canonical_url(path, params=None):

        if not params:
            return path

        query = urlencode(
            sorted(params.items())
        )

        return f"{path}?{query}"

    # ---------------------------------------------------------

    @staticmethod
    def canonical_headers(headers=None):

        """
        Signature-Headers support.

        We're not using signed custom headers yet,
        but the SDK supports them.
        """

        if not headers:
            return "", ""

        keys = sorted(headers.keys())

        signature_headers = ":".join(keys)

        header_block = ""

        for key in keys:
            header_block += f"{key}:{headers[key]}\n"

        return signature_headers, header_block

    # ---------------------------------------------------------

    def string_to_sign(
        self,
        method,
        path,
        params=None,
        body=None,
        signed_headers=None,
    ):

        _, header_block = self.canonical_headers(
            signed_headers
        )

        return (
            method.upper()
            + "\n"
            + self.content_hash(body)
            + "\n"
            + header_block
            + "\n"
            + self.canonical_url(path, params)
        )

    # ---------------------------------------------------------

    def sign(
        self,
        method,
        path,
        params=None,
        body=None,
        token=None,
        signed_headers=None,
    ):

        timestamp = self.timestamp()
        nonce = self.nonce()

        sts = self.string_to_sign(
            method,
            path,
            params,
            body,
            signed_headers,
        )

        sign_str = self.client.access_id

        if token:
            sign_str += token

        sign_str += timestamp
        sign_str += nonce
        sign_str += sts

        signature = hmac.new(
            self.client.access_secret.encode(),
            sign_str.encode(),
            hashlib.sha256,
        ).hexdigest().upper()

        return signature, timestamp, nonce

    # ---------------------------------------------------------

    def request(
        self,
        method,
        path,
        *,
        params=None,
        body=None,
        token_required=True,
        signed_headers=None,
    ):

        token = None

        if token_required:
            token = self.client.ensure_token()

        sign, timestamp, nonce = self.sign(
            method,
            path,
            params=params,
            body=body,
            token=token,
            signed_headers=signed_headers,
        )

        headers = {
            "client_id": self.client.access_id,
            "sign": sign,
            "t": timestamp,
            "nonce": nonce,
            "sign_method": "HMAC-SHA256",
            "Content-Type": "application/json",
        }

        if token:
            headers["access_token"] = token

        if signed_headers:
            headers["Signature-Headers"] = (
                ":".join(sorted(signed_headers.keys()))
            )

            headers.update(signed_headers)

        url = (
            self.client.endpoint
            + self.canonical_url(path, params)
        )

        body_json = self.canonical_json(body)
        
        print("\n========== TUYA REQUEST ==========")
        print("URL:", url)
        print("Method:", method)
        print("Timestamp:", timestamp)
        print("Nonce:", nonce)
        print("Body:", body_json)
        print("Content SHA:", self.content_hash(body))
        print("Signature:", sign)
        print("==================================\n")

        response = requests.request(
            method,
            url,
            headers=headers,
            data=body_json if body else None,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("success"):

            # token expired

            if (
                data.get("code")
                in (1010, 1011, 1012)
                and token_required
            ):
                self.client.invalidate_token()

                return self.request(
                    method,
                    path,
                    params=params,
                    body=body,
                    token_required=True,
                    signed_headers=signed_headers,
                )

            raise RuntimeError(data)

        return data