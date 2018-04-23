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

    def add(self, view, route, url, *args, **kwargs):
        """
        Add routing for view.
        - view: view class or dotted url to it
        - route: name for the route
        - url - url pattern
        """
        self.pyramid.add_route(route, url, *args, **kwargs)

        self.add_view(view, route_name=route)

    def add_view(self, view, **kwargs):
        """
        Add view/view handler.
        - view: view class or dotted url to it
        """
        view = self.pyramid.maybe_dotted(view)

        for name in self.values_to_set:
            self.set_view_config(kwargs, view, name)

        self.pyramid.add_view(view, **kwargs)

    def set_view_config(self, kwargs, view, name):
        value = getattr(view, name, None)
        if value:
            kwargs[name] = value
