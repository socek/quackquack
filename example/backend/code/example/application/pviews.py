from sapp.plugins.pyramid.views import RestfulView


class SimpleView(RestfulView):
    def get(self):
        """
        List all active panels.
        """
        return {"hello": True}
