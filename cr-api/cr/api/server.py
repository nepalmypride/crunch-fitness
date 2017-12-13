import cherrypy
import json
import sys
import hashlib
import datetime
import itertools
import numpy as np
from cr.db.store import global_settings as settings, connect


class Root(object):

    def __init__(self, settings):
        self.db = connect(settings)

    def index(self):
        return 'Welcome to Crunch.  Please <a href="/login">login</a>.'
    index.exposed = True

    def users(self, **kwargs):
        """
        for GET: update this to return a json stream defining a listing of the users
        for POST: should add a new user to the users collection, with validation

        Only logged-in users should be able to connect.  If not logged in, should return the
        appropriate HTTP response.  Password information should not be revealed.

        note: Always return the appropriate response for the action requested.
        """

        try:
            user_id = cherrypy.session['user_id']
            this_user = self.db.users.find_one({"_id": user_id})
            if this_user:

                if cherrypy.request.method == "GET":
                    return json.dumps({'users': [{'first_name': u['first_name'],
                                                  'last_name': u['last_name'],
                                                  'company': u['company'],
                                                  'email': u['email']} for u in self.db.users.find()]})

                elif cherrypy.request.method == "POST":

                    post_data = cherrypy.request.body.params
                    password_hash = hashlib.sha1(post_data['password']).hexdigest()
                    fname, lname = post_data['first_name'], post_data['last_name']
                    latitude, longitude = post_data['latitude'], post_data['longitude']
                    company = post_data['company']
                    # Only email is validated to see if there is already user present with the email address
                    # In that case, redirected to the "/login" page (Not right...but directing anywhere.. :D)
                    email = post_data['email']
                    if email in [u["email"] for u in self.db.users.find()]:  # email should be unique for each user
                        return "Email you are trying to use already exists in the system. Try with new one..."
                    # Creating date of registered on the server than accepting value from client for authenticity
                    registered = datetime.datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
                    document = {"longitude": longitude,
                                "latitude": latitude,
                                "registered": registered,
                                "email": email,
                                "company": company,
                                "last_name": lname,
                                "first_name": fname,
                                "hash": password_hash,
                                }
                    self.db.users.insert_one(document)
                    return "{} {} is successfully added to the database".format(fname, lname)

        except KeyError:
            raise cherrypy.HTTPRedirect("/login")

    users.exposed = True

    @cherrypy.expose
    def newuser(self, **kwargs):
        if cherrypy.request.method == "GET":
            return """
                <html>
                    <head></head>
                    <body>
                        <h3>Please Login Using Below Form</h3>
                        <form method="post" action="/users">
                            First Name: <input type="text" name="first_name" /> <br/><br/>
                            Last Name: <input type="text" name="last_name" /> <br/><br/>
                            Latitude: <input type="number" step=any name="latitude" /><br/><br/>
                            Longitude: <input type="number" step=any name="longitude" /><br/><br/>
                            Company: <input type="text" name="company" /> <br/><br/>
                            Email: <input type="email" name="email" /> <br/><br/>
                            Password: <input type="password" name="password" /> <br/><br/>
                            <input type="submit" value="submit" />
                        </form>
                    </body>
                </html>
            """

    @cherrypy.expose
    def login(self, **kwargs):
        """
        a GET to this endpoint should provide the user login/logout capabilities

        a POST to this endpoint with credentials should set up persistence tokens for the user,
        allowing them to access other pages.

        hint: this is how the admin's password was generated:
              import hashlib; hashlib.sha1('123456').hexdigest()
        """

        if cherrypy.request.method == "POST":
            post_data = cherrypy.request.body.params
            password = hashlib.sha1(post_data['password']).hexdigest()
            this_user = self.db.users.find_one({'first_name': post_data['fname'],
                                                'last_name': post_data['lname'],
                                                'hash': password})
            if this_user:
                cherrypy.session['user_id'] = this_user['_id']
                return "<h3>You are the logged in</h3>"
            else:
                return """
                <html>
                    <head></head>
                    <body>
                        <h3>Please Login Using Below Form</h3>
                        <form method="post">
                            First Name: <input type="text" name="fname" /> <br/><br/>
                            Last Name: <input type="text" name="lname" /> <br/><br/>
                            Password: <input type="password" name="password" /> <br/><br/>
                            <input type="submit" value="submit" />
                        </form>
                        <h3 style="background-color:red"> Password do not match. Please try again </h3>
                    </body>
                </html>
                """

        if cherrypy.request.method == "GET":
            return """
            <html>
                <head></head>
                <body>
                    <h3>Please Login Using Below Form</h3>
                    <form method="post">
                        First Name: <input type="text" name="fname" /> <br/><br/>
                        Last Name: <input type="text" name="lname" /> <br/><br/>
                        Password: <input type="password" name="password" /> <br/><br/>
                        <input type="submit" value="submit" />
                    </form>
                </body>
            </html>
            """

    @cherrypy.expose
    def logout(self):
        """
        Should log the user out, rendering them incapable of accessing the users endpoint, and it
        should redirect the user to the login page.
        """
        cherrypy.session.delete()
        raise cherrypy.HTTPRedirect("/login")

    @cherrypy.expose
    def distances(self):
        """
        Each user has a lat/lon associated with them.  Using only numpy, determine the distance
        between each user pair, and provide the min/max/average/std as a json response.
        This should be GET only.

        Don't code, but explain how would you scale this to 1,000,000 users, considering users
        changing position every few minutes?

        THOUGHTS:

        If we have, for example, 1000000 users then every time one user changes the position, there will be 999,999
        pairs of positions that needs to be recalculated!
        A simple approach ( I might come up with more elegant and efficient one later :) )
        - A object representing each user and its position (latitude and longitude)- Object A
        - Another object storing each pair storing all possible (1000000)C(2) (1000000 choose 2) combination - Object B
        - Object A should store references for all object-Bs where object A is present
        - when position of object A changes, an update is sent to object B if A has B in its reference
        - with receive of the update, the relevant distance is recalculated and pertinent json can be returned

        """
        try:
            user_id = cherrypy.session['user_id']
            lat_and_long_list = [[np.radians(float(u["latitude"])),
                                  np.radians(float(u["longitude"]))] for u in self.db.users.find()]
            # list of all possible combination of two user's latitude and longitude
            all_combo = list(itertools.combinations(lat_and_long_list, 2))
            distance_list = []
            for each_pair in all_combo:
                lon1, lon2 = each_pair[0][1], each_pair[1][1]
                lat1, lat2 = each_pair[0][0], each_pair[1][0]
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
                c = 2 * np.arcsin(np.sqrt(a))
                # Radius of earth is 6371 km
                km = 6371 * c
                distance_list.append(km)
            geo_json = {'minimum': round(min(distance_list), 3), 'maximum': round(max(distance_list), 3),
                        'average': round(np.average(distance_list), 3),
                        'std. deviation': round(np.std(distance_list), 3),
                        'unit measured': 'km'}
            return json.dumps(geo_json)

        except KeyError:
            raise cherrypy.HTTPRedirect("/login")


def run():
    """Modified the method to activate session """
    settings.update(json.load(file(sys.argv[1])))
    cherrypy.quickstart(Root(settings),  "/", {'/': {'tools.sessions.on': True}})

if __name__ == "__main__":

    settings.update({'url': "mongodb://localhost:27017/test_crunch_fitness"})
    cherrypy.quickstart(Root(settings), "/", {'/': {'tools.sessions.on': True}})
