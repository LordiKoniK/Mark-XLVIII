"""
group.py

Represents a collection of Tuya devices.
"""

class DeviceGroup:

    def __init__(self, name, devices):
        self.name = name
        self.devices = devices

    def __iter__(self):
        return iter(self.devices)

    def __len__(self):
        return len(self.devices)

    # -----------------------------------------------------

    def on(self):
        for device in self.devices:
            try:
                device.on()
            except Exception:
                pass

    def off(self):
        for device in self.devices:
            try:
                device.off()
            except Exception:
                pass

    # -----------------------------------------------------

    def brightness(self, value):

        for device in self.devices:

            try:
                device.brightness(value)
            except Exception:
                pass

    # -----------------------------------------------------

    def temperature(self, value):

        for device in self.devices:

            try:
                device.temperature(value)
            except Exception:
                pass

    # -----------------------------------------------------

    def colour(self, value):

        for device in self.devices:

            try:
                device.colour(value)
            except Exception:
                pass

    # -----------------------------------------------------

    def send(self, function, value):

        for device in self.devices:

            try:
                device.send(function, value)
            except Exception:
                pass

    # -----------------------------------------------------

    def __repr__(self):
        return f"<DeviceGroup {self.name} ({len(self.devices)} devices)>"