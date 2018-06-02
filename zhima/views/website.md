Zhima Website "How To"
======================

Member fields
-------------

 - Id: member unique Xin Che Jian Id
 - Openid: WeChat Open Id used for linking a Member to its WeChat account
 - RFID: MIFARE card ID used by the Memebr (cab be a personal card or a XCJ member card)
 - Username: unique user name to allow the consultation of this website's pages
 - Passwd: the password associated to this account
 
 - Avatar url: link to a WeChat photo - not currently used
 
 - Email: email (duh!)
 
 - Satus: important field evaluated every night (OK --> NOT_OK if membership is running out of time):
    - OK: member is valid and has paid its dues
    - NOT_OK: member is valid but did not paid its dues
    - Invalid: member no longer valid but we keep track of its records, especially if it has transactions
    
 - Role:
    - Visitor: temporary registered member
    - Member: basic membership
    - Master: Member + access to machine room i.e. has received the necessary training
    - Group: association within XCJ of members allowed to create event QR Codes for its participants
    - Staff: Master + adminsitration privileges on this website to manage member list and their transactions
    - Admin: website administrator / all privileges on database access
    
    
 - City, Province, Country: geographic info
 - Gender:
    - Unassigned: default value, keep it if you do not like Male or Female
    - Male or Female
    - Event: creation of events - see below

 - Language: on the form zh_CN or en_UK i.e. language and local code
 
Calculated fields: not editable

  - Last Active Type: last message  posted in the LOG table for that member
  - Last Active Time: datetime of that LOG entry
  - Create Time: datetime of this member record's creation
  - Last update: datetime the this member's record last update
  - Validity: memership validity last day i.e. valid until <date>
 
 

How To: New Member Creation
---------------------------

Connect to the site with an account having a **role** 'Staff' or greater.

In the top menu, choose 'Members' and click on the link _/members/new_. A blank form is presented.

 - Replace in the *Username* field "<New>" by name agreed with member. It must be unique in the database. WeChat Id is a suggestion.
 - *Passwd* and *Passwdchk* must be identical: this is the user's password. This password is encrypted.
 - *Email* is optional but strongly recommended since notifications are only sent by email.

Adjust "Role" as necessary. Statuus will be defaulted to "NOT_OK" until first membership payment is recorded.


 


