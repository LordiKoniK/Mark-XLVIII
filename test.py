from tuya import client
from tuya.devices import DEVICES

client.command(
    DEVICES["lightbar"]["id"],
    "switch_white",
    False
)

print("Success!")