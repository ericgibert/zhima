#!/usr/bin/env python3
""" HTTP server for XCJ member database management

- Record the members
- Record their payments (called transactions)

"""
__author__ = "Eric Gibert"
__version__ = "1.0.20180204"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
import sys
from shutil import copy2
from os import path, system, getpid
import argparse
from collections import OrderedDict
from datetime import datetime
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

def need_login(callback):
    """decorator to ensure a function is only callable when the user is logged in"""
    def wrapper(*args, **kwargs):
        session = session_manager.get_session()
        if session['valid'] and (('id' in kwargs and kwargs['id']==session['id']) or session['admin']):
            return callback(*args, **kwargs)
        else:
            return '<h3>Sorry, you are not authorized to perform this action</h3>Try to login first'
    return wrapper

def need_admin(callback):
    """decorator to ensure a function is only callable when the user is logged as administrator"""
    def wrapper(*args, **kwargs):
        session = session_manager.get_session()
        if session['valid'] and session['admin']:
            return callback(*args, **kwargs)
        else:
            return '<h3>Sorry, you are not authorized to perform this action</h3>Try to login first'
    return wrapper

@http_view.route('/')
def default():
    # sql = "SELECT * from tb_log WHERE type='ERROR' and datediff(CURDATE(), created_on)  < 8 ORDER BY created_on desc"
    # rows = http_view.controller.db.fetch(sql, (), one_only=False)
    return template("default", controller=http_view.controller, session=session_manager.get_session())  # rows=rows,

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
@need_admin
def list_entries(page=0):
    sql = """SELECT code, message, created_on from tb_log 
             WHERE (type='OPEN' or type='NOT_OK') and datediff(CURDATE(), created_on) < 32 
             ORDER BY created_on desc LIMIT {}, {}""".format(page * PAGE_LENGTH, PAGE_LENGTH)
    rows = http_view.controller.db.fetch(sql, (), one_only=False)
    return template("entries", rows=rows, current_page=page, session=session_manager.get_session())

@http_view.get('/log')
@http_view.get('/log/<page:int>')
@need_admin
def log(page=0):
    """Log dump - can be filterer with filter=<log_type>"""
    sql, req_query = list_sql("tb_log", "type", "created_on DESC", page)
    rows = http_view.controller.db.fetch(sql, one_only=False)
    return template("log", rows=rows, current_page=page, req_query=req_query, session=session_manager.get_session())


@http_view.get('/members')
@http_view.get('/members/<page:int>')
@need_admin
def list_members(page=0):
    """List the members and provide link to add new ones"""
    sql, req_query = list_sql("users", "status", page)
    rows = http_view.controller.db.fetch(sql, one_only=False)
    return template("members", rows=rows, current_page=page, req_query=req_query, session=session_manager.get_session())


@http_view.get('/member/<id:int>')
@need_login
def get_member(id):
    """Display the form in R/O mode for a member"""
    member = Member(id)
    qr_file = "images/XCJ_{}.png".format(id)
    if member.data['status']=="OK":
        qrcode_text = member.encode_qrcode()
        img = make_qrcode(qrcode_text)
        img.save(qr_file)
    else:
        member.qrcode_is_valid = False
        copy2("images/emoji-not-happy.jpg", qr_file)
    return template("member", member=member, read_only=True, session=session_manager.get_session())

@http_view.get('/member/edit/<id:int>')
@need_admin
def upd_form_member(id):
    """update a member database record"""
    member = Member(id)
    return template("member", member=member, read_only=False, session=session_manager.get_session())

@http_view.post('/member/edit/<id:int>')
@need_admin
def upd_member(id):
    """update a member database record"""
    if str(id) not in request.forms['id']:
        return "<h1>Error - The form's id is not the same as the id on the link</h1>"
    CANT_UPD_FIELDS = ('submit', 'id', 'openid', 'passwdchk')
    member = Member(member_id=id)  # get current db record or an empty member if id==0
    # force username to lower case and ensure its unicity:
    try:
        request.forms['username'] = request.forms['username'].lower()
        nb_username = member.fetch("select count(id) as cnt from users where username=%s and id<>%s", (request.forms[field], id))
        if nb_username['cnt']>0:
            return "<h1>Error - This Username already exists - Duplicates are forbidden</h1>"
    except:
        pass
    # if the user has changed the value of a legit fioeld then add it to the list of updates
    need_upd = {}
    for field in [f for f in request.forms if f not in CANT_UPD_FIELDS]:
        print(field)
        if id==0 or (request.forms[field] != str(member.data[field])):
            need_upd[field] = request.forms[field]
            # # check unicity of the 'username'
            # if field=='username':
            #     nb_username = member.fetch("select count(id) as cnt from users where username=%s and id<>%s", (request.forms[field], id))
            #     if nb_username['cnt']>0:
            #         return "<h1>Error - This Username already exists - Duplicates are forbidden</h1>"
    if need_upd:
        if id:
            need_upd['id'] = id
            member.update('users', **need_upd)
        else:
            need_upd['openid'] = 0
            id = member.insert('users', **need_upd)
    else:
        print("Post has nothing to do...")
    redirect('/member/{}'.format(id))

@http_view.get('/members/new')
@need_admin
def new_form_member():
    """add a new member database record"""
    member = Member()
    member.data = OrderedDict({
    'id': 0,
    'username': '<New>',
    'passwd': '',
    'passwdchk': '',
    'email': '',
    'birthdate': 'YYYY-MM-DD',
    'status': 'OK',
    'role': 0,
    'createTime': datetime.now(),
    'lastUpdate': datetime.now(),
    })
    return template("member", member=member, read_only=False, session=session_manager.get_session())

@http_view.get('/transaction/<member_id:int>')
@http_view.get('/transaction/<member_id:int>/<id:int>')
@need_admin
def get_transaction(member_id, id=0):
    if id:
        transaction = Transaction(id)
        read_only = True
    elif member_id:
        transaction = Transaction(member_id=member_id)
        read_only = False
    return template("transaction", transaction=transaction, read_only=read_only, session=session_manager.get_session())

@http_view.post('/transaction/add')
@need_admin
def add_transaction():
    transaction = Transaction()
    if request.forms['id'] == 'None':
        id = transaction.insert('transactions',
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
    return template("transaction", transaction=transaction, read_only=True, session=session_manager.get_session())

#
### Login/Logout form & process
#
@http_view.route('/Login')
def login():
    return template('login.tpl', error="", session=session_manager.get_session())

@http_view.post('/Login')
def do_login():
    """
    Fetch the login/password from the form and check this couple against the tb_user table
    """
    username = request.forms.get('username').lower()
    password = request.forms.get('password')

    if not username or not password:
        return template('login.tpl', error='Please specify username and password', session=session_manager.get_session())

    session = session_manager.get_session()
    new_user = Member()
    new_user = new_user.select('users', username=username, passwd=password)
    if new_user:
        session['valid'] = True
        session['name'] = username
        session['admin'] = new_user['role'] > 1 and new_user['status'] == 'OK'
        session['id'] = new_user['id']
        session_manager.save(session)
        BaseTemplate.defaults['login_logout'] = "Logout"
    else:
        session['valid'], session['admin'], session['name'], session['id'] = False, False, "", -1
        session_manager.save(session)
        return template('login.tpl', error='Username or password is invalid', session=session_manager.get_session())
    redirect(request.get_cookie('validuserloginredirect', '/member/{}'.format(new_user['id'])))

@http_view.route('/Logout')
def logout():
    session = session_manager.get_session()
    session['valid'], session['admin'], session['name'], session['id'] = False, False, "", -1
    session_manager.save(session)
    BaseTemplate.defaults['login_logout'] = "Login"
    redirect('/')

@http_view.route('/restart')
@need_admin
def restart():
    """Restarts the application"""
    session = session_manager.get_session()
    if session['admin']:
        system(path.dirname(path.abspath(__file__)) + "/zhima.sh restart")
        redirect('/')

@http_view.route('/stop')
@need_admin
def stop():
    """Stops the application"""
    session = session_manager.get_session()
    if session['admin']:
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

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bottle", dest="bottle_ip", help="Optional: Raspberry Pi IP address to allow remote connections", required=False,  default="127.0.0.1")
    parser.add_argument('-v', '--version', action='version', version=__version__)
    # parser.add_argument('config_file', nargs='?', default='')
    args, unk = parser.parse_known_args()

    with open("http_view.pid", "wt") as fpid:
        print(getpid(), file=fpid)

    http_view.run(host=args.bottle_ip)
