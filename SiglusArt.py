import sys
import io
import struct
from PIL import Image
import SiglusLzss as siglz

#We use pillow to convert the decoded raw bitmap to PNG/BMP

#Header: byte "type" followed by uint16_t width and height.
#the 24-bit variant has an extra uint32_t pair for compressed and uncompressed length.

#There are 3 main types of G00 file: 8-bit image, 24-bit RGB, and directory, which are likely multiple image files in one.
#denoted by a start byte of 0, 1, or 2, respectively.

if len(sys.argv) < 2:
  print ("Usage:",sys.argv[0],"<infile>")
  sys.exit(1)

infile = open(sys.argv[1],'rb')

type = infile.read(1)[0] #is a byte. not exactly much to process here...
width = struct.unpack("<H",infile.read(2))[0]
height = struct.unpack("<H",infile.read(2))[0]

if (type == 0):
    #we're a 24-bit image
    complen = struct.unpack("<I", infile.read(4))[0]
    decomplen = struct.unpack("<I", infile.read(4))[0]
    if (complen > decomplen):
        print("WTF: Compressed file length is more the the decompressed?")
        sys.exit()
    #decomp = lzss.decode(infile.read(complen))
    decomp = siglz.decompress_24(infile.read(complen), decomplen) #not standard lzss?
    if (len(decomp) != decomplen):
        print("WARN: Decompressed", "more" if len(decomp) > decomplen else "less","data than expected!")
    #SiglusExtract appears to flip the image from RGBA to BGRA (or maybe vertical flip? can barely read it...) but pillow can use it directly.
    img = Image.frombytes("RGBA",[width,height],bytes(decomp),"raw","BGRA")
    img.show()
if (type == 1):
    pass #not done yet...
    #8-bit!
if (type == 2):
    pass
    #A directory. recursion time!
