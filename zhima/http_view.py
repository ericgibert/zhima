#!/usr/bin/env python3
""" HTTP server for XCJ member database management

- Record the members
- Record their payments (called transactions)

"""
__author__ = "Eric Gibert"
__version__ = "1.0.20180520 Dong Bei"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
import sys
from shutil import copy2
from os import path, system, getpid
from json import dumps
import argparse
from collections import OrderedDict
from datetime import datetime
from bottle import Bottle, template, request, BaseTemplate, redirect, error, static_file, HTTPResponse
from bottlesession import authenticator, PickleSession
from member import Member
from member_api import Member_Api
from make_qrcode import make_qrcode
from transaction import Transaction
from rpi_gpio import Rpi_Gpio
from glob import glob
from markdown import markdown


session_manager = PickleSession(session_dir=r"../Private/sessions", cookie_expires=12 * 3600)
#  NOTE: must amend the bottlesession.py script to declare files as binary as follow:
#
#  line 116:        with open(filename, 'rb') as fp:
#  line 124:        with open(tmpName, 'wb') as fp:

valid_user = authenticator(session_manager)

http_view = Bottle()
BaseTemplate.defaults['login_logout'] = "Login"
PAGE_LENGTH = 25  # rows per page

@error(404)
def error404(error):
    return '404 error:<h2>%s</h2>' % error

def whitelisted(callback):
    """decorator to check that the API is called by a whitelisted server"""
    def wrapper(*args, **kwargs):
        if request.remote_addr in http_view.controller.db.access['whitelist']:
            return callback(*args, **kwargs)
        else:
            print("Unauthorized access from", request.remote_addr)
            return HTTPResponse(status=403, body='<h3>Sorry, you are not authorized to perform this action</h3>WL: ' + request.urlparts.hostname)
    return wrapper

def need_login(callback):
    """decorator to ensure a function is only callable when the user is logged in"""
    def wrapper(*args, **kwargs):
        session = session_manager.get_session()
        if session['valid'] and (('id' in kwargs and kwargs['id']==session['id']) or session['admin']):
            return callback(*args, **kwargs)
        else:
            return '<h3>Sorry, you are not authorized to perform this action</h3>Try to <a href="/Login">login</a> first'
    return wrapper

def need_staff(callback):
    """decorator to ensure a function is only callable when the user is logged with a role >= STAFF"""
    def wrapper(*args, **kwargs):
        session = session_manager.get_session()
        if session['valid'] and session['admin']:
            return callback(*args, **kwargs)
        else:
            return HTTPResponse(status=403, body='<h3>Sorry, you are not authorized to perform this action</h3>Try to <a href="/Login">login</a> first')
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
@need_staff
def list_entries(page=0):
    """List all the entries (door opening) recorded in the LOG table"""
    sql = """SELECT code, message, created_on from tb_log 
             WHERE (type='OPEN' or type='NOT_OK') and datediff(CURDATE(), created_on) < 32 
             ORDER BY created_on desc LIMIT {}, {}""".format(page * PAGE_LENGTH, PAGE_LENGTH)
    rows = http_view.controller.db.fetch(sql, (), one_only=False)
    return template("entries", rows=rows, current_page=page, session=session_manager.get_session())

@http_view.get('/log')
@http_view.get('/log/<page:int>')
@need_staff
def log(page=0):
    """Log dump - can be filterer with ?filter=<log_type>"""
    sql, req_query = list_sql("tb_log", "type", "created_on DESC", page)
    rows = http_view.controller.db.fetch(sql, one_only=False)
    return template("log", rows=rows, current_page=page, req_query=req_query, session=session_manager.get_session())


@http_view.get('/members')
@http_view.get('/members/<page:int>')
@need_staff
def list_members(page=0):
    """List the members and provide link to add new one or edit existing ones"""
    sql, req_query = list_sql("users", "status", page=page)
    rows = http_view.controller.db.fetch(sql, one_only=False)
    return template("members", rows=rows, current_page=page, req_query=req_query, session=session_manager.get_session())


@http_view.get('/member/<id:int>')
@need_login
def get_member(id):
    """Display the form in R/O mode for a member"""
    member = Member(id)
    qr_file = "images/XCJ_{}.png".format(id)
    if member['status'] == "OK":
        qrcode_text = member.encode_qrcode()
        img = make_qrcode(qrcode_text)
        img.save(qr_file)
    else:
        member.qrcode_is_valid = False
        copy2("images/emoji-not-happy.jpg", qr_file) # overwrite any previous QR code .png
    return template("member", member=member, read_only=True, session=session_manager.get_session())

@http_view.get('/member/edit/<id:int>')
@need_staff
def upd_form_member(id):
    """update a member database record - Display current data for input modification"""
    member = Member(id)
    return template("member", member=member, read_only=False, session=session_manager.get_session())

@http_view.post('/member/edit/<id:int>')
@need_staff
def upd_member(id):
    """update a member database record - Post the modified data from the form above"""
    if str(id) not in request.forms.get('id', '0'):
        return "<h1>Error - The form's id is not the same as the id on the link</h1>"
    CANT_UPD_FIELDS = ('submit', 'id', 'passwdchk', 'validity')
    member = Member(id)  # get current db record or an empty member if id==0
    # force username to lower case and ensure its unicity:
    try:
        request.forms['username'] = request.forms['username'].lower()
        nb_username = member.fetch("select count(id) as cnt from users where username=%s and id<>%s", (request.forms['username'], id))
        if nb_username['cnt']>0:
            return "<h1>Error - This Username already exists - Duplicates are forbidden</h1>"
    except:
        pass
    # if the user has changed the value of a legit fioeld then add it to the list of updates
    need_upd = {}
    for field in [f for f in request.forms if f not in CANT_UPD_FIELDS]:
        # print(field, ",", request.forms[field], ",", str(member[field] or ''))
        if id==0 or (request.forms[field] != str(member.data[field] or '')):
            need_upd[field] = request.forms[field]
    if need_upd:
        if id:
            need_upd['id'] = id
            member.update('users', **need_upd)
        else:
            need_upd['openid'] = 0
            id = member.insert('users', **need_upd)
            member.update('users', id=id, openid=id)
    else:
        print("Post has nothing to do...")
    redirect('/member/{}'.format(id))

@http_view.get('/members/new')
@need_staff
def new_form_member():
    """add a new member database record"""
    member = Member()
    member.data = OrderedDict([
        # ('id', 0),
        ('username', '<New>'),
        ('passwd', ''),
        ('passwdchk', ''),
        ('email', ''),
        # ('birthdate', 'YYYY-MM-DD'),
        ('status', 'OK'),
        ('role', 1),
        ('create_time', datetime.now()),
        ('last_update', datetime.now()) ])
    return template("member", member=member, read_only=False, session=session_manager.get_session())

@http_view.get('/member/email_qrcode/<id:int>')
@need_staff
def email_my_qrcode(id):
    """Email a member its QR code"""
    member = Member(id=id)
    if member['email']:
        try:
            member.email_qrcode()
        except ValueError as err:
            redirect('/member/{}?msg=Error: No Email sent {}"'.format(id, err))
        else:
            redirect('/member/{}?msg=Email sent"'.format(id))
    redirect('/member/{}?msg=Error: No Email address"'.format(id))


@http_view.get('/transaction/<member_id:int>')
@http_view.get('/transaction/<member_id:int>/<id:int>')
@need_staff
def get_transaction(member_id, id=0):
    if id:
        transaction = Transaction(id)
        read_only = True
    elif member_id:
        transaction = Transaction(member_id=member_id)
        read_only = False
    return template("transaction", transaction=transaction, read_only=read_only, session=session_manager.get_session())

@http_view.get('/transaction/update/<id:int>')
@need_staff
def upd_transaction(id=0):
    if id:
        transaction = Transaction(id)
    return template("transaction", transaction=transaction, read_only=False, session=session_manager.get_session())

@http_view.post('/transaction/add')
@need_staff
def add_transaction():
    transaction = Transaction()
    member_id = int(request.forms['member_id'])
    id = request.forms.get('id')
    if id:
        transaction.update(
            id = id,
            type = request.forms['type'],
            description = request.forms['description'],
            amount = float(request.forms['amount']),
            currency = request.forms['currency'],
            valid_from = request.forms['valid_from'],
            valid_until = request.forms['valid_until'],
            created_on = datetime.now()
        )
    else:
        id = transaction.insert('transactions',
                                member_id = member_id,
                                type = request.forms['type'],
                                description = request.forms['description'],
                                amount = float(request.forms['amount']),
                                currency = request.forms['currency'],
                                valid_from = request.forms['valid_from'],
                                valid_until = request.forms['valid_until'],
                                created_on = datetime.now()
                              )
        transaction.update_member_status(member_id)
    redirect("/transaction/{}/{}".format(member_id, id))

@http_view.get('/transaction/qrcode/<id:int>')
def make_event_qrcode(id):
    """Generate the QR Code of an Event"""
    trans = Transaction(id)
    event_member = Member(id=trans["member_id"])
    if event_member["status"] == "OK" and event_member["gender"] == 5:
        # use the event_member to set all necessary information to generate a QR Code Version 3
        qrcode = event_member.encode_qrcode(version=3, from_date=trans["valid_from"], until_date=trans["valid_until"])
        img_qrcode = make_qrcode(qrcode)
        qr_file = "images/XCJevent_{}.png".format(id)
        img_qrcode.save(qr_file)
        return "<img src='/{}' />".format(qr_file)
    else:
        return "<h2>This event has not a valid status or gender.</h2>"


@http_view.get('/daypass')
@http_view.post('/daypass')
@need_staff
def get_daypass():
    """Present a calendar to choose the daypass pariod (from/to) - default is today"""
    if request.method == "POST":
        from_date, until_date = request.forms['from_date'], request.forms['until_date']
        admin = Member(id=1)
        qr_code = admin.encode_qrcode(version=3,
                from_date=datetime.strptime(from_date, "%Y-%m-%d"),
                until_date=datetime.strptime(until_date, "%Y-%m-%d"))
        img_qrcode = make_qrcode(qr_code)
        qr_code = "images/XCJ_{}.png".format(from_date)
        img_qrcode.save(qr_code)
        print("QR code:", qr_code)
    else:
        qr_code = None
    return template("daypass", qr_code=qr_code, session=session_manager.get_session())


#
####  *.md documents posted in the 'views' folder
#
@http_view.route('/docs')
@http_view.route('/docs/<doc_name>')
@need_staff
def docs(doc_name=""):
    if doc_name:
        with open(path.join('views', doc_name), "rt") as doc:
            http_rendered = markdown("".join(doc.readlines()))
        return template("docs", text=http_rendered, session=session_manager.get_session())
    else:
        text = "<h1>List of Documents</h1>"
        for file_ in glob("views/*.md"):
            text += "<a href='/docs/{f}'>{f}</a><br />".format(f=path.basename(file_))
        return template("docs", text=text, session=session_manager.get_session())


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
        session['admin'] = new_user['role'] >= Member.ROLE['STAFF'] and new_user['status'] == 'OK'
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
@need_staff
def restart():
    """Restarts the application"""
    session = session_manager.get_session()
    if session['admin']:
        system(path.dirname(path.abspath(__file__)) + "/zhima.sh restart")
        redirect('/')

@http_view.route('/stop')
@need_staff
def stop():
    """Stops the application"""
    session = session_manager.get_session()
    if session['admin']:
        # http_view.controller.stop(from_bottle=True)
        sys.stderr.close()

@http_view.route("/images/<filepath>")
def img(filepath):
    return static_file(filepath, root="images")

###  APIs
@http_view.get('/api/v1.0/member/<id>')
@whitelisted
def get_member_by_id(id):
    """Return a Member JSON object based on a member db record and its last transaction"""
    member = Member_Api(id=id)
    return member.to_json()

@http_view.get('/api/v1.0/member/openid/<openid>')
@whitelisted
def get_member_by_openid(openid):
    """Return a Member JSON object based on a member db record and its last transaction"""
    member = Member_Api(openid=openid)
    return member.to_json()

@http_view.patch('/api/v1.0/member/openid/<openid>')
@whitelisted
def upd_member(openid):
    """
    If operation is "update": Update a member record designated by the provided 'openid'
    If operation is "add": Add a new transaction to the designated member
    """
    member = Member_Api(openid=openid)
    if member.id:
        operations = request.json
        if operations['op'] == "update": # update a member's profile
            upd_fields = {'id': member.id}
            for field in [f for f in operations['data'] if f in Member_Api.API_MAPPING_TO_DB]:
                upd_fields[Member_Api.API_MAPPING_TO_DB[field]] = operations['data'][field]
            if upd_fields:
                if http_view.controller.debug: print("Update", openid, "with", upd_fields)
                result = member.update(**upd_fields)
        elif operations['op'] == "add": # add a new payment record
            result = member.add_payment(operations['data'])
    else:
        result = member.to_json()  # generates the 1999 message
    return result

@http_view.post('/api/v1.0/member/new')
@whitelisted
def add_member():
    member = Member_Api() # empty new member
    result = member.create_from_json(request.json)
    return result

@http_view.post('/api/v1.0/open/seconds')
@whitelisted
def open_door():
    """get the number of seconds from the API body"""
    try:
        sec = int(request.json.get('seconds'))
    except (KeyError, TypeError, ValueError):
        sec = -1
    if 0 < sec < 99999:
        rpi = Rpi_Gpio()
        rpi.relay.flash("SET", sec)
        return dumps({ "errno": 1000, 'errmsg': "Door is now opened", 'data': {} })
    else:
        return dumps({ "errno": 1998, 'errmsg': "Incorrect call to open the door:" + str(request.json.get('seconds')), 'data': {} })

@http_view.post('/api/v1.0/log/add')
@whitelisted
def add_log():
    """Add a log record to the table
    Expects:
    {
        log_type, code, message, debug
    }
    """
    log = request.json
    log_id = http_view.controller.db.log(log["log_type"], log["code"], log["msg"], http_view.controller.debug)
    return HTTPResponse(status=201, body='log entry {} inserted'.format(log_id))

if __name__ == "__main__":
    from model_db import Database
    class ctrl:
        def __init__(self, db, debug):
            self.db = db
            self.debug = debug

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bottle", dest="bottle_ip", help="Optional: Raspberry Pi IP address to allow remote connections", required=False,  default="127.0.0.1")
    parser.add_argument("-p", "--port", dest="port", help="Optional: port for HTTP (8080: test / 80: PROD)", required=False,  default=8080, type=int)
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('-d', '--debug', dest='debug', help='debug mode - keep photos', action='store_true', default=False)
    # parser.add_argument('config_file', nargs='?', default='')
    args, unk = parser.parse_known_args()

    with open("http_view.pid", "wt") as fpid:
        print(getpid(), file=fpid)

    http_view.controller = ctrl(Database(debug=args.debug), args.debug)
    http_view.run(host=args.bottle_ip, port=args.port)
