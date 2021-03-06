# Dependencies
# bcrypt : pip3 install bcrypt
# mysql : sudo apt-get install python3-pymysql
# tkinter : sudo apt-get install python3-tk

# System Imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
from pathlib import Path            # Gives OS independent path manipulation - coz I'm running on Linux

import time
import random
import datetime

# Our Modules
from tkclock import Clock
from tkdialog import Dialog
from tkdisclaimer import DisclaimerDialog
from tkchangepassword import ChangePasswordDialog
from tkphone import ChangePhoneDialog
from tknewuser import AddUserDialog
from tkmentorpassword import MentorPasswordDialog
from tkaddnotes import AddNotesDialog

import mysqldb
import mypassword as pw  # for password hashing and checking functions

# Custom Colours
DK_BLUE = '#0A5973'

# Custom Fonts
STATUS_FONT = ('verdana', 10, 'normal')
TITLE_FONT = ('verdana', 16, 'normal')
CAPTION_FONT = ('verdana', 10, 'normal')
LIST_FONT = ('verdana', 10, 'normal')
LABEL_FONT = ('verdana', 10, 'normal')
TEXT_FONT = ('verdana', 9, 'normal')
FIXED_FONT = ('courier new', 10, 'normal')
REG_IN_FONT = ('courier new', 10, 'normal')
REG_OUT_FONT = ('courier new', 10, 'overstrike')
TEXT_COLOUR = 'LightSteelBlue4'

# Defines
LIST_WIDTH = 65                     # Width of register list in characters (not pixels)
VERSION = "(V2.7 9-Feb-19)"         # Version number

# Set up our image/icon paths
# This is OS independant so should work on Windows and Linux without change
IMAGE_FOLDER = Path(os.path.dirname(os.path.realpath(__file__))) / "images"

IMG_SIGN_IN = IMAGE_FOLDER / "sign-in.gif"
IMG_SIGN_OUT = IMAGE_FOLDER / "sign-out.gif"
IMG_PLUS = IMAGE_FOLDER / "plus.gif"
IMG_TIMES = IMAGE_FOLDER / "times.gif"
IMG_BOOK = IMAGE_FOLDER / "book.gif"
IMG_BOOK_ICO = IMAGE_FOLDER / "book.ico"


class StatusBar(ttk.Frame):
    """ Status bar with text (left) and embedded clock (right) """
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.columnconfigure(0, weight=1)
        self.staustext=tk.StringVar()        
        self.label=ttk.Label(self, relief=tk.SUNKEN, anchor=tk.W,  
                                     textvariable=self.staustext, style='Status.TLabel')
        self.label.grid(padx=4, pady=4, ipadx=2, sticky=tk.W+tk.E)
        self.label.columnconfigure(0, weight=1)
        self.staustext.set(' Status')
        self.clock = Clock(self)
        self.clock.grid(in_=self.label, sticky=tk.E, pady=4, padx=4)      
        
class TitleBar(ttk.Frame):
    """ Title Bar at top of window """
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.titletext=tk.StringVar() 
        self.label=ttk.Label(self, relief=tk.SUNKEN, anchor=tk.W, justify=tk.LEFT,
                           textvariable=self.titletext,  style='Title.TLabel')
        
        self.titletext.set(' Dojo')
        self.label.grid(padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E+tk.W)        
        self.columnconfigure(0, weight=1)

class RegisterList(ttk.Frame):
    """ List of entries in the register (left-hand side) """
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.captiontext=tk.StringVar()        
        self.caption= ttk.Label(self, relief=tk.FLAT, anchor=tk.W, justify=tk.LEFT,
                           textvariable=self.captiontext, style='Caption.TLabel')
        caption = str.format(" Time In {0:^67} Time Out", "Who's " + random.choice(["in the house", "rolling with the crew", 
                                                            "on the block", "chillin out", "getting jiggy with it",
                                                            "maxin not relaxin", "right here right now"]) +"...")
        self.captiontext.set(caption)
        self.caption.grid(padx=4, ipadx=2, pady=4, ipady=2)
        
        self.yScroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.yScroll.grid(row=1, column=1, sticky=tk.N+tk.S)
        self.listbox = tk.Text(self, yscrollcommand=self.yScroll.set,
                                             width=LIST_WIDTH, height=22,
                                             font=FIXED_FONT)
        self.listbox.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W, padx=0, pady=0, ipadx=0, ipady=4)
        self.yScroll['command'] = self.listbox.yview
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.indojo = {}    # Initialise dictionary for members logged-in
        
class LoginArea(ttk.Frame):
    """ Login fields and botton (on left) """
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.Text1=tk.Text(self, height=5, width=20, relief=tk.FLAT, wrap=tk.WORD)
        self.Text1.insert("1.0", """If you already have a Nickname and Password, enter them below and press the 'Login' button. 

To Logout (when you leave) enter the same details again but press the 'Logout' button.""")
        self.Text1.config(state=tk.DISABLED, font=TEXT_FONT, bg=defaultbg, fg=TEXT_COLOUR)
        self.Text1.grid(row=0, column=0, columnspan=2, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E+tk.W)
        self.rowconfigure(0, weight=0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        self.lframe = tk.LabelFrame(self)
        self.lframe.grid(row=1, column=0, padx=8, pady=4, ipadx=4, ipady=4, columnspan=2, sticky=tk.E+tk.W)
        
        self.nickname_label=ttk.Label(self.lframe, relief=tk.FLAT, anchor=tk.E, text='Nickname', style='Label.TLabel')
        self.nickname_label.grid(row=0, column=0, padx=4, pady=8, ipadx=2, ipady=2, sticky=tk.E)
        self.nickname_entry=ttk.Entry(self.lframe, width=30)
        self.nickname_entry.grid(row=0, column=1, padx=4, pady=8, ipadx=2, ipady=2)

        self.password_label=ttk.Label(self.lframe, relief=tk.FLAT, anchor=tk.E, text='Password', style='Label.TLabel')
        self.password_label.grid(row=1, column=0, padx=4, pady=8, ipadx=2, ipady=2, sticky=tk.E)
        self.password_entry=ttk.Entry(self.lframe, width=30, show='*')
        self.password_entry.grid(row=1, column=1, padx=4, pady=8, ipadx=2, ipady=2)
        
        self.lframe.grid_columnconfigure(0, weight=1)
        self.lframe.grid_columnconfigure(1, weight=1)

        button_width = 16
        self.login_img = tk.PhotoImage(file=IMG_SIGN_IN)
        self.login = ttk.Button(self.lframe, compound=tk.LEFT, image=self.login_img, default=tk.ACTIVE,
                                               text='Login', width=button_width, style="LButton.TButton")
        self.login.grid(row=2, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.W)

        self.logout_img = tk.PhotoImage(file=IMG_SIGN_OUT)
        self.logout = ttk.Button(self.lframe, compound=tk.LEFT, image=self.logout_img,
                                                 text='Logout', width=button_width, style="LButton.TButton")
        self.logout.grid(row=2, column=1, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        

        self.Text2=tk.Text(self, height=8, width=28, relief=tk.FLAT, wrap=tk.WORD)
        self.Text2.insert("1.0", """If you DON'T already have a Nickname and Password, press 'Add New User' to create a new account. 

Next time you login or logout you will use the boxes above.""")
        self.Text2.config(state=tk.DISABLED, font=TEXT_FONT, bg=defaultbg, fg=TEXT_COLOUR)
        self.Text2.grid(row=3, column=0, columnspan=1, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E+tk.W)
        self.rowconfigure(3, weight=0)

        self.newuser_img = tk.PhotoImage(file=IMG_PLUS)
        self.newuser = ttk.Button(self, compound=tk.LEFT, image=self.newuser_img,
                                                    text='Add New User', width=button_width, style="LButton.TButton")
        self.newuser.grid(row=3, column=1, padx=4, pady=16, ipadx=2, ipady=2, sticky=tk.W)
        

        self.Text3=tk.Text(self, height=8, width=28, relief=tk.FLAT, wrap=tk.WORD)
        self.Text3.insert("1.0", """If you want to change your password, or can't remember what it is and want to reset it use 'Change Password'.

You will need a Mentor's help if you cannot remember your password.""")
        self.Text3.config(state=tk.DISABLED, font=TEXT_FONT, bg=defaultbg, fg=TEXT_COLOUR)
        self.Text3.grid(row=4, column=1, columnspan=1, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E+tk.W)
        self.rowconfigure(4, weight=0)

        self.changepw_img = tk.PhotoImage(file=IMG_BOOK)
        self.changepw = ttk.Button(self, compound=tk.LEFT, image=self.changepw_img,
                                                    text='Change Password', width=button_width, style="LButton.TButton")
        self.changepw.grid(row=4, column=0, padx=4, pady=16, ipadx=2, ipady=2, sticky=tk.E)
        
        self.exit_img = tk.PhotoImage(file=IMG_TIMES)
        self.exit_ = ttk.Button(self, compound=tk.LEFT, image=self.exit_img,
                                                    text='Shutdown', width=button_width, style="LButton.TButton")
        self.exit_.grid(row=5, padx=4, pady=8, ipadx=2, ipady=2, sticky=tk.W+tk.S)
        self.rowconfigure(5, weight=1)


class Register(ttk.Frame):
    """ Main Register Class - window layout defined here """
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        self.titlebar = TitleBar(self)
        self.titlebar.grid(sticky=tk.N+tk.E+tk.W, columnspan=2)
        
        self.login = LoginArea(self)
        self.login.grid(row=1, stick=tk.N+tk.S, pady=4)
        
        self.registerlist = RegisterList(self)
        self.registerlist.grid(row=1, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.statusbar = StatusBar(self)
        self.statusbar.grid(row=3, sticky=tk.S+tk.E+tk.W, columnspan=2)
        
        parent.protocol("WM_DELETE_WINDOW", self.Shutdown)
     
        parent.bind("<Return>", self.Login)
        parent.bind("<Escape>", self.ClearDetails)

        self.login.login.configure(command=self.Login)
        self.login.exit_.configure(command=self.Shutdown)
        self.login.logout.configure(command=self.Logout)
        self.login.newuser.configure(command=self.NewUser)
        self.login.changepw.configure(command=self.ChangeUserPassword)

        # Load our current Dojo and set the title accordingly
        self.dojo = mysqldb.GetDojo()
        if( self.dojo == None ):
            self.statusbar.staustext.set(" Houston we have a problem... Where's the data?")
            return
        else:
            self.titlebar.titletext.set(str.format(' Dojo #{0} : {1:%a %d %b %Y}', self.dojo['DojoId'], self.dojo['DojoDate']))
            self.statusbar.staustext.set(" Ready for action...")
        
        self.dojoid = self.dojo['DojoId']   # Cache this as we'll use it quite a bit

        # Load the current register entries for today (may be empty)
        self.LoadRegister()

        # Load the disclaimer
        self.disclaimer = DisclaimerDialog(self)

        # 'Current' user - used to cache details from database
        self.user = None
        self.ClearDetails()

     
    def LoadRegister(self):
        ''' Delete all entries in register list and re-load '''
        # Load the current register entries for today (may be empty)
        self.registerlist.listbox.delete("0.0", tk.END)
        registerlist = mysqldb.GetRegisterList(self.dojoid)
        self.incount = 0
        self.outcount = 0
        for reg in registerlist:
            line = self.GetListEntry(reg['Login'], reg['Logout'], reg['NickName'], reg['FirstName'], reg['LastName'], reg['UserType'] == "Mentor")
            self.registerlist.indojo[reg['UserID']] = tk.IntVar()
            if( not reg['Logout'] == None and reg['Logout'] > reg['Login'] ):
                rin = False
                self.outcount += 1
            else:
                self.incount += 1
                rin = True

            if( rin ):
                cb = tk.Checkbutton(self, text=line, font=REG_IN_FONT, variable=self.registerlist.indojo[reg['UserID']])
            else:
                cb = tk.Checkbutton(self, text=line, font=REG_IN_FONT, state=tk.DISABLED)
            # If we not doing the first entry then insert a new-line first
            if( not ((self.incount == 1 and self.outcount == 0) or (self.incount == 0 and self.outcount == 1))):
                self.registerlist.listbox.insert("1.end", "\n")
            self.registerlist.listbox.window_create("1.0", window=cb)
            self.registerlist.listbox.bind("<BackSpace>", lambda x : "break")   # Disable backspace
            self.registerlist.listbox.bind("<Delete>", lambda x : "break")      # Disable delete

        if( self.incount > 0 or self.outcount > 0 ):
            self.UpdateStatus()
        
    def GetListEntry(self, login, logout, nickname, firstname, lastname, mentor):
        ''' Format the data for an entry in the list '''
        if(mentor):
            name = "(M) " + str.format("{0} {1}", firstname, lastname)
        else:
            name = str.format("{0} {1}", firstname, lastname)
        if( not logout == None and logout > login ):
            out = str.format('{0:%H:%M}', logout)
        else:
            out = "     "
        line = str.format(' {0:%H:%M}  {1:17} {2:29} {3} ', login, nickname, name, out)

        return line
            
    def UpdateStatus(self, msg = 'Ready for action...'):
        self.statusbar.staustext.set(str.format(" {0} {1} In : {2} Out", msg, self.incount, self.outcount ))
        
    def Shutdown(self, parent=None):
        if( tk.messagebox.askyesno("Going to shutdown now...", "Really?\n\nAre we really done?\n\nYou sure?")):
            if( AddNotesDialog(root, title="Update the Dojo Notes...").result == 1 ):
                # Close our DB Connection
                mysqldb.DBConnection(True)
                self.parent.quit()

    def ChangeUserPassword(self):
        tkchpw = ChangePasswordDialog(root, title="Change Password", user=self.user)

    def WelcomeFred(self):
        messages = ["Hey Fred - welcome back to Dojo",
                    "How's it going?",
                    "Isn't it great when you get a *personal* welcome?",
                    "I bet this really improves the end-user experience.",
                    "Nearly done now...",
                    "Just one more to go...",
                    "Before the next one comes up...",
                    "and then you'll be done. Logged in.",
                    "Finally.",
                    "You made it.",
                    "Well done.",
                    "Is it time to leave yet?",
                    "See you again real soon!",
                    "Oh - one more thing...",
                    "Nevermind - I 'll ask you next time..."
                    ]
        for msg in messages:
            tk.messagebox.showinfo("Welcome Back Fred!", msg)

            
    def Login(self, parent=None, nname=None, npassword=None):
        if( nname == None and npassword == None ):
            name = self.login.nickname_entry.get()
            password = self.login.password_entry.get()
        else:
            name = nname
            password = npassword

        if( name == "" or password == "" ):
            tk.messagebox.showerror("Doofus Error", "It *really* helps if you provide a Nickname AND a Password...\n\nTry again...")
            return
        # See if this nickname is valid before we check password
        self.user = mysqldb.GetUser(name)
        if(  self.user == None ):
            tk.messagebox.showerror("Ponderous Error", "We don't have a record of that Nickname...\n\nDo you need to register as a New User?")
            return
        # First check the new password - if not found then check the old one
        # If the old one is found and it matches then generate a new hash for next time     
        if( not pw.CheckPassword(self.user['Hash'], password) ):
            # We don't have the new style password - so check old
            if( not pw.CheckOldPassword(self.user['Password'], password)):
                tk.messagebox.showerror("Memslip Error", "Nope. That's not the password used with this Nickname.\n\nTry again hacker...")
                return
            # Old style password OK - so create new hash for next time
            mysqldb.SetPassword(self.user['UserID'], password)

        # OK - we have a valid login attempt - but are we already logged in?
        # If so then ask if we want to logout
        register = mysqldb.GetRegister(self.dojoid, self.user['UserID'])
        if( not register == None and register['Logout'] == None ):
            if(tk.messagebox.askyesno("Logout?", "You're already logged-in. Do you want to logout now?")):
                self.Logout()
            return
        
        # Finally - show the disclaimer
        if( not self.disclaimer.ShowDisclaimer() ):
            tk.messagebox.showerror("Nocompliance Error", "Doh! - You have to accept the disclaimer to log in (and stay at the Dojo).\n\nTry again...")
            return
        
        # Now check that we have a contact number for people under 18 - show last one recorded - update if changed
        needcontact, contactnumber = mysqldb.GetContactNumber(self.user['UserID'])
        if( needcontact ):
            ChangePhoneDialog(root, title="Check Your Contact Number", user=self.user, number=contactnumber)

        # add to register, the list and increase login count
        mysqldb.Login(self.user['UserID'])

        self.LoadRegister()     # Update the Register List
        
        if(self.user['LastSeen'] != None):
            tk.messagebox.showinfo("Welcome Back " + self.user['FirstName'] + "!", 
                "Hi " + self.user['FirstName'] + 
                ", you are now logged in.\n\nYou last logged in at: " + self.user['LastSeen'].strftime('%H:%M on %a %d-%b-%y') + 
                "\n\nWelcome back!")
        else:
            tk.messagebox.showinfo("Welcome " + self.user['FirstName'] + "!", 
                "Hi " + self.user['FirstName'] + ", you are now logged in.\n\nHope you enjoy the dojo.")

        # Give Fred a special welcome 'fredjellis' = 17
        #if self.user['UserID'] == 17:
        #    self.WelcomeFred()

        self.ClearDetails()

            
    def Logout(self, parent=None):
        # We have a dictionary of the member (nicknames) and a flag for the check-box
        # If we have any 'ticks' we will assume we are performing a 'mentor logout' of one or more members
        # Mentor has to provide their username/password then all 'ticked' users will be logged out
        locount = 0
        incount = 0
        for member, flag in self.registerlist.indojo.items():
            incount += 1
            if(flag.get()):
                locount += 1

        if( locount >= 1 ):
            if(tk.messagebox.askyesno("Mentor Logout", "You have select " + str(locount) + \
                " users to logout.\n\nYou need to be a mentor to do this.\n\nProceed?\n\n" + \
                " (Did you know there's a new feature that logs out all users without all that tedious ticking as well?)")):
                doit = MentorPasswordDialog(root, "Mentor Multi-Logout", None).result 
                if( doit == 1 ):
                    # OK - log them all out
                    for member, flag in self.registerlist.indojo.items():
                        if(flag.get()):
                            mysqldb.Logout(member)
                    self.LoadRegister()
                    return       
            return

        name = self.login.nickname_entry.get()
        password = self.login.password_entry.get()
        if( name == "" or password == "" ):
            tk.messagebox.showerror("Shnazbot Error", "Am I supposed to guess who you are?\n\nPerhaps you expect me to smell you?\n\nIt *really* helps if you provide a Nickname AND a Password...\n\nTry again...")
            return

        # See if this nickname is valid before we check password
        self.user = mysqldb.GetUser(name)
        if(  self.user == None ):
            tk.messagebox.showerror("Ponderous Error", "We don't have a record of that Nickname...\n\nLook in the list for your Nickname...")
            return
        if( not pw.CheckPassword(self.user['Hash'], password) ):
            if( not pw.CheckOldPassword(self.user['Password'], password)):
                tk.messagebox.showerror("Memslip Error", "Nope. That's not the password used with this Nickname.\n\nTry again hacker...")
                return

        # OK - we have a valid login attempt - but are we already logged out?
        register = mysqldb.GetRegister(self.dojoid, self.user['UserID'])
        if( register == None or not register['Logout'] == None ):
            if(tk.messagebox.askyesno("Login?", "You're already logged OUT! Do you want to log in again?")):
                self.Login()
            return

        # If a mentor logs out we will offer an option to log out everyone else at the same time
        # even if no others selected - saves tedious selection...
        if( mysqldb.GetMentor(name, password) != None and incount > 1):
            if(tk.messagebox.askyesno("Group Logout", "Hey Mentor - do you want to log out the other " + str(incount-1) + " users at the same time?")):
                for member, flag in self.registerlist.indojo.items():
                    mysqldb.Logout(member)
                self.LoadRegister()
                return       

        # We can  now log out, update the list and counts.
        # Easiest way is to update register and then re-load the whole list
        mysqldb.Logout(self.user['UserID'])
        self.incount -= 1
        self.outcount += 1
        self.UpdateStatus()
        tk.messagebox.showinfo("See Ya!", "You are now logged out\n\nCome back soon!")
        self.ClearDetails()
        self.LoadRegister()
            
    def NewUser(self):
        if( tk.messagebox.askyesno("Adding new user...", "Hey welcome!\n\nDid you really want to create a new user?")):
            result = AddUserDialog(root, "Welcome Padawan").result
            # If we have the new details then we will log them in immediately
            if( result != None and result[0] != None and result[1] != None ):
                self.Login(nname=result[0], npassword=result[1])

    def ClearDetails(self, parent=None):
        self.login.nickname_entry.delete(0, tk.END)
        self.login.password_entry.delete(0, tk.END)
        self.login.nickname_entry.focus_set()

# Our main program loop - sets window title and size then executes mainloop()
if __name__ == "__main__":
    root = tk.Tk()
    # Start maximised (get screen dimensions and use to set geometry)
    root.geometry("%dx%d+0+0" % (root.winfo_screenwidth(), root.winfo_screenheight()))
    root.title("Dojo Register " + VERSION)
    if(os.name == 'nt'):                  # Windows reports as 'nt' - Linux as 'posix'
        root.wm_iconbitmap(IMG_BOOK_ICO)  # Icon doesn't work on Linux - probably need different format file
    root.columnconfigure(0, weight=1)     # We want to resize and use all window width
    root.rowconfigure(0, weight=1)        # We want to resize and use all window height
    defaultbg = root.cget('bg')

    # ttk Styles
    s = ttk.Style()
    s.configure('Title.TLabel', font=TITLE_FONT,  background=DK_BLUE, foreground='white')   
    s.configure('Status.TLabel', font=STATUS_FONT)
    s.configure('Caption.TLabel', font=CAPTION_FONT)
    s.configure('Label.TLabel', font=LABEL_FONT)
    s.configure('LButton.TButton', anchor=tk.W+tk.E )
    s.configure('Label.Fixed', font=FIXED_FONT)

    # Create the main frame for our widgets
    Register(root, padding=(2, 2, 2, 2)).grid(sticky=tk.N+tk.S+tk.E+tk.W)
    
    root.mainloop()
