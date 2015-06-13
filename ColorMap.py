
__author__ = 'Dan.Simon'

import numpy as np

def colorMap(gray):
    out = np.zeros((gray.shape[0],gray.shape[1],3),dtype=np.float64)
    gray -= np.amin(gray)
    gray /= np.amax(gray)
    gray *= 3
    out[:,:,2] = np.clip(gray,0,1.0)
    out[:,:,1] = np.clip(gray-1,0,1.0)
    out[:,:,0] = np.clip(gray-2,0,1.0)
    out *= 255
    return out.astype(np.uint8)

if __name__ == '__main__':
    import cv2
    a = cv2.imread("C:\\Users\\Dan.Simon\\PycharmProjects\\untitled\\lena.tif",0).astype(np.float64)
    color = colorMap(a)
    cv2.imshow("out",color)
    cv2.waitKey(0)
    cv2.destroyAllWindows()