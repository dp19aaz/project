from aescipher import AESCipher
from time import time

with open('cipherkey.txt', 'r') as f:key = f.read()
assert len(key) in (16, 24, 32), 'cipher key must be of length 16, 24, or 32'
CIPHER = AESCipher(key)



with open('latest.jpg', 'rb') as f:
	data = f.read()





def main(data=data):
	s = time()
	enc = CIPHER.encrypt(data)
	t1 = time()
	print(t1-s)
	dec = CIPHER.decrypt(enc)
	print(time()-t1)

	print(list(map(len, (data, enc, dec))))
	print(len(enc)/len(data))
	print()

main()