class Routing(object):

    values_to_set = [
        'permission',
        'attr',
        'renderer',
        'http_cache',
        'wrapper',
        'decorator',
        'mapper',
        'context',
        'request_type',
        'request_method',
        'request_param',
        'match_param',
        'containment',
        'xhr',
        'accept',
        'header',
        'path_info',
        'check_csrf',
        'physical_path',
        'effective_principals',
        'custom_predicates',
        'predicates',
        'require_csrf',
    ]

    def __init__(self, pyramid):
        self.pyramid = pyramid

    def add(self, controller, route, url, *args, **kwargs):
        """
        Add routing for controller.
        - controller: controller class or dotted url to it
        - route: name for the route
        - url - url pattern
        """
        self.pyramid.add_route(route, url, *args, **kwargs)

        self.add_view(controller, route_name=route)

    def add_view(self, controller, **kwargs):
        """
        Add view/controller handler.
        - controller: controller class or dotted url to it
        """
        controller = self.pyramid.maybe_dotted(controller)

        for name in self.values_to_set:
            self.set_controller_config(kwargs, controller, name)

        self.pyramid.add_view(controller, **kwargs)

    def set_controller_config(self, kwargs, controller, name):
        value = getattr(controller, name, None)
        if value:
            kwargs[name] = value
