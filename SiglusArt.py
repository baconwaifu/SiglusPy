import sys
import io
import struct
from PIL import Image, ImageFile
import SiglusLzss as siglz
import SiglusImage

#We use pillow to convert the decoded raw bitmap to PNG/BMP

#Header: byte "type" followed by uint16_t width and height.
#the 24-bit variant has an extra uint32_t pair for compressed and uncompressed length.

#There are 3 main types of G00 file: 8-bit image, 24-bit RGB, and directory, which are likely multiple image files in one.
#denoted by a start byte of 0, 1, or 2, respectively.

if len(sys.argv) < 2:
  print ("Usage:",sys.argv[0],"<infile>")
  sys.exit(1)

new = True

if new:
  ImageFile.LOAD_TRUNCATED_IMAGES = True
  #decoder implemented in the PIL plugin SiglusImage
  img = Image.open(sys.argv[1])
  img.show()
else:
  #manual decoder
  infile = open(sys.argv[1],'rb')
  type = infile.read(1)[0] #is a byte. not exactly much to process here...
  width = struct.unpack("<H",infile.read(2))[0]
  height = struct.unpack("<H",infile.read(2))[0]
  complen, decomplen = struct.unpack("<II", infile.read(8))
  decomp = bytearray(decomplen) 
  siglz.decompress_24(infile.read(complen), decomp, decomplen)
  img = Image.frombytes("RGBA", [width,height], bytes(decomp), "raw" , "BGRA")
  img.show()
