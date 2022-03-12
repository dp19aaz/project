# from aescipher import AESCipher

# with open('cipherkey.txt', 'r') as f:key = f.read()
# CIPHER = AESCipher(key)


# msgs = {'go left':False,'go right':True}
# msgs = "\n".join(['#'.join(map(str,i)) for i in msgs.items()])
# msgs = CIPHER.encrypt(msgs.encode())

# print(msgs)



# key = 'realy'
# CIPHER = AESCipher(key)


# msgs = CIPHER.decrypt(msgs).decode()

# print(msgs)


# with open('cam_settings.txt', 'r') as f:
# 	data = f.read()

# data = [i.split(':') for i in data.split('\n')]


# for s, v in data:
# 	print(s, v)