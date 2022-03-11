from skimage.metrics import structural_similarity as ssim

import numpy as np
import cv2



### Calculate mean squared error given two image filenames
def calc_mse(self, filenameA, filenameB):
	#https://pyimagesearch.com/2014/09/15/python-compare-two-images/
	imageA = cv2.imread(filenameA)
	imageB = cv2.imread(filenameB)

	try:
		mse = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
		mse /= float(imageA.shape[0] * imageA.shape[1])
		return mse
	except:
		return -1


### Calculate structural similarity given two image filenames
def calc_ssim(self, filenameA, filenameB, channel_axis=2):
	imageA = cv2.imread(filenameA)
	imageB = cv2.imread(filenameB)

	try:
		return ssim(imageA, imageB, channel_axis=channel_axis)
	except:
		return -1