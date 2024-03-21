## Hotkeys PHAL plugin

plugin for Keyboard hotkeys, define key combos to trigger bus events

## Install

the `keyboard` package needs root to run, instead you should use this [maintained fork](https://github.com/Quentium-Forks/keyboard) and give permissions to your user instead

`pip install git+https://github.com/Quentium-Forks/keyboard`

add user to the `tty` and `input` groups

`sudo usermod -a -G tty,input $USER`

more info in [this issue](https://github.com/boppreh/keyboard/issues/312)

Finally, install the plugin

`pip install ovos-PHAL-plugin-hotkeys`

## Configuration

Add any bus message + key combo under `"mappings"`

For the Mark2 drivers you can find the emitted key events in  the [sj201-buttons-overlay.dts](https://github.com/OpenVoiceOS/VocalFusionDriver/blob/main/sj201-buttons-overlay.dts#L18) file

```json
 "PHAL": {
    "ovos-PHAL-plugin-hotkeys": {
        "mappings": {
            "mycroft.mic.listen": 143,
            "mycroft.mic.mute.toggle": 113,
            "mycroft.volume.increase": 115,
            "mycroft.volume.decrease": 114
       }
    }
}
```
> NOTE: see [VocalFusionDriver/issues/6](https://github.com/OpenVoiceOS/VocalFusionDriver/issues/6) about moving from `143` to `582`

A complete example based on events from a generic G20 USB remote

```json
 "PHAL": {
    "ovos-PHAL-plugin-hotkeys": {
        "debug": false,
        "mappings": {
            "mycroft.mic.listen": 582,
            "mycroft.mic.mute.toggle": 190,
            "mycroft.mic.mute": "shift+m",
            "mycroft.mic.unmute": "shift+u",
            "mycroft.volume.increase": 115,
            "mycroft.volume.decrease": 114,
            "mycroft.volume.mute.toggle": 113,
            "mycroft.volume.mute": "ctrl+shift+m",
            "mycroft.volume.unmute": "ctrl+shift+u",
            "homescreen.manager.show_active": 144,
            "ovos.common_play.play_pause": 164
       }
    }
}
```

## Finding keys

Some key presses might not be correctly detected and show up as "unknown"

In this case you can enable the `debug` flag in the config, then check the logs

```commandline
DEBUG {"event_type": "down", "scan_code": 57, "name": "space", "time": 1711050758.24674, "device": "/dev/input/event4", "is_keypad": false, "modifiers": []}
DEBUG {"event_type": "down", "scan_code": 24, "name": "o", "time": 1711050758.510758, "device": "/dev/input/event4", "is_keypad": false, "modifiers": []}
DEBUG {"event_type": "down", "scan_code": 115, "name": "unknown", "time": 1711050858.940323, "device": "/dev/input/event3", "is_keypad": false, "modifiers": []}
DEBUG {"event_type": "down", "scan_code": 114, "name": "unknown", "time": 1711050864.262953, "device": "/dev/input/event3", "is_keypad": false, "modifiers": []}
```

You can then use the `scan_code` integer in your config instead of `name` string