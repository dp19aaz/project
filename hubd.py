from tkinter import *

from aescipher import AESCipher
from datetime import datetime
from time import sleep, time
from PIL import ImageTk,Image

import threading
import socket
import numpy as np
import cv2


key = 'thisisAreallygoodpassword'
CIPHER = AESCipher(key)

TIMEOUT = 2
MAX_LENGTH = 2048

MSE_LIMIT = 120



### Calculate mean square error of two images
def calc_mse(imageA, imageB):
	mse = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	mse /= float(imageA.shape[0] * imageA.shape[1])
	return mse




class Main(Tk):
	def __init__(self, socket):
		super().__init__()

		self.socket = socket


		self.geometry('964x700+300+300')#w,h,x,y
		self.title(IP)
		# self.protocol('WM_DELETE_WINDOW',self.stop)#close window (X)
		self.bind('<F5>', self.manage)

		#image
		self.image_canvas = Canvas(self)

		try:
			latest = Image.open("latest.jpg")
		except:
			latest = Image.open('noimage.jpg')

		self.tkimagelatest = ImageTk.PhotoImage(master=self.image_canvas, image=latest)
		self.latestlabel = Label(self.image_canvas, image=self.tkimagelatest, bg='black')

		self.image_capturedate_label = Label(self, text='Image captured: n/a')
		self.mse_label = Label(self, text='MSE: n/a')

		update_btn = Button(self, text='refresh', command=self.manage)

		#geometry management
		self.image_canvas.grid()
		self.latestlabel.grid()

		self.image_capturedate_label.grid()
		self.mse_label.grid()

		update_btn.grid()



	def manage(self, event=None):
		#Get latest captured image
			#latest_filename = date and time of image capture
			#latest_bytes = byte stream of image
		info = self.get_latest()

		if info:
			latest_filename, latest_bytes = info
		else:
			return

		#If image captured too long ago, check for errors
		...


		#Calculate MSE
		mse = self.calc_mse('latest.jpg', 'prev.jpg')
		self.mse_label.config(text='MSE: {:,.2f}'.format(mse))

		if mse >= MSE_LIMIT:
			print('\nMSE above limit.\nTime: %s\nFilename: %s\n'%(time(), latest_filename))
			self.write_file(latest_filename, latest_bytes)

		#Update displayed image
		self.update_image(latest_filename)




	def write_file(self, filename, bytes):
		with open(filename, 'wb') as f:
			f.write(bytes)



	def update_image(self, capturedate):
		print('updating image')
		try:
			latest = Image.open('latest.jpg')
		except:
			latest = Image.open('noimage.jpg')
		self.tkimagelatest = ImageTk.PhotoImage(master=self.image_canvas, image=latest)
		self.latestlabel.config(image=self.tkimagelatest) 

		self.image_capturedate_label['text'] = 'Image captured: %s'%capturedate


	def calc_mse(self, filenameA, filenameB):
		imageA = cv2.imread(filenameA)
		imageB = cv2.imread(filenameB)

		try:
			return calc_mse(imageA, imageB)
		except:
			return -1


	def socket_send(self, data, encode=True, encrypt=True):
		if encode:
			data = data.encode()
		if encrypt:
			data = CIPHER.encrypt(data)

		self.socket.sendall(data)



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




	### Request latest captured image
	def get_latest(self):

		#Request file
		self.socket_send('SEND_LATEST#')

		#Receive file header data
		buf = self.socket_receive(length=120, decode=True)
		# buf = buf.decode()
		print(buf)
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






PORT = 9090
# IP = input('IP of camera:')
IP = '192.168.0.21'


while 1:

	print('Connecting...',end='')
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(TIMEOUT)

	try:
		s.connect( (IP, PORT) )
		print('Connected.')
	except socket.timeout:
		print('Timed out.')
		continue


	try:
		main = Main(s)
		main.mainloop()
	except Exception as err:
		print(err)
		pass
