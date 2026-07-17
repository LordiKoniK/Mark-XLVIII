"""
devices.py

Defines every smart device known to JARVIS.

IDs live inside .env.
Everything else is metadata describing the device.
"""

import os
from dotenv import load_dotenv

load_dotenv()

DEVICES = {

    # ==========================================================
    # Monitor Light Bar
    # ==========================================================

    "lightbar": {
        "id": os.getenv("TUYA_LIGHTBAR"),
        "name": "Monitor Light Bar",
        "type": "lightbar",
        "group": "desk",

        "aliases": [
            "lightbar",
            "light bar",
            "monitor light",
            "monitor lamp",
            "desk light",
            "desk lamp",
        ],

        "dp": {
            # White lamp
            "white_power": "switch_white",
            "brightness": "bright_value",
            "temperature": "temp_value",

            # RGB strip
            "rgb_power": "switch_led",
            "colour": "colour_data",

            # Shared
            "mode": "work_mode",
        }
    },

    # ==========================================================
    # Left Room Bulb
    # ==========================================================

    "room_left": {

        "id": os.getenv("TUYA_ROOM_LIGHT_LEFT"),
        "name": "Left Room Light",
        "type": "bulb",
        "group": "room",

        "aliases": [
            "left light",
            "left bulb",
            "left room light",
            "left lamp",
        ],

        "dp": {
            "power": "switch_led",
            "mode": "work_mode",
            "brightness": "bright_value_v2",
            "temperature": "temp_value_v2",
            "colour": "colour_data_v2",

            # Future support
            "scene": "scene_data_v2",
            "music": "music_data",
            "control": "control_data",
            "countdown": "countdown_1",

            "sleep_mode": "sleep_mode",
            "wakeup_mode": "wakeup_mode",
            "rhythm_mode": "rhythm_mode",

            "power_memory": "power_memory",
            "do_not_disturb": "do_not_disturb",

            "cycle_timer": "cycle_timing",
            "random_timer": "random_timing",
        }
    },

    # ==========================================================
    # Right Room Bulb
    # ==========================================================

    "room_right": {
        "id": os.getenv("TUYA_ROOM_LIGHT_RIGHT"),
        "name": "Right Room Light",
        "type": "bulb",
        "group": "room",

        "aliases": [
            "right light",
            "right bulb",
            "right room light",
            "right lamp",
        ],

        "dp": {
            "power": "switch_led",
            "mode": "work_mode",
            "brightness": "bright_value_v2",
            "temperature": "temp_value_v2",
            "colour": "colour_data_v2",

            # Future support
            "scene": "scene_data_v2",
            "music": "music_data",
            "control": "control_data",
            "countdown": "countdown_1",

            "sleep_mode": "sleep_mode",
            "wakeup_mode": "wakeup_mode",
            "rhythm_mode": "rhythm_mode",

            "power_memory": "power_memory",
            "do_not_disturb": "do_not_disturb",

            "cycle_timer": "cycle_timing",
            "random_timer": "random_timing",
        }
    }
}