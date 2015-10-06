import fnmatch
import cv2
import sys
import descriptors
import random
import numpy as np

G = True

def disturbImage(img):
	SZ = len(img)
	nSZ = SZ*(1+random.random()/2)

	rows,cols = img.shape

	Mt = np.float32([[1,0,10],[0,1,00]])
	Mr = cv2.getRotationMatrix2D((cols/2,rows/2),10,1.2)
	print "mt"
	print Mt
	print "mr"
	print Mr
	print "========="
	print Mt*Mr
	dx = 0

	while True:
		Mt = np.float32([[1,0,10],[0,1,00]])
		Mr = cv2.getRotationMatrix2D((cols/2,rows/2),10,1.2)
		Mr[0][2] = dx
		dst = cv2.warpAffine(img,Mr,(cols,rows))
		cv2.imshow('abc', dst)
		ch = cv2.waitKey(1) & 0xFF
		if ch == ord('q') or ch == 27:
			break
		if ch == ord('w'):
			dx = dx + 2
		if ch == ord('e'):
			dx = dx - 2


	img = cv2.resize(img, (SZ, SZ))
	return img

def getDescriptor(filename):
	img = cv2.imread(filename)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	if G:
		N = 10
	else:
		N = 1

	res = []
	for i in range(N):
		if(G):
			res.append(descriptors.lbp(disturbImage(img)))
		else:
			res.append(descriptors.lbp(img))

	#return descriptors.hog(img)
	return res

def main(argv):
	for filename in argv[1:]:
		res = getDescriptor(filename)
		
		for vec in res:
			for i in vec:
				print i,
			print
	
main(sys.argv)
