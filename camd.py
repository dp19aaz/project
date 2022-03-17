from aescipher import AESCipher
from datetime import datetime
from time import sleep, time

import picamera
import threading
import socket



#Global variables
with open('cipherkey.txt', 'r') as f:key = f.read()
CIPHER = AESCipher(key)

TIMEOUT = 2
MAX_LENGTH = 200



### Main program


### Convert unix timestamp to string date
def unix_to_date(unix):
	return datetime.utcfromtimestamp(unix).strftime('%Y_%m_%d-%H%M%S')


### Convert string date to unix timestamp
def date_to_unix(date):
	unix = datetime.strptime(date, '%Y_%m_%d-%H%M%S')
	unix = datetime.mktime(unix.timetuple())
	return unix


### Send data
def socket_send(s, data, encode=True, encrypt=True):
	if encode :data = data.encode()
	if encrypt:data = CIPHER.encrypt(data)
	s.sendall(data)


### Send latest captured image to hub
def send_latest(conn, filename, append_jpg=True):
	if filename == None:print('Could to find latest image');return -1
	if append_jpg: filename += '.jpg'

	filename = 'pics/'+filename

	#read file
	with open(filename, 'rb') as f:
		data = f.read()

	encrypted_file = CIPHER.encrypt(data) #encrypt file

	#send header
	header = '%s#%s'%(filename, len(encrypted_file))
	socket_send(conn, header)
	
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
	unix = time()
	date = unix_to_date(unix)

	filename = 'pics/'+date+'.jpg' if store_pic else latest.jpg

	camera.capture(filename) #take pic and store to filename
	# print(time(), filename, 'captured.')
	return unix



### Set camera settings to parameter
def set_settings(file):
	with open('cam_settings.txt', 'w') as f:
		f.write(file)

	update_settings()


### Update settings according to cam_settings.txt
def update_settings():
	global camera

	with open('cam_settings.txt', 'r') as f:
		data = f.read()

	if data.endswith('\n'):data=data[:-1]
	

	#c  = contrast,       b = brightness,  s  = saturation,
	#e  = exposure mode,  r = rotation,   drc = drc strength
	#zp = zoom position, za = zoom amount, re = resolution
	c,b,s,e,r,drc,zp,za,re = data.split(',')	

	re = [int(i) for i in re.split('x')] #resolution

	za = float(za) #zoom amount
	zxy = 1 - za   #zoom position

	#                              (x    , y    , w    , h )
	if   zp == 'top left':     z = (0    , 0    , za   , za)
	elif zp == 'top right':    z = (zxy  , 0    , za   , za)
	elif zp == 'bottom left':  z = (0    , zxy  , za   , za)
	elif zp == 'bottom right': z = (zxy  , zxy  , za   , za)
	elif zp == 'centre':       z = (zxy/2, zxy/2, za   , za)	
	else:                      z = (0    , 0    , 1    , 1 )

	camera._set_contrast(int(c))
	camera._set_brightness(int(b))
	camera._set_saturation(int(s))
	camera._set_exposure_mode(e)
	camera._set_rotation(int(r))
	camera._set_drc_strength(drc)
	camera._set_zoom(z)
	camera._set_resolution(re)



### Send camera settings
def send_cam_settings(conn):
	settings = get_cam_settings()
	socket_send(conn, settings)



### Return camera settings
def get_cam_settings():
	with open('cam_settings.txt', 'r') as f:
		data = f.read()	
	return data



### 
def handle():

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

		if not latest_image_unix:
			latest_image_unix = take_pic()

		elif (time() - latest_image_unix > 60):
			latest_image_unix = take_pic()

		if latest_image_unix == -1:
			sleep(0.5)
			continue
		else:
			latest_image_date = unix_to_date(latest_image_unix)


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

		#print(time(), buf)

		signal, value = buf.split('#')


		#make factoryclass?
		if signal == 'PING':
			pong(conn)


		if signal == 'SEND_LATEST':
			latest_image_unix = take_pic()
			latest_image_date = unix_to_date(latest_image_unix)
			send_latest(conn, latest_image_date)


		if signal == 'SET_SETTINGS':
			set_settings(value)


		if signal == 'SEND_CAM_SETTINGS':
			send_cam_settings(conn)



###############

IP = '192.168.0.21'



while 1:
	global camera

	#setup camera
	camera = picamera.PiCamera()
	# update_settings()

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
