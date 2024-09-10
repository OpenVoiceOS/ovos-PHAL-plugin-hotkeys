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
from ovos_bus_client.message import Message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.log import LOG

import ovos_phal_plugin_hotkeys.keyboard as keyboard


class HotKeysPlugin(PHALPlugin):
    """Keyboard hotkeys, define key combo to trigger listening"""

    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-hotkeys", config=config)
        self.register_callbacks()

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

