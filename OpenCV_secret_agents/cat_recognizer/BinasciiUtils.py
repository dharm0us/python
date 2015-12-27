import binascii

def fourCharsToInt(s):
  return int(binascii.hexlify(s), 16)

def intToFourChars(i):
  return binascii.unhexlify(format(i, 'x'))

if __name__ == '__main__':
  print intToFourChars(fourCharsToInt('dhar'))