#https://pyimagesearch.com/2014/09/15/python-compare-two-images/

from skimage.metrics import structural_similarity as ssim
from cv2 import imread 
from numpy import sum as npsum




### cv2.imread() images
def read_images(filenameA, filenameB):
	return imread(filenameA), imread(filenameB)


### Calculate mean squared error given two image filenames
def calc_mse(self, filenameA, filenameB):
	imageA, imageB = read_images(filenameA, filenameB)

	try:
		mse = npsum((imageA.astype("float") - imageB.astype("float")) ** 2)
		mse /= float(imageA.shape[0] * imageA.shape[1])
		return mse
	except:
		return -1


### Calculate structural similarity given two image filenames
def calc_ssim(self, filenameA, filenameB, channel_axis=2):
	imageA, imageB = read_images(filenameA, filenameB)

	try:
		return ssim(imageA, imageB, channel_axis=channel_axis)
	except:
		return -1