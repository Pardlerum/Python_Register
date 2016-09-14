# Dialog to handle entry of a mentor user and password
import tkinter as tk
from tkinter import ttk

import tkdialog
import mysqldb as db     # for db functions

class MentorPasswordDialog(tkdialog.Dialog):

    def __init__(self, parent, title, mentor):
        self.mentor = mentor
        tkdialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        row = 1

        self.mentor_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Mentor:', style='Label.TLabel')
        self.mentor_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.mentor_entry=ttk.Entry(master, width=30)
        self.mentor_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2)
        if( not self.mentor == None ):
            self.mentor_entry.insert(0, self.mentor)
        row += 1

        self.mpassword_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Mentor Password:', style='Label.TLabel')
        self.mpassword_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.mpassword_entry=ttk.Entry(master, width=30, show='*')
        self.mpassword_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2)
        row += 1

        if(not self.mentor == None):
            return self.mpassword_entry
        else:
            return self.mentor_entry

    def validate(self):
        # If we have a valid mentor nickname and password then allow password reset without existing password
        mentorreset = (self.mentor_entry.get() != "" and self.mpassword_entry.get() != "")
        if( mentorreset ):
            mentor = db.GetMentor(self.mentor_entry.get(), self.mpassword_entry.get())
            if( mentor == None ):
                tk.messagebox.showerror("Mentor Error", "Mentor details aren't right mate...\n\nYou need a valid *Mentor* Nickname and Password")
                return 0
            else:
                return 1

        return 0

    def apply(self):
        return 1

        

        