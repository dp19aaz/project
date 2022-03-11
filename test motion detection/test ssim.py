import calculations



def get_images():
	for i in range(10):
		yield 'testimage%s.jpg'%i

images = tuple(get_images())
print(images)