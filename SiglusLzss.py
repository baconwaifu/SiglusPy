import struct

def decompress_24(buf, decomplen):
    outbuf = bytearray(decomplen)
    outcount = 0
    count = 0
    while outcount < decomplen:
#      print(decomplen,outcount)
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
          seekback = seekback >> 4
          seekback = seekback << 2 #divide by two and clamp to a multiple of datum size
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
    return outbuf

