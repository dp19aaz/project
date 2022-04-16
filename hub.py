from calculations import *
from tkinter import *
from aescipher import AESCipher
from datetime import datetime
from time import sleep, time
from PIL import ImageTk,Image

import threading
import socket
import tkinter.ttk as ttk



### Print with time of print. For debugging and testing.
def printm(out, print_time=True, end='\n'):
	if print_time:
		print('{:.2f}'.format(time()), end=' | ')
	print(out, end=end)



### Write bytestream to file
def write_file(filename, byte_stream):
	with open(filename, 'wb') as f:
		f.write(byte_stream)


### Append filename to motionlog.txt
def append_motion_log(start, new):
	#Get motion log
	with open('motionlog.txt', 'r') as f:
		data = f.read()

	#Get start time for each log
	filenames = data.split('\n')
	start_times = [i.split(',')[0] for i in filenames]

	#Append new time or create new item
	if start not in start_times:
		with open('motionlog.txt', 'a') as f:
		 	# f.write('\n%s,%s'%(start, new))
		 	f.write('\n%s'%(start))

	else:
		filenames[start_times.index(start)] += ',%s'%new
		with open('motionlog.txt', 'w') as f:
			f.write('\n'.join(filenames))


### Returns latest.jpg as Image object (from PIL)
def open_latest():
	try:    latest = Image.open('latest.jpg')
	except: latest = Image.open('noimage.jpg')

	return latest



###########################
### Global variables
###########################
with open('cipherkey.txt', 'r') as f:key = f.read()
assert len(key) in (16, 24, 32), 'cipher key must be of length 16, 24, or 32'
CIPHER = AESCipher(key)

RUNNING = False
MAX_LENGTH = 4096 #max length of data per socket.recv()



###########################
### Main window
###########################
class Main(Tk):
	def __init__(self, socket):
		super().__init__()

		#args
		self.socket = socket

		#window
		self.geometry('964x700+300+200')#width,height,x,y
		self.title(IP)#window title
		self.bind('<F5>', self.update)#bind F5 key to call self.update


		#flags
		self.config_window = None
		self.auto_update = False
		
		self.do_save_all = False
		self.do_motion_detection = True
		self.motion_detection_count = 0 #no. consecutive frames where motion is detected
		self.motion_start_filename = None

		self.prev_filename_capture = None


		#threads
		self.autoupdate_thread = None


		#image
		self.image_canvas = Canvas(self)

		latest = open_latest()

		self.tkimagelatest = ImageTk.PhotoImage(master=self.image_canvas, image=latest)
		self.latestlabel = Label(self.image_canvas, image=self.tkimagelatest, bg='black')


		#image details
		self.capturedate_label = Label(self, text='Image captured: n/a')
		self.mse_label = Label(self, text='MSE: n/a')


		#buttons
		self.update_btn = Button(self, text='Update once', command=self.update)
		self.config_btn = Button(self, text='Config', command=self.open_config)

		self.autoupdate_btn = Button(self, text='Enable autoupdate',
			command=self.toggle_autoupdate)
		
		self.mot_det_btn = Button(self, text='Disable motion detection',
			command=self.toggle_motion_detection)
		
		self.save_all_btn = Button(self, text='Save all images',
			command=self.toggle_save_all)

		completely_quit_btn = Button(self, text='Completely quit', command=self.completely_quit)


		#geometry management
			#master=self
		self.image_canvas.     grid(row=0, column=0, columnspan=2, sticky='nesw')

		self.capturedate_label.grid(row=1, column=0, columnspan=2, sticky='nesw')
		self.mse_label.        grid(row=2, column=0, columnspan=1, sticky='nesw')

		self.update_btn.       grid(row=3, column=0, columnspan=1, sticky='nesw')
		self.config_btn.       grid(row=3, column=1, columnspan=1, sticky='nesw')
		self.autoupdate_btn.   grid(row=4, column=0, columnspan=2, sticky='nesw')
		self.mot_det_btn.      grid(row=5, column=0, columnspan=1, sticky='nesw')
		self.save_all_btn.     grid(row=5, column=1, columnspan=1, sticky='nesw')
		completely_quit_btn.   grid(row=6, column=0, columnspan=2, sticky='nesw')

			#master=self.image_canvas
		self.latestlabel.grid(row=0, column=0, columnspan=1, sticky='nesw')



	### Toggle motion detection
	def toggle_motion_detection(self, set_to=None):
		#toggle flag
		if set_to: self.do_motion_detection = set_to
		else:      self.do_motion_detection = not self.do_motion_detection

		#change button text
		if self.do_motion_detection: #enable motion detection
			self.mot_det_btn.config(text='Disable motion detection')

		else: #disable motion detection
			self.mot_det_btn.config(text='Enable motion detection')



	### Toggle saving all images
	def toggle_save_all(self):
		#toggle flag
		self.do_save_all = not self.do_save_all

		if self.do_save_all: #enable saving all images
			self.save_all_btn.config(text='Disable saving every frame')
			self.toggle_motion_detection(set_to=False)
			self.mot_det_btn.config(state='disabled')


		else: #disable saving all images
			self.save_all_btn.config(text='Enable saving every frame')
			self.mot_det_btn.config(state='normal')




	### Toggle auto_update
	def toggle_autoupdate(self):
		#toggle flag
		self.auto_update = not self.auto_update

		if self.auto_update: #enable autoupdate
			self.autoupdate_btn.config(text='Disable autoupdate')
			self.update_btn.config(state='disabled')
			self.config_btn.config(state='disabled')

			self.autoupdate_thread = threading.Thread(target=self.autoupdate)
			self.autoupdate_thread.start() #begin autoupdate thread


		else: #disable autoupdate
			self.autoupdate_btn.config(text='Enable autoupdate')	
			self.update_btn.config(state='normal')
			self.config_btn.config(state='normal')

			if self.autoupdate_thread:
				self.autoupdate_thread.join(1) #wait for thread to end



	### Thread to call self.update() repeatedly
	def autoupdate(self):
		global RUNNING

		while self.auto_update and RUNNING:
			self.update()
			sleep(DELAY)

		# if self.auto_update: self.toggle_autoupdate()
		if self.auto_update: self.auto_update = False



	### Main thread
	def update(self, event=None):
		#Get latest captured image
			#latest_filename = date and time of image capture
			#latest_bytes    = bytestream of image

		try:    latest_filename, latest_bytes = self.get_latest_capture()
		except: return

		if latest_filename == self.prev_filename_capture:return

		#Motion detection and image saving
		do_write = self.do_save_all

		if self.do_motion_detection:
			mse = calc_mse('latest.jpg', 'prev.jpg')

			if mse >= MSE_LIMIT:
				self.motion_detection_count += 1
				do_write = True

				if not self.motion_start_filename:
					self.motion_start_filename = latest_filename.split('/')[1][:-4]

			else:
				self.motion_detection_count //= 2#div 2. similar to int(x/2)



			if self.motion_detection_count >= MC_LIMIT:
				print('Motion detected.',self.motion_detection_count)
				append_motion_log(self.motion_start_filename, latest_filename.split('/')[1][:-4])

				do_write = True


			else:
				self.motion_start_filename = None
		
		else:#self.do_motion_detection is false
			mse = -1

		if do_write:
			write_file(latest_filename, latest_bytes)


		#Update displayed image
		self.update_image(latest_filename, mse)


		self.prev_filename_capture = latest_filename



	### Update cam settings
	def update_cam_settings(self, settings):
		self.socket_send('SET_SETTINGS#%s'%settings)



	### Get cam current settings
	def get_cam_settings(self):
		self.socket_send('SEND_CAM_SETTINGS#') #request cam settingss
		sleep(0.01)
		settings = self.socket_receive(length=200, decode=True, decrypt=True)
		return settings



	### Close config camera settings window
	def close_config(self):
		if self.config_window:
			self.config_window.destroy()
			self.config_window = None



	### Open configure camera settings window
	def open_config(self):
		#check if config window already open
		if self.config_window:
			self.close_config()

		self.config_window = config_window(self, 'Configure %s'%IP)
		self.config_window.mainloop()



	### Update image and related labels
	def update_image(self, capturedate, mse):
		latest = open_latest()
		self.tkimagelatest = ImageTk.PhotoImage(master=self.image_canvas, image=latest)
		self.latestlabel.config(image=self.tkimagelatest) 

		self.capturedate_label['text'] = 'Image captured: %s'%capturedate

		mse_text = 'MSE: {:,.2f}'.format(mse) if mse != -1 else 'MSE: n/a'

		self.mse_label.config (text=mse_text)



	### Send data via self.socket
	def socket_send(self, data, encode=True, encrypt=True):

		if encode:  data = data.encode()
		if encrypt: data = CIPHER.encrypt(data)

		self.socket.sendall(data)



	### Receive data via self.socket
	def socket_receive(self, length=MAX_LENGTH, decode=False, decrypt=True):

		s = self.socket
		s.settimeout(TIMEOUT)

		try:
			buf = s.recv(length)
			if buf == b'':return -1
			if decrypt: buf = CIPHER.decrypt(buf)
			if decode:  buf = buf.decode()

		except socket.timeout:
			printm('sockettimeout')
			return b''

		return buf



	### Request and receive latest captured image
	def get_latest_capture(self):

		#Request file
		self.socket_send('SEND_LATEST#')


		#Receive file header data
		buf = self.socket_receive(length=120, decode=True)
		if buf == -1:return None
		filename, filesize = buf.split('#')
		filesize = int(filesize)	


		#Receive file data
		file = b''
		while len(file) < filesize:
			buf = self.socket_receive(decode=False, decrypt=False)
			if buf == -1:
				continue
			file += buf

		file = CIPHER.decrypt(file)


		#Copy latest.jpg to prev.jpg
		try:
			with open('latest.jpg', 'rb') as f:
				data = f.read()
			write_file('prev.jpg', data)
		except FileNotFoundError:
			pass


		#Write file
		write_file('latest.jpg', file)

		self.prev_filename_capture = filename


		return filename, file



	### Quit program, not just close window
	def completely_quit(self, event=None):
		global RUNNING
		
		RUNNING = False

		if self.autoupdate_thread:
			self.autoupdate_thread.join(1)

		self.destroy()




###########################
### Config window
###########################
class config_window(Toplevel):
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





###########################
### Setup window
###########################
class setup(Tk):
	def __init__(self):
		super().__init__()

		input_frame = Frame(self)
		main_frame = Frame(self)



		#optionmenus

		#OptionMenu values. index0 is default
		MSE_LIMIT_VALUES = (100, 25, 50, 75, 150, 200, 350, 500)
		MC_LIMIT_VALES   = (2, 3, 4, 5, 6, 1, 0)
		DELAY_VALUES     = (0.1, 0.3, 0.5, 0.7, 1, 2, 0)
		TIMEOUT_VALUES   = (2, 1, 3, 5, 10)


		#create optionmenus
		self.vars = []

		options = (
			  ('MSE Limit', IntVar, MSE_LIMIT_VALUES, input_frame)
			, ('Motion count limit', IntVar, MC_LIMIT_VALES, input_frame)
			, ('Autoupdate delay', DoubleVar, DELAY_VALUES, input_frame)
			, ('Socket timeout', IntVar, TIMEOUT_VALUES, input_frame)
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
			#all checks must be true or input is invalid
			checks = (
				  S.isdigit() or S=='.'
				, P.count('.') <= 3
				, len(P) <= 15
				)
			
			for check in checks:
				if not check: return False

			return True

		reg_ip_vcmd = (self.register(ip_vcmd), '%P','%s','%S')#register vcmd

		ip_lbl = Label(input_frame, text='IP')
		self.ip_ent = Entry(input_frame, validate='key', vcmd=reg_ip_vcmd)
		
		ip_lbl.     grid(row=index+1, column=0, sticky='w')
		self.ip_ent.grid(row=index+1, column=1, sticky='nesw')


		#confirm

		confirm_btn = Button(main_frame, text='Confirm', command=self.confirm)
		confirm_btn.grid(row=0, column=0)


		#geometry management

		input_frame.grid(row=0, column=0)
		ttk.Separator(self, orient='horizontal').grid(
			             row=1, column=0, sticky='nesw', pady=12)
		main_frame. grid(row=2, column=0)


	def confirm(self):

		#mse_limit, mc_limit, delay, timeout, ip
		values = [var.get_value() for var in self.vars]
		values.append(self.ip_ent.get())
		print(values)

		global MSE_LIMIT, MC_LIMIT, DELAY, TIMEOUT, IP, RUNNING, PORT
		MSE_LIMIT, MC_LIMIT, DELAY, TIMEOUT, IP = values
		RUNNING = True
		PORT = 9090

		self.destroy()



	#label & optionmenu item for setup window
	class inputdata:
		def __init__(self, text, var_type, options, frame):
			self.var = var_type()
			self.var.set(options[0])
			self.lbl = Label(frame, text=text)
			self.opt = OptionMenu(frame, self.var, *options)


		def get_value(self):
			return self.var.get()


		def grid(self, row, column):
			self.lbl.grid(row=row, column=column  , sticky='w')
			self.opt.grid(row=row, column=column+1, sticky='nesw')




###########################
### Main
###########################
def main():
	setup().mainloop()

	assert RUNNING, "did not complete setup"

	print(IP, 'starting.')
	while RUNNING:
		sleep(1)


		#create socket
		printm('Connecting...', end='')
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(TIMEOUT)


		#attempt connecting to camera
		try:
			s.connect( (IP, PORT) )
			printm('Connected.', print_time=False)
		except socket.timeout:
			printm('Timed out.', print_time=False)
			sleep(1)
			continue


		#open tk window to run main program
		try:
			main = Main(s)
			main.mainloop()
		except Exception as err:
			printm(err)

		#failsafe
		try:    s.close()#close socket
		except: pass



if __name__ == '__main__':
	main()