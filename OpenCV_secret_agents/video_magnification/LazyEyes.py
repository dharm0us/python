import collections
import numpy
from CVForwardCompat import cv2
import threading
import timeit
import wx

import pyfftw.interfaces.cache
from pyfftw.interfaces.scipy_fftpack import fft
from pyfftw.interfaces.scipy_fftpack import ifft
from scipy.fftpack import fftfreq

import ResizeUtils
import WxUtils


class LazyEyes(wx.Frame):

    def __init__(self, maxHistoryLength=360,
                 minHz=5.0/6.0, maxHz=1.0,
                 amplification=32.0, numPyramidLevels=2,
                 useLaplacianPyramid=True,
                 useGrayOverlay=True,
                 numFFTThreads = 4, numIFFTThreads=4,
                 cameraDeviceID=0, imageSize=(320, 240),
                 title='Lazy Eyes'):

        self.mirrored = True
        
        self._running = True

        self._capture = cv2.VideoCapture(cameraDeviceID)
        size = ResizeUtils.cvResizeCapture(
                self._capture, imageSize)
        w, h = size
        self._imageWidth = w
        self._imageHeight = h

        self._useGrayOverlay = useGrayOverlay
        if useGrayOverlay:
            historyShape = (maxHistoryLength,
                            h >> numPyramidLevels,
                            w >> numPyramidLevels)
        else:
            historyShape = (maxHistoryLength,
                            h >> numPyramidLevels,
                            w >> numPyramidLevels, 3)

        self._maxHistoryLength = maxHistoryLength
        self._history = numpy.empty(historyShape,
                                    numpy.float32)
        self._historyTimestamps = collections.deque()

        self._numPyramidLevels = numPyramidLevels
        self._useLaplacianPyramid = useLaplacianPyramid

        self._minHz = minHz
        self._maxHz = maxHz
        self._amplification = amplification

        self._numFFTThreads = numFFTThreads
        self._numIFFTThreads = numIFFTThreads

        pyfftw.interfaces.cache.enable()
        pyfftw.interfaces.cache.set_keepalive_time(1.0)

        style = wx.CLOSE_BOX | wx.MINIMIZE_BOX | \
                wx.CAPTION | wx.SYSTEM_MENU | \
                wx.CLIP_CHILDREN
        wx.Frame.__init__(self, None, title=title,
                          style=style, size=size)
        
        self.Bind(wx.EVT_CLOSE, self._onCloseWindow)
        
        quitCommandID = wx.NewId()
        self.Bind(wx.EVT_MENU, self._onQuitCommand,
                  id=quitCommandID)
        acceleratorTable = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE,
             quitCommandID)
        ])
        self.SetAcceleratorTable(acceleratorTable)
        
        self._staticBitmap = wx.StaticBitmap(self,
                                             size=size)
        self._showImage(None)
        
        rootSizer = wx.BoxSizer(wx.VERTICAL)
        rootSizer.Add(self._staticBitmap)
        self.SetSizerAndFit(rootSizer)
        
        self._captureThread = threading.Thread(
                target=self._runCaptureLoop)
        self._captureThread.start()
    
    def _onCloseWindow(self, event):
        self._running = False
        self._captureThread.join()
        pyfftw.interfaces.cache.disable()
        self.Destroy()
    
    def _onQuitCommand(self, event):
        self.Close()

    def _runCaptureLoop(self):
        while self._running:
            success, image = self._capture.read()
            if image is not None:
                self._applyEulerianVideoMagnification(
                        image)
                if (self.mirrored):
                    image[:] = numpy.fliplr(image)
            wx.CallAfter(self._showImage, image)
    
    def _applyEulerianVideoMagnification(self, image):
        
        timestamp = timeit.default_timer()

        if self._useGrayOverlay:
            smallImage = cv2.cvtColor(
                    image, cv2.COLOR_BGR2GRAY).astype(
                            numpy.float32)
        else:
            smallImage = image.astype(numpy.float32)

        # Downsample the image using a pyramid technique.
        i = 0
        while i < self._numPyramidLevels:
            smallImage = cv2.pyrDown(smallImage)
            i += 1
        if self._useLaplacianPyramid:
            smallImage[:] -= \
                cv2.pyrUp(cv2.pyrDown(smallImage))

        historyLength = len(self._historyTimestamps)
        
        if historyLength < self._maxHistoryLength - 1:
            
            # Append the new image and timestamp to the
            # history.
            self._history[historyLength] = smallImage
            self._historyTimestamps.append(timestamp)
            
            # The history is still not full, so wait.
            return
        
        if historyLength == self._maxHistoryLength - 1:
            # Append the new image and timestamp to the
            # history.
            self._history[historyLength] = smallImage
            self._historyTimestamps.append(timestamp)
        else:
            # Drop the oldest image and timestamp from the
            # history and append the new ones.
            self._history[:-1] = self._history[1:]
            self._historyTimestamps.popleft()
            self._history[-1] = smallImage
            self._historyTimestamps.append(timestamp)
        
        # The history is full, so process it.
        
        # Find the average length of time per frame.
        startTime = self._historyTimestamps[0]
        endTime = self._historyTimestamps[-1]
        timeElapsed = endTime - startTime
        timePerFrame = \
                timeElapsed / self._maxHistoryLength
        #print 'FPS:', 1.0 / timePerFrame
        
        # Apply the temporal bandpass filter.
        fftResult = fft(self._history, axis=0,
                        threads=self._numFFTThreads)
        frequencies = fftfreq(
                self._maxHistoryLength, d=timePerFrame)
        lowBound = (numpy.abs(
                frequencies - self._minHz)).argmin()
        highBound = (numpy.abs(
                frequencies - self._maxHz)).argmin()
        fftResult[:lowBound] = 0j
        fftResult[highBound:-highBound] = 0j
        fftResult[-lowBound:] = 0j
        ifftResult = ifft(fftResult, axis=0,
                          threads=self._numIFFTThreads)

        # Amplify the result and overlay it on the
        # original image.
        overlay = numpy.real(ifftResult[-1]) * \
                          self._amplification
        i = 0
        while i < self._numPyramidLevels:
            overlay = cv2.pyrUp(overlay)
            i += 1
        if self._useGrayOverlay:
            overlay = cv2.cvtColor(overlay,
                                   cv2.COLOR_GRAY2BGR)
        cv2.convertScaleAbs(image + overlay, image)

    def _showImage(self, image):
        if image is None:
            # Provide a black bitmap.
            bitmap = wx.EmptyBitmap(self._imageWidth,
                                    self._imageHeight)
        else:
            # Convert the image to bitmap format.
            bitmap = WxUtils.wxBitmapFromCvImage(image)
        # Show the bitmap.
        self._staticBitmap.SetBitmap(bitmap)


def main():

    app = wx.App()

    # Show motion at edges with grayscale contrast.
    lazyEyes = LazyEyes()

    # Show motion in all areas with color contrast.
    #lazyEyes = LazyEyes(useLaplacianPyramid=False,
    #                    useGrayOverlay=False,
    #                    imageSize=(320, 240))

    # Show motion in all areas with color contrast, at
    # frequencies optimized for Joe's heartbeat.
    #lazyEyes = LazyEyes(minHz=1.4, maxHz=1.5,
    #                    useLaplacianPyramid=False,
    #                    useGrayOverlay=False,
    #                    imageSize=(320, 240))

    lazyEyes.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()