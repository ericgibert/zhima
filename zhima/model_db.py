#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


"""
__author__ = "Eric Gibert"
__version__ = "1.0.20180128"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"

from datetime import datetime
import json
from subprocess import check_output
# try:
#     import pymysql
#     from pymysql.cursors import DictCursorMixin, Cursor
#     _simulation = False
# except ImportError:
#     _simulation = True
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
    key = None
    mailbox = {}

    def __init__(self, table=None, *args, **kwargs):
        """Load from Private file the various connection parameters the first time a DB object is instantiated"""
        self.table = table
        if self.dbname is None:
            # MySQL database parameters
            with open("../Private/db_access.data") as json_file:
                self.access = json.load(json_file)
            my_IP = check_output(['hostname', '-I']).decode("utf-8").strip()
            ip_3 = '.'.join(my_IP.split('.')[:3])
            # print("My IP:", my_IP, "ip_3:", ip_3, "\nThis access:",self.access[ip_3])
            # print(self.access)
            try:
                Database.dbname = self.access[ip_3]["dbname"]
                Database.login = self.access[ip_3]["login"]
                Database.passwd = self.access[ip_3]["passwd"]
                Database.server_ip = "localhost" if my_IP==self.access[ip_3]["server_ip"] else self.access[ip_3]["server_ip"]
                Database.key = self.access["key"].encode("utf-8")
                Database.mailbox = self.access["mailbox"]
            except KeyError as err:
                print("Cannot find entry {} in db_access.data".format(err))
                exit(1)
        self.key = Database.key
        self.mailbox = Database.mailbox

    def fetch(self, sql, params = (), one_only=True):
        """execute a SELECT statement with the parameters and fetch row/rows"""
        try:
            with pymysql.connect(Database.server_ip, Database.login, Database.passwd, Database.dbname).cursor(OrderedDictCursor) as cursor:
                cursor.execute(sql, params)
                data = cursor.fetchone() if one_only else cursor.fetchall()
        except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as err:
            print(err)
            print(sql)
            print(params)
            return None
        else:
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

    def execute_sql(self, sql, params):
        """Generic SQL statement execution"""
        try:
            with pymysql.connect(Database.server_ip, Database.login, Database.passwd, Database.dbname) as cursor:
                cursor.execute(sql, params)
                return cursor.lastrowid
        except (TypeError, ValueError, pymysql.err.OperationalError) as err:
            print('ERROR on sql execute:', err)
            print(sql)
            print(params)
        return None

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
    result = db.fetch("select count(*) from users", ())
    print(result)
    row_id = db.log('INFO', 1, "Testing log INSERT", debug=True)
    print(row_id)
    db.update('tb_log', id=row_id, code=2)
    row = db.select('tb_log', id=row_id)
    print(row)
