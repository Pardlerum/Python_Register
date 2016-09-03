import tkinter as tk
from tkinter import ttk

import time

CLOCK_FONT = ('arial', 9, 'bold')

class Clock(ttk.Label):
    """ Class that contains the clock widget and clock refresh """
    def __init__(self, parent=None, seconds=False, colon=True, clockfont_=CLOCK_FONT, clockfg_="grey35", anchor_=tk.E):
        """
        Create and place the clock widget into the parent element
        It's an ordinary Label element with two additional features.
        """
        s = ttk.Style()
        s.configure('Clock.TLabel', font=CLOCK_FONT,  foreground=clockfg_)   
    
        ttk.Label.__init__(self, parent, style='Clock.TLabel', anchor=anchor_)

        self.display_seconds = seconds
        if self.display_seconds:
            self.time     = time.strftime('%H:%M:%S')
        else:
            self.time     = time.strftime('%I:%M %p').lstrip('0')
        self.display_time = self.time
        self.configure(text=self.display_time)

        if colon:
            self.blink_colon()

        self.after(400, self.tick)

    def tick(self):
        """ Updates the display clock every 400 milliseconds """
        if self.display_seconds:
            new_time = time.strftime('%H:%M:%S')
        else:
            new_time = time.strftime('%I:%M %p').lstrip('0')
        if new_time != self.time:
            self.time = new_time
            self.display_time = self.time
            self.config(text=self.display_time)
        self.after(400, self.tick)

    def blink_colon(self):
        """ Blink the colon every second """
        if ':' in self.display_time:
            self.display_time = self.display_time.replace(':',' ')
        else:
            self.display_time = self.display_time.replace(' ',':',1)
        self.config(text=self.display_time)
        self.after(1000, self.blink_colon)
