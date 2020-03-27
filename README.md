# SiglusPy

SiglusPy is a library and set of tools designed to aid in working with SiglusEngine game files.
It is intended as a cross-platform alternative to SiglusExtract.

## SiglusArt
SiglusArt is a viewer and extraction tool for `.g00` files.
It handles 24-bit RGB, 32-bit RGBA multi-image archives, and (untested) 8-bit images.

## SiglusImage
A PIL plugin that adds immediate on-import support for 'simple' g00 files.  
complex files containing more than one image require calling `decodedir(file, [width,height])`
to recieve a list of Image objects. the size parameter is optional, and is used during
the block compositing step to place the parts on a canvas the size of the full image,
rather than just the part. useful if exporting face overlays, as they can be overlaid
onto the base with no extra work or information.

Chunked decompression is currently broken in a manner likely related to PIL's buffer handling, 
so this uses `pull_fp` to access the file-like directly.


## SiglusLzss
SiglusLzss is an implementation of the modified LZSS dictionary-coding compression algorithm used by SiglusEngine.
For 24-bit image files, each literal is a 24-bit RGB tuple, and each sequence length refers to such tuples, rather than bytes.

It decompresses to 32-bit RGBA, assuming a fully opaque image.

It also contains a standard 8-bit LZSS implementation in pure-python.

## TODO:
* Script and Scene unpacking
* Re-compressing modified images (a cheap hack is present in Lzss, but it fakes the compression)
* Proper Modularization
