from cv2 import imread 
from numpy import sum as npsum


### Calculate mean squared error given two image filenames
def calc_mse(filenameA, filenameB):
	##############################################################
	#
	# Title        : MSE Function in Python
	# Author       : Arora et al.
	# Date         : 2016
	# Availability : https://ieeexplore.ieee.org/document/7877503
	#
	##############################################################
	try:
		imageA, imageB = imread(filenameA), imread(filenameB)
		mse = npsum((imageA.astype("float") - imageB.astype("float")) ** 2)
		mse /= float(imageA.shape[0] * imageA.shape[1])
		return mse

	except:
		return -1