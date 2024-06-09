# write your first unittest!
import unittest
from ovos_plugin_manager.phal import find_phal_plugins


class TestPlugin(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.skill_id = "ovos-PHAL-plugin-hotkeys"

    def test_find_plugin(self):
        plugins = find_phal_plugins()
        self.assertIn(self.skill_id, list(plugins))
