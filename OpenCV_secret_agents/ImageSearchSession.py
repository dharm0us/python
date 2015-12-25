import bing_search_api
import numpy
import cv2
import pprint
import RequestUtils

class ImageSearchSession:
   def __init__(self):
    self.verbose = False
    self._bing = bing_search_api.BingSearchAPI()
    self._query = ''
    self._results = []
    self._offset = 0
    self._numResultsRequested = 0
    self._numResultsReceived = 0
    self._numResultsAvailable = 0

   @property
   def query(self):
    return self._query

   @property
   def offset(self):
    return self._offset

   @property
   def numResultsRequested(self):
    return self._numResultsRequested

   @property
   def numResultsReceived(self):
    return self._numResultsReceived

   @property
   def numResultsAvailable(self):
    return self._numResultsAvailable

   def searchPrev(self):
    if self._offset == 0:
      return
    offset = max(0, self._offset - self._numResultsRequested)
    self.search(self._query, self._numResultsRequested, offset)

   def searchNext(self):
    if self._offset + self._numResultsRequested >= self._numResultsAvailable:
      return
    offset = self._offset + self._numResultsRequested
    self.search(self._query, self._numResultsRequested, offset)

   def search(self, query, numResultsRequested=20, offset=0):
    self._query = query
    self._numResultsRequested = numResultsRequested
    self._offset = offset
    params = {
      'ImageFilters': '"color:color+style:photo"',
      '$format': 'json',
      '$top': numResultsRequested,
      '$skip': offset
    }

    response = self._bing.search('image', query, params)
    if not RequestUtils.validateResponse(response):
      self._offset = 0
      self._numResultsReceived = 0
      return

    # In some versions, requests.Response.json is a dict.
    # In other versions, it is a method returning a dict.
    # Get the dict in either case.
    json = response.json
    if (hasattr(json, '__call__')):
      json = json()

    metaResults = json[u'd'][u'results'][0]
    if self.verbose:
      print 'Got results of Bing image search for "%s":' %  query
      pprint.pprint(metaResults)

    self._results = metaResults[u'Image']
    self._offset = int(metaResults[u'ImageOffset'])
    self._numResultsReceived = len(self._results)
    self._numResultsAvailable = int(metaResults[u'ImageTotal'])

   def getCvImageAndUrl(self, index, useThumbnail = False):
    if index >= self._numResultsReceived:
      return None, None
    result = self._results[index]
    url = result[u'MediaUrl']
    if useThumbnail:
      result = result[u'Thumbnail'], url
    return RequestUtils.cvImageFromUrl(url), url

def main():
  session = ImageSearchSession()
  session.verbose = True
  session.search('luxury condo sales')
  image, url = session.getCvImageAndUrl(3)
  cv2.imwrite('image.png', image)

if __name__ == '__main__':
  main()
