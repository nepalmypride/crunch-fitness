import webtest
import cherrypy
from cr.api.server import Root
from cr.db.store import global_settings as settings
from cr.db.loader import load_data

def get_app():
    cherrypy.tree.mount(Root(settings), '/')
    return cherrypy.tree

_app = None
def app():
    global _app
    settings.update({"url": "mongodb://localhost:27017/test_crunch_fitness"})
    if _app is None:
        _app = webtest.TestApp(get_app())
        load_data(settings, clear=True)
    return _app


class TestBase(object):

    def setup(self):
        self.app = app()
