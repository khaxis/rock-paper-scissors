import cv2
import sys
from sklearn import svm
import os
from sklearn.externals import joblib
import descriptors
import pickle

def detect(img, clf, minValues, maxValues):
    if clf is None or minValues is None or maxValues is None:
        return None
    if len(img) == 0:
        return None
    d =  descriptors.lbp(img)

    # normalization

    dim = len(d)
    for j in range(dim):
        if minValues[j] == maxValues[j]:
            continue
        d[j] = (d[j] - minValues[j]) / (maxValues[j] - minValues[j])
    # predict
    res = clf.predict(d)
    return res

def main(argv):
    cascPath = argv[1]

    clf = None
    minValues = None
    maxValues = None

    if len(argv)>2:
        SVM_DIR = os.path.split(argv[2])[0]
        svmPath = SVM_DIR + "/svm.pkl"
        normalizationPath = SVM_DIR + "/normalization"
        clf = joblib.load(svmPath)
        with open(normalizationPath) as f:
            minValues, maxValues = pickle.load(f)
        print "Classificator found"
    else:
        print "Classificator not found"

    faceCascade = cv2.CascadeClassifier(cascPath)

    video_capture = cv2.VideoCapture(0)
    w = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    h = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    print "Original resolution: (%dx%d)"%(w, h)
    r = 800/w
    w = int(r*w)
    h = int(r*h)
    print "Using resolution: (%dx%d)"%(w, h)
    video_capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, w)
    video_capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, h)

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        #frame = cv2.imread()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            res = detect(gray[x:x+w, y:y+h], clf, minValues, maxValues)
            if res is not None:
                print res

        # Display the resulting frame
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()


main(sys.argv)