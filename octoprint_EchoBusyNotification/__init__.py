# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import octoprint.printer
import requests

class EchoBusyNotificationPlugin(
        octoprint.plugin.StartupPlugin,
        octoprint.plugin.TemplatePlugin,
        octoprint.plugin.SettingsPlugin,
        octoprint.printer.PrinterCallback,
):
        def __init__(self):
            self.consecutive_busy = 0

	def on_after_startup(self):
            self._logger.info("EBNP active; makerkey: %s"% self._settings.get(["makerkey"]))
            self._printer.register_callback(self)

	def get_settings_defaults(self):
		return dict(
                        makerkey="",
                        trigger_name="octoprintEchoBusy",
                        busy_threshold=20
                )

	def get_template_configs(self):
		return [
			dict(type="settings", template="settings.jinja2", custom_bindings=False)
		]

        def log_consecutive_busy(self):
            self._logger.info("consecutive_busy: %s" % self.consecutive_busy)

        def on_printer_add_message(self, line):
            if "echo:busy" not in line:
                if self.consecutive_busy > 0:
                    self.log_consecutive_busy()
                self.consecutive_busy = 0
                return

            self.consecutive_busy += 1
            self.log_consecutive_busy()

            if self.consecutive_busy == self._settings.get_int(["busy_threshold"]):
                self._logger.info("sending IFTTT request")
                makerkey = self._settings.get(["makerkey"])
                trigger_name = self._settings.get(["trigger_name"])
                self._logger.info("makerkey %s; trigger_name: %s" % (makerkey, trigger_name))
                payload = { "value1": self.consecutive_busy }
                url = "https://maker.ifttt.com/trigger/%s/with/key/%s" % (trigger_name, makerkey)
                response = requests.post(url, json=payload)
                self._logger.info("response: %s" % response.text)


        def get_update_information(self):
            return dict(EchoBusyNotification=dict(
                displayName="EchoBusyNotificationPlugin",
                displayVersion=self._plugin_version,

                type="github_release",
                user="tjjfvi",
                repo="OctoPrint-EchoBusyNotification",
                current=self._plugin_version,

                pip="https://github.com/tjjfvi/OctoPrint-EchoBusyNotification/archive/{target_version}.zip"
            ))

__plugin_name__ = "EchoBusyNotification"
__plugin_implementation__ = EchoBusyNotificationPlugin()

