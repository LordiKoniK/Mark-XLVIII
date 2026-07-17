"""
light_control.py

High-level lighting action for JARVIS.

This module translates natural language parameters into
Tuya SDK calls.

The SDK handles authentication, HTTP, signing and device IDs.
"""

from __future__ import annotations

import json

from tuya import client


# ==========================================================
# Named colours
# ==========================================================

COLOURS = {

    "red":       0,
    "orange":    30,
    "yellow":    60,
    "lime":      90,
    "green":     120,
    "cyan":      180,
    "blue":      240,
    "purple":    270,
    "magenta":   300,
    "pink":      330,

    "white":     None,
    "warm":      None,
    "warm white":None,
    "cool":      None,
    "cool white":None,

}


# ==========================================================
# Utility
# ==========================================================

def clamp(value, minimum, maximum):

    return max(minimum, min(maximum, value))


def pct_to_tuya(percent):

    return int(
        clamp(percent, 0, 100)
        * 10
    )


def parse_colour(name):

    if not name:
        raise ValueError("No colour supplied.")

    name = name.lower().strip()

    if name not in COLOURS:

        raise ValueError(
            f"Unknown colour '{name}'."
        )

    hue = COLOURS[name]

    if hue is None:
        return None

    return {

        "h": hue,
        "s": 1000,
        "v": 1000

    }


def find_target(name):

    if not name:
        raise ValueError("No light specified.")

    name = name.lower().strip()

    if name in (
        "room",
        "room lights",
        "bedroom",
        "bedroom lights"
    ):
        return client.group("room")

    if name in (
        "all",
        "everything",
        "all lights"
    ):
        return client.all_devices()

    return client.device(name)


# ==========================================================
# Primitive actions
# ==========================================================

def action_power(target, state, section=None):

    if state:
        target.on(section)
    else:
        target.off(section)

    return "Done."


def action_brightness(target, brightness):

    brightness = pct_to_tuya(int(brightness))

    target.brightness(
        brightness
    )

    return f"Brightness set to {brightness//10}%."


def action_temperature(target, temperature):

    value = pct_to_tuya(int(temperature))

    target.temperature(value)

    return "Colour temperature updated."


def action_colour(target, colour):

    colour = colour.lower()

    # White requests should switch mode.

    if colour in (
        "white",
        "warm",
        "warm white",
        "cool",
        "cool white"
    ):

        try:

            target.send(
                "mode",
                "white"
            )

        except Exception:
            pass

        return "White mode enabled."

    payload = parse_colour(
        colour
    )

    try:

        target.send(
            "mode",
            "colour"
        )

    except Exception:
        pass

    target.colour(
        payload
    )

    return f"Changed colour to {colour}."


# ==========================================================
# Light Bar Specialisation
# ==========================================================

def lightbar_action(device, section, action, value=None):

    section = (
        section or "white"
    ).lower()

    if section == "white":

        if action == "on":

            device.white_on()

            return "Desk light on."

        if action == "off":

            device.white_off()

            return "Desk light off."

        if action == "brightness":

            device.brightness(
                pct_to_tuya(
                    int(value)
                )
            )

            return "Desk light brightness updated."

        if action == "temperature":

            device.temperature(
                pct_to_tuya(
                    int(value)
                )
            )

            return "Desk light temperature updated."

    elif section in (
        "rgb",
        "backlight",
        "ambient"
    ):

        if action == "on":

            device.rgb_on()

            return "RGB backlight on."

        if action == "off":

            device.rgb_off()

            return "RGB backlight off."

        if action == "colour":

            payload = parse_colour(
                value
            )

            device.colour(
                payload
            )

            return "RGB colour updated."

        if action == "brightness":

            device.send(

                "brightness",

                pct_to_tuya(
                    int(value)
                )

            )

            return "RGB brightness updated."

    raise ValueError(
        "Unsupported light bar command."
    )


# ==========================================================
# Lookup table
# ==========================================================

ACTION_TABLE = {

    "on":
        action_power,

    "off":
        action_power,

    "brightness":
        action_brightness,

    "temperature":
        action_temperature,

    "colour":
        action_colour,

    "color":
        action_colour,

}

# ==========================================================
# Main dispatcher
# ==========================================================

def dispatch(parameters):

    device_name = (
        parameters.get("device")
        or parameters.get("target")
        or parameters.get("light")
    )

    action = (
        parameters.get("action")
        or ""
    ).lower()

    value = parameters.get("value")

    section = parameters.get("section")

    target = find_target(device_name)

    # --------------------------------------------------
    # Light Bar
    # --------------------------------------------------

    try:

        if hasattr(target, "config"):

            if target.config["type"] == "lightbar":

                if action in (
                    "on",
                    "off",
                    "brightness",
                    "temperature"
                ):

                    return lightbar_action(
                        target,
                        section or "white",
                        action,
                        value
                    )

                if action in (
                    "colour",
                    "color"
                ):

                    return lightbar_action(
                        target,
                        section or "rgb",
                        "colour",
                        value
                    )

    except Exception:
        pass

    # --------------------------------------------------
    # Generic devices/groups
    # --------------------------------------------------

    if action == "on":
        return action_power(target, True)

    if action == "off":
        return action_power(target, False)

    if action in (
        "brightness",
        "dim"
    ):
        return action_brightness(
            target,
            value
        )

    if action in (
        "temperature",
        "temp"
    ):
        return action_temperature(
            target,
            value
        )

    if action in (
        "colour",
        "color"
    ):
        return action_colour(
            target,
            value
        )

    raise ValueError(
        f"Unsupported action '{action}'."
    )


# ==========================================================
# Public Action
# ==========================================================

def light_control(
    parameters,
    response=None,
    player=None
):

    try:

        result = dispatch(parameters)

        return result

    except Exception as e:

        return f"Lighting error: {e}"