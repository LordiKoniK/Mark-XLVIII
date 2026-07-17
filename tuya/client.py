import os
import hashlib
import hmac
import time
import requests

from .devices import DEVICES
from .device import TuyaDevice
from .group import DeviceGroup

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
        
        
            # -----------------------------------------------------

    def device(self, name: str):

        """
        Find a device by key, display name or alias.
        """

        if not name:
            raise ValueError("No device specified.")

        name = name.lower().strip()

        for key, config in DEVICES.items():

            if key.lower() == name:
                return TuyaDevice(self, config)

            if config["name"].lower() == name:
                return TuyaDevice(self, config)

            aliases = [
                alias.lower()
                for alias in config.get("aliases", [])
            ]

            if name in aliases:
                return TuyaDevice(self, config)

        raise ValueError(f"Unknown device: {name}")

    # -----------------------------------------------------

    def group(self, group_name: str):

        """
        Returns every device belonging to a group.
        """

        group_name = group_name.lower().strip()
        
        group_name = group_name.lower().strip()

        GROUP_ALIASES = {
            "lights": "room",
            "room lights": "room",
            "bedroom": "room",
            "bedroom lights": "room",
            "all lights": "all",
            "everything": "all",
        }

        group_name = GROUP_ALIASES.get(group_name, group_name)

        devices = []

        for config in DEVICES.values():

            if config.get("group", "").lower() == group_name:

                devices.append(
                    TuyaDevice(self, config)
                )

        if not devices:
            raise ValueError(
                f"Unknown group: {group_name}"
            )
            
        if group_name == "all":
            return self.all_devices()

        return DeviceGroup(group_name, devices)

    # -----------------------------------------------------

    def all_devices(self):

        return DeviceGroup(

            "all",

            [
                TuyaDevice(self, config)
                for config in DEVICES.values()
            ]

        )