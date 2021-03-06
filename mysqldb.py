# MySQL Access functions
import pymysql
import datetime
import os
from pathlib import Path            # Gives OS independent path manipulation

import mypassword as pw  # for password hashing and checking functions

connection = None        # Our database connection

# Get our current install/running location - SSL certificates are in the sub-folder .\SSL
# (Assumes we're running on Windows)
dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
ssl_path = dir_path / "ssl"

def CloseDB():
    DBConnection(True)


def DBConnection(close=False):
    ''' Open or close the database connection
    Returns the current connection if already open
    '''
    password = os.getenv('RegisterPassword')
    if( password == None ):
        print("You need to set the Environment variable: RegisterPassword")
        return None

    
    global connection
    if(close and connection != None):
        connection.close()
        connection = None
    else:
        if connection == None:
            connection = pymysql.connect(host='horshamcoderdojo.org.uk',
                                         user='register',
                                         password=password,
                                         db='register',
                                         charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor,
                                         ssl={'key': ssl_path / 'client-key.pem', 'cert': ssl_path / 'client-cert.pem'})

    return connection


def GetDojo():
    ''' Get the current Dojo
    This creates a new Dojo record if one does not exist for today's date
    If one already exists then return it
    Opens database connection if not already open (does not close it)
    '''
    con = DBConnection()

    try:
        with con.cursor() as cur:
            sql = "SELECT DojoId, DojoDate, Title, Notes FROM Dojo WHERE DojoDate = CURDATE()"
            cur.execute(sql)
            row = cur.fetchone()

            if row == None:
                # Create a new row for today's Dojo - only need to set date - the ID is automatically
                # incremented with each row
                sql = "INSERT INTO Dojo (DojoDate) VALUES (CURDATE())"
                cur.execute(sql)
                con.commit()
            # Now read in this row...
                row = GetDojo()

    except Exception as e:
        print("Error : ", e)
    finally:
        pass

    return row

def AddDojoNotes(title, notes):
    ''' Add a title and notes to the current Dojo record
    '''
    # Get currnt Dojo
    dojo = GetDojo()

    con = DBConnection()
    
    try:
      with con.cursor() as cur:
            sql = '''UPDATE Dojo SET Title = %s, Notes = %s WHERE DojoId = %s'''

            cur.execute(sql, (title, notes, dojo['DojoId']))
            con.commit()

    except Exception as e:
        print("Error : ", e)
    finally:
        pass

def LoadUser(lookfor, column='UserID'):
    '''Get an existing user record, pass in the thing to look for in 'lookfor' ,
    and the column to search in 'lookin'.
    lookin could be UserID (default) or NickName
    '''
    con = DBConnection()

    try:
        with con.cursor() as cur:
            sql = '''SELECT UserID, FirstName, LastName, NickName, 
                      Password, CreatedDate, DOB, UserType, LastUpdate,
                      ContactNumber, Hash FROM User WHERE '''

            if(column == 'UserID'):
                sql += 'UserID = %s'
            elif(column == 'NickName'):
                sql += 'NickName = %s'
            else:
                return None
            cur.execute(sql, lookfor)
            row = cur.fetchone()
            return row

    except Exception as e:
        print("Error : ", e)
    finally:
        pass

    return None

def GetContactNumber(userid):
    ''' Get the current contact number for a user, if they're under 18 then return False as not needed '''
    user = LoadUser(userid)
    if( user == None ): # Problem - where's this user gone?
        return False, None

    today = datetime.date.today()
    born = user['DOB']
    if( not born == None ):
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    else:
        age = 18
    if( age < 18 ):
        return True, user['ContactNumber']
    else:
        return False, None

def UpdateContactNumber(userid, contactnumber):
    ''' Update the existing contact number with the new one provided '''
    user = LoadUser(userid)
    if( user['ContactNumber'] == contactnumber or contactnumber == "" ):
        return

    # Need to update as different
    now_timestamp = datetime.datetime.now().isoformat()

    con = DBConnection()

    try:
        with con.cursor() as cur:
            sql = '''UPDATE User SET ContactNumber = %s, LastUpdate = %s WHERE UserID = %s'''

            cur.execute(sql, (contactnumber, now_timestamp, userid))
            con.commit()

    except Exception as e:
        print("Error : ", e)
    finally:
        pass


def AddNewUser(user):
    '''Add a new user record
    the 'user' argument is a dictionary of columns/values to create the record
    Will fail of the NickName is not unique.
    UserID is automatically allocated on creation

    Passwords provided are converted to hash (if provided) or None if not

    FirstName, LastName, NickName, DOB, ContactNumber are the only values used '''
    # Deal with case where Nickname not in the dictionary (or it's blank)
    if ('NickName' not in user or user['NickName'] == ''):
        return -1, "User must have a NickName"

    if(GetUser(user['NickName']) != None):
        return -2, "A user already exists with that NickName"

    # Valid to not have a password in the dictionary
    # Need to test so we don't throw an exception
    if('Password' in user and user['Password'] != ''):
        passwordhash = pw.GetPasswordHash(user['Password'])
    else:
        passwordhash = None

    con = DBConnection()

    now_date = datetime.date.today().strftime('%Y-%m-%d')
    now_timestamp = datetime.datetime.now().isoformat()

    # Add our additional items to the user dictionary
    user['Password'] = passwordhash
    user['CreatedDate'] = now_date
    user['UserType'] = 'Student'        # This can be over-ridden later
    user['LastUpdate'] = now_timestamp

    try:
        with con.cursor() as cur:
            sql = '''
                    INSERT INTO User (NickName, FirstName, LastName, DOB, ContactNumber, Hash, 
                    CreatedDate, UserType, LastUpdate) 
                    VALUES (%(NickName)s, %(FirstName)s, %(LastName)s, %(DOB)s, %(ContactNumber)s, 
                    %(Password)s, %(CreatedDate)s, %(UserType)s, %(LastUpdate)s)
                    '''
            cur.execute(sql, user)
            con.commit()
            return 0, "OK"  # No problems here

    except Exception as e:
        print("Error : ", e)
    finally:
        pass

    return -3, "Something went wrong..."


def GetUser(nickname):
    ''' Get the UserID, password hash and name for a NickName '''
    if(nickname == ''):
        return None

    con = DBConnection()

    try:
        with con.cursor() as cur:
            sql = '''
            SELECT
                UserID,
                NickName,
                Password,
                FirstName,
                LastName,
                (SELECT
                    Register.Login
                FROM
                    Register
                WHERE
                    Register.UserID = User.UserID
                ORDER BY
                    Register.Login DESC
                LIMIT 1)
                AS LastSeen,
                Hash
            FROM
                User
            WHERE 
                NickName = %s'''

            cur.execute(sql, nickname)
            row = cur.fetchone()
            if(row == None):
                return None

            return row

    except Exception as e:
        print("Error : ", e)
    finally:
        pass

    return None

def GetMentor(nickname, password):
    ''' Get a mentor - returns None if UserType != Mentor '''
    mentor = LoadUser(nickname, "NickName")
    if( mentor == None ):
        return None

    if(not pw.CheckPassword(mentor["Hash"], password)):
        return None

    if( mentor["UserType"] != "Mentor"):
        return None

    return mentor
    
def SetPassword(userid, password):
    ''' Set a user's password - identified by UserID
       Converts password (string) into a bcrypt hash '''
    passwordhash = pw.GetPasswordHash(password)
    now_timestamp = datetime.datetime.now().isoformat()

    con = DBConnection()

    try:
        with con.cursor() as cur:
            sql = '''UPDATE User SET Hash = %s, LastUpdate = %s WHERE UserID = %s'''

            cur.execute(sql, (passwordhash, now_timestamp, userid))
            con.commit()

    except Exception as e:
        print("Error : ", e)
    finally:
        pass

def GetRegisterList(dojoid):
    ''' Get a list of all entries for this dojoid 
        returns a list of tuples containing data (may be empty) '''
    con = DBConnection()

    try:
        with con.cursor() as cur:
            sql = '''SELECT User.UserID, User.NickName, User.FirstName, User.LastName, Register.Login, Register.Logout, User.UserType 
                     FROM Register 
                     LEFT JOIN User on User.UserID = Register.UserID
                     WHERE DojoID = %s
                     ORDER BY Register.Login'''

            cur.execute(sql, dojoid)
            row = cur.fetchall()
            return row
            
    except Exception as e:
        print("Error : ", e)
    finally:
        pass

    return None


def GetRegister(dojoid, userid):
    '''Get a register row for this dojo and user'''
    con = DBConnection()

    try:
        with con.cursor() as cur:
            sql = '''SELECT UserID, DojoID, Login, Logout FROM Register WHERE UserID = %s AND DojoID = %s
                       ORDER BY Login Desc'''

            cur.execute(sql, (userid, dojoid))
            row = cur.fetchone()
            return row  # May be None

    except Exception as e:
        print("Error : ", e)
    finally:
        pass

    return None


def AddRegister(dojoid, userid):
    ''' Add a new Register entry and record the Login time '''
    con = DBConnection()

    row = {'UserID': userid,
           'DojoID': dojoid,
           'Login': datetime.datetime.now().isoformat()}

    try:
        with con.cursor() as cur:
            sql = '''INSERT into Register (UserID, DojoID, Login) 
                      VALUES (%(UserID)s, %(DojoID)s, %(Login)s)'''

            cur.execute(sql, row)
            con.commit()

    except Exception as e:
        print("Error : ", e)
    finally:
        pass


def Login(userid):
    ''' Record a user login - only if not already logged in (and not logged out) today '''
    dojo = GetDojo()
    dojoid = dojo['DojoId']

    row = GetRegister(dojoid, userid)
    if (row != None):
        # We have a register entry - may have logged out so need to create a new login
        # may not have yet logged out - this is an error so report already
        # logged in
        if(row['Logout'] == None):
            return -1, "User already logged in - logout if you want to login again..."

    AddRegister(dojoid, userid)
    return 0, "OK"


def Logout(userid):
    ''' record a user logout - only valid if already logged in today '''
    dojo = GetDojo()
    dojoid = dojo['DojoId']

    row = GetRegister(dojoid, userid)
    if(row == None):
        return -1, "User is not currently logged in."

    now_timestamp = datetime.datetime.now().isoformat()

    con = DBConnection()

    try:
        with con.cursor() as cur:
            sql = '''UPDATE Register SET Logout = %s WHERE UserID = %s
                      AND DojoId = %s AND Logout IS NULL'''

            cur.execute(sql, (now_timestamp, userid, dojoid))
            con.commit()
            return 0, "OK"

    except Exception as e:
        print("Error : ", e)
    finally:
        pass

    return -2, "Something bad happened..."

# Test Code
if __name__ == "__main__":
    row = GetDojo()
    print('Dojo: ', row)

    rows = GetRegisterList(row['DojoId'])
    print('Register: ', rows)    
    
    id = GetUserID('gmac')
 
    ret, err = Login(id)

    if(ret):
        print('Login Error: ', err)

    rows = GetRegisterList(row['DojoId'])
    print('Register: ', rows)    
 
    ret, err = Logout(id)

    if(ret):
        print('Logout Error: ', err)
