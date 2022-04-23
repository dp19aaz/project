from calculations import *
from tkinter import *
from custom_tk import *
from aescipher import AESCipher
from datetime import datetime
from time import sleep, time
from PIL import ImageTk,Image

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
		self.socket = socket


		#flags
		self.auto_update = False
		self.motion_detection_count = 0 #no. consecutive frames where motion is detected
		self.motion_start_filename = None

		self.prev_filename_capture = None


		global RUNNING
		while RUNNING:
			self.update()



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
			printm('socket_send error', err)

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
		MC_LIMIT_VALES   = (2, 3, 4, 5, 6, 1, 0)
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




###########################
### Main
###########################
def main():
	global RUNNING
	setup().mainloop()

	assert RUNNING, "did not complete setup"

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