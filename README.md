## Hotkeys PHAL plugin

plugin for Keyboard hotkeys, define key combos to trigger bus events

## Install

you need to add your user to the `tty` and `input` groups

`sudo usermod -a -G tty,input $USER`

more info in [this issue](https://github.com/boppreh/keyboard/issues/312)

Then install the plugin

`pip install ovos-PHAL-plugin-hotkeys`

## Configuration

There are a number of ways configuration can happen.

### Autoconfig

This plugin comes with a few pre-configured devices located in the `config` directory.  If one of those devices is found, it will automatically be configured to use.

When there is no configuration given, this will look for the file `/etc/OpenVoiceOS/i2c_platform` which is created when using [ovos-i2csound](https://github.com/OpenVoiceOS/ovos-i2csound).

If `ovos-i2csound` is not being used, or you would like to override the results, a file can be defined in config.

You can add any config for any device that you may want to use by creating a file in one of two places

`/usr/local/share/OpenVoiceOS/hotkey_devices`
`~/.local/share/OpenVoiceOS/hotkey_devices`

#### Config file format

Add any bus message + key combo under `"key_down"` and  `"key_up"`

You may want to react when a key is pressed, or when a key is released

A complete example based on events from a generic G20 USB remote

Create a file for your configuration.

`nano ~/.local/share/OpenVoiceOS/hotkey_devices/G20_config.json`

Add valid json to the file

```json
"key_down": {
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
```

**NOTE** you do not need to add the plugin name when you create a separate file.

### User defined config in `~/.config/mycroft/mycroft.conf`

When adding to your mycroft.conf file, you need to make sure it is using the correct plugin.

A complete example based on events from a generic G20 USB remote

```json
 "PHAL": {
    "ovos-PHAL-plugin-hotkeys": {
        "debug": false,
        "key_down": {
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

If there is configuration in `mycroft.conf`, autoconfigure will not be used even if `"autoconfigure": true`.

```json
"PHAL": {
    "ovos-PHAL-plugin-hotkeys": {
        "autoconfigure": true,
        "debug": false,
        "key_down": {
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

For the Mark2 drivers you can find the emitted key events in  the [sj201-buttons-overlay.dts](https://github.com/OpenVoiceOS/VocalFusionDriver/blob/main/sj201-buttons-overlay.dts#L18) file

```json
 "PHAL": {
    "ovos-PHAL-plugin-hotkeys": {
        "key_down": {
            "mycroft.mic.listen": 582,
            "mycroft.mic.mute": 248,
            "mycroft.volume.increase": 115,
            "mycroft.volume.decrease": 114
       },
        "key_up": {
            "mycroft.mic.unmute": 248
       }
    }
}
```
> gpios 22-24 are the momentary switches; 25 is MuteMic SW connected to 3.3v or GND


## Finding keys

A list of valid key scancodes can be found [here](http://wiki.linuxcnc.org/cgi-bin/wiki.pl?Scancodes)

Some key presses might not be correctly detected and show up as "unknown", some devices might also emit the wrong keycodes

In this case you can enable the `debug` flag in the config, then check the logs

```commandline
DEBUG {"event_type": "down", "scan_code": 57, "name": "space", "time": 1711050758.24674, "device": "/dev/input/event4", "is_keypad": false, "modifiers": []}
DEBUG {"event_type": "down", "scan_code": 24, "name": "o", "time": 1711050758.510758, "device": "/dev/input/event4", "is_keypad": false, "modifiers": []}
DEBUG {"event_type": "down", "scan_code": 115, "name": "unknown", "time": 1711050858.940323, "device": "/dev/input/event3", "is_keypad": false, "modifiers": []}
DEBUG {"event_type": "down", "scan_code": 114, "name": "unknown", "time": 1711050864.262953, "device": "/dev/input/event3", "is_keypad": false, "modifiers": []}
```

You can then use the `scan_code` integer in your config instead of `name` string

## Credits

- keyboard handling taken from [boppreh/keyboard](https://github.com/boppreh/keyboard) package
