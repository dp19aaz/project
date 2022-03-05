from aescipher import AESCipher
from datetime import datetime
from time import sleep, time

import threading
import socket



key = 'thisisAreallygoodpassword'
CIPHER = AESCipher(key)

TIMEOUT = 1
MAX_LENGTH = 50



### Convert unix timestamp to string date
def unix_to_date(unix):
	return datetime.utcfromtimestamp(unix).strftime('%Y_%m_%d-%H:%M:%S')


### Convert string date to unix timestamp
def date_to_unix(date):
	# time.mktime(datetime.strptime(s, "%d/%m/%Y").timetuple())
	unix = datetime.strptime(date, '%Y_%m_%d-%H:%M:%S')
	unix = datetime.mktime(unix.timetuple())
	return unix


### Send data
def socket_send(s, data, encode=True, encrypt=True):
	if encode:data = data.encode()
	if encrypt:data = CIPHER.encrypt(data)
	s.sendall(data)


### Send latest captured image to hub
def send_latest(conn, filename, append_jpg=True):

	if filename == None:
		print('Could to find latest image');return -1

	if append_jpg: filename += '.jpg'

	with open(filename, 'rb') as f:
		data = f.read()

	header = '%s#%s'%(filename, len(data))

	socket_send(conn, header)
	socket_send(conn, data, encode=False)


### Respond to ping
def pong(conn):
	socket_send(conn, 'PONG')


### Ping socket connection
def ping(conn):
	socket_send(conn, 'PING')


### Take picture
def take_pic():
	print('take_pic disabled for testing.');return time()
	unix = time()
	date = unix_to_date(unix)
	filename = date+'.jpg'

	camera.capture(date)
	print(filename, 'captured.')
	return time


### Set camera rotation
def set_rotation(value):
	camera.rotation = value


### 
def handle():
	# print('minorloop');sleep(1);return
	print('!Handling.')

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# s.bind( ('127.0.0.1', 9090) )
	s.bind( ('192.168.0.21', 9090) )
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


		buf = cipher.decrypt(buf)
		buf = buf.decode('utf-8')

		if len(buf) == 0:
			print('break')
			break

		print(buf)

		signal, value = buf.split('#')

		if signal == 'PING':
			pong(conn)

		if signal == 'SEND_LATEST':
			send_latest(conn, latest_image_date)

		if signal == 'SET_ROTATION':
			set_rotation(value)

	print('!Handling stopped.\n')






while 1:
	print('*Thread running.')

	setup camera
	camera = picamera.PiCamera()
	camera.resolution = (960, 540)
	camera.rotation = 180


	ct = threading.Thread(target=handle)
	ct.run()

	camThread = threading.Thread()
	while camThread.is_alive():
		camThread.join(1)
	camThread.run()

	print('*Thread ended.\n')
	# close cam if client disconnects
	camera.close()