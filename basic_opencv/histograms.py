import cv2
import numpy as np
from matplotlib import pyplot as plt

#basic example of generating and plotting histogram of an image

img = cv2.imread('red.png') #it's a 135x94 image with every pixel red, i.e. RGB = (255,0,0)
color = ('b','g','r')
# blue, green, red. Note that the ordering is important since the channels variable in the
# following for loop passes the indices as argument to calcHist.
for i,col in enumerate(color):
    print i,col
    channels = [i]
    histsize = [256]
    ranges = [0,256]
    #histsize and ranges are depended on channels. If channels = [0,1,2] then histsize would be something like [256,256,256] and
    #ranges would be [0,256,0,256,0,256]
    histr = cv2.calcHist([img],channels,None,histsize,ranges)
    #histize is number of bins. if histsize = 10, all the values will be bucketed in 10 bins.

    #ranges determine which values we are considering. if channels = [0], ranges = [10,20] then only those pixels will be considered
    #for which B value(as in RGB) is between 10 to 20(inclusive)

    #So, here histr is a 1-d array of length = histsize. If channels = [0,1] then it would be 2-d array of dimensions specified in histsize
    print histr
    print np.sum(histr)#number of pixels used in computing this histogram
    plt.plot(histr,color = col)
    plt.xlim([-100,300])

plt.show()
