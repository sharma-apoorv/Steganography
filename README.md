# Steganography

**Steganography** is the practice of concealing a file, message, image, or video within another file, message, image, or video. The word steganography combines the Greek words *steganos*, meaning "covered, concealed, or protected", and *graphein* meaning "writing".

The first recorded use of the term was in 1499 by Johannes Trithemius in his Steganographia, a treatise on cryptography and steganography, disguised as a book on magic. Generally, the hidden messages appear to be (or to be part of) something else: images, articles, shopping lists, or some other cover text.


# Project Description

This project can be conceptually divided into two main tasks: 

 1. Embedding a payload image into a carrier image
 2. Extracting a payload from a carrier.
 
![ProjectBlockDiagram](https://www.dropbox.com/s/9pv134y6berv032/ProjectBlockDiagram.png?dl=0)

## Embedding the Payload into the Carrier

### Raster Scan
An image is a 2D or a 3D Array of pixels. While a gray-scale image is a two dimensional data structure, it is useful to think of it, and process it, as a one dimensional array. This is referred to as a “Raster Scan”, and it is done by reading the image, starting at the upper left corner, and reading the first row, left to right, until the end. Then, we go to the second row, and read it left to right, and so on. Note that for color images, which are three dimensional data structures, there are more than one way to perform a scan. For this project, we will scan each channel independently, i.e. scan the Red channel for the whole image, the Green channel, then the Blue channel, and concatenate them together to have a one-dimensional array.

![RasterScan](https://www.dropbox.com/s/o27dn2z2nsrlh41/RasterScan.png?dl=0)

### Data Compression
Once the payload image is raster-scanned into an array, we are going to apply data compression to “potentially” reduce the size of the payload. The Python standard modules include a module called zlib which provides implementation for compressing data using the gzip file format. Note that we will only need to use the compress, and decompress functions from that module. The output of the compression process is also going to be an array of bytes, but its size will be different from its input.

![DataCompression](https://www.dropbox.com/s/tbjkotj21v4sxbs/Compression.png?dl=0)

### The XML Serialization
In order to be able to reconstruct the payload from the one dimensional array, we will need to know additional information about the payload dimensions, its type, etc. One easy way to include such metadata with the payload is to use the XML format, where we can add any number of desired attributes. For this project, we will use the following XML format:

    <?xml version="1.0" encoding="UTF-8"?>
    <payload type="[Color or Gray]" size="[rows,columns]" compressed="[True or False]">
    [CONTENT GOES HERE!]
    </payload>

There are three attributes that we will need: the type, size and compressed. The type is either “Gray” or “Color”, and the size holds the dimensions of the payload image. The size should be written as “rows,columns”, with a single comma and no space between the values. The last attribute is compressed, which is a Boolean flag indicating whether the data has been compressed or not. Finally, the compressed payload data is inserted as a sequence of numbers separated by commas. An example of an XML string would be:

    <?xml version="1.0" encoding="UTF-8"?>
    <payload type="Color" size="480,640" compressed="True">
    218,77,155,9,212,77,229,26,199,77,155,9,212,77,229,26,...
    ...
    </payload>

The final point to mention is that the example shown above is intended for illustrating the details of the XML structure and attributes. In the implementation, however, you are required to remove all newline characters from the XML string, making effectively a single line of text, as in:

    <?xml version="1.0" encoding="UTF-8"?><payload type="Color" ...>218,77,155,...</payload>
    
![XMLString](https://www.dropbox.com/s/admsv24blh7eotb/XMLString.png?dl=0)
### Base64 Encoding
At this point, we have obtained an XML string that contains the payload, along with its metadata. The next task to convert this array of 8-bit elements into 6-bit elements, which will be of certain advantage for the embedding process. You can certainly write your own implementation to perform this task, but one other option is to use the Base64 encoding, which aims to encode a sequence of bytes into an encoded string, where each character is only 6-bits, which can then be used to transfer data in a printable and human-readable form. This functionality is available in the base644 Python module. At the end of this process, the payload is represented as a sequence of numbers, where each number is guaranteed to be of size 6-bits.

![Base46Encoding](https://www.dropbox.com/s/o4z9m0drb710u54/Base64.png?dl=0)

### Embedding in the Carrier
The carrier in this project is also a color image, which, again, is a sequence of pixels, where each pixel consists of three bytes: Red, Green and Blue. We can now embed the payload sequence into the carrier, where each 6-bit element is embedded into one carrier pixel as follows:

 1. Obtain the binary representation of the payload element. For example, if the payload element is 30, its binary representation is 011110. Note that the binary representation should always occupy 6-bits, so 4 should be represented as 000100, as opposed to just 100.
 2. Split the binary value into three 2-bit parts. So, for the payload value 011110, we will have 01, 11 and 10. Note that the order of these parts matters.
 3. Obtain the binary representation of the RGB values of target carrier pixel. For example, let us assume those values to be R = 85, G = 112, B = 47, so their binary representations are:

    R = 01010101.
    G = 01110000.
    B = 00101111.
    

 4. Embed each of the 2-bit parts into the two least significant bits of these values:
 10 → 01010101 =⇒ 01010110.
 11 → 01110000 =⇒ 01110011.
 01 → 00101111 =⇒ 00101101.
![Embedding](https://www.dropbox.com/s/osmafvd7v6gx5vh/Embedding.png?dl=0)

## Extracting the Payload from the Carrier

Given a carrier image that has a payload embedded into it, we can obtain that payload back by reversing the steps taken to embed it, which is as follows: 
1. For the first pixel in the carrier, extract the two least significant bits from the Red, Green and Blue channels, and combine them to obtain the 6-bit element. 
2. Repeat the extraction until you obtain all of the elements. (Note that the payload may not have required all the pixels of the carrier, so you will need to know when to stop.) 
3. Once the payload is obtained, you will need to convert the 6-bit elements back into their 8-bit counterpart. If you have used Base64 encoding, then you will need to perform Base64 decoding. This will give us back the serialized XML string, with the rasterized data (possibly compressed) being its content. 
4. We can easily use the metadata stored in the XML attributes to reconstruct the payload image. As mentioned earlier, you should obtain an image that is an exact match to the starting payload.