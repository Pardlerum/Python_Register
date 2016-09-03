import hashlib


# This is our secret 'salt' - must be same for all programs that need to check passwords
# If this value is changed once passwords have been created they will all break and cannot be decoded!
# (So don't change this value unless you REALLY know what you're doing - and keep a copy
#  of the old value just in case...)
# 67813abf79eb495bb3844501d50966cc
oursalt = '67813abf79eb495bb3844501d50966cc'.encode('utf-8')

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
