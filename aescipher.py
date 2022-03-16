from base64 import b64decode, b64encode
from hashlib import sha256

from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):

	def __init__(self, key): 
		self.bs = AES.block_size
		self.key = sha256(key.encode()).digest()
		# self.key=key

	def encrypt(self, raw):
		raw = self._pad(raw)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return b64encode(iv + cipher.encrypt(raw))

	def decrypt(self, enc):
		enc = b64decode(enc)
		iv = enc[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return self._unpad(cipher.decrypt(enc[AES.block_size:]))#.decode('utf-8')

	def _pad(self, s):
		padding = (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs).encode()
		return s + padding

	@staticmethod
	def _unpad(s):
		return s[:-ord(s[len(s)-1:])]



def main(msg, key):
	cipher = AESCipher(key)

	print(msg, len(msg))

	enc = cipher.encrypt(msg.encode())
	print(enc, len(enc))

	dec = cipher.decrypt(enc).decode()
	print(dec)




if __name__ == '__main__':
	main('go left', '12345678901234567890123456789012')#32 characters
	# print(AES.block_size)