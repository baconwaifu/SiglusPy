import struct

try:
  import lzss #use this if it's available for the byte-level lzss; it's faster than the "pure" implementation below
  lzflag = True
except ImportError:
  lzflag = False

#tweaked lzss that operates on pixels instead of bytes. file pixels are 24 bits BGR, memory pixels are 32-bit BGRA (assumed opaque)
#stoppixel is intended as a crude "roll back to start of block" function. index 0 of the buffer should be the returned index from the last call.
#unfortunately, it doesn't work properly. might decide to calculate the length of a given block on the fly and only process it if it's complete
def decompress_24(buf, outbuf, decomplen, stoppixel=0):
    outcount = stoppixel
    count = 0
    blockp = 0
    try:
     if (outcount >= decomplen):
       print ("Done!")
       return (stoppixel,-1)
     while outcount < decomplen:
#      print(decomplen,outcount)
      blockp = count
      stoppixel = outcount
      tagmask = buf[count] #get a block of 8 items
      count += 1
      tagcount = 0x8
      while outcount < decomplen and tagcount > 0:
        if (tagmask % 2) == 0x01: #is pixel literal? append RGB to RGBA.
          outbuf[outcount] = buf[count]
          outbuf[outcount+1] = buf[count+1]
          outbuf[outcount+2] = buf[count+2]
          outbuf[outcount+3] = 0xff
          count += 3
          outcount += 4
        else: #is sequence; fish it out and play it back
          seekback = struct.unpack("<H",buf[count:count+2])[0] #seekback; could probably speed this step up by doing manual conversion...
          count += 2
          seqlen = seekback
          seekback = seekback >> 4 #strip off the 4-bit sequence length to get the 12-bit "walk-back" distance (in pixels)
          seekback = seekback << 2  #multiply by pixel size to get walk-back in bytes
          seqlen &= 0xf
          seqlen += 1
          backseek = outcount
          backseek -= seekback
          while (seqlen > 0):
            seqlen -= 1
#            print(tmpcount,hold)
            for i in range(4): #we're copying dwords here, not bytes. (0,1,2,3)
              outbuf[outcount] = outbuf[backseek]
              outcount += 1
              backseek += 1
        tagmask = tagmask >> 1 #get next bit in the mask
        tagcount -= 1
    except (IndexError, struct.error):
      print ("Incomplete Block")
      return (stoppixel, blockp) #this means the block is done for now...
    stoppixel = outcount
    blockp = count
    print ("Decompressed")
    return (stoppixel, blockp) #we're done, but it needs one more pass before echoing -1

#standard byte-level lzss?
def decompress_8(buf, outbuf, decomplen, stoppixel=0):
    #can't use the lzss library, no support for partial decode as far as I can tell, which is practically required for PIL plugins.
    outcount = stoppixel
    count = 0
    blockp = 0
    try:
     while outcount < decomplen:
#      print(decomplen,outcount)
      blockp = count
      tagmask = buf[count] #get a block of 8 items
      count += 1
      tagcount = 0x8
      while outcount < decomplen and tagcount > 0:
        if (tagmask % 2) == 0x01: #is literal? append.
          outbuf[outcount] = buf[count]
          count += 1
          outcount += 1
        else: #is sequence; fish it out and play it back
          seekback = struct.unpack("<H",buf[count:count+2])[0] #seekback; could probably speed this step up by doing manual conversion...
          count += 2
          seqlen = seekback
          seekback = seekback >> 4 #strip the sequence length to get a 12-bit walkback (in bytes)
          seqlen &= 0xf
          seqlen += 2 #minimum byte sequence is 2 bytes, to avoid the tag taking more space than the sequence...
          backseek = outcount
          backseek -= seekback
          while (seqlen > 0):
            seqlen -= 1
#            print(tmpcount,hold)
            outbuf[outcount] = outbuf[backseek]
            outcount += 1
            backseek += 1
        tagmask = tagmask >> 1 #get next bit in the mask
        tagcount -= 1
    except (IndexError) as e: #incomplete block (or malformed stream...)
      return (stoppixel, blockp)
    except struct.error:
      return (stoppixel, blockp) #return the recorded state with the number of bytes consumed
    return (stoppixel, -1)

def compress_24(buf):
    #this isn't exactly "compression" but it abuses the format enough for the engine to pick it up...
    #takes a flat ***BGR*** image. *NOT* BGRA. CONVERT IT FIRST.
    #also, this does *not* include the compression header.
    out = b''
    count = 0
    while count < len(buf):
      b += [0xff]
      b += buf[count:count+(8*3)]
      count += (8*3)
    return out
