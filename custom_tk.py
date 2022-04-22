import tkinter as tk



global BG, FG
BG, FG = 'gray40', 'white'
HOVER_BG, HOVER_FG = 'gray20', 'white'

ON_BG, OFF_BG = 'dark slate gray', 'saddle brown'



### Button
class Button(tk.Button):
	def __init__(self, master, *args, **kw):
		if 'bg' not in kw: kw['bg'] = BG
		if 'fg' not in kw: kw['fg'] = FG
		tk.Button.__init__(self, master, *args, **kw)

		self.hover = True

		self['activebackground'] = HOVER_BG
		self['activeforeground'] = HOVER_FG

		self.defaultBackground = self['bg']
		self.defaultForeground = self['fg']

		self.bind('<Enter>', self.on_enter)
		self.bind('<Leave>', self.on_leave)


	def config_hover(self, activebg, activefg):
		self['activebackground'] = activebg
		self['activeforeground'] = activefg

	def on_enter(self, event=None):
		if self.hover:
			self['background'] = self['activebackground']
			self['foreground'] = self['activeforeground']


	def on_leave(self, event=None):
		if self.hover:
			self['background'] = self.defaultBackground
			self['foreground'] = self.defaultForeground


	def disable(self):
		self.config(state='disabled')
		self.on_leave()
		self.hover = False
		

	def enable(self):
		self.config(state='normal')
		self.hover = True



### Label
class Label(tk.Label):
	def __init__(self, master, *args, **kw):
		if 'bg' not in kw: kw['bg'] = BG
		if 'fg' not in kw: kw['fg'] = FG
		tk.Label.__init__(self, master, *args, **kw)

		self.defaultBackground = self['bg']
		self.defaultForeground = self['fg']

		self.menu = tk.Menu(self, tearoff=0)
		self.menu.add_command(label='test', command=self.master.destroy)


	def set_to_default(self):
		self['bg'] = self.defaultBackground
		self['fg'] = self.defaultForeground



### Tooltip
class CreateToolTip(object):
	##############################################################
	#
	# Title        : CreateToolTip
	# Author(s)    : crxguy52, edited by Stevoisiak (stackoverflow users)
	# Date         : 2016, edited 2018
	# Availability : https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
	#
	##############################################################    
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left', \
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()



### testing
if __name__ == '__main__':
	root = tk.Tk()
	root.config(bg=BG)

	btn = Button(root, text='btn')
	btn.config(activebackground='firebrick4', activeforeground='white')
	btn.grid()


	lbl = Label(root, text='lbl')
	lbl_ttp = CreateToolTip(lbl, \
		'line 1\n'
		'line 2')
	lbl.grid()



	root.mainloop()