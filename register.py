# System Imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

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
FIXED_FONT = ('courier new', 10, 'normal')
REG_IN_FONT = ('courier new', 10, 'normal')
REG_OUT_FONT = ('courier new', 10, 'overstrike')

# Defines
LIST_WIDTH = 65         # Width of register list in characters (not pixels)

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

        self.lframe = tk.LabelFrame(self)
        self.lframe.grid(row=0, column=0, padx=4, pady=8, ipadx=4, ipady=4, columnspan=2, sticky=tk.E)
        
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
        self.login_img = tk.PhotoImage(file='images\\sign-in.gif')
        self.login = ttk.Button(self.lframe, compound=tk.LEFT, image=self.login_img, default=tk.ACTIVE,
                                               text='Login', width=button_width, style="LButton.TButton")
        self.login.grid(row=2, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.W)

        self.logout_img = tk.PhotoImage(file='images\\sign-out.gif')
        self.logout = ttk.Button(self.lframe, compound=tk.LEFT, image=self.logout_img,
                                                 text='Logout', width=button_width, style="LButton.TButton")
        self.logout.grid(row=2, column=1, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        
        self.newuser_img = tk.PhotoImage(file='images\\plus.gif')
        self.newuser = ttk.Button(self, compound=tk.LEFT, image=self.newuser_img,
                                                    text='Add New User', width=button_width, style="LButton.TButton")
        self.newuser.grid(row=3, column=1, padx=4, pady=16, ipadx=2, ipady=2, sticky=tk.E)
        
        self.changepw_img = tk.PhotoImage(file='images\\book.gif')
        self.changepw = ttk.Button(self, compound=tk.LEFT, image=self.changepw_img,
                                                    text='Change Password', width=button_width, style="LButton.TButton")
        self.changepw.grid(row=4, column=1, padx=4, pady=16, ipadx=2, ipady=2, sticky=tk.E)
        
        self.exit_img = tk.PhotoImage(file='images\\times.gif')
        self.exit_ = ttk.Button(self, compound=tk.LEFT, image=self.exit_img,
                                                    text='Shutdown', width=button_width, style="LButton.TButton")
        self.exit_.grid(row=5, padx=4, pady=64, ipadx=2, ipady=2, sticky=tk.W+tk.S)
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
        self.login.grid(row=1, stick=tk.N, pady=25)
        
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
            line = self.GetListEntry(reg['Login'], reg['Logout'], reg['NickName'], reg['FirstName'], reg['LastName'])
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
                self.registerlist.listbox.insert("end", "\n")
            self.registerlist.listbox.window_create("end", window=cb)

        if( self.incount > 0 or self.outcount > 0 ):
            self.UpdateStatus()
        
    def GetListEntry(self, login, logout, nickname, firstname, lastname):
        ''' Format the data for an entry in the list '''
        name = str.format("({0} {1})", firstname, lastname)
        if( not logout == None and logout > login ):
            out = str.format('{0:%H:%M}', logout)
        else:
            out = "     "
        line = str.format(' {0:%H:%M}  {1:14} {2:32} {3} ', login, nickname, name, out)

        return line
            
    def UpdateStatus(self, msg = 'Ready for action...'):
        self.statusbar.staustext.set(str.format(" {0} {1} In : {2} Out", msg, self.incount, self.outcount ))
        
    def Shutdown(self, parent=None):
        if( tk.messagebox.askyesno("Going to shutdown now...", "Really?\n\nAre we really done?\n\nYou sure?")):
            # Close our DB Connection
            mysqldb.DBConnection(True)
            self.parent.quit()

    def ChangeUserPassword(self):
        tkchpw = ChangePasswordDialog(root, title="Change Password", user=self.user)

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
        if( not pw.CheckPassword(self.user['Password'], password) ):
            tk.messagebox.showerror("Memslip Error", "Nope. That's not the password used with this Nickname.\n\nTry again hacker...")
            return

        # OK - we have a valid login attempt - but are we already logged in?
        # If so then ask if we want to logout
        register = mysqldb.GetRegister(self.dojoid, self.user['UserID'])
        if( not register == None and register['Logout'] == None ):
            if(tk.messagebox.askyesno("Logout?", "You're logged-in. Do you want to logout now?")):
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
        
        tk.messagebox.showinfo("Welcome Back!", "You are now logged in")
        self.ClearDetails()

            
    def Logout(self, parent=None):
        # We have a dictionary of the member (nicknames) and a flag for the check-box
        # If we have any 'ticks' we will assume we are performing a 'mentor logout' of one or more members
        # Mentor has to provide their username/password then all 'ticked' users will be logged out
        locount = 0
        for member, flag in self.registerlist.indojo.items():
            if(flag.get()):
                locount += 1

        if( locount ):
            if(tk.messagebox.askyesno("Mentor Logout", "You have select " + str(locount) + " users to logout.\n\nYou need to be a mentor to do this.\n\nProceed?")):
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
        if( not pw.CheckPassword(self.user['Password'], password) ):
            tk.messagebox.showerror("Memslip Error", "Nope. That's not the password used with this Nickname.\n\nTry again hacker...")
            return
        # OK - we have a valid login attempt - but are we already logged out?
        register = mysqldb.GetRegister(self.dojoid, self.user['UserID'])
        if( register == None or not register['Logout'] == None ):
            if(tk.messagebox.askyesno("Login?", "You're currently logged OUT. Do you want to login again?")):
                self.Login()
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
            result = AddUserDialog(root, "Welcome Padawan")
            if( result[0] != None and result[1] != None ):
                self.Login(nname=result[0], npassword=result[1])

    def ClearDetails(self, parent=None):
        self.login.nickname_entry.delete(0, tk.END)
        self.login.password_entry.delete(0, tk.END)
        self.login.nickname_entry.focus_set()

# Our main program loop - sets window title and size then executes mainloop()
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("990x720")
    root.title("Dojo Register")
    root.wm_iconbitmap(bitmap="images\\book.ico")
    root.columnconfigure(0, weight=1)     # We want to resize and use all window width
    root.rowconfigure(0, weight=1)        # We want to resize and use all window height
    
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
