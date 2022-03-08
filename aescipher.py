import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):

	def __init__(self, key): 
		self.bs = AES.block_size
		self.key = hashlib.sha256(key.encode()).digest()

	def encrypt(self, raw):
		raw = self._pad(raw)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return base64.b64encode(iv + cipher.encrypt(raw))

	def decrypt(self, enc):
		enc = base64.b64decode(enc)
		iv = enc[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return self._unpad(cipher.decrypt(enc[AES.block_size:]))#.decode('utf-8')

	def _pad(self, s):
		padding = (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs).encode()
		# print(type(padding), [padding])
		return s + padding

	@staticmethod
	def _unpad(s):
		return s[:-ord(s[len(s)-1:])]


# def main():
# 	key = 'k123'
# 	cipher = AESCipher(key)

# 	data = b'goleftatthebluetree'
# 	enc = cipher.encrypt(data)
# 	dec = cipher.decrypt(enc)

# 	for i in (data,enc,dec):
# 		print(i.decode())



# if __name__ == '__main__':
# 	main()
# 	print('\n\n')