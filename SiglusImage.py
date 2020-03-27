#provides a PIL decode function for basic g00 images,
#and more advanced "ImageFactory" methods for complex images (multi-part images; usually face data)
import SiglusLzss as siglz
import struct
from PIL import Image, ImageFile

def decode24(fp): #takes a file-like object pointing to the compression header; is broken off for comples image decoding
        complen = struct.unpack("<I", fp.read(4))[0]
        decomplen = struct.unpack("<I", fp.read(4))[0]
        if (complen > decomplen):
          raise IndexError("WTF: Compressed file length is more the the decompressed?")
        #decomp = lzss.decode(infile.read(complen))
        decomp = siglz.decompress_24(fp.read(complen), decomplen) #is lzss, but on whole pixels
        if (len(decomp) != decomplen):
          raise IndexError("Decompressed less data than expected!") #the "more" condition is never true; the decoder yields or raises an IndexError 
                                                                    #(TODO: check if it's for the output array and raise it higher if so)
        return decomp

def decodedir(fp): #takes file-like, returns dict of numbered SiglusImages, with further dirs nesting.
  pass
#for complex archive elements; just has placement X/Y info tacked on
#class SiglusImage(Image):
#    def __init__(self):
#      pass

class SiglusImageDecode(ImageFile.PyDecoder):
    def init(self, args):
      self.mode = args[0]
      self.start = True
      self._pulls_fd = True
    def decode(self, buffer):
      if not self.fd:
        print("ERROR: pulls_fd isn't working!")
      if self.start: #this is the first time we have access to the buffer...
        self.complen, self.decomplen = struct.unpack("<II", self.fd.read(8)) #we don't care about compressed length anymore; just go till we have all the data.
#        print(self.complen)
#        print(self.decomplen)
        self.total = 0
        self.decbuf = bytearray(self.decomplen) #we keep our own state here; the math to convert pixel coords to buffer index would slow things down
#        self.buf = b''
#        self.buf += buffer[8:]
        self.start = False
#      else:
#        self.buf += buffer
#      return (len(self.buf),0)
#    def cleanup(self): #a cheeky hack; chunked decompression is currently broken in an unexplainable manner. need to do more testing.
#      buffer = self.buf
      buffer = self.fd.read(self.complen)
      self.stoppx = 0
      if self.mode == "RGBA":
        if self.start:
          self.stoppx, consumed = siglz.decompress_24(buffer[8:], self.decbuf, self.decomplen) #strip the header if we're just starting out
        else:
          self.stoppx, consumed = siglz.decompress_24(buffer, self.decbuf, self.decomplen, self.stoppx) #otherwise it's just block data from here out
      if self.mode == "L":
        if self.start:
          self.stoppx, consumed = siglz.decompress_8(buffer[8:], self.decbuf, self.decomplen) #strip the header if we're just starting out
        else:
          self.stoppx, consumed = siglz.decompress_8(buffer, self.decbuf, self.decomplen, self.stoppx) #otherwise it's just block data from here out
      if self.start:
        self.start = False
      self.total += consumed
#      print ("consumed",consumed,"bytes out of",len(buffer),"for a total of",self.total,"bytes consumed")
      return (consumed, 0)
    def cleanup(self):
      self.set_as_raw(bytes(self.decbuf), "BGRA") #we're decompressed, so shit out the image!
#be careful with this; it does some quick sanity checks, but g00 has no magic.
class SiglusImageFile(ImageFile.ImageFile):
    format = "G00"
    format_description = "SiglusEngine G00 Image"
    def _open(self, complex=False):
     try:
      type = self.fp.read(1)[0] #is a byte. not exactly much to process here...
      self._size = struct.unpack("<HH",self.fp.read(4)) #can just read width/height directly into tuple...
      

      if (type == 0):
      #we're a 24-bit image
        self.mode = "RGBA"
        self.tile = [
          ("Siglus", (0,0) + self.size, self.fp.tell(), ("RGBA", 0, 1))
        ]
#        decomp = decode24(self.fp)
#        img = Image.frombytes("G00_24",[width,height],bytes(decomp),"raw","BGRA")
#        img.show()
      elif (type == 1):
      #we're an 8-bit image
        self.mode = "L"
        self.tile = [
          ("Siglus", (0,0) + self.size, self.fp.tell(), ("8", 0, 1))
        ]
      elif (type == 2):
        if not complex:
          raise SyntaxError("Complex g00 image archives are not supported with trivial decode")
        raise NotImplementedError()
     except Exception as e:
       print(e)
Image.register_decoder("Siglus", SiglusImageDecode)
Image.register_open("G00", SiglusImageFile)
Image.register_extension("G00", ".g00")
