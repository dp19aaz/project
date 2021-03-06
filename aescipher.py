##############################################################
#
# Title        : AESCipher
# Author       : mnothic (stackoverflow user)
# Date         : 2014
# Availability : https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
#
##############################################################

from base64 import b64decode, b64encode
from hashlib import sha256
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher(object):

	def __init__(self, key): 
		self.bs = AES.block_size
		# self.key = sha256(key.encode()).digest()
		self.key = key.encode()

	def encrypt(self, raw):
		raw = self._pad(raw)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return b64encode(iv + cipher.encrypt(raw))

	def decrypt(self, enc):
		enc = b64decode(enc)
		iv = enc[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return self._unpad(cipher.decrypt(enc[AES.block_size:]))

	def _pad(self, s):
		padding = (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs).encode()
		return s + padding

	@staticmethod
	def _unpad(s):
		return s[:-ord(s[len(s)-1:])]