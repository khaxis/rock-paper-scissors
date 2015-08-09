import sys
import numpy as np
import cv2
from time import gmtime, strftime # need for names of the files
import os # need to create a directory
import uuid
import random
import glob

drawing = False # true if mouse is pressed
mode = True # if True, draw rectangle. Press 'm' to toggle to curve
ix,iy = -1,-1
img = None
img_src = None
imgRect = None
rect = None
outliers = None

class Rectangle:
	def __init__(self):
		x, y, w, h = 0, 0, 0, 0
	
	#def __init__(self, rectangle):
	#	x, y, w, h = rectangle.x, rectangle.y, rectangle.w, rectangle.h

def getUniqueName():
	return str(uuid.uuid1())

def getHelp(argv):
	res = ""
	res += "Use format: python {0} <dir> <cascadePath>\n".format(argv[0])
	res += "\t: describes where to store images"
	return res
	
def intersects(a, b):
	x00, x01 = a.x, a.x+a.w
	x10, x11 = b.x, b.x+b.w
	y00, y01 = a.y, a.y+a.h
	y10, y11 = b.y, b.y+b.h
	
	if x01<x10 or x11<x00:
		return False
	if y01<y10 or y11<y00:
		return False
	return True

def multiIntersects(a, arr):
	for b in arr:
		if intersects(a, b):
			return True
	return False

def getOutsideRects(field, rect):
	res = []
	
	M = 1
	N = 10
	for j in range(M):
		tmp = []
		for i in range(N):
			
			r = Rectangle()
			r.x, r.y = random.randint(0, field.w-rect.w-1), random.randint(0, field.h-rect.h-1)
			#r.x, r.y = 1 ,1 #field.w-rect.x-1,field.h-rect.y-1
			r.w = rect.w
			r.h = rect.h
			if not intersects(r, rect) :# and not multiIntersects(r, tmp):
				tmp.append(r)
		
		if len(tmp)>len(res):
			res = tmp
	
	return res
	
	
def draw_rect(x,y, ix, iy):
	global img, img_src, imgRect, rect, outliers
	img = img_src.copy()
	drawing = False
	cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),2)
	rect = Rectangle();
	rect.x, rect.y = min(ix, x), min(iy, y)
	rect.w, rect.h = max(ix, x) - rect.x, max(iy, y) - rect.y
	outliers = getOutsideRects(imgRect, rect)
	for r in outliers:
		cv2.rectangle(img,(r.x,r.y),(r.x+r.w,r.y+r.h),(0,0,255),2)
		
		
def testImage(imgPath, cascade):
	global img, img_src, imgRect, rect, outliers
	
	fileName, fileExtension = os.path.splitext(imgPath)
	goodFilename = fileName + "_pos.txt"
	badFilename = fileName + "_neg.txt"
	if os.path.isfile(goodFilename):
		return
	
	img_src = cv2.imread(imgPath)
	img = img_src.copy()
	imgRect = Rectangle();
	imgRect.x, imgRect.y, imgRect.w, imgRect.h = 0, 0, img_src.shape[1], img_src.shape[0];
	cv2.namedWindow('image')
	gray = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)
	
	objs = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )
    
	for (x, y, w, h) in objs:
		rect = Rectangle();
		rect.x, rect.y, rect.w, rect.h = x, y, w, h
		draw_rect(x, y, x+w, y+h)
		while(True):
			# Display the resulting frame
			cv2.imshow('image',img)
			ch = cv2.waitKey(1) & 0xFF
			if ch == ord('q') or ch == 27:
				break
			if ch == ord('\n') or ch == 32:
				f = open(goodFilename, 'w')
				f.write(str(rect.x) + " " + str(rect.y) + " " + str(rect.w) + " " + str(rect.h) + "\n");
				f.close();
				
				f = open(badFilename, 'w')
				for r in outliers:
					f.write(str(r.x) + " " + str(r.y) + " " + str(r.w) + " " + str(r.h) + "\n");
				f.close();
				break
		break # bidlocodding

def main(argv):
	#cascPath = sys.argv[2]
	#cascade = cv2.CascadeClassifier(cascPath)
	#testImage("/tmp/a.png", cascade)
	#cv2.destroyAllWindows()
	#exit(0)
	if len(argv) < 3:
		print getHelp(argv)
		exit(1)
	else:
		filenames = glob.glob(argv[1] + "/*.png");
		cascPath = sys.argv[2]
		cascade = cv2.CascadeClassifier(cascPath)
		for i in range(len(filenames)):
			print str((i*100)/len(filenames)) + "%"
			testImage(filenames[i], cascade)
	
if __name__ == "__main__":
	main(sys.argv)
