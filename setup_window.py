from tkinter import *
from custom_tk import *

import tkinter.ttk as ttk


###########################
### Setup window
###########################
class setup(Tk):
	def __init__(self):
		super().__init__()

		self.config(bg=BG)
		self.title('Setup window')

		input_frame = Frame(self, bg=BG)
		main_frame = Frame(self, bg=BG)


		#optionmenus

		#OptionMenu values. index0 is default
		MSE_LIMIT_VALUES = (100, 25, 50, 75, 150, 200, 350, 500)
		MC_LIMIT_VALES   = (1, 2, 3, 4, 5, 6, 0)
		DELAY_VALUES     = (0.1, 0.3, 0.5, 0.7, 1, 2, 0)
		TIMEOUT_VALUES   = (2, 1, 3, 5, 10)


		#create optionmenus
		self.vars = []

		options = (
			  ('MSE Limit', IntVar, MSE_LIMIT_VALUES, input_frame,
					'Mean Squared Error limit before motion is considered detected.')
			, ('Motion count limit', IntVar, MC_LIMIT_VALES, input_frame,
					'No. consecutive frames containing motion before frames are recorded. Select 0 to save all frames with motion.')
			, ('Autoupdate delay', DoubleVar, DELAY_VALUES, input_frame,
					'Delay between updates when autoupdate is enabled.')
			, ('Socket timeout', IntVar, TIMEOUT_VALUES, input_frame,
					'Timeout value of socket connection.')
			  )

		for index, option in enumerate(options):
			tmp = self.inputdata(*option)
			tmp.grid(row=index, column=0)
			self.vars.append(tmp)



		#ip entry

		#tk entry validation command. to check if input/data is valid
		def ip_vcmd(P,s,S):
			#P:value_if_allowed      s:prior_value      S:text inserted

			#example valid ip: 192.168.0.17
			if len(P) > 15:return False

			if P.count('.') > 3:return False

			for i in S:
				if not (i.isdigit() or i=='.'):
					return False

			return True

		reg_ip_vcmd = (self.register(ip_vcmd), '%P','%s','%S')#register vcmd

		ip_lbl = Label(input_frame, text='IP')
		ip_lbl_ttp = CreateToolTip(ip_lbl, 'IP of camera to connect to.')
		self.ip_ent = Entry(input_frame, validate='key', vcmd=reg_ip_vcmd)
		self.ip_ent.config(bg=BG, fg='white')
		self.ip_ent.bind('<Return>', self.confirm)
		
		ip_lbl.     grid(row=index+1, column=0, sticky='w')
		self.ip_ent.grid(row=index+1, column=1, sticky='nesw')


		#confirm

		confirm_btn = Button(main_frame, text='Confirm', command=self.confirm)
		confirm_btn.config_hover('darkolivegreen4', 'white')
		confirm_btn.grid(row=0, column=0)


		#geometry management

		input_frame.grid(row=0, column=0)
		ttk.Separator(self, orient='horizontal').grid(
						 row=1, column=0, sticky='nesw', pady=12)
		main_frame. grid(row=2, column=0)


		self.ip_ent.focus()
		self.ip_ent.insert(0, '192.168.0.11')


	### confirm choices and continue
	def confirm(self, event=None):

		#mse_limit, mc_limit, delay, timeout, ip
		values = [var.get_value() for var in self.vars]
		values.append(self.ip_ent.get())

		global MSE_LIMIT, MC_LIMIT, DELAY, TIMEOUT, IP, RUNNING, PORT
		MSE_LIMIT, MC_LIMIT, DELAY, TIMEOUT, IP = values
		RUNNING = True
		PORT = 9090

		self.destroy()



	#label & optionmenu item for setup window
	class inputdata:
		def __init__(self, text, var_type, options, frame, description):
			self.var = var_type()
			self.var.set(options[0])
			self.lbl = Label(frame, text=text)
			lbl_ttp = CreateToolTip(self.lbl, description)
			self.opt = OptionMenu(frame, self.var, *options)
			self.opt.config(bg=BG, fg=FG, highlightthickness=0,
				activebackground=HOVER_BG, activeforeground=HOVER_FG)


		def get_value(self):
			return self.var.get()


		def grid(self, row, column):
			self.lbl.grid(row=row, column=column  , sticky='w')
			self.opt.grid(row=row, column=column+1, sticky='nesw', padx=2, pady=2)