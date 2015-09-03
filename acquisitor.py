import sys
import numpy as np
import cv2
from time import gmtime, strftime # need for names of the files
import os # need to create a directory
import uuid

cap = cv2.VideoCapture(0)
w = cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
print "Original resolution: (%dx%d)"%(w, h)
r = 800/w
w = int(r*w)
h = int(r*h)
print "Using resolution: (%dx%d)"%(w, h)

cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, h)

def getUniqueName():
	return str(uuid.uuid1())

def camProcessor(directory):
	while(True):
		# Capture frame-by-frame
		ret, frame = cap.read()

		# Our operations on the frame come here
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# Display the resulting frame
		cv2.imshow('frame',cv2.flip(gray, 1) )
		#size = 200, 200, 3
		#m = np.zeros(size, dtype=np.uint8)
		#cv2.imshow('frame', m )
		ch = cv2.waitKey(1) & 0xFF
		if ch == ord('q') or ch == 27:
			break
		if ch == ord(' '):
			imgPath = directory + getUniqueName() + ".png"
			cv2.imwrite(imgPath, frame)
			print imgPath + " saved"

	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()

def getHelp(argv):
	res = ""
	res += "Use format: python {0} <dir>\n".format(argv[0])
	res += "\t: describes where to store images"
	return res

def main(argv):
	if len(argv) == 1:
		print getHelp(argv)
		exit(1)
	else:
		directory = argv[1].rstrip("/\\")
		if not os.path.exists(directory):
			os.makedirs(directory)
		camProcessor(directory + "/")
	
if __name__ == "__main__":
	main(sys.argv)
