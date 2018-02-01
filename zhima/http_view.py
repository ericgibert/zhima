#!/usr/bin/env python3
import sys
from os import path, system
from bottle import Bottle, template, request, BaseTemplate, redirect, error
from bottlesession import CookieSession, authenticator
from member_db import Member

session_manager = CookieSession()    #  NOTE: you should specify a secret
valid_user = authenticator(session_manager)

http_view = Bottle()
BaseTemplate.defaults['login_logout'] = "Login"

@error(404)
def error404(error):
    return '404 error:<h2>%s</h2>' % error


@http_view.route('/')
def default():
    session = session_manager.get_session()
    sql = "SELECT * from tb_log WHERE type='ERROR' and datediff(CURDATE(), created_on)  < 8 ORDER BY created_on desc"
    rows = http_view.controller.db.fetch(sql, (), one_only=False)
    return template("default", session_valid=session["valid"], controller=http_view.controller, rows=rows)

@http_view.get('/entries')
def list_entries():
    sql = "SELECT * from tb_log WHERE type='OPEN' and datediff(CURDATE(), created_on)  < 32 ORDER BY created_on desc"
    rows = http_view.controller.db.fetch(sql, (), one_only=False)
    return template("entries", rows=rows)

@http_view.get('/log')
@http_view.get('/log/<page:int>')
def log(page=0):
    """Log dump - can be filterer with filter=<log_type>"""
    PAGE_LENGTH = 25  # rows per page
    try:
        req_query = "?filter=" + request.query["filter"]
        sql = "SELECT * FROM tb_log WHERE type='{}'".format(request.query["filter"])
    except KeyError:
        sql, req_query = "SELECT * FROM tb_log", ""
    sql += " ORDER BY created_on DESC LIMIT {},{}".format(page * PAGE_LENGTH, PAGE_LENGTH)
    rows = http_view.controller.db.fetch(sql, one_only=False)
    return template("log", rows=rows, current_page=page, req_query=req_query)

#
### Login/Logout form & process
#
@http_view.route('/Login')
def login():
    return template('login.tpl', error="")

@http_view.post('/Login')
def do_login():
    """
    Fetch the login/password from the form and check this couple against the tb_user table
    """
    username = request.forms.get('username')
    password = request.forms.get('password')

    if not username or not password:
        return template('login.tpl', error='Please specify username and password')

    session = session_manager.get_session()
    session['valid'] = False

    new_user = Member(http_view.controller.db)
    new_user_id = new_user.db.fetch("SELECT id from users where username=%s and role>0", (username,))
    if new_user_id:
        new_user.get_user(new_user_id)
        if new_user.id:
            session['valid'] = True
            session['name'] = username

    session_manager.save(session)
    if not session['valid']:
        return template('login.tpl', error='Username or password is invalid')

    BaseTemplate.defaults['login_logout'] = "Logout"
    redirect(request.get_cookie('validuserloginredirect', '/'))

@http_view.route('/Logout')
def logout():
    session = session_manager.get_session()
    session['valid'] = False
    session_manager.save(session)
    BaseTemplate.defaults['login_logout'] = "Login"
    redirect('/')

@http_view.route('/restart')
def restart():
    """Restarts the application"""
    system(path.dirname(path.abspath(__file__)) + "/zhima.sh restart")

@http_view.route('/stop')
def stop():
    """Stops the application"""
    # http_view.controller.stop(from_bottle=True)
    sys.stderr.close()

if __name__ == "__main__":
    from model_db import Database
    http_view.controller = object()
    http_view.controller.db = Database()
    http_view.run()