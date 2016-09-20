# Dialog to handle entry of the dojo 'title' and notes
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as tkst

import tkdialog
import mysqldb as db     # for db functions

class AddNotesDialog(tkdialog.Dialog):

    def __init__(self, parent, title):
        self.dojo = db.GetDojo()
        tkdialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        row = 1

        self.title_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Title:', style='Label.TLabel')
        self.title_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)

        self.title_entry=ttk.Entry(master, width=90)
        self.title_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2)
        if( not self.dojo['Title'] == None ):
            self.title_entry.insert(0, self.dojo['Title'])
        row += 1


        self.notes_label=ttk.Label(master, relief=tk.FLAT, anchor=tk.E, text='Notes:', style='Label.TLabel')
        self.notes_label.grid(row=row, column=0, padx=4, pady=4, ipadx=2, ipady=2, sticky=tk.E)

        self.notes_entry=tkst.ScrolledText(master, width=75, height=8, relief=tk.FLAT, wrap=tk.WORD)
        self.notes_entry.config(font=('verdana', 8, 'normal'))
        self.notes_entry.grid(row=row, column=1, padx=4, pady=4, ipadx=2, ipady=2)
        if( not self.dojo['Notes'] == None ):
            self.notes_entry.insert("1.0", self.dojo['Notes'])
        row += 1

        return self.title_entry

    def validate(self):
        return 1

    def apply(self):
        db.AddDojoNotes(self.title_entry.get(), self.notes_entry.get("1.0", tk.END))
        return 1

    def buttonbox(self):
        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Escape>", self.cancel)
        box.pack() 

        