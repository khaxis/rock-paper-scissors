import sys
import numpy as np
import cv2
import os # need to create a directory
import glob
import uuid
from optparse import OptionParser
import random

def getUniqueName():
	return str(uuid.uuid1())

def lineToRect(line):
	words = line.split(" ")
	x, y, w, h = 0, 0, 0, 0
	if len(words) == 4:
		x = int(words[0])
		y = int(words[1])
		w = int(words[2])
		h = int(words[3])
	return x, y, w, h

# make a square out of a rect
def squareRect(x, y, w, h):
	dx, dy = 0, 0
	dw, dh = 0, 0
	if w<h:	# vertical
		dx = -(h-w)/2
		dw = h-w
	if h<w:	# horizontal
		dy = -(w-h)/2
		dh = w-h
	return x + dx, y + dy, w + dw, h + dh
		
def checkRect(img, x, y, w, h):
	height, width = img.shape[:2]
	if x<0 or y<0 or x+w>=width or y+h>=height:
		return False;
	return True;
		
def cropImage(imgPath, posDir, negDir, cascade=None, numberOfSamples=1, dx=0, dy=0, scale=1.0, angle=0.0, numberOfNegSamples=1):
	fileName, fileExtension = os.path.splitext(imgPath)
	posFilename = fileName + "_good.txt"
	negFilename = fileName + "_bad.txt"
	if not os.path.isfile(posFilename):
		return
	img = cv2.imread(imgPath)
	
	rects = []
	
	if cascade is not None:
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		objs = cascade.detectMultiScale(
			gray,
			scaleFactor=1.1,
			minNeighbors=5,
			minSize=(30, 30),
			flags=cv2.cv.CV_HAAR_SCALE_IMAGE
		)
		for (x, y, w, h) in objs:
			rects.append((x, y, w, h, True))
	elif os.path.isfile(posFilename):
		f = open(posFilename, 'r')
		line = f.readline();
		f.close()
		x, y, w, h = lineToRect(line)
		x, y, w, h = squareRect(x, y, w, h)
		rects.append((x, y, w, h, True))
	
	# populate rects with negative samples
	if os.path.isfile(negFilename):
		f = open(negFilename, 'r')
		for line in f:
			x, y, w, h = lineToRect(line)
			x, y, w, h = squareRect(x, y, w, h)
			if w*h != 0 and checkRect(img, x, y, w, h):
				rects.append((x, y, w, h, False))
		f.close()
		
	for (x0, y0, w0, h0, isPositive) in rects:
		if isPositive:
			dstDir = posDir
			N = numberOfSamples
		else:
			dstDir = negDir
			N = numberOfNegSamples
			
		for i in range(N):
			x, y, w, h = x0, y0, w0, h0
			
			# shift transform
			x += random.randint(-dx, dx)
			y += random.randint(-dy, dy)
			
			# scale transform
			s = random.uniform(1/scale, scale)
			ws, hs = int(w*s), int(h*s)
			x += (w-ws)/2
			y += (h-hs)/2
			w, h = ws, hs
			
			# rotation transform
			a = random.uniform(-angle, angle)
			rows,cols, tmp = img.shape
			Mr = cv2.getRotationMatrix2D((x+w/2,y+h/2), a, 1.0)
			imgC = cv2.warpAffine(img,Mr,(cols,rows))
			
			if w*h != 0 and checkRect(imgC, x, y, w, h):
				img_dst = imgC[y:y+h, x:x+w]
				cv2.imwrite(dstDir + "/" + getUniqueName() + "_r.png", img_dst)
				cv2.imwrite(dstDir + "/" + getUniqueName() + "_l.png", cv2.flip(img_dst, 1))
				#cv2.imshow(str(isPositive) + str((x, y, w, h, a)), img_dst)

def main(argv):
	parser = OptionParser(usage='usage: %prog [options] path')
	parser.add_option("-c", "--cascade_path", dest="cascadePath",
					  help="Cascade xml FILE", metavar="FILE")
	parser.add_option("-p", "--number_of_samples", dest="numberOfSamples", default=1, type="int",
					  help="Number of generated samples")
	parser.add_option("-n", "--number_of_negative_samples", dest="numberOfNegSamples", default=1, type="int",
					  help="Number of generated samples")
	parser.add_option("-x", "--dx", dest="dx", default=0, type="int",
					  help="Random shift on x axis in pixels")
	parser.add_option("-y", "--dy", dest="dy", default=0, type="int",
					  help="Random shift on y axis in pixels")
	parser.add_option("-s", "--scale", dest="scale", default=1.0, type="float",
					  help="Random scale transformation (1/scale, scale)")
	parser.add_option("-a", "--angle", dest="angle", default=0.0, type="float",
					  help="Random angle (rotation) transformation")
					  

	(options, args) = parser.parse_args()
	cascade = None
	if options.cascadePath is not None:
		cascade = cv2.CascadeClassifier(options.cascadePath)
	
	#directory = "/home/ivan/workspace/rock-paper-scissors/data/paper"
	#filename = "/home/ivan/workspace/rock-paper-scissors/data/paper/3b153647-51df-11e5-8d9e-985aeb8f0792.png"
	#posDir = directory + "/pos"
	#negDir = directory + "/neg"
	#cropImage(filename, 
			  #posDir, 
			  #negDir, 
			  #cascade, 
			  #numberOfSamples=options.numberOfSamples, 
			  #dx=options.dx, 
			  #dy=options.dy, 
			  #scale=options.scale, 
			  #angle=options.angle, 
			  #numberOfNegSamples=options.numberOfNegSamples
			  #)
	#while(True):
		#ch = cv2.waitKey(1) & 0xFF
		#if ch == ord('q') or ch == 27:
			#break
	#cv2.destroyAllWindows()
	#exit(0)
	
	if len(args) == 0:
		parser.print_help()
		exit(1)
	else:
		for d in args:
			directory = d.rstrip("/\\")
			posDir = directory + "/pos"
			negDir = directory + "/neg"
			if not os.path.exists(posDir):
				os.makedirs(posDir)
			if not os.path.exists(negDir):
				os.makedirs(negDir)
				
			for filename in glob.glob(directory + "/*.png"):
				cropImage(filename, 
				  posDir, 
				  negDir, 
				  cascade, 
				  numberOfSamples=options.numberOfSamples, 
				  dx=options.dx, 
				  dy=options.dy, 
				  scale=options.scale, 
				  angle=options.angle, 
				  numberOfNegSamples=options.numberOfNegSamples
				  )
				#break;
	
if __name__ == "__main__":
	main(sys.argv)
