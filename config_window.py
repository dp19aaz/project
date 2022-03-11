from tkinter import *




class window(Toplevel):
	def __init__(self, controller, title):
		super().__init__()

		self.controller = controller

		self.resizable(width=False, height=False)
		self.title(title)


		self.current_settings = self.get_cam_settings()

		self.entry_variables = {}
		self.settings_values_dictionary = self.get_option_values()


		for setting in self.settings_values_dictionary.keys():
			values = self.settings_values_dictionary[setting]

			option_var = self.create_lbl_btn(setting, values)
			self.entry_variables[setting] = option_var


		update_settings_btn = Button(self, text='Update settings', command=self.update_settings)
		update_settings_btn.grid()


	def update_cam_settings(self):
		...
		#send full settings
		new_settings = ...

		self.controller.update_cam_settings()



	def get_cam_settings(self):
		...
		# get settings from camera



	def set_menus_to_values(self, values):
		...



	def get_option_values(self):
		with open('cam_setting_values.txt', 'r') as f:
			data = f.read()

		data = data.split('\n')

		dic = {}
		for line in data:
			setting, values = line.split('#')
			values = values.split(',')

			dic[setting] = values


		return dic



	def create_lbl_btn(self, setting, values):
		frame = self

		label = Label(frame, text=setting)

		option_var = StringVar()
		optionmenu = OptionMenu(frame, option_var, *values)



		label.grid()
		optionmenu.grid()

		return option_var



	def socket_send(self, data, encode=True, encrypt=True):
		self.controller.socket_send(data, encode, encrypt)



	def close(self):
		self.controller.close_config()
