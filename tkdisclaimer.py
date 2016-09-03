# Disclaimer class to show text (loaded from file) and get
# agreement
import tkinter as tk
from tkinter import ttk

class DisclaimerDialog():
	def __init__(self, parent):
		''' Open the source file and load the text
		    Supress errors - we're not that bothered '''
		disc_f = None
		try:
			disc_f = open("disclaimer.txt")
		except Exception as e:
			pass

		if( disc_f == None ):
			self.disclaimer_text = "*** Couldn't find disclaimer text ***"
		else:
			self.disclaimer_text = disc_f.read()

	def ShowDisclaimer(self):
		return tk.messagebox.askyesno("Disclaimer", self.disclaimer_text)
