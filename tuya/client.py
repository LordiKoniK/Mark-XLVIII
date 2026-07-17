import os
import hashlib
import hmac
import time
import requests

from dotenv import load_dotenv

from .request import TuyaRequest

load_dotenv()


class TuyaClient:

    def __init__(self):
        self.access_id = os.getenv("TUYA_ACCESS_ID")
        self.access_secret = os.getenv("TUYA_ACCESS_SECRET")

        self.endpoint = os.getenv(
            "TUYA_API_ENDPOINT"
        ).rstrip("/")

        self.token = None
        self.expire_time = 0
        self.http = TuyaRequest(self)


    def _timestamp(self):
        return str(int(time.time() * 1000))
    
    
    def invalidate_token(self):
        self.token = None
        self.expire_time = 0


    def ensure_token(self):
        if self.token and time.time() < self.expire_time:
            return self.token

        data = self.http.request(
            "GET",
            "/v1.0/token",
            params={
                "grant_type": 1
            },
            token_required=False
        )

        result = data["result"]
        self.token = result["access_token"]
        self.expire_time = (
            time.time()
            + result["expire_time"]
            - 60
        )

        return self.token


    def command(
        self,
        device_id,
        code,
        value
    ):

        return self.http.request(
            "POST",
            f"/v1.0/iot-03/devices/{device_id}/commands",
            body={
                "commands": [
                    {
                        "code": code,
                        "value": value
                    }
                ]
            }
        )


    def commands(
        self,
        device_id,
        commands
    ):

        payload = {
            "commands": [
                {
                    "code": code,
                    "value": value
                }
                for code, value in commands
            ]
        }

        return self.http.request(
            "POST",
            f"/v1.0/iot-03/devices/{device_id}/commands",
            body=payload
        )