from base import TestBase


class TestRoot(TestBase):
    """
    Expand this to test the api you have created.

    """

    def test_index(self):
        resp = self.app.get('/')
        assert resp.status_int == 200
        assert 'Welcome to Crunch.' in resp