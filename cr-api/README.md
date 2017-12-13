Welcome to the Crunch.io api fitness test.

Here you will find a python package to help us evaluate your skills with:

1. Problem Solving
2. Web Server API Design
3. Request-time data manipulation
4. Testing strategies

Instructions

1. Fork the repo into a private repo.
2. Create a virtualenv for this project and install the cr-api and cr-db packages into your environment.
3. Modify the cr-api package to complete the task, the code is commented with task items.
4. Let us know when you have finished.

Deliverable

Publish your work in a GitHub repository.  Please use Python 2.x for your coding.  Feel free to modify this
readme to give any additional information a reviewer might need.

Implementation Details

<siv.niznam@gmail.com for the coding test for youGov>

Assumptions

- Modified server.py so that I can also run it directly.

-  id from document is used for session (not ideal but sufficient for demonstration)

- DUMMY METHOD FOR BROWSER support -added newuser() method in Root to facilitate adding new record/document
 to the Mongodb. newuser() directs to /users upon POST. newuser() DOES NOT check session but just
  redirects. If record/document is added using newuser() but without logging in, users() redirects
   to /login page upon post

-With regards to validation the record/inputs, only email is validated in users() method upon post.
 Assuming all other fields need not to be unique and comes as a string, email is checked if
 it exists in database and if it does, a message is returned.

-Thoughts on how to perform distance aggregation when large number of users are present is included in the
 docstrings for distances() method
