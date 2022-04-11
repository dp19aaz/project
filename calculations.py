from cv2 import imread 
from numpy import sum as npsum


### Calculate mean squared error given two image filenames
def calc_mse(filenameA, filenameB):
	imageA, imageB = imread(filenameA), imread(filenameB)

	try:
		mse = npsum((imageA.astype("float") - imageB.astype("float")) ** 2)
		mse /= float(imageA.shape[0] * imageA.shape[1])
		return mse
	except:
		return -1