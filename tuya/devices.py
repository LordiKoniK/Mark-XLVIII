import os
from dotenv import load_dotenv

load_dotenv()

DEVICES = {

    "lightbar": {

        "id": os.getenv("TUYA_LIGHTBAR"),

        "type": "lightbar",

        "aliases": [
            "lightbar",
            "desk",
            "desk light",
            "monitor",
            "monitor light",
            "work light"
        ]
    },

    "room_left": {

        "id": os.getenv("TUYA_ROOM_LIGHT_LEFT"),

        "type": "bulb",

        "aliases": [
            "left",
            "left light",
            "left bulb"
        ]
    },

    "room_right": {

        "id": os.getenv("TUYA_ROOM_LIGHT_RIGHT"),

        "type": "bulb",

        "aliases": [
            "right",
            "right light",
            "right bulb"
        ]
    }

}