from tkinter import *
from tkinter import ttk



class window(Toplevel):
	def __init__(self, controller, title):
		super().__init__()

		self.controller = controller

		self.resizable(width=False, height=False)
		self.title(title)


		self.current_settings = self.get_cam_settings()

		self.entry_variables = {}
		self.settings_values_dictionary = self.get_option_values()



		for index, setting in enumerate(self.settings_values_dictionary.keys()):
			values, curr_value = self.settings_values_dictionary[setting]

			option_var = self.create_lbl_btn(setting, values, curr_value, index)
			self.entry_variables[setting] = option_var

		ttk.Separator(self, orient='horizontal').grid(columnspan=2, sticky='nesw', pady=12)

		update_settings_btn = Button(self, text='Update settings', command=self.update_cam_settings)
		update_settings_btn.grid(columnspan=2, sticky='nesw')


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



	def create_lbl_btn(self, setting, values, curr_value, index):
		frame = self

		label = Label(frame, text=setting)

		option_var = StringVar()
		option_var.set(curr_value)
		optionmenu = OptionMenu(frame, option_var, *values)



		label.     grid(row=index, column=0, sticky='nesw')
		optionmenu.grid(row=index, column=1, sticky='nesw')

		return option_var



	def close(self):
		self.controller.close_config()





### TESTING

class test_window(Tk):
	def __init__(self):
		super().__init__()
		self.geometry('0x0+0+0')#width,height,x,y


	def get_cam_settings(self):
		return '0,50,0,auto,180,off,centre,1.0'


	def update_cam_settings(self, _):
		...

	def close_config(self):
		self.destroy()



if __name__ == '__main__':
	root = test_window()
	window(root, 'testwindow').mainloop()