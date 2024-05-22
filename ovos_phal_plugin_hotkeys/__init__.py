# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json
from json.decoder import JSONDecodeError
from os import walk
from os.path import exists, join, basename, dirname

from ovos_bus_client.message import Message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.log import LOG
from ovos_utils.xdg_utils import XDG_DATA_DIRS, XDG_DATA_HOME

# TODO: Update ovos-PHAL to differentiate sj201 v6/v10
# Currently, it only detects v6
from ovos_PHAL.detection import is_respeaker_2mic, is_mycroft_sj201

from ovos_plugin_manager.templates.phal import PHALValidator

import ovos_phal_plugin_hotkeys.keyboard as keyboard


def get_preconfigured_devices():
    local_config = f"{dirname(__file__)}/config"
    device_dir = "OpenVoiceOS/hotkey_devices"
    devices = []
    for (p, d, f) in walk(local_config):
        for filename in f:
            devices.append(f"{p}/{filename}")
    for directory in XDG_DATA_DIRS:
        if exists(f"{directory}/{device_dir}"):
            for (p, d, f) in walk(f"{directory}/{device_dir}"):
                for filename in f:
                    devices.append(f"{p}/{filename}")
    if exists(f"{XDG_DATA_HOME}/{device_dir}"):
        for (p, d, f) in walk(f"{XDG_DATA_HOME}/{device_dir}"):
            for filename in f:
                devices.append(join(p, filename))
    LOG.debug(f"devices found {devices}")
    return devices


# File is defined in ovos-i2csound
# https://github.com/OpenVoiceOS/ovos-i2csound/blob/dev/ovos-i2csound#L76
I2C_PLATFORM_FILE = "/etc/OpenVoiceOS/i2c_platform"


class HotKeysPluginValidator(PHALValidator):
    @staticmethod
    def validate(config=None):
        # If the user enabled the plugin no need to go further
        if config.get("enabled"):
            LOG.debug("user enabled")
            return True
        # This plugin needs configuration to work.  If there is none, no need to load
        if "key_up" in config or "key_down" in config:
            # User has predefined settings.
            LOG.debug("User manually defined a configuration")
            return True
        # Do a direct hardware check
        if is_mycroft_sj201() or is_respeaker_2mic():
            LOG.debug("Direct hardware detection")
            return True
        LOG.debug("no validation")
        return False


class HotKeysPlugin(PHALPlugin):
    """Keyboard hotkeys, define key combo to trigger listening"""
    validator = HotKeysPluginValidator

    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-hotkeys", config=config)
        self.devices = get_preconfigured_devices() or []
        # Check for existing configuration of 'key_up' and 'key_down'
        if "key_up" in self.config or "key_down" in self.config:
            # User has predefined settings.
            LOG.debug("User manually defined a configuration")
            if self.config.get("autoconfigure"):
                # User wants to use personal settings
                LOG.warning(
                    "ignoring automatic configuration, user defined it's own mycroft.conf")
        elif self.config.get("autoconfigure", True):
            LOG.debug("Attempting to auto configure plugin")
            self._autoconfig()
        else:
            # No configuration given and auto config disabled by user in mycroft.conf
            raise ValueError(
                "no configuration given. Please configure the plugin in mycroft.conf")

        self.register_callbacks()

    def _autoconfig(self):
        def get_device_config(device):
            for filename in self.devices:
                if basename(filename).split(".")[0].lower() == device.lower():
                    with open(filename) as config:
                        try:
                            device = json.load(config)
                            self.add_config(device)
                        except JSONDecodeError:
                            LOG.error(f"Config for {device} is not valid")
                    break
        # Check for a user defined device
        if self.config.get("user_device"):
            get_device_config(self.config.get("user_device"))
        # Check for file i2csound created
        # Make sure the file exists
        elif exists(I2C_PLATFORM_FILE):
            with open(I2C_PLATFORM_FILE) as config:
                i2c_platform = config.readline().strip()
                get_device_config(i2c_platform)
                # Check direct hardware detection
        elif is_mycroft_sj201:
            for device in self.devices:
                if "sj201v6" in device.lower():
                    get_device_config(device)
        elif is_respeaker_2mic:
            for device in self.devices:
                if "wm8960" in device.lower():
                    get_device_config(device)
        else:
            LOG.error("No valid configuration available")
            raise Exception("No valid configuration")

    def add_config(self, config):
        for k, v in config.items():
            if k == "key_down":
                self.config["key_down"] = {}
                for kd, kdv in v.items():
                    self.config["key_down"][kd] = kdv
            if k == "key_up":
                self.config["key_up"] = {}
                for ku, kuv in v.items():
                    self.config["key_up"][ku] = kuv
            else:
                self.config[k] = v

    def register_callbacks(self):
        """combos are registered independently
        NOTE: same combo can only have 1 callback (up or down)"""
        for msg_type, key in self.config.get("key_down", {}).items():
            if isinstance(key, int):
                continue

            def do_emit(k=key, m=msg_type):
                LOG.info(f"hotkey down {k} -> {m}")
                self.bus.emit(Message(m))

            keyboard.add_hotkey(key, do_emit)

        for msg_type, key in self.config.get("key_up", {}).items():
            if isinstance(key, int):
                continue

            def do_emit(k=key, m=msg_type):
                LOG.info(f"hotkey up {k} -> {m}")
                self.bus.emit(Message(m))

            keyboard.add_hotkey(key, do_emit, trigger_on_release=True)

    def run(self):
        self._running = True

        while self._running:
            # Wait for the next event.
            event = keyboard.read_event()
            ev = json.loads(event.to_json())
            scan_code = ev["scan_code"]

            if event.event_type == keyboard.KEY_DOWN:
                for msg_type, k in self.config.get("key_down", {}).items():
                    if scan_code == k:
                        LOG.info(f"hotkey down {scan_code} -> {msg_type}")
                        self.bus.emit(Message(msg_type))

            if event.event_type == keyboard.KEY_UP:
                for msg_type, k in self.config.get("key_up", {}).items():
                    if scan_code == k:
                        LOG.info(f"hotkey up {scan_code} -> {msg_type}")
                        self.bus.emit(Message(msg_type))

            if self.config.get("debug"):
                LOG.info(f"{event.event_type} - {ev}")

    def shutdown(self):
        keyboard.unhook_all_hotkeys()
        super().shutdown()


if __name__ == "__main__":
    # debug
    from ovos_utils import wait_for_exit_signal
    from ovos_utils.messagebus import FakeBus

    p = HotKeysPlugin(FakeBus(), {"debug": True}
                      #            "key_down": {"test": 57, "test2": 28},
                      #            "key_up": {"test": 57, "test2": 28}}
                      )

    wait_for_exit_signal()