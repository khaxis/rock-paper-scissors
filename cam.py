import sys
import numpy as np
import cv2
from time import gmtime, strftime # need for names of the files
import os # need to create a directory
import uuid

cap = cv2.VideoCapture(0)
cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 600)

def getUniqueName():
	return str(uuid.uuid1())

def camProcessor():
	while(True):
		# Capture frame-by-frame
		ret, frame = cap.read()

		# Display the resulting frame
		# define range of blue color in HSV
		lower = np.array([0, 10, 60], dtype=np.uint8)
		upper = np.array([20, 150, 255], dtype=np.uint8)
		
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		ttt = cv2.inRange(hsv, lower, upper)
		ttt = cv2.cvtColor(ttt, cv2.COLOR_GRAY2BGR)
		
		res = np.concatenate((hsv, ttt), axis=1)
		
		cv2.imshow('frame',cv2.flip(res, 1) )
		ch = cv2.waitKey(1) & 0xFF
		if ch == ord('q') or ch == 27:
			break
		if ch == ord(' '):
			#cv2.imwrite(imgPath, frame)
			print " saved"

	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()

def getHelp(argv):
	res = ""
	res += "Use format: python {0} <dir>\n".format(argv[0])
	res += "\t: describes where to store images"
	return res

def main(argv):
	camProcessor()
	
if __name__ == "__main__":
	main(sys.argv)
