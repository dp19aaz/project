from calculations import *
from tkinter import *
from aescipher import AESCipher
from datetime import datetime
from time import sleep, time
from PIL import ImageTk,Image

import threading
import socket
import config_window



### Print. for testing
def printm(out, print_time=True, end='\n'):
	if print_time:
		print(round(time(),2), end=' | ')
	print(out, end=end)



def write_file(latest_filename, latest_bytes):
	with open(latest_filename, 'wb') as f:
		f.write(latest_bytes)



def append_motion_log(start, new):

	with open('motionlog.txt', 'r') as f:
		data = f.read()

	filenames = data.split('\n')
	start_times = [i.split(',')[0] for i in filenames]

	if start not in start_times:
		with open('motionlog.txt', 'a') as f:
		 	f.write('\n%s,%s'%(start, new))

	else:
		filenames[start_times.index(start)] += ',%s'%new
		with open('motionlog.txt', 'w') as f:
			f.write('\n'.join(filenames))




### Returns latest.jpg as Pillow image object
def open_latest():
	try:    latest = Image.open('latest.jpg')
	except: latest = Image.open('noimage.jpg')

	return latest



#Global variables
with open('cipherkey.txt', 'r') as f:key = f.read()
CIPHER = AESCipher(key)

DELAY = 0.1
TIMEOUT = 2
MAX_LENGTH = 4096
RUNNING = True


MSE_LIMIT = 100
MOTION_COUNT_LIMIT = 2



### Main window
class Main(Tk):
	def __init__(self, socket):
		super().__init__()

		#args
		self.socket = socket

		#window
		self.geometry('964x750+300+200')#width,height,x,y
		self.title(IP)#window title
		self.bind('<F5>', self.update)#bind F5 key to call self.update


		#flags
		self.config_window = None
		self.auto_update = False
		self.motion_detection_count = 0#no consecutive frames motion is detected
		self.motion_start_filename = None


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
		update_btn = Button(self, text='Update', command=self.update)
		config_btn = Button(self, text='Config', command=self.open_config)
		self.autoupdate_btn = Button(self, text='Enable autoupdate', command=self.toggle_autoupdate)
		completely_quit_btn = Button(self, text='Completely quit', command=self.completely_quit)


		#geometry management
			#master=self
		self.image_canvas.     grid(row=0, column=0, columnspan=2, sticky='nesw')

		self.capturedate_label.grid(row=1, column=0, columnspan=2, sticky='nesw')
		self.mse_label.        grid(row=2, column=0, columnspan=1, sticky='nesw')

		update_btn.            grid(row=3, column=0, columnspan=1, sticky='nesw')
		config_btn.            grid(row=3, column=1, columnspan=1, sticky='nesw')
		self.autoupdate_btn.   grid(row=4, column=0, columnspan=2, sticky='nesw')
		completely_quit_btn.   grid(row=5, column=0, columnspan=2, sticky='nesw')

			#master=self.image_canvas
		self.latestlabel.grid(row=0, column=0, columnspan=1, sticky='nesw')


	### Toggle or enable/disable auto_update
	def toggle_autoupdate(self):
		#toggle flag
		self.auto_update = not self.auto_update

		if self.auto_update: #enabling
			self.autoupdate_btn.config(text='Disable autoupdate')

			self.autoupdate_thread = threading.Thread(target=self.autoupdate)
			self.autoupdate_thread.start()

		else: #disabling
			self.autoupdate_btn.config(text='Enable autoupdate')	
			if self.autoupdate_thread:
				self.autoupdate_thread.join(1)



	### Thread to call self.update() repeatedly
	def autoupdate(self):
		global RUNNING

		while self.auto_update and RUNNING:
			self.update()
			# sleep(DELAY)



	### Save current displayed frame
	def save_frame(self):
		...



	### Update cam settings
	def update_cam_settings(self, settings):
		self.socket_send('SET_SETTINGS#%s'%settings)



	### Get cam current settings
	def get_cam_settings(self):
		self.socket_send('SEND_CAM_SETTINGS#')
		sleep(0.2)
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
			return

		self.config_window = config_window.window(self, 'Configure %s'%IP)
		self.config_window.mainloop()



	### Main thread
	def update(self, event=None):
		#Get latest captured image
			#latest_filename = date and time of image capture
			#latest_bytes = byte stream of image
		info = self.get_latest_capture()

		if info:
			latest_filename, latest_bytes = info
		else:
			return


		#If image captured too long ago, check for errors
		...


		#Motion detection
		mse = calc_mse('latest.jpg', 'prev.jpg')

		if mse >= MSE_LIMIT:
			self.motion_detection_count += 1
			write_file(latest_filename, latest_bytes)

			if not self.motion_start_filename:
				self.motion_start_filename = latest_filename.split('/')[1][:-4]

		else:
			self.motion_detection_count //= 2#div 2. similar to int(x/2)



		if self.motion_detection_count >= MOTION_COUNT_LIMIT:
			print('Motion detected.',self.motion_detection_count)
			append_motion_log(self.motion_start_filename, latest_filename.split('/')[1][:-4])

			if mse < MSE_LIMIT:
				write_file(latest_filename, latest_bytes)

		else:
			self.motion_start_filename = None


		#Update displayed image
		self.update_image(latest_filename, mse)



	### Update image and related labels
	def update_image(self, capturedate, mse):
		latest = open_latest()
		self.tkimagelatest = ImageTk.PhotoImage(master=self.image_canvas, image=latest)
		self.latestlabel.config(image=self.tkimagelatest) 

		self.capturedate_label['text'] = 'Image captured: %s'%capturedate
		self.mse_label.config (text= 'MSE: {:,.2f}'.format(mse))



	### Send data via self.socket
	def socket_send(self, data, encode=True, encrypt=True):
		if encode:  data = data.encode()
		if encrypt: data = CIPHER.encrypt(data)

		self.socket.sendall(data)



	### Receive data via self.socket
	def socket_receive(self, length=MAX_LENGTH, timeout=TIMEOUT, decode=False, decrypt=True):
		s = self.socket
		s.settimeout(timeout)

		try:
			buf = s.recv(length)
			if buf == b'':return -1
			if decrypt: buf = CIPHER.decrypt(buf)
			if decode:  buf = buf.decode()

		except socket.timeout:
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
			with open('prev.jpg', 'wb') as f:
				f.write(data)
		except FileNotFoundError:
			pass


		#Write file
		with open('latest.jpg', 'wb') as f:
			f.write(file)


		return filename, file



	### Quit program, not just close window
	def completely_quit(self, event=None):
		global RUNNING
		
		RUNNING = False

		if self.autoupdate_thread:
			self.autoupdate_thread.join(1)

		self.destroy()





PORT = 9090
# IP = input('IP of camera:')
IP = '192.168.0.21'


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
		continue


	#open tk window to run main program
	try:
		main = Main(s)
		main.mainloop()
	except Exception as err:
		printm(err)


	#close socket
	try:    s.close()
	except: pass
