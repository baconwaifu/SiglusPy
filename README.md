# SiglusPy

SiglusPy is a library and set of tools designed to aid in working with SiglusEngine game files.
It is intended as a cross-platform alternative to SiglusExtract.

## SiglusArt
SiglusArt is a viewer for `.g00` files. currently only 24-bit RGB files are supported.

## SiglusImage
***CURRENTLY BROKEN***
A PIL plugin that adds support for 'simple' g00 files.  
complex files containing more than one image are planned later.

Chunked decompression is currently broken in a manner likely related to PIL's buffer handling.


## SiglusLzss
SiglusLzss is an implementation of the modified LZSS dictionary-coding compression algorithm used by SiglusEngine.
For 24-bit image files, each literal is a 24-bit RGB tuple, and each sequence length refers to such tuples, rather than bytes.

It decompresses to 32-bit RGBA, assuming a fully opaque image.

## TODO:
* multi-texture image support
* Script and Scene unpacking
* Re-compressing modified images
* Export to File
* Proper terminal automation flags
* Proper Modularization
