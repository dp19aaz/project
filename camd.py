from aescipher import AESCipher
from datetime import datetime
from time import sleep, time

import picamera
import threading
import socket



with open('cipherkey.txt', 'r') as f:key = f.read()
CIPHER = AESCipher(key)

TIMEOUT = 2
MAX_LENGTH = 100



### Convert unix timestamp to string date
def unix_to_date(unix):
	return datetime.utcfromtimestamp(unix).strftime('%Y_%m_%d-%H%M%S')


### Convert string date to unix timestamp
def date_to_unix(date):
	# time.mktime(datetime.strptime(s, "%d/%m/%Y").timetuple())
	unix = datetime.strptime(date, '%Y_%m_%d-%H%M%S')
	unix = datetime.mktime(unix.timetuple())
	return unix


### Send data
def socket_send(s, data, encode=True, encrypt=True):
	#print('encrypting:', data)
	if encode:data = data.encode()
	if encrypt:data = CIPHER.encrypt(data)
	#data = data.encode()
	#print('sending: ',data)
	s.sendall(data)


### Send latest captured image to hub
def send_latest(conn, filename, append_jpg=True):

	if filename == None:
		print('Could to find latest image');return -1

	if append_jpg: filename += '.jpg'

	filename = 'pics/'+filename

	with open(filename, 'rb') as f:
		data = f.read()

	encrypted_file = CIPHER.encrypt(data)

	#send header
	header = '%s#%s'%(filename, len(encrypted_file))
	socket_send(conn, header)#, encode=False)

	#send file
	socket_send(conn, encrypted_file, encrypt=False, encode=False)


### Respond to ping
def pong(conn):
	socket_send(conn, 'PONG')


### Ping socket connection
def ping(conn):
	socket_send(conn, 'PING')


### Take picture
def take_pic(store_pic=True):
	#print('take_pic disabled for testing.');return time()
	unix = time()
	date = unix_to_date(unix)
	filename = 'pics/'+date+'.jpg' if store_pic else latest.jpg

	camera.capture(filename)
	print(filename, 'captured.')
	return unix


### Set camera settings
def set_settings(values):
	...


### Send camera settings
def send_cam_settings():
	settings = get_cam_settings()


### Return camera settings
def get_cam_settings():
	...





### 
def handle():
	# print('minorloop');sleep(1);return
	#print('!Handling.')

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# s.bind( ('127.0.0.1', 9090) )
	s.bind( (IP, 9090) )
	s.settimeout(TIMEOUT)

	s.listen(1)

	try:
		conn, addr = s.accept()
		conn.settimeout(TIMEOUT)
		print(addr, 'connected')
	except socket.timeout:
		print('Socket timed out.')
		conn, addr = None, None


	latest_image_unix = None
	latest_image_date = None


	while 1:
		# sleep(1)

		if not latest_image_unix:
			latest_image_unix = take_pic()

		elif (time() - latest_image_unix > 60):
			latest_image_unix = take_pic()

		if latest_image_unix == -1:
			sleep(0.5)
			continue
		else:
			latest_image_date = unix_to_date(latest_image_unix)


		# if not conn:
		# 	try:
		# 		conn, addr = s.accept()
		# 		conn.settimeout(TIMEOUT)
		# 		print(addr, 'connected')
		# 	except socket.timeout:
		# 		print('Socket timed out.')
		# 		continue
		if not conn:break


		#stop waiting for recv after TIMEOUT to take pic
		try:
			buf = conn.recv(MAX_LENGTH)
		except socket.timeout:
			continue
		except Exception as err:
			print(err)
			break


		buf = CIPHER.decrypt(buf)
		buf = buf.decode('utf-8')

		if len(buf) == 0:
			print('break')
			break

		print(buf)

		signal, value = buf.split('#')


		#make factoryclass?
		if signal == 'PING':
			pong(conn)


		if signal == 'SEND_LATEST':
			latest_image_unix = take_pic()
			latest_image_date = unix_to_date(latest_image_unix)
			send_latest(conn, latest_image_date)


		if signal == 'SET_SETTINGS':
			values = conn.recv(MAX_LENGTH)
			values = CIHPER.decrypt(values)
			set_settings(values)


		if signal == 'SEND_CAM_SETTINGS'
			send_cam_settings()


	#print('!Handling stopped.\n')



IP = '192.168.0.21'




while 1:
	#print('*Thread running.')

	#setup camera
	camera = picamera.PiCamera()
	camera.resolution = (960, 540)
	camera.rotation = 180

	try:
		ct = threading.Thread(target=handle)
		ct.run()

		camThread = threading.Thread()
		while camThread.is_alive():
			camThread.join(1)
		camThread.run()
	except Exception as err:
		print(err)

	print('*Thread ended. ctrl+C twice quickly to close.\n')
	# close cam if client disconnects
	camera.close()

	sleep(1)
