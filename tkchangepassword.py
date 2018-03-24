# Dialog to handle password change
# Prompts for existing password, gets new password entered twice to validate/match
import tkinter as tk
from tkinter import ttk

import tkdialog
import mysqldb as db     # for db functions
import mypassword as pw  # for password hashing and checking functions

class ChangePasswordDialog(tkdialog.Dialog):

    def __init__(self, parent, title, user):
        self.user = user
        tkdialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        row = 1

        self.user_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Nickname:', style='Label.TLabel')
        self.user_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.user_entry=ttk.Entry(master, width=30)
        self.user_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2)
        if( not self.user == None ):
            self.user_entry.insert(0, self.user['NickName'])
        row += 1

        self.epassword_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Existing Password:', style='Label.TLabel')
        self.epassword_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.epassword_entry=ttk.Entry(master, width=30, show='*')
        self.epassword_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2)
        row += 1

        self.n1password_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Enter New Password:', style='Label.TLabel')
        self.n1password_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.n1password_entry=ttk.Entry(master, width=30, show='*')
        self.n1password_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2)
        row += 1

        self.n2password_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Repeat New Password:', style='Label.TLabel')
        self.n2password_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.n2password_entry=ttk.Entry(master, width=30, show='*')
        self.n2password_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2)
        row += 1

        self.note= ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text="If you can't remember your old password, get a Mentor to help!", style='Label.TLabel')
        self.note.grid(row=row, column=0, columnspan=2, padx=4, pady=16, ipadx=2, ipady=2, sticky=tk.E)
        row += 1

        self.mentor_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Mentor:', style='Label.TLabel')
        self.mentor_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.mentor_entry=ttk.Entry(master, width=30)
        self.mentor_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2)
        row += 1

        self.mpassword_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Mentor Password:', style='Label.TLabel')
        self.mpassword_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.mpassword_entry=ttk.Entry(master, width=30, show='*')
        self.mpassword_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2)
        row += 1

        if(not self.user == None):
            return self.epassword_entry
        else:
            return self.user_entry

    def validate(self):
        # Check that current password matches that already stored and that the two new passwords are identical
        # return 1 for OK and 0 for Error state

        # If we have a valid mentor nickname and password then allow password reset without existing password
        mentorreset = (self.mentor_entry.get() != "" and self.mpassword_entry.get() != "")
        if( mentorreset ):
            mentor = db.GetMentor(self.mentor_entry.get(), self.mpassword_entry.get())
            if( mentor == None ):
                tk.messagebox.showerror("Mentor Error", "Mentor details aren't right mate...\n\nIf you are trying to reset a password you\nneed a valid Mentor Nickname and Password")
                mentorreset = False

        nickname = self.user_entry.get()
        user = db.GetUser(nickname)
        if( user == None ):
            tk.messagebox.showerror("Identi Error", "Can't find your details mate...\n\nDid you enter the right Nickname?")
            return 0

        if( not mentorreset and not pw.CheckPassword(user['Password'], self.epassword_entry.get()) ):
            tk.messagebox.showerror("Memslip Error", "Nope. You haven't entered the password used with this Nickname.\n\nTry again hacker...")
            return 0

        # So we have the right Nickname and the current password
        # Now make sure the password isn't too dumb
        new_password = self.n1password_entry.get()
        if( new_password != self.n2password_entry.get() ):
            tk.messagebox.showerror("Memory Error", "Nope. You haven't entered the new password the same way twice.\n\nTry again...")
            return 0

        if( new_password.lower() in ["password", "12345678", "qwertyui", "asdfghjk", "zxcvbnm"] ):
            tk.messagebox.showerror("Bad Idea Error", "Nope. You chose a really dumb password.\n\nTry again...")
            return 0

        if( new_password.lower() == nickname.lower() ):
            tk.messagebox.showerror("Bad Idea Error", "Nope. You can't use your Nickname as your password.\n\nTry again...")
            return 0

        #if( new_password.lower() == new_password ):
        #    tk.messagebox.showerror("Lazybones Error", "Nope. You must have at least one UPPERCASE letters in your password.\n\nTry again...")
        #    return 0

        if( len(new_password) < 8 ):
            tk.messagebox.showerror("Lazybones Error", "Nope. You must have at least 8 characters in your password.\n\nTry again...")
            return 0

        return 1

    def apply(self):
        # We're good to go (Validate will already have been completed)
        user = db.GetUser(self.user_entry.get())
        db.SetPassword(user['UserID'], self.n1password_entry.get())
        tk.messagebox.showinfo("Success!", "Your password has been changed. Don't forget it!")
        

        