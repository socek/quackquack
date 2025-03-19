from typing import Any

from qq.context import Context
from qq.types import Application
from qq.types import Plugin as PluginType
from qq.types import PluginKey


class Plugin(PluginType):
    key: PluginKey = None

    def init(self, key: PluginKey):
        """
        Initialize the plugin during creation.
        key - key which is used in the Application.plugins dict for this plugin.
        """
        self.key = key

    def start(self, application: Application) -> Any:
        """
        This method will be called at the start of the Application. It will be
        called only once and the result will be set in the Application.globals.
        """

    def enter(self, context: Context) -> Any:
        """
        This method will be called when the Application will be used as context
        manager, but only when the plugin will be called. This is the enter phase.
        Result will be set in the Context dict with the self.key as the key in
        that dict.
        """

    def exit(self, context: Context, exc_type, exc_value, traceback):
        """
        This method will be called when the Application will be used as context
        manager. This is the exit phase.
        """
