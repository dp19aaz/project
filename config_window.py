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
			values, curr_value = self.settings_values_dictionary[setting]

			option_var = self.create_lbl_btn(setting, values, curr_value)
			self.entry_variables[setting] = option_var


		update_settings_btn = Button(self, text='Update settings', command=self.update_cam_settings)
		update_settings_btn.grid()


	def update_cam_settings(self):
		settings = [i.get() for i in self.entry_variables.values()]
		settings = ",".join(settings)

		self.controller.update_cam_settings(settings)



	def get_cam_settings(self):
		return self.controller.get_cam_settings()



	def get_option_values(self):
		curr_values = self.current_settings.split(',')

		with open('settings_values.txt', 'r') as f:
			data = f.read()	

		data = data.split('\n')

		dic = {}
		for index, line in enumerate(data):
			setting, values = line.split(':')
			values = values.split(',')

			dic[setting] = (values, curr_values[index])

		return dic



	def create_lbl_btn(self, setting, values, curr_value):
		frame = self

		label = Label(frame, text=setting)

		option_var = StringVar()
		option_var.set(curr_value)
		optionmenu = OptionMenu(frame, option_var, *values)



		label.grid()
		optionmenu.grid()

		return option_var



	def close(self):
		self.controller.close_config()

