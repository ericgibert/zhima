#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Access the database for all basic operations (SELECT/UPDATE/INSERT)

Reads the JSON configuration file to retrieve:

- either given to __init__ as parameter "db_access=/the/path/to/file" or defaulted to "../Private/db_access.data"
- content is expressed as a JSON structure, no comments allowed
----------------+----------------------------------------------------------------------------------
Key             | Value
----------------+----------------------------------------------------------------------------------
IP mask         | Dictionary to provide database access:
                | - login
                | - passwd
                | - dbname
                | - server_ip   (can be a sever name if DNS is resolved) ; will be replaced by 'localhost' if on master
----------------+----------------------------------------------------------------------------------
key             | Encryption key - must be 8 bytes
----------------+----------------------------------------------------------------------------------
mailbox         | Information to connect to SMTP external server to send notification emails
                | - username
                | - password
                | - server (URL)
                | - port (secured: 465 recommended
----------------+----------------------------------------------------------------------------------
whitelist       | List of IP or names which are unable to access the APIs
----------------+----------------------------------------------------------------------------------
has_camera      | Boolean 0/1: this Raspi is equiped with a camera for QR code recognition
----------------+----------------------------------------------------------------------------------
has_RFID        | Boolean 0/1: this Raspi is equiped with a RFID card reader
----------------+----------------------------------------------------------------------------------
open_with       | One of "RELAY", "BLE", "BOTH", "API". Method to open the door - refer to zhima.py for more information
----------------+----------------------------------------------------------------------------------
wait_to_close   | Boolean 0/1: this Raspi is equiped with a detection of door status (open or close) ; relay released only when closed
----------------+----------------------------------------------------------------------------------


"""
__author__ = "Eric Gibert"
__version__ = "1.0.20180128"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"

from datetime import datetime
import json
from subprocess import check_output
import pymysql
from pymysql.cursors import DictCursorMixin, Cursor
from collections import OrderedDict
class OrderedDictCursor(DictCursorMixin, Cursor):
    dict_type = OrderedDict

class Database():
    """Database interface"""
    dbname = None
    login = None
    passwd = None
    server_ip = None
    db_server = None
    key = None
    mailbox = {}

    def __init__(self, table=None, *args, **kwargs):
        """Load from Private file the various connection parameters the first time a DB object is instantiated
        - based on the netmask --> get the Master Server address
        - based on "mailbox": get the SMTP parameters
        - extra information:
            * "has_camera": 0/1 for False/True --> allow Raspi with camera to read barcode
            * "has_RFID": 0/1 for False/True --> allow Raspi to get RFDI card UID on contact (PN532 reader)
            * "whitelist": list of servers authorized to call the APIs

        Note: if Database.server_ip == "localhost" then this Raspi is the master (access database and door) else slave

        """
        self.table = table
        self.debug = kwargs.get('debug', False)
        if self.dbname is None:
            # MySQL database parameters
            file_path = kwargs.get("db_access") or "../Private/db_access.data"
            with open(file_path) as json_file:
                self.access = json.load(json_file)
            my_IP = check_output(['hostname', '-I']).decode("utf-8").strip()
            ip_3 = '.'.join(my_IP.split('.')[:3])
            # print("My IP:", my_IP, "ip_3:", ip_3, "\nThis access:",self.access[ip_3])
            # print(self.access)
            try:
                Database.dbname = self.access[ip_3]["dbname"]
                Database.login = self.access[ip_3]["login"]
                Database.passwd = self.access[ip_3]["passwd"]
                Database.db_server = "localhost" if my_IP==self.access[ip_3]["server_ip"] else self.access[ip_3]["server_ip"]
                Database.server_ip = self.access[ip_3]["server_ip"]
                Database.key = self.access["key"].encode("utf-8")
                Database.mailbox = self.access.get("mailbox")
            except KeyError as err:
                print("model_db.py: Cannot find entry {} in db_access.data".format(err))
                exit(1)
        self.key = Database.key
        self.mailbox = Database.mailbox

    def fetch(self, sql, params = (), one_only=True):
        """execute a SELECT statement with the parameters and fetch row/rows"""
        if self.debug:
            print("Fetch:", sql, params)
        data = {}
        # print ("Database parameters:", Database.db_server, Database.login, Database.passwd, Database.dbname)
        connection = pymysql.connect(Database.db_server, Database.login, Database.passwd, Database.dbname, cursorclass=OrderedDictCursor)
        try:
            # with pymysql.connect(Database.db_server, Database.login, Database.passwd, Database.dbname).cursor(OrderedDictCursor) as cursor:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                data = cursor.fetchone() if one_only else cursor.fetchall()
        except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as err:
            print(err)
            print(sql)
            print(params)
        # else:
        #    return data
        finally:
            connection.close()
        return data

    def select(self, table=None, columns='*', one_only=True, order_by="", **where):
        """build a SELECT statement and fetch its row(s)"""
        table = table or self.table
        sql = "SELECT {} from {}".format(columns, table)
        params = []
        if where:
            where_clause = []
            for col, val in where.items():
                where_clause.append(col+("=%s" if col!='passwd' else "=PASSWORD(%s)"))
                params.append(val)
            sql += " WHERE " + " AND ".join(where_clause)
        if order_by: sql += " ORDER BY " + order_by
        return self.fetch(sql, params, one_only)

    def __getitem__(self, field):
        """Allow sub_class["field"] to get a table field's value or None"""
        return self.data.get(field)


    def execute_sql(self, sql, params):
        """Generic SQL statement execution"""
        if self.debug:
            print("Execute:", sql, params)
        lastrow = None
        connection = pymysql.connect(Database.db_server, Database.login, Database.passwd, Database.dbname, cursorclass=OrderedDictCursor)
        try:
            # with pymysql.connect(Database.db_server, Database.login, Database.passwd, Database.dbname) as cursor:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                lastrow = cursor.lastrowid
            connection.commit()
        except (TypeError, ValueError, pymysql.err.OperationalError) as err:
            print('ERROR on sql execute:', err)
            print(sql)
            print(params)
        finally:
            connection.close()
        return lastrow

    def update(self, table=None, **kwargs):
        """
        Update the fields given as parameters with their values using the 'kwargs' dictionary
        'id' should be part of the kwargs to ensure a single row update
        If the table's primary key is not named 'id' then provide its name on the 'id_col_name' argument
        """
        table = table or self.table
        col_value, id, id_col_name = [], None, 'id'
        for col, val in kwargs.items():
            if col=='id':
                id = val
            elif col=='id_col_name':
                id_col_name = val
            else:
                col_value.append((col, val))
        if col_value:
            sql = "UPDATE {0} SET {1} WHERE {2}=%s".format(table,
                                                          ",".join([c+("=%s" if c!='passwd' else "=PASSWORD(%s)") for c, v in col_value]),
                                                          id_col_name)
            self.execute_sql(sql, [v for c, v in col_value] + [ id ])
        return id

    def insert(self, table=None, **kwargs):
        """INSERT a record in the table"""
        table= table or self.table
        col_value = []
        for col, val in kwargs.items():
            col_value.append((col, val))
        if col_value:
            sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(table,
                                                              ",".join([c for c, v in col_value]),
                                                              ",".join([("%s" if c!='passwd' else "PASSWORD(%s)") for c, v in col_value]))
            return self.execute_sql(sql, [v for c, v in col_value])
        else:
            return None

    def delete(self):
        """Remove the current record from its table - no parameter as the object must be instantiated properly"""
        self.execute_sql("DELETE from {} where id=%s".format(self.table), (self.id, ))
        self.data, self.id = None, None

    def log(self, log_type, code, message, debug=False):
        """
        :param log_type: ENTRY when a user gets in or INFO/WARNING/ERROR for technical issue
        :param code: either the member id concerned by the log entry OR the error code
        :param message: the log message
        :return: last inserted row id
        """
        if debug:
            print(datetime.now(), log_type, code, message)
        log_id = self.insert('tb_log', type=log_type, code=code, message=message)
        if int(code)>0:
            self.update('users', id=code, last_active_type="[{}] {}".format(log_type, message),
                        last_active_time=datetime.now())
        return log_id

    def create_tables(self):
        """

        """
        pass

if __name__ == "__main__":
    db = Database()
    # print(db.access)
    result = db.fetch("select count(*) as nb_users from users", ())
    print(result['nb_users'],"records in the 'users' table")
    row_id = db.log('INFO', 1, "Testing log INSERT", debug=True)
    print("New log entry:", row_id)
    db.update('tb_log', id=row_id, code=2)
    row = db.select('tb_log', id=row_id)
    print("Updated 'code' from 1 to 2:", row)
    # db.delete()
    # print("row deleted")
    # row = db.select('tb_log', id=row_id)
    # print(row)

