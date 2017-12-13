from base import TestBase
import datetime


class TestRoot(TestBase):
    """
    Expand this to test the api you have created.

    """

    def test_index(self):
        resp = self.app.get('/')
        assert resp.status_int == 200
        assert 'Welcome to Crunch.' in resp

    def test_login(self):
        resp = self.app.get('/login')
        assert resp.status_int == 200
        assert 'form' in resp
        login_form = resp.form
        login_form['fname'], login_form['lname'], login_form['password'] = 'The', 'Admin', '123456'
        resp = login_form.submit('submit')
        assert resp.status_int == 200
        assert resp.cookies["user_id"] == "985076770cb0173a5b015c32"

    def test_logout(self):
        resp = self.app.get('/logout')
        assert not resp.cookies.get("user_id")  # cookie should be already gone

    def test_users(self):
        self.test_logout()  # making sure that user is logged out
        resp = self.app.get('/users')
        assert resp.status_int == 200
        assert 'form' in resp  # /users without logging in should redirect to login page with form
        self.test_login()  # using test_login to login and set the session/cookie
        resp = self.app.get('/users')  # this time, app will let the client because he/she is already logged in
        assert resp.json.get("users")  # TODO: just checking is key "users" exists, should be more comprehensive
        resp = self.app.post('/users', {"longitude": 360.00,
                                        "latitude": 360.00,
                                        "registered": datetime.datetime.now().strftime("%A, %B %d, %Y %I:%M %p"),
                                        "email": 'tester@gmail.com',
                                        "company": "Testing Company",
                                        "last_name": "Testory",
                                        "first_name": "Testor",
                                        "password": "test",
                                        })
        assert "successfully added" in resp  # TODO: simple assertion, doesn't check data-validity...should be improved
        self.test_logout()
