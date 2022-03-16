from aescipher import AESCipher

with open('cipherkey.txt', 'r') as f:key = f.read()
CIPHER = AESCipher(key)

msg = '0,50,0,0,auto,180,off,75,640x480'
print(msg, len(msg))

msg = CIPHER.encrypt(msg.encode())
print(msg, len(msg))