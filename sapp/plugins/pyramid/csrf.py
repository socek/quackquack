from sapp.plugin import Plugin


class CsrfPlugin(Plugin):
    """
    Add csrf mechanism to the pyramid app.
    """

    def __init__(self, policy_cls):
        self.policy_cls = policy_cls

    def start_plugin(self, configurator):
        self.settings = self.configurator.settings

    def start_pyramid(self, pyramid):
        pyramid.set_csrf_storage_policy(self.policy_cls())
        pyramid.set_default_csrf_options(
            require_csrf=True,
            token=self.settings['csrf_token_key'],
            header=self.settings['csrf_header_key'])
