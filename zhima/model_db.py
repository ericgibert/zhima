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
try:
    import pymysql
    _simulation = False
except ImportError:
    _simulation = True

class Database():
    """Database interface"""
    def __init__(self):
        # MySQL database parameters
        self.access = json.load(open("../Private/db_access.data"))
        my_IP = check_output(['hostname', '-I']).decode("utf-8").strip()
        # print("My IP:", my_IP)
        ip_3 = '.'.join(my_IP.split('.')[:3])
        try:
            self.dbname = self.access[ip_3]["dbname"]
            self.login = self.access[ip_3]["login"]
            self.passwd = self.access[ip_3]["passwd"]
            self.server_ip = "localhost" if my_IP==self.access[ip_3]["server_ip"] else self.access[ip_3]["server_ip"]
            self.key = self.access["key"].encode("utf-8")
        except KeyError:
            print("Cannot find entry {} in db_access.data".format(ip_3))
            exit(1)

    def fetch(self, sql, params, one_only=True):
        """execute a SELECT statment with theparameters and fetch one row only"""
        try:
            with pymysql.connect(self.server_ip, self.login, self.passwd, self.dbname) as cursor:
                cursor.execute(sql, params)
                data = cursor.fetchone() if one_only else cursor.fetchall()
        except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as err:
            print(err)
            print(sql)
            print(params)
            return None
        else:
            return data

    def select(self, table, columns='*', one_only=True, **where):
        """build a SELECT statment and fetch its row"""
        sql = "SELECT {} from {}".format(columns, table)
        params = []
        if where:
            where_clause = []
            for col, val in where.items():
                where_clause.append(col+"=%s")
                params.append(val)
            sql += " WHERE " + ",".join(where_clause)
        return self.fetch(sql, params, one_only)



    def execute_sql(self, sql, params):
        try:
            with pymysql.connect(self.server_ip, self.login, self.passwd, self.dbname) as cursor:
                cursor.execute(sql, params)
                # self.db.conn.commit()
                last_row_id = cursor.lastrowid
        except (TypeError, ValueError, pymysql.err.OperationalError) as err:
            print('ERROR on sql execute:', err)
            print(sql)
            print(params)
            last_row_id = None
        return last_row_id

    def update(self, table, **kwargs):
        """update the fields given as parameters with their values using the 'kwargs' dictionary"""
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
                                                          ",".join([c+"=%s" for c, v in col_value]),
                                                          id_col_name)
            self.execute_sql(sql, [v for c, v in col_value] + [ id ])
        return id

    def insert(self, table, **kwargs):
        """INSERT a record in the table"""
        col_value, id, id_col_name, last_row_id = [], None, 'id', None
        for col, val in kwargs.items():
            if col=='id':
                id = val
            elif col=='id_col_name':
                id_col_name = val
            else:
                col_value.append((col, val))
        if col_value:
            sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(table,
                                                              ",".join([c for c, v in col_value]),
                                                              ",".join(["%s" for i in range(len(col_value))]))
            last_row_id = self.execute_sql(sql, [v for c, v in col_value])
        return last_row_id

    def log(self, log_type, code, message, debug=False):
        """
        :param log_type: ENTRY when a user gets in or INFO/WARNING/ERROR for technical issue
        :param code: either the member id concerned by the log entry OR the error code
        :param message: the log message
        --
        -- Table structure for table `tb_log`
        --

        CREATE TABLE `tb_log` (
          `id` int(11) NOT NULL,
          `type` varchar(20) NOT NULL,
          `code` int(11) NOT NULL,
          `message` text NOT NULL,
          `created_on` timestamp NOT NULL DEFAULT current_timestamp()
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

        --
        -- Indexes for dumped tables
        --

        --
        -- Indexes for table `tb_log`
        --
        ALTER TABLE `tb_log`
          MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
        COMMIT;
        :return:
        """
        if debug:
            print(datetime.now(), log_type, code, message)
        return self.insert('tb_log', type=log_type, code=code, message=message)
        # sql = "INSERT INTO tb_log(type, code, message) values (%s,%s,%s)"
        # try:
        #     with pymysql.connect(self.server_ip, self.login, self.passwd, self.dbname) as cursor:
        #         cursor.execute(sql, (log_type, code, message))
        # except pymysql.err.OperationalError as err:
        #     print(err) # cannot log as we have en error!

if __name__ == "__main__":
    db = Database()
    result = db.fetch("select count(*) from users", ())
    print(result)
    row_id = db.log('INFO', 1, "Testing log INSERT", debug=True)
    print(row_id)
    db.update('tb_log', id=row_id, code=2)
    row = db.select('tb_log', id=row_id)
    print(row)