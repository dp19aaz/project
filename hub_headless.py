from calculations import *
from tkinter import *
from custom_tk import *
from aescipher import AESCipher
from datetime import datetime
from time import sleep, time
from PIL import ImageTk,Image
from setup_window import setup

import socket
import tkinter.ttk as ttk



### Print with time of print. For debugging and testing.
def printm(out, *args, print_time=True, end='\n'):
	if print_time:
		print('{:.2f}'.format(time()), end=' | ')
	print(out, *args, end=end)



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
class Main:
	def __init__(self, socket):
		super().__init__()

		#args
		global RUNNING, DELAY
		self.socket = socket


		#flags
		self.motion_detection_count = 0 #no. consecutive frames where motion is detected
		self.motion_start_filename = None

		self.prev_filename_capture = None


		while RUNNING:
			self.update()
			sleep(DELAY)



	### Main thread
	def update(self, event=None):
		#Get latest captured image
			#latest_filename = date and time of image capture
			#latest_bytes    = bytestream of image

		try:    latest_filename, latest_bytes = self.get_latest_capture()
		except: return

		if latest_filename == self.prev_filename_capture:return

		printm('Received', latest_filename)

		#Motion detection and image saving
		do_write = False

		mse = calc_mse('latest.jpg', 'prev.jpg')

		if mse >= MSE_LIMIT:
			self.motion_detection_count += 1
			do_write = True

			if not self.motion_start_filename:
				self.motion_start_filename = latest_filename.split('/')[1][:-4]

		else:
			self.motion_detection_count //= 2#div 2. similar to int(x/2)



		if self.motion_detection_count >= MC_LIMIT:
			printm('Motion detected.',self.motion_detection_count)
			append_motion_log(self.motion_start_filename, latest_filename.split('/')[1][:-4])

			do_write = True


		else:
			self.motion_start_filename = None
		

		if do_write:
			write_file(latest_filename, latest_bytes)


		self.prev_filename_capture = latest_filename





	### Send data via self.socket
	def socket_send(self, data, encode=True, encrypt=True):
		if encode:  data = data.encode()
		if encrypt: data = CIPHER.encrypt(data)

		try:
			self.socket.sendall(data)
		except Exception as err:
			# printm('socket_send error', err)
			# print(5)
			self.close()



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
			printm('sockettimeout in socket_receive')
			self.close()

		except Exception as err:
			printm('socket_receive error', err)
			self.close()

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

		sleep(0.1)

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


		return filename, file



	### Close window, but not completely quit program
	def close(self, event=None):
		global RUNNING
		RUNNING = False



###########################
### Main
###########################
def main():
	global RUNNING, MSE_LIMIT, MC_LIMIT, DELAY, TIMEOUT, IP
	setup_win = setup()
	setup_win.mainloop()

	assert setup_win.complete, "did not complete setup"
	PORT = setup_win.PORT
	RUNNING = setup_win.complete
	MSE_LIMIT, MC_LIMIT, DELAY, TIMEOUT, IP = setup_win.values

	print('Starting. IP:', IP)
	while RUNNING:
		sleep(1)


		#create socket
		printm('Connecting... ', end='')
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

		except Exception as err:
			printm('Connection failed.', print_time=False)
			printm('err: %s'%err)
			RUNNING = False
			break


		#open tk window to run main program
		try:
			main = Main(s)
			main.mainloop()
		except Exception as err:
			printm(err)

		#failsafe
		try:    s.close()#close socket
		except: pass

		#delay
		if RUNNING:
			for _ in range(3):
				print('.', end='')
				sleep(1)
			print()


if __name__ == '__main__':
	main()