## mms-birthday-app
----
### To run the application for the first time:
1. $ python3 -m venv venv
2. $ . venv/bin/activate
3. $ pip3 install -e .
4. $ export FLASK_APP=mms-birthday-web
5. $ export FLASK_ENV=development
6. $ flask init-db
7. $ flask run

### Available commands:
* $ flask init-db
* $ flask make-admin <username>
* $ flask make-active <username>
* $ flask make-inactive <username>
