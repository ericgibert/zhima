#!/usr/bin/env python3
import sys
from shutil import copy2
from os import path, system
from datetime import datetime
from bottle import Bottle, template, request, BaseTemplate, redirect, error, static_file
from bottlesession import CookieSession, authenticator
from member_db import Member
from make_qrcode import make_qrcode
from transaction_db import Transaction

session_manager = CookieSession()    #  NOTE: you should specify a secret
valid_user = authenticator(session_manager)

http_view = Bottle()
BaseTemplate.defaults['login_logout'] = "Login"
PAGE_LENGTH = 25  # rows per page

@error(404)
def error404(error):
    return '404 error:<h2>%s</h2>' % error


@http_view.route('/')
def default():
    session = session_manager.get_session()
    sql = "SELECT * from tb_log WHERE type='ERROR' and datediff(CURDATE(), created_on)  < 8 ORDER BY created_on desc"
    rows = http_view.controller.db.fetch(sql, (), one_only=False)
    return template("default", session_valid=session["valid"], controller=http_view.controller, rows=rows)

def list_sql(table, filter_col, order_by="", page=0, select_cols="*"):
    try:
        req_query = "?filter=" + request.query["filter"]
        sql = "SELECT {} FROM {} WHERE {}='{}'".format(select_cols, table, filter_col, request.query["filter"])
    except KeyError:
        sql, req_query = "SELECT {} FROM {}".format(select_cols, table), ""
    sql +=  " ORDER BY {}".format(order_by) if order_by else ""
    sql += " LIMIT {},{}".format(page * PAGE_LENGTH, PAGE_LENGTH)
    return sql, req_query

@http_view.get('/entries')
@http_view.get('/entries/<page:int>')
def list_entries(page=0):
    sql = """SELECT code, message, created_on from tb_log 
             WHERE type='OPEN' and datediff(CURDATE(), created_on) < 32 
             ORDER BY created_on desc LIMIT {}, {}""".format(page * PAGE_LENGTH, PAGE_LENGTH)
    rows = http_view.controller.db.fetch(sql, (), one_only=False)
    return template("entries", rows=rows, current_page=page)

@http_view.get('/log')
@http_view.get('/log/<page:int>')
def log(page=0):
    """Log dump - can be filterer with filter=<log_type>"""
    sql, req_query = list_sql("tb_log", "type", "created_on DESC", page)
    rows = http_view.controller.db.fetch(sql, one_only=False)
    return template("log", rows=rows, current_page=page, req_query=req_query)


@http_view.get('/members')
@http_view.get('/members/<page:int>')
def list_members(page=0):
    """List the members and provide link to add new ones"""
    sql, req_query = list_sql("users", "status", page)
    rows = http_view.controller.db.fetch(sql, one_only=False)
    return template("members", rows=rows, current_page=page, req_query=req_query)


@http_view.get('/member/<id:int>')
def get_member(id):
    """Display the form in R/O mode for a member"""
    member = Member(http_view.controller.db, id)
    qr_file = "images/XCJ_{}.png".format(id)
    if member.data['status']=="OK":
        qrcode_text = member.encode_qrcode()
        img = make_qrcode(qrcode_text)
        img.save(qr_file)
    else:
        copy2("images/emoji-not-happy.jpg", qr_file)
    return template("member", member=member, read_only=True)

@http_view.get('/member/edit/<id:int>')
def upd_member(id):
    """update a member database record"""
    pass

@http_view.get('/transaction/<member_id:int>')
@http_view.get('/transaction/<member_id:int>/<id:int>')
def get_transaction(member_id, id=0):
    if id:
        transaction = Transaction(http_view.controller.db, id)
        read_only = True
    elif member_id:
        transaction = Transaction(http_view.controller.db, member_id=member_id)
        read_only = False
    return template("transaction", transaction=transaction, read_only=read_only)

@http_view.post('/transaction/add')
def add_transaction():
    transaction = Transaction(http_view.controller.db)
    if request.forms['id'] == 'None':
        id = transaction.db.insert('transactions',
                                member_id = int(request.forms['member_id']),
                                type = request.forms['type'],
                                description = request.forms['description'],
                                amount = float(request.forms['amount']),
                                currency = request.forms['currency'],
                                valid_from = request.forms['valid_from'],
                                valid_until = request.forms['valid_until'],
                                created_on = datetime.now()
                              )
        redirect("/transaction/{}/{}".format(request.forms['member_id'], id))
    return template("transaction", transaction=transaction, read_only=True)

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

@http_view.route("/images/<filepath>")
def img(filepath):
    return static_file(filepath, root="images")

if __name__ == "__main__":
    from model_db import Database
    class ctrl:
        def __init__(self, db):
            self.db = db
    http_view.controller = ctrl(Database())
    http_view.run()