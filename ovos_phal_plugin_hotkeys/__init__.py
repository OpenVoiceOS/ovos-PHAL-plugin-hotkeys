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
from os.path import exists

from ovos_bus_client.message import Message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.log import LOG

import ovos_phal_plugin_hotkeys.keyboard as keyboard
from ovos_phal_plugin_hotkeys.boards import WM8960, SJ201

# Add boards from ovos-i2csound here, or custom boards from boards.py
# Be sure to add the import if getting from boards.py
KNOWN_BOARDS = ["wm8960", "SJ201"]


class HotKeysPlugin(PHALPlugin):
    """Keyboard hotkeys, define key combo to trigger listening"""

    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-hotkeys", config=config)
        # Assign a value to 'autoconfig_file'
        # Can either contain a single line with values from 'ovos-i2csound',
        # Or can be valid json with 'key_up' and or 'key_down'
        self.autoconfig_file = self.config.get(
            "autoconfig_file", "/home/ovos/.config/mycroft/i2c_platform")
        # Check for existing configuration of 'key_up' and 'key_down'
        if "key_up" in self.config or "key_down" in self.config:
            # User has predefined settings.  Check for override
            if self.config.get("autoconfigure"):
                # User wants to override personal settings
                self.autoconfig(self.autoconfig_file)
        else:
            # No configuration given, try to autodetect
            LOG.debug(
                f"no configuration given.  Trying to autodetect from {self.autoconfig_file}")
            self.autoconfig(self.autoconfig_file)

        self.register_callbacks()

    def autoconfig(self, config_file):
        # Make sure the file exists
        if exists(config_file):
            # Check for json
            try:
                with open(config_file) as config:
                    LOG.debug(f"loading json from {config_file}")
                    new_config = json.load(new_config)
                    self.load_config(new_config, json=True)
            except JSONDecodeError:
                with open(config_file, "r") as config:
                    LOG.debug(f"file {config_file} is not json")
                    platform = config.readline().strip()
                    if platform in KNOWN_BOARDS:
                        LOG.debug(f"loading config for {platform}")
                        self.load_config(platform)
        else:
            LOG.debug(f"config file {config_file} does not exist")

    def load_config(self, new_config, json=False):
        def add_config(config):
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
        # If config not a dict, it is coming from boards.py
        if not json:
            # Check for the known boards
            if new_config == "wm8960":
                add_config(WM8960)
            if new_config == "SJ201":
                add_config(SJ201)
        else:
            add_config(new_config)

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