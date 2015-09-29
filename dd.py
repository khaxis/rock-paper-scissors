import os
import cv2
import sys
import glob
import numpy as np

THRESHOLD = 25

class Rectangle:
    def __init__(self):
        x, y, w, h = 0, 0, 0, 0

def readRects(filename):
    res = []
    try:
        with open(filename) as f:
            for line in f:
                arr = line.split(' ')
                r = Rectangle()
                r.x, r.y, r.w, r.h = int(arr[0]), int(arr[1]), int(arr[2]), int(arr[3])
                res.append(r)
    finally: 
        return res

def rectIn(bigRect, smallRect):
    if bigRect.x<=smallRect.x and bigRect.y<=smallRect.y and smallRect.x + smallRect.w <= bigRect.x + bigRect.w and smallRect.y + smallRect.h <= bigRect.y + bigRect.h:
        return True
    return False


def isRectOK(posRect, rect):
    global THRESHOLD
    posBig = Rectangle()
    posBig.x, posBig.y, posBig.w, posBig.h = posRect.x-THRESHOLD, posRect.y-THRESHOLD, posRect.w+THRESHOLD*2, posRect.h+THRESHOLD*2

    posSmall = Rectangle()
    posSmall.x, posSmall.y, posSmall.w, posSmall.h = posRect.x+THRESHOLD, posRect.y+THRESHOLD, posRect.w-THRESHOLD*2, posRect.h-THRESHOLD*2 

    if rectIn(posBig, rect) :#and rectIn(rect, posSmall):
        return True
    return False

def testImage(cascades, imgPath):
    global THRESHOLD
    rectFilename = os.path.splitext(imgPath)[0] + '_good.txt'
    posRects = readRects(rectFilename);
    
    # Capture frame-by-frame
    frame = cv2.imread(imgPath)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    objects = None
    for cascade in cascades:
        objs = cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        if objects is None or len(objects)==0:
            objects = objs
        elif objs is not None and len(objs)>0:
            objects = np.concatenate((objects,objs))

    TP, FP = 0, 0

    # Draw a rectangle around the faces
    for (x, y, w, h) in objects:
        r = Rectangle()
        r.x, r.y, r.w, r.h = x, y, w, h
        pos = False
        for posRect in posRects:
            if isRectOK(posRect, r):
                pos = True
        if pos:
            TP = TP + 1
        else:
            FP = FP + 1

    for r in posRects:
        x, y, w, h = r.x, r.y, r.w, r.h
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

        x, y, w, h = r.x-THRESHOLD, r.y-THRESHOLD, r.w+THRESHOLD*2, r.h+THRESHOLD*2
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 1)
        x, y, w, h = r.x+THRESHOLD, r.y+THRESHOLD, r.w-THRESHOLD*2, r.h-THRESHOLD*2
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 1)

    for (x, y, w, h) in objects:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame,'%d, %d'%(TP, FP),(1, 50), font, 2,(255,255,255),2)

    #cv2.imshow('frame', frame )
    #ch = cv2.waitKey(0)
    #if ch & 0xFF == ord('q') :
    #    exit(1)

    return TP, FP


def generateTriples():
    m = 17
    M = 25
    for r in range(m, M+1):
        for p in range(m, M+1):
            for s in range(m, M+1):
                yield [r, p, s]



def getHelp(argv):
    res = ""
    res += "Use format: python {0} <dir> [<cascade> ... ]\n".format(argv[0])
    res += "\t: describes where to store images"
    return res

def main(argv):
    if len(argv) < 2:
        print getHelp(argv)
        exit(1)
    else:
        print ",".join(["Rock", "Paper", "Scissors", "TP", "FP"])

        for triple in generateTriples():
            rFilename = "cascades/rock/cascade_%d.xml"%triple[0]
            pFilename = "cascades/paper/cascade_%d.xml"%triple[1]
            sFilename = "cascades/scissors/cascade_%d.xml"%triple[2]
            cascades = []
            for cascadeFilename in [rFilename, pFilename, sFilename]:
                cascade = cv2.CascadeClassifier(cascadeFilename)
                cascades.append(cascade)

            filenames = glob.glob(argv[1] + "/*.png");
            TP, FP = 0, 0
            for i in range(len(filenames)):
                #print str((i*100)/len(filenames)) + "%"
                r = testImage(cascades, filenames[i])
                TP = TP + r[0]
                FP = FP + r[1]
            print ",".join( [ str(i) for i in [ triple[0], triple[1], triple[2], TP, FP ] ] )
            sys.stderr.write("%s %d %d %d\n"%(argv[1], triple[0], triple[1], triple[2]))
            sys.stdout.flush()

            cv2.destroyAllWindows()
        
    
if __name__ == "__main__":
    main(sys.argv)
