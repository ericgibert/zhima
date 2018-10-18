#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Simple transcation database access

    Connects to the database or emulate a connection

    pre-requisite:
        sudo pip3 install PyMySQL


    sudo systemctl restart httpd
    http://127.0.0.1/phpMyAdmin/

    Transactions table:
    --
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `id` int(11) NOT NULL,
  `member_id` int(11) NOT NULL,
  `type` varchar(20) NOT NULL,
  `description` text NOT NULL,
  `amount` float NOT NULL,
  `currency` varchar(4) NOT NULL,
  `valid_from` date NOT NULL,
  `valid_until` date NOT NULL,
  `created_on` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
from datetime import datetime, timedelta, date
from collections import OrderedDict
from model_db import Database
from member import Member

class Transaction(Database):
    """
    A transaction record in the database - SELECT mode only supported
    """
    def __init__(self, transac_id=None, member_id=None, *args, **kwargs):
        """
        Select a record from the database based on a transactions table id
        :param transac_id: int for transaction table key
        """
        super().__init__(table="transactions", *args, **kwargs)
        self.MEMBERSHIP = Member.MEMBERSHIP
        if transac_id:
            self.get_from_db(transac_id)
        elif member_id:
            member = Member(id=member_id)
            default_membership = self.MEMBERSHIP[0]
            valid_from = max(date.today(), member['validity'])
            self.data = OrderedDict([  #  ('id', None),
                ('member_id', member_id),
                ('type', default_membership[0]),
                ('description', ""),
                ('amount', default_membership[2]),
                ('currency', 'CNY'),
                ('valid_from', valid_from),
                ('valid_until', valid_from+timedelta(days=default_membership[3])),
                ('created_on', datetime.now()) ])
        else:
            self.data = OrderedDict()

    def get_from_db(self, transac_id):
        """Connects to the database to fetch a transaction table record or simulation"""
        self.data = self.select(id=transac_id)
        self.id = transac_id

    def update_member_status(self, member_id):
        """Update the status of a member to OK or NOT_OK accordingly to the mambership payment"""
        result = self.fetch("select max(valid_until) as max_valid from transactions where member_id=%s and right(type,10)='MEMBERSHIP'", params=(member_id,))
        try:
            new_status = 'OK' if result['max_valid']>=date.today() else 'NOT_OK'
        except TypeError:
            new_status = 'NOT_OK'
        member = Member(member_id=member_id)
        member.update(id=member_id, status=new_status)

