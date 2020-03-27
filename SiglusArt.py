import sys
import io
import argparse
import os
import os.path as path
import struct
from PIL import Image, ImageFile
import SiglusLzss as siglz
import SiglusImage

#We use pillow to convert the decoded raw bitmap to PNG/BMP

#Header: byte "type" followed by uint16_t width and height.
#the 24-bit variant has an extra uint32_t pair for compressed and uncompressed length.

#There are 3 main types of G00 file: 8-bit image, 24-bit RGB, and directory, which are likely multiple image files in one.
#denoted by a start byte of 0, 1, or 2, respectively.


def view(src,target):
  for s in src:
    if args.new:
      ImageFile.LOAD_TRUNCATED_IMAGES = True
      SiglusImage.SiglusImageFile.LOAD_COMPLEX = True
      #decoder implemented in the PIL plugin SiglusImage
      fd = open(s,'rb')
      if (fd.read(1)[0] == 2):
        raise ValueError("Multi-part image file! use '--old' or '-x' to view!")
      fd.seek(0)
      img = Image.open(fd)
      img.show()
    else:
      #the old manual decoder with compression split off. TESTING ONLY: this does *NOT* handle anything other than 24-bit images.
      infile = open(s,'rb')
      type = infile.read(1)[0] #is a byte. not exactly much to process here...
      width = struct.unpack("<H",infile.read(2))[0]
      height = struct.unpack("<H",infile.read(2))[0]
      if (type == 0):
        #24-bit!
        complen, decomplen = struct.unpack("<II", infile.read(8))
        decomp = bytearray(decomplen) 
        siglz.decompress_24(infile.read(complen), decomp, decomplen)
        img = Image.frombytes("RGBA", [width,height], bytes(decomp), "raw" , "BGRA")
        img.show()
      if (type == 1):
        #8-bit!
        complen, decomplen = struct.unpack("<II", infile.read(8))
        decomp = bytearray(decomplen)
        siglz.decompress_8(infile.read(complen), decomp, decomplen)
        img = Image.frombytes("L", [width,height], bytes(decomp))
        img.show()
      if (type == 2):
        #A directory. recursion time!
        images = SiglusImage.decodedir(infile, [width,height])
        for i in images:
          i.show()
       
def extract(src, target):
  for s in src:
      infile = open(s,'rb')
      type = infile.read(1)[0] #is a byte. not exactly much to process here...
      width = struct.unpack("<H",infile.read(2))[0]
      height = struct.unpack("<H",infile.read(2))[0]
      if (type == 0):
        #24-bit!
        complen, decomplen = struct.unpack("<II", infile.read(8))
        decomp = bytearray(decomplen) 
        siglz.decompress_24(infile.read(complen), decomp, decomplen)
        img = Image.frombytes("RGBA", [width,height], bytes(decomp), "raw" , "BGRA")
        if target is None:
          target = path.join(path.basedir(s), path.splitext(path.basename(s))[0] + ".png")
        if (path.exists(target)):
          if (not path.isdir(target)):
            input("WARN: file already exists! press Ctrl-C to abort, or enter to continue")
            out = target
          else:
            out = os.path.join(target,path.splitext(path.basename(s))[0] + ".png")
        else:
          if (path.isdir(target)):
            os.makedirs(target, exist_ok=True)
            out = os.path.join(target,path.splitext(path.basename(s))[0] + ".png")
          else:
            out = target
      if (type == 1):
        #8-bit!
        complen, decomplen = struct.unpack("<II", infile.read(8))
        decomp = bytearray(decomplen)
        siglz.decompress_8(infile.read(complen), decomp, decomplen)
        img = Image.frombytes("L", [width,height], bytes(decomp))
        if target is None:
          target = path.join(path.basedir(s), path.splitext(path.basename(s))[0] + ".png")
        if (path.exists(target)):
          if (not path.isdir(target)):
            input("WARN: file already exists! press Ctrl-C to abort, or enter to continue")
            out = target
          else:
            out = os.path.join(target,path.splitext(path.basename(s))[0] + ".png")
        else:
          if (path.isdir(target)):
            os.makedirs(target, exist_ok=True)
            out = os.path.join(target,path.splitext(path.basename(s))[0] + ".png")
          else:
            out = target
        img.save(out, "PNG")
      if (type == 2):
        #A directory. recursion time!
        images = SiglusImage.decodedir(infile, [width,height])
        if target is None:
          target = path.join(path.basedir(s), path.splitext(path.basename(s))[0])
        if path.exists(target) and not path.isdir(target):
          raise ValueError("Target path must either not exist, or be a directory!")
        if not path.exists(target):
          os.makedirs(target, exist_ok=True)
        count = 0
        for i in images:
          count += 1
          out = path.join(target,str(count)+".png")
          print(out)
          i.save(out, "PNG")

if (__name__ == '__main__'):
    if len(sys.argv) < 2:
      print ("Usage:",sys.argv[0],"[flags] <infile> ... [outfile]")
      sys.exit(1)
    p = argparse.ArgumentParser()
    p.add_argument('--extract', dest='action', action='store_const',
                   const=extract, default=view)
    p.add_argument('-x', dest='action', action='store_const',
                   const=extract, default=view)
    p.add_argument('--old', dest='new', const=False, action='store_const', default=True)
    p.add_argument('infiles', metavar='infiles', nargs='+')

    args = p.parse_args()
      
    if len(args.infiles) > 1 and args.action is extract:
      outfile = args.infiles[-1]
      args.infiles = args.infiles[:len(args.infiles)-1]
    else:
      outfile = None
    args.action(args.infiles, outfile)
