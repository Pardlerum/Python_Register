# Dialog to add a new user 
# Validates does not exist
import tkinter as tk
from tkinter import ttk

import datetime          # for DOB validation

import tkdialog
import mysqldb as db     # for db functions
import mypassword as pw  # for password hashing and checking functions


class AddUserDialog(tkdialog.Dialog):

    def __init__(self, parent, title):
        tkdialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        row = 1
        width = 90

        self.Text1=tk.Text(master, relief=tk.FLAT, width=width, height=10, wrap=tk.WORD)
        self.Text1.insert("1.0", """Please complete all the details below. If you're under 18 we need a contact number.

Please choose your Nickname carefully - it will stay with you forever and will appear in other Dojo projects and be seen by other Dojo students.

You will use your Nickname to log in each time you come back to Dojo - so choose something you will definitely remember!

You will also need to remember your password (min 8 characters) - that's two things to remember - are you up for that challenge???""")
        self.Text1.config(state=tk.DISABLED)
        self.Text1.grid(row=row, column=0, columnspan=2, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E+tk.W)
        row += 1

        self.user_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Your Nickname:', style='Label.TLabel')
        self.user_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.user_entry=ttk.Entry(master, width=30)
        self.user_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.W)
        row += 1

        self.first_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='First Name:', style='Label.TLabel')
        self.first_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.first_entry=ttk.Entry(master, width=30)
        self.first_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.W)
        row += 1

        self.last_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Last Name:', style='Label.TLabel')
        self.last_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.last_entry=ttk.Entry(master, width=30)
        self.last_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.W)
        row += 1

        self.DOB_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Date of Birth (DD/MM/YYYY):', style='Label.TLabel')
        self.DOB_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.DOB_entry=ttk.Entry(master, width=10)
        self.DOB_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.W)
        row += 1

        self.Text2=tk.Text(master, relief=tk.FLAT, width=width, height=1, wrap=tk.WORD)
        self.Text2.insert("1.0", """The contact number provided must be for a parent or guardian over 18.""")
        self.Text2.grid(row=row, column=0, columnspan=2, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E+tk.W)
        self.Text2.config(state=tk.DISABLED)
        row += 1

        self.contact_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Contact Number:', style='Label.TLabel')
        self.contact_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.contact_entry=ttk.Entry(master, width=15)
        self.contact_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.W)
        row += 1

        self.n1password_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Enter a memorable Password:', style='Label.TLabel')
        self.n1password_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.n1password_entry=ttk.Entry(master, width=30, show='*')
        self.n1password_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.W)
        row += 1

        self.n2password_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Repeat the same Password:', style='Label.TLabel')
        self.n2password_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)
        self.n2password_entry=ttk.Entry(master, width=30, show='*')
        self.n2password_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.W)
        row += 1

        self.Text3=tk.Text(master, relief=tk.FLAT, width=width, height=1, wrap=tk.WORD)
        self.Text3.insert("1.0", """When you're all done... press 'OK' to create your Dojo account.""")
        self.Text3.grid(row=row, column=0, columnspan=2, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E+tk.W)
        self.Text3.config(state=tk.DISABLED)

        return self.user_entry


    def validate(self):
        # Check that we have all the required details...
        # return 1 for OK and 0 for Error state
        
        # Now make sure the password isn't too dumb
        new_password = self.n1password_entry.get()
        if( new_password != self.n2password_entry.get() ):
            tk.messagebox.showerror("Memory Error", "Nope. You haven't entered the password the same way twice.\n\nTry again...")
            return 0

        if( new_password.lower() in ["password", "12345678", "qwertyui", "asdfghjk", "zxcvbnm", 
            "87654321", "poiuytre", "lkjhgfds", ",mnbvcxz", "1qaz2wsx", "princess", "iloveyou",
            "abcd1234", "1234abcd"] ):
            tk.messagebox.showerror("Bad Idea Error", "Nope. You chose a really dumb password.\n\nTry again...")
            return 0

        if( new_password.lower() == self.user_entry.lower() ):
            tk.messagebox.showerror("Bad Idea Error", "Nope. You can't use your Nickname as your password.\n\nTry again...")
            return 0

        if( len(new_password) < 8 ):
            tk.messagebox.showerror("Lazybones Error", "Nope. You must have at least 8 characters in your password.\n\nTry again...")
            return 0

        nickname = self.user_entry.get()
        if( ' ' in nickname ):
            tk.messagebox.showerror("Too Creative Error", "Nope. It's a bad idea to have spaces in your Nickname.\n\nTry again...")
            return 0

        if( len(nickname) < 4 ):
            tk.messagebox.showerror("Weenie Error", "Your Nickname must be at least 4 characters!\n\nTry again...")
            return 0

        if( db.GetUser(nickname) != None ):
            tk.messagebox.showerror("Too Popular Error", "Nope. That Nickname is already registered!\n\nHave you already got an account?\n\nYou need to choose a unique Nickname...")
            return 0

        if( self.first_entry.get() == "" or self.last_entry.get() == "" ):
            tk.messagebox.showerror("Shyness Error", "Don't be shy. Please provide both your (real) First and Last names.\n\nTry again...")
            return 0

        if( self.first_entry.get().lower() == "first" or self.last_entry.get().lower() == "last" ):
            tk.messagebox.showerror("Shyness Error", "Ha Ha.\n\nDon't be shy. Please provide both your (real) First and Last names.\n\nTry again...")
            return 0

        try:
            DOB = datetime.datetime.strptime(self.DOB_entry.get(), '%d/%m/%Y')
        except ValueError:
            tk.messagebox.showerror("Odd One Error", "It doesn't look like your DOB is in the right format.\n\nPlease use DD/MM/YYYY...")
            return 0

        today = datetime.date.today()
        age = today.year - DOB.year - ((today.month, today.day) < (DOB.month, DOB.day))

        if( age < 6 ):
            tk.messagebox.showerror("Odd One Error", "You seem a little young...is your DOB in the right format?\n\nPlease use DD/MM/YYYY...")
            return 0

        if( age > 100 ):
            tk.messagebox.showerror("Odd One Error", "You seem a little old...is your DOB in the right format?\n\nPlease use DD/MM/YYYY...")
            return 0

        # Contact number only needed if under 18
        if( age < 18 ):            
            number = self.contact_entry.get()
            count = sum(c.isdigit() for c in number)
            if( count == 0 ):
                tk.messagebox.showerror("Phone Home Error", "As you're under 18 we need a guardian's contact number...\n\nPlease provide a valid number.")
                return 0

            if( count < 10 ):
                tk.messagebox.showerror("Phone Home Error", "It doesn't look like there are enough digits in the contact number mate...\n\nDid you enter the right one?")
                return 0

            count = sum(c.isalpha() for c in number)
            if( count > 0 ):
                tk.messagebox.showerror("Phone Home Error", "Hey! What kind of screwy number has letters in it?\n\nDid you enter the right contact number?")
                return 0

            if( number[0] != '0' ):
                tk.messagebox.showerror("Phone Home Error", "Hey! Doesn't your phone number start with a '0'?\n\nDid you enter the right contact number?")
                return 0

        return 1

    def apply(self):
        # We're good to go (Validate will already have been completed)
        # Only need to save if it's changed
        msg = "OK - last chance!\n\nShall I create an account with the details shown below? (Please check)\n\nIf everything is OK press 'Yes' or press 'No' to edit\n\n"
        msg += "Nickname : " + self.user_entry.get() + "     <-- You need to remember this!\n\n"
        msg += "Your Name: " + self.first_entry.get().title() + " " + self.last_entry.get().title() + "\n"

        DOB = datetime.datetime.strptime(self.DOB_entry.get(), '%d/%m/%Y')
        today = datetime.date.today()
        age = today.year - DOB.year - ((today.month, today.day) < (DOB.month, DOB.day))
        msg += "Your birthday : " + DOB.strftime("%d %B %Y") + "   Age: " + str(age) + "\n\n"
        msg += "Contact  : " + self.contact_entry.get() + "\n\n"
        msg += "Password : " + '*'*len(self.n1password_entry.get()) + "\n"

        if (tk.messagebox.askyesno("Last Chance...", msg)):
            user = {"NickName": self.user_entry.get(),
                    "FirstName": self.first_entry.get().title(),
                    "LastName": self.last_entry.get().title(),
                    "DOB": datetime.datetime.strftime(DOB, '%Y-%m-%d'),
                    "ContactNumber": self.contact_entry.get(),
                    "Password": self.n1password_entry.get()
                    }
            code, msg = db.AddNewUser(user)
            if( code != 0 ):
                tk.messagebox.showerror("Oh No! Error", "Whoops! Looks like you broke it...\n\nSomething went wrong\n(" + str(code) +" : " + msg + ")")
                return 0
            else:
                tk.messagebox.showinfo("Great!", "You're in!\n\nNow remember to log out when you leave.")
                return (user["NickName"], self.n1password_entry.get())



        