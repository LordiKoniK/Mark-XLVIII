"""
device.py

Represents a single Tuya device.

The rest of JARVIS should never need to know
device IDs or DP codes.
"""

from __future__ import annotations


class TuyaDevice:

    def __init__(self, client, config: dict):
        self.client = client
        self.config = config

    @property
    def id(self):
        return self.config["id"]

    @property
    def name(self):
        return self.config["name"]

    @property
    def aliases(self):
        return self.config.get("aliases", [])

    @property
    def dp(self):
        return self.config["dp"]
    
    # -----------------------------------------------------
    
    @staticmethod
    def hsv_to_lightbar_hex(h: int, s: int, v: int) -> str:
        """
        Convert HSV values into the 12-character format expected by the
        monitor light bar.

        Example:
            h=230, s=1000, v=1000
            -> "00e603e803e8"
        """

        h = max(0, min(360, int(h)))
        s = max(0, min(1000, int(s)))
        v = max(0, min(1000, int(v)))

        return f"{h:04x}{s:04x}{v:04x}"
    
    # -----------------------------------------------------
    
    def _prepare_value(self, function: str, value):
        """
        Convert values into the format expected by this device.
        """

        # Light bar RGB expects a 12-character HSV hex string
        if (
            self.config.get("type") == "lightbar"
            and function == "colour"
            and isinstance(value, dict)
        ):
            return TuyaDevice.hsv_to_lightbar_hex(
                value["h"],
                value["s"],
                value["v"]
            )

        return value

    # -----------------------------------------------------

    def send(self, function: str, value):

        if function not in self.dp:
            raise ValueError(
                f"{function} is not supported by {self.name}"
            )

        value = self._prepare_value(function, value)

        return self.client.command(
            self.id,
            self.dp[function],
            value
        )

    # -----------------------------------------------------

    def send_many(self, commands):

        payload = []

        for function, value in commands:
            
            if function not in self.dp:
                raise ValueError(
                    f"{function} is not supported by {self.name}"
                )

            value = self._prepare_value(function, value)
            
            payload.append({
                "code": self.dp[function],
                "value": value
            })

        return self.client.commands(
            self.id,
            payload
        )

    # -----------------------------------------------------

    def on(self, section=None):
        if self.config.get("type") == "lightbar":
            dp = "rgb_power" if section == "rgb" else "white_power"
            return self.send(dp, True)

        return self.send("power", True)


    def off(self, section=None):
        if self.config.get("type") == "lightbar":
            dp = "rgb_power" if section == "rgb" else "white_power"
            return self.send(dp, False)

        return self.send("power", False)

    # -----------------------------------------------------

    def brightness(self, value):
        return self.send(
            "brightness",
            value
        )

    def temperature(self, value):
        return self.send(
            "temperature",
            value
        )

    def colour(self, value):
        return self.send(
            "colour",
            value
        )
        
    # -----------------------------------------------------

    def white_on(self):
        return self.send(
            "white_power",
            True
        )

    def white_off(self):
        return self.send(
            "white_power",
            False
        )

    # -----------------------------------------------------

    def rgb_on(self):
        return self.send(
            "rgb_power",
            True
        )

    def rgb_off(self):

        return self.send(
            "rgb_power",
            False
        )

    # -----------------------------------------------------

    def __repr__(self):

        return f"<TuyaDevice {self.name}>"