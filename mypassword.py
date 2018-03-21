import hashlib
import os
import bcrypt

# We will support two methodologies - the 'Old' uses a fixed Salt from an environment variable.
# The newer version will use a user-specific salt and bcrpyt functions.
# The code will migrate only 'old' users to the new methodology when they next log in - eventually we will deprecate the old methodology 

# Old Salt is stored in an environment variable and must not change once passwords have been hashed
# All systems accessing the passwords need the same salt
oursalt = os.environ['RegisterSalt'].encode('utf-8')

def GetPasswordHash(password, salt_ = None):
    ''' Convert a password (string) into a hash value 
        if no salt_ is provided a new one is created.
        bcrypt encodes the salt into the first part of the hash so passing in the hash provides the salt
        that was used to generate the hash originally '''
    if( salt_ == None ): salt_ = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt_)

def GetOldPasswordHash(password):
    return hashlib.sha512(password.encode('utf-8') + oursalt).hexdigest()
    
def CheckPassword(hash_, password):
    ''' Check that the hash provided matches the hash generated from the
        password string provided - Returns True if they match '''
    myhash = GetPasswordHash(password, hash_.encode("utf-8"))
    return (myhash == hash_) 

def CheckOldPassword(hash_, password):
    ''' Check that the hash provided (128 character) matches the hash generated from the
        password string provided 
        Returns True if they match '''
    myhash = GetOldPasswordHash(password)
    return (myhash == hash_) 
        
# Test Code
if __name__ == "__main__":
  
    while 1:
        password = input('Input password: ')
        hash1 = GetPasswordHash(password)
        print( hash1 )
        
        p2 = input('Same Password?: ')
        hash2 = GetPasswordHash(p2, hash1)
        print( hash2 )
        
        print('Passwords match? :', CheckPassword(hash1, p2))
