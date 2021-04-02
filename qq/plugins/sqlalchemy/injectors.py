from qq.context import Context
from qq.injector import ContextManagerInjector
from qq.injector import Injector
from qq.plugins.settings import SettingsPlugin


@Injector
def SAQuery(context: Context, key: str):
    return context[key]


class SACommand(ContextManagerInjector):
    def __init__(self, application, *args, **kwargs):
        super().__init__(application, *args, **kwargs)

    def __enter__(self, context, key, settings_key=SettingsPlugin.DEFAULT_KEY):
        return context[key]

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
        context,
        key,
        settings_key=SettingsPlugin.DEFAULT_KEY,
    ):
        is_tests = context[settings_key][key].get("tests", False)
        if is_tests:
            context[key].flush()
        elif not exc_type:
            context[key].commit()
