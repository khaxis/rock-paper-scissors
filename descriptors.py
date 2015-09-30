import cv2
import numpy as np

SZ=64
bin_n = 16 # Number of bins
affine_flags = cv2.WARP_INVERSE_MAP|cv2.INTER_LINEAR
LBP_BLOCK_SIZE = 16
LBP_BIN_N = 16

def d(img):
	return img[1,1]

def deskew(img):
	img = cv2.resize(img, (SZ, SZ))
	m = cv2.moments(img)
	if abs(m['mu02']) < 1e-2:
		return img.copy()
	skew = m['mu11']/m['mu02']
	M = np.float32([[1, skew, -0.5*SZ*skew], [0, 1, 0]])
	img = cv2.warpAffine(img,M,(SZ, SZ),flags=affine_flags)
	return img

def hog(img):
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
    mag, ang = cv2.cartToPolar(gx, gy)
    bins = np.int32(bin_n*ang/(2*np.pi))    # quantizing binvalues in (0...16)
    bin_cells = bins[:10,:10], bins[10:,:10], bins[:10,10:], bins[10:,10:]
    mag_cells = mag[:10,:10], mag[10:,:10], mag[:10,10:], mag[10:,10:]
    hists = [np.bincount(b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
    hist = np.hstack(hists)     # hist is a 64 bit vector
    return hist

def calcLBP(img):
	center = img[1, 1]
	code = 0
	code |= (img[0,0] > center) << 7;
	code |= (img[0,1] > center) << 6;
	code |= (img[0,2] > center) << 5;
	code |= (img[1,2] > center) << 4;
	code |= (img[2,2] > center) << 3;
	code |= (img[2,1] > center) << 2;
	code |= (img[2,0] > center) << 1;
	code |= (img[1,0] > center) << 0;
	return code

def singleBlockLBP(img):
	#cv2.imshow('abc', img)
	#while True:
	#	if cv2.waitKey(1) & 0xFF == ord('q'):
	#		break
	values = [ calcLBP(img[i-1:i+2, j-1:j+2]) for i in range(1, LBP_BLOCK_SIZE-1) for j in range(1, LBP_BLOCK_SIZE-1) ]
	bins = np.arange(0, 256+1, LBP_BIN_N)
	hist = np.histogram(values, bins = bins)[0] #np.hstack(hists)
	return hist

def lbp(img):
	img = cv2.resize(img, (SZ, SZ))
	N = SZ/LBP_BLOCK_SIZE
	vectors = []
	for i in range(N):
		for j in range(N):
			v = singleBlockLBP(img[i*LBP_BLOCK_SIZE:(i+1)*LBP_BLOCK_SIZE, j*LBP_BLOCK_SIZE:(j+1)*LBP_BLOCK_SIZE])
			vectors.append(v);
	return np.hstack(vectors)

