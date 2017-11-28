from sapp.plugin import Plugin


class AuthPlugin(Plugin):
    """
    Add authorization to the pyramid app.
    """

    def __init__(self, authn_policy_cls, authz_policy_cls, root_factory=None):
        self.authn_policy_cls = authn_policy_cls
        self.authz_policy_cls = authz_policy_cls
        self.root_factory = root_factory

    def start_plugin(self, configurator):
        self.settings = self.configurator.settings

    def start_pyramid(self, pyramid):
        authn_policy = self.authn_policy_cls(self.settings['secret'])
        authz_policy = self.authz_policy_cls()
        self.config.set_authentication_policy(authn_policy)
        self.config.set_authorization_policy(authz_policy)
        if self.root_factory:
            self.config.set_root_factory(self.root_factory)
