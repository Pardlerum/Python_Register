# Dialog to handle phone number changes
# Shows existing phone number and allows edit
import tkinter as tk
from tkinter import ttk

import tkdialog
import mysqldb as db     # for db functions

class ChangePhoneDialog(tkdialog.Dialog):

    def __init__(self, parent, title, number, user):
        self.number = number
        self.user = user
        tkdialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        row = 1

        self.label1=ttk.Label(master, relief=tk.FLAT, text='This is the contact number we hold for you:', style='Label.TLabel')
        self.label1.grid(row=row, column=0, columnspan=3, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E+tk.W)
        row += 1

        self.number_entry=ttk.Entry(master, width=10)
        self.number_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E+tk.W)
        self.number_entry.insert(0, self.number)
        row += 1

        self.label2=ttk.Label(master, relief=tk.FLAT, text="If it's still OK press 'OK' - if not the please update it.", 
                                  style='Label.TLabel')
        self.label2.grid(row=row, column=0, columnspan=3, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E+tk.W)

        return self.number_entry


    def validate(self):
        # Check that we have a number (min 11 digits)
        # return 1 for OK and 0 for Error state
        number = self.number_entry.get()
        count = sum(c.isdigit() for c in number)
        if( count < 10 ):
            tk.messagebox.showerror("Counti Error", "It doesn't look like there are enough digits in your number mate...\n\nDid you enter the right one?")
            return 0

        return 1

    def apply(self):
        # We're good to go (Validate will already have been completed)
        # Only need to save if it's changed
        if( self.number != self.number_entry.get() ):
            db.UpdateContactNumber(self.user['UserID'], self.number_entry.get())
            tk.messagebox.showinfo("Success!", "Your contact number has been updated.")
        

        