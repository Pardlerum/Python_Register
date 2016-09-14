import hashlib
import os

# Salt is stored in an environment variable and must not change once passwords have been hashed
# All systems accessing the passwords need the same salt
oursalt = os.environ['RegisterSalt'].encode('utf-8')

def GetPasswordHash(password):
    ''' Convert a password (string) into a 128 character hash value '''
    return hashlib.sha512(password.encode('utf-8') + oursalt).hexdigest()
    
def CheckPassword(hash_, password):
    ''' Check that the hash provided (128 character) matches the hash generated from the
       password string provided 
       Returns True if they match '''
    myhash = GetPasswordHash(password)
    return (myhash == hash_) 
        
# Test Code
if __name__ == "__main__":
    while 1:
        password = input('Input password: ')
        hash1 = GetPasswordHash(password)
        print( hash1 )
        
        p2 = input('Same Password?: ')
        hash2 = GetPasswordHash(p2)
        print( hash2 )
        
        print('Passwords match? :', CheckPassword(hash1, p2))
