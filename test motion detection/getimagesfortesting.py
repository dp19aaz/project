from calculations import *
from tkinter import *
from aescipher import AESCipher
from datetime import datetime
from time import sleep, time
from PIL import ImageTk,Image

import threading
import socket
import config_window


### Write bytes to a filename
def write_file(filename, bytes):
	with open(filename, 'wb') as f:
		f.write(bytes)
	print('written', filename)



### Returns latest.jpg as Pillow image object
def open_latest():
	try:    latest = Image.open('latest.jpg')
	except: latest = Image.open('noimage.jpg')

	return latest



#Global variables
global RUNNING

with open('cipherkey.txt', 'r') as f:key = f.read()
CIPHER = AESCipher(key)

TIMEOUT = 2
MAX_LENGTH = 2048
RUNNING = True

MSE_LIMIT = 120
SSIM_LIMIT = 0.96

FOLDER = 'test2/'
IMAGENAME = 'image'




### Main window
class Main(Tk):
	def __init__(self, socket):
		super().__init__()

		#args
		self.socket = socket

		#window
		self.geometry('964x700+300+300')#width,height,x,y
		self.title(IP)#window title
		self.bind('<F5>', self.update)#bind F5 key to call self.manage


		#flags
		self.config_window = None
		self.image_count = 0


		#image
		self.image_canvas = Canvas(self)

		latest = open_latest()

		self.tkimagelatest = ImageTk.PhotoImage(master=self.image_canvas, image=latest)
		self.latestlabel = Label(self.image_canvas, image=self.tkimagelatest, bg='black')

		self.capturedate_label = Label(self, text='Image captured: n/a')
		self.mse_label = Label(self, text='MSE: n/a')


		#buttons
		update_and_save_btn = Button(self, text='Update and save pic', command=self.update_and_save)
		completely_quit_btn = Button(self, text='Completely quit', command=self.completely_quit)


		#geometry management
		self.image_canvas.grid()
		self.latestlabel.grid()

		self.capturedate_label.grid()
		self.mse_label.grid()

		update_and_save_btn.grid()
		completely_quit_btn.grid()


	### Run self.update with save_pic as True
	def update_and_save(self):
		self.update(save_pic=True)



	### Update cam settings
	def update_cam_settings(self, settings):
		...



	### Close config camera settings window
	def close_config(self):
		if self.config_window:
			self.config_window.destroy()
			self.config_window = None



	### Open configure camera settings window
	def open_config(self):
		if self.config_window:
			#check if config window already open
			return

		self.config_window = config_window.window(self, 'Configure %s'%IP)
		self.config_window.mainloop()



	### Main thread
	def update(self, save_pic=False, event=None):
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


		#Calculate MSE
		mse = calc_mse('latest.jpg', 'prev.jpg')


		#Calculate SSIM
		ssim = calc_ssim('latest.jpg', 'prev.jpg')


		if mse >= MSE_LIMIT:
			print('\nMSE above limit.\nTime: %s\nFilename: %s\n'%(time(), latest_filename))
		if ssim <= SSIM_LIMIT:
			print('\nSSIM above limit.')

		if (mse >= MSE_LIMIT) or (ssim >= SSIM_LIMIT) or save_pic:
			filename = '%s%s%s.jpg'%(FOLDER, IMAGENAME, self.image_count)
			self.image_count += 1
			write_file(latest_filename, latest_bytes)
			self.write_next_image = False


		#Update displayed image
		self.update_image(latest_filename, mse, ssim)



	### Update image and related labels
	def update_image(self, capturedate, mse, ssim):
		print('updating image')
		latest = open_latest()
		self.tkimagelatest = ImageTk.PhotoImage(master=self.image_canvas, image=latest)
		self.latestlabel.config(image=self.tkimagelatest) 

		self.capturedate_label['text'] = 'Image captured: %s'%capturedate
		self.mse_label.config(text='MSE: {:,.2f}'.format(mse))



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
			# print('buf:',buf[:60])
			if buf == b'':return -1
			if decrypt:buf = CIPHER.decrypt(buf)
			if decode:buf = buf.decode()

		except socket.timeout:
			return -1

		return buf



	### Request and receive latest captured image
	def get_latest_capture(self):

		#Request file
		self.socket_send('SEND_LATEST#')

		#Receive file header data
		buf = self.socket_receive(length=120, decode=True)
		# print(buf)
		if buf == -1:return None
		filename, filesize = buf.split('#')
		filesize = int(filesize)

		#Receive file data
		file = b''

		while len(file) < filesize:
			buf = self.socket_receive(decode=False, decrypt=False)
			# print('buf:',buf)
			if buf == -1:
				continue
			file += buf

		file = CIPHER.decrypt(file)

		#Copy latest to prev
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

		print('written latest.jpg')

		return filename, file



	### Quit program, not just close window
	def completely_quit(self, event=None):
		global RUNNING
		
		RUNNING = False
		self.destroy()





PORT = 9090
# IP = input('IP of camera:')
IP = '192.168.0.21'


while RUNNING:
	sleep(1)


	#create socket
	print('Connecting...',end='')
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(TIMEOUT)


	#attempt connecting to camera
	try:
		s.connect( (IP, PORT) )
		print('Connected.')
	except socket.timeout:
		print('Timed out.')
		continue


	#open tk window to run main program
	try:
		main = Main(s)
		main.mainloop()
	except Exception as err:
		print(err)


	#close socket
	try:    s.close()
	except: pass
