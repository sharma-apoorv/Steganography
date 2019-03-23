from pprint import pprint as pp
import numpy as np
import zlib
import base64
import re
from scipy.misc import imread


class Payload:
    def __init__(self, img=None, compressionLevel=-1, content=None):
        if compressionLevel < -1 or compressionLevel > 9:
            raise ValueError("compressionLevel must be between -1 and 9, inclusive.")

        if img is None and content is None:
            raise ValueError("The content or image must be provided.")

        if type(content) != np.ndarray and type(img) != np.ndarray:
            raise TypeError("content and img must be of type numpy.ndarray")

        if img is None:
            self.content = content
            self.img = self.reconstructPayloadImage(content)
        elif content is None:
            self.img = img
            self.content = self.generateContentArray(compressionLevel)

    def generateContentArray(self, compressionLevel):
        xmlString = '<?xml version="1.0" encoding="UTF-8"?>'

        if self.img.ndim == 3:
            payloadType = "Color"
            (row, col, ch) = self.img.shape
            size = "%d,%d" % (row, col)

            # Extract the red, green and blue pixels --> reshape() can also be used. Need to check complexity
            fullImg = np.concatenate([self.img[:, :, 0].flat, self.img[:, :, 1].flat, self.img[:, :, 2].flat])

            # Compress the image given the compression level; ignore if -1
            if compressionLevel != -1:
                compress = "True"
                xmlString += '<payload type="%s" size="%s" compressed="%s">' % (payloadType, size, compress)

                # Compress the data with the relevant compression level
                compressData = zlib.compress(bytearray(fullImg), compressionLevel)

                # Add the compressed payload data to the XmlString
                xmlString += ",".join(map(str, list(compressData)))

            else:
                compress = False
                xmlString += '<payload type="{payLoad}" size="{rowCol}" compressed="{comp}">'.format(
                    payLoad=payloadType, rowCol=size, comp=compress)

                # Add the payload data to the XmlString
                xmlString += ",".join(map(str, list(fullImg)))

        elif self.img.ndim == 2:
            payloadType = "Gray"
            (row, col) = self.img.shape
            size = "{r},{c}".format(r=row, c=col)

            # Extract the red, green and blue pixels --> reshape() can also be used. Need to check complexity
            fullImg = list(self.img.flatten())

            if compressionLevel != -1:
                compress = True
                xmlString += '<payload type="{payLoad}" size="{rowCol}" compressed="{comp}">'.format(
                    payLoad=payloadType, rowCol=size, comp=compress)

                # Compress the data with the relevant compression level
                compressData = zlib.compress(bytearray(fullImg), compressionLevel)

                # Add the compressed payload data to the XmlString
                xmlString += ",".join(map(str, list(compressData)))

            else:
                compress = False
                xmlString += '<payload type="{payLoad}" size="{rowCol}" compressed="{comp}">'.format(
                    payLoad=payloadType, rowCol=size, comp=compress)

                # Add the payload data to the XmlString
                xmlString += ",".join(map(str, list(fullImg)))

        # Add ending part to finish the xmlString
        xmlString += "</payload>"

        # Covert xmlString to base64 encoded data
        encoded = base64.b64encode(xmlString.encode('utf-8'))

        l = self.get6BitSeq(list(encoded))
        # print(l)

        # Convert the list to np.array() type
        content = np.array(l, dtype=np.uint8)

        return content

    def get6BitSeq(self, l):
        table = self.charToNumTable()
        l_ret = []

        if l[-1] == 61 and l[-2] == 61:
            l = l[:-2]
        elif l[-1] == 61:
            l = l[:-1]

        a = np.array(l)

        l_map = np.vectorize(table.get)(a)
        #print(list(l_map))

        return list(l_map)

    def get8bitSeq(self, l):
        inv_map = self.numtoCharTable()
        a = np.array(l)

        l_map = np.vectorize(inv_map.get)(a)
        l_map = l_map.flat
        ret_str = "".join(map(str, list(l_map)))

        if (len(l) * 3 % 4) == 2:
            ret_str += "=="
        elif (len(l) * 3 % 4) == 1:
            ret_str += "="

        ret_str = bytes(ret_str, 'utf-8')

        return ret_str

    def charToNumTable(self):
        d = {43: 62,
             47: 63,
             48: 52,
             49: 53,
             50: 54,
             51: 55,
             52: 56,
             53: 57,
             54: 58,
             55: 59,
             56: 60,
             57: 61,
             65: 0,
             66: 1,
             67: 2,
             68: 3,
             69: 4,
             70: 5,
             71: 6,
             72: 7,
             73: 8,
             74: 9,
             75: 10,
             76: 11,
             77: 12,
             78: 13,
             79: 14,
             80: 15,
             81: 16,
             82: 17,
             83: 18,
             84: 19,
             85: 20,
             86: 21,
             87: 22,
             88: 23,
             89: 24,
             90: 25,
             97: 26,
             98: 27,
             99: 28,
             100: 29,
             101: 30,
             102: 31,
             103: 32,
             104: 33,
             105: 34,
             106: 35,
             107: 36,
             108: 37,
             109: 38,
             110: 39,
             111: 40,
             112: 41,
             113: 42,
             114: 43,
             115: 44,
             116: 45,
             117: 46,
             118: 47,
             119: 48,
             120: 49,
             121: 50,
             122: 51
             }

        return d

    def numtoCharTable(self):
        d = {0: 'A',
             1: 'B',
             2: 'C',
             3: 'D',
             4: 'E',
             5: 'F',
             6: 'G',
             7: 'H',
             8: 'I',
             9: 'J',
             10: 'K',
             11: 'L',
             12: 'M',
             13: 'N',
             14: 'O',
             15: 'P',
             16: 'Q',
             17: 'R',
             18: 'S',
             19: 'T',
             20: 'U',
             21: 'V',
             22: 'W',
             23: 'X',
             24: 'Y',
             25: 'Z',
             26: 'a',
             27: 'b',
             28: 'c',
             29: 'd',
             30: 'e',
             31: 'f',
             32: 'g',
             33: 'h',
             34: 'i',
             35: 'j',
             36: 'k',
             37: 'l',
             38: 'm',
             39: 'n',
             40: 'o',
             41: 'p',
             42: 'q',
             43: 'r',
             44: 's',
             45: 't',
             46: 'u',
             47: 'v',
             48: 'w',
             49: 'x',
             50: 'y',
             51: 'z',
             52: '0',
             53: '1',
             54: '2',
             55: '3',
             56: '4',
             57: '5',
             58: '6',
             59: '7',
             60: '8',
             61: '9',
             62: '+',
             63: '/'
             }

        return d

    def reconstructPayloadImage(self, content):
        # Convert the radix 64 list into utf-8 list
        encoded = self.get8bitSeq(content)

        xmlString = base64.b64decode(encoded)

        l = xmlString.split(b'</payload>')
        xmlString = str(l[0] + b'</payload>')

        # Convert the utf-8 list into xmlString
        # xmlString = str(base64.b64decode(encoded), 'utf-8')
        # print(xmlString)

        #Get rid of the extra stuff

        # Extract relevant information from the xmlString
        pattern = r"type=\"([a-zA-Z]+)\" size=\"([0-9]+),([0-9]+)\" compressed=\"([a-zA-Z]+)\">(.*)<"
        vals = re.search(pattern, xmlString)

        if vals:
            imgType = str(vals.group(1))
            row = int(vals.group(2))
            col = int(vals.group(3))
            compress = str(vals.group(4))
            imgData = list(map(int, str(vals.group(5)).split(",")))

        # If it is a color image set the dimension number to 3
        if (imgType == "Color"):
            dimn = 3

            # Check if the image data was compressed or not
            if compress == "True":
                fullImg = list(zlib.decompress(bytearray(imgData)))
            elif compress == "False":
                fullImg = imgData

            # l = self.completeArray(fullImg)
            # img = (np.array(l, dtype='uint8').reshape(row, col, dimn))

            img = self.completeArray(fullImg)
            img = np.reshape(img, (row, col, dimn))


        elif imgType == "Gray":
            # Check if the image data was compressed or not
            if compress == "True":
                fullImg = list(zlib.decompress(bytearray(imgData)))
            elif compress == "False":
                fullImg = imgData

            img = (np.array(list(fullImg), dtype='uint8').reshape(row, col))

        return img

    def completeArray(self, rgbImg):
        # fullImg = len(rgbImg) * [0]
        # fullImg[::3] = rgbImg[:int(len(rgbImg) / 3)]
        # fullImg[1::3] = rgbImg[int(len(rgbImg) / 3):int(len(rgbImg) * 2 / 3)]
        # fullImg[2::3] = rgbImg[int(len(rgbImg) * 2 / 3):]

        # return list(fullImg)

        rgbImg = np.array(rgbImg)
        allVals = np.split(rgbImg, 3)

        verticalVals = np.vstack([allVals[0], allVals[1], allVals[2]])
        fullImg = np.transpose(verticalVals)
        fullImg = np.uint8(fullImg)

        return fullImg

class Carrier:
    def __init__(self, img):
        if type(img) != np.ndarray:
            raise TypeError("Image being passed in must be of type np.ndarray")

        self.img = img

    def payloadExists(self):

        if self.img.ndim == 3:
            header = self.img[0][:7]
            headerList = list(((header & 0b11) << np.array([0, 2, 4])).sum(axis=1))
            headerStr = self.get8bitSeq(headerList)
            headerStr = base64.b64decode(headerStr)

        elif self.img.ndim == 2:
            header = self.img[0][:21]
            list2d = np.array(list(zip(header[::3], header[1::3], header[2::3])))
            headerList = list(((list2d & 0b11) << np.array([0, 2, 4])).sum(axis=1))
            headerStr = self.get8bitSeq(headerList)
            headerStr = base64.b64decode(headerStr)



        if headerStr == b'<?xml':
            return True

        return False

    def clean(self):
        randVals = np.random.randint(0, 4, self.img.shape)
        imgCpy = self.img ^ randVals

        # imgCpy = np.copy(self.img)
        # imgCpy = imgCpy & ~1

        return imgCpy

    def embedPayload(self, payload, override=False):
        # Check for type of payload
        if type(payload) != Payload:
            raise TypeError("The payload needs to be of type Payload.")

        # Check if the payload can be embedded into the image or not
        if len(self.img.shape) == 3:
            payloadSize = len(payload.content)
            maxSize = self.img.shape[0] * self.img.shape[1] * 3

            if payloadSize > maxSize:
                raise ValueError("Payload size is larger than what the carrier can hold.")

        if len(self.img.shape) == 2:
            payloadSize = len(payload.content) * 3
            maxSize = self.img.size

            if payloadSize > maxSize:
                raise ValueError("Payload size is larger than what the carrier can hold.")

        if override == False and self.payloadExists() == True:
            raise Exception("Current carrier already contains a payload.")

        # imgCpy = np.copy(self.img)

        # imgPart = imgCpy[0][:len(payload.content)]
        # contentArr = np.copy(payload.content).reshape(imgPart.shape)

        # high6Bits = (imgPart & ~0b11) # << np.array([0, 2, 4])).sum(axis=2)
        # embeddedPart = high6Bits | (contentArr & 3)

        #otherImg = imgCpy[]

        if self.img.ndim == 3:
            contentArr = np.copy(payload.content)
            imgCpy = (np.copy(self.img)).flat

            imgPart = imgCpy[0:len(payload.content) * 3]

            embeddedR = imgPart[::3]
            embeddedG = imgPart[1::3]
            embeddedB = imgPart[2::3]

            embeddedR = (embeddedR & ~3) | (contentArr & 3)
            embeddedG = (embeddedG & ~3) | ((contentArr & 12) >> 2)
            embeddedB = (embeddedB & ~3) | ((contentArr & 48) >> 4)

            embeddedPart = np.array(self.completeArray(list(embeddedR), list(embeddedG), list(embeddedB)))
            otherImg = imgCpy[len(payload.content) * 3:]

            embeddedCarrier = np.append(embeddedPart, otherImg)

            embeddedCarrier = np.reshape(embeddedCarrier, self.img.shape)
            embeddedCarrier = np.uint8(embeddedCarrier)

        elif self.img.ndim == 2:
            contentArr = np.copy(payload.content)
            imgCpy = (np.copy(self.img)).flat

            imgPart = (imgCpy[:len(contentArr) * 3]) & ~3
            otherImg = imgCpy[len(contentArr) * 3:]

            Rvals = (contentArr & 3)
            Gvals = ((contentArr & 12) >> 2)
            Bvals = ((contentArr & 48) >> 4)

            fullCtn = np.vstack([Rvals, Gvals, Bvals])
            fullCtn = np.transpose(fullCtn).flatten()

            embeddedCarrier = imgPart | fullCtn
            embeddedCarrier = np.concatenate([embeddedCarrier, otherImg])
            embeddedCarrier = np.reshape(embeddedCarrier, self.img.shape)
            embeddedCarrier = np.uint8(embeddedCarrier)

        return embeddedCarrier

    def completeArray(self, rList, gList, bList):
        fullImg = rList + gList + bList

        fullImg[::3] = rList
        fullImg[1::3] = gList
        fullImg[2::3] = bList

        return fullImg

    def extractPayload(self):
        if self.payloadExists() == False:
            raise Exception

        # if self.img.ndim == 3:
        #     header = self.img[0][:126]
        #     headerList = list(((header & 0b11) << np.array([0, 2, 4])).sum(axis=1))
        #     headerStr = self.get8bitSeq(headerList)
        #     headerStr = str(base64.b64decode(headerStr))
        #     print(headerStr)
        #
        #     pattern = r"type=\"([a-zA-Z]+)\" size=\"([0-9]+),([0-9]+)\" compressed=\"([a-zA-Z]+)\">"
        #     vals = re.search(pattern, headerStr)
        #
        #     if vals:
        #         row = int(vals.group(2))
        #         col = int(vals.group(3))
        #
        #     print(row, col)
        #
        #     imgCpy = np.copy(self.img[:row][:col])
        #     fulCtn = ((imgCpy & 0b11) << np.array([0, 2, 4])).sum(axis=2)
        #     fulCtn = fulCtn.flat
        #
        #     encoded = self.get8bitSeq(fulCtn)
        #     xmlString = base64.b64decode(encoded)
        #     print(xmlString)
        #     l = xmlString.split(b'</payload>')
        #     xmlString = str(l[0] + b'</payload>')
        #     # print(xmlString)
        #
        #     encoded = base64.b64encode(xmlString.encode('utf-8'))
        #     l = self.get6BitSeq(list(encoded))
        #
        #     ctn = np.array(l, dtype=np.uint8)
        #
        # # return Payload(content=ctn)

        if len(self.img.shape) == 3:
            fulCtn = ((self.img & 0b11) << np.array([0, 2, 4])).sum(axis=2)
            fulCtn = fulCtn.flatten()

        elif self.img.ndim == 2:
            imgCpy = np.copy(self.img).flat

            list2d = np.array(list(zip(imgCpy[::3], imgCpy[1::3], imgCpy[2::3])))
            fulCtn = list(((list2d & 0b11) << np.array([0, 2, 4])).sum(axis=1))
            fulCtn = np.array(fulCtn)

        return Payload(content=fulCtn)


        # if len(self.img.shape) == 3:
        #     fulCtn = ((self.img & 0b11) << np.array([0, 2, 4])).sum(axis=2)
        #     fulCtn = fulCtn.flat
        #
        #     # Convert the radix 64 list into utf-8 list
        #     encoded = self.get8bitSeq(fulCtn)
        #
        #     # Convert the utf-8 list into xmlString
        #     xmlString = base64.b64decode(encoded)
        #
        #     l = xmlString.split(b'</payload>')
        #     xmlString = str(l[0] + b'</payload>')
        #
        #     # Covert xmlString to base64 encoded data
        #     encoded = base64.b64encode(xmlString.encode('utf-8'))
        #
        #     l = self.get6BitSeq(list(encoded))
        #
        #     # Convert the list to np.array() type
        #     ctn = np.array(l, dtype=np.uint8)
        #
        # elif self.img.ndim == 2:
        #     imgCpy = np.copy(self.img).flat
        #
        #     list2d = np.array(list(zip(imgCpy[::3], imgCpy[1::3], imgCpy[2::3])))
        #     fulCtn = list(((list2d & 0b11) << np.array([0, 2, 4])).sum(axis=1))
        #
        #     # Convert the radix 64 list into utf-8 list
        #     encoded = self.get8bitSeq(fulCtn)
        #
        #     # Convert the utf-8 list into xmlString
        #     xmlString = base64.b64decode(encoded)
        #
        #     l = xmlString.split(b'</payload>')
        #     xmlString = str(l[0] + b'</payload>')
        #
        #     # Covert xmlString to base64 encoded data
        #     encoded = base64.b64encode(xmlString.encode('utf-8'))
        #
        #     l = self.get6BitSeq(list(encoded))
        #
        #     ctn = np.array(l, dtype=np.uint8)
        #
        # return Payload(content=ctn)

    def get8bitSeq(self, l):
        inv_map = self.numtoCharTable()
        a = np.array(l)

        l_map = np.vectorize(inv_map.get)(a)
        l_map = l_map.flat
        ret_str = "".join(map(str, list(l_map)))

        if (len(l) * 3 % 4) == 2:
            ret_str += "=="
        elif (len(l) * 3 % 4) == 1:
            ret_str += "="

        ret_str = bytes(ret_str, 'utf-8')

        return ret_str

    def numtoCharTable(self):
        d = {0: 'A',
             1: 'B',
             2: 'C',
             3: 'D',
             4: 'E',
             5: 'F',
             6: 'G',
             7: 'H',
             8: 'I',
             9: 'J',
             10: 'K',
             11: 'L',
             12: 'M',
             13: 'N',
             14: 'O',
             15: 'P',
             16: 'Q',
             17: 'R',
             18: 'S',
             19: 'T',
             20: 'U',
             21: 'V',
             22: 'W',
             23: 'X',
             24: 'Y',
             25: 'Z',
             26: 'a',
             27: 'b',
             28: 'c',
             29: 'd',
             30: 'e',
             31: 'f',
             32: 'g',
             33: 'h',
             34: 'i',
             35: 'j',
             36: 'k',
             37: 'l',
             38: 'm',
             39: 'n',
             40: 'o',
             41: 'p',
             42: 'q',
             43: 'r',
             44: 's',
             45: 't',
             46: 'u',
             47: 'v',
             48: 'w',
             49: 'x',
             50: 'y',
             51: 'z',
             52: '0',
             53: '1',
             54: '2',
             55: '3',
             56: '4',
             57: '5',
             58: '6',
             59: '7',
             60: '8',
             61: '9',
             62: '+',
             63: '/'
             }

        return d

    def get6BitSeq(self, l):
        table = self.charToNumTable()
        l_ret = []

        if l[-1] == 61 and l[-2] == 61:
            l = l[:-2]
        elif l[-1] == 61:
            l = l[:-1]

        a = np.array(l)

        l_map = np.vectorize(table.get)(a)
        #print(list(l_map))

        return list(l_map)

    def charToNumTable(self):
        d = {43: 62,
             47: 63,
             48: 52,
             49: 53,
             50: 54,
             51: 55,
             52: 56,
             53: 57,
             54: 58,
             55: 59,
             56: 60,
             57: 61,
             65: 0,
             66: 1,
             67: 2,
             68: 3,
             69: 4,
             70: 5,
             71: 6,
             72: 7,
             73: 8,
             74: 9,
             75: 10,
             76: 11,
             77: 12,
             78: 13,
             79: 14,
             80: 15,
             81: 16,
             82: 17,
             83: 18,
             84: 19,
             85: 20,
             86: 21,
             87: 22,
             88: 23,
             89: 24,
             90: 25,
             97: 26,
             98: 27,
             99: 28,
             100: 29,
             101: 30,
             102: 31,
             103: 32,
             104: 33,
             105: 34,
             106: 35,
             107: 36,
             108: 37,
             109: 38,
             110: 39,
             111: 40,
             112: 41,
             113: 42,
             114: 43,
             115: 44,
             116: 45,
             117: 46,
             118: 47,
             119: 48,
             120: 49,
             121: 50,
             122: 51
             }

        return d


if __name__ == "__main__":
    # img = np.arange(30).reshape(2, 5, 3)
    # # img2d = np.arange(30).reshape(2, 5, 3)
    # cLevel = 3
    # encoded = [15, 3, 61, 56, 27, 22, 48, 32, 29, 38, 21, 50, 28, 54, 37, 47, 27, 35, 52, 34, 12, 18, 56, 48, 8, 34, 1,
    #            37, 27, 38, 13, 47, 25, 6, 37, 46, 25, 51, 52, 34, 21, 21, 17, 6, 11, 19, 32, 34, 15, 51, 56, 60, 28, 6,
    #            5, 57, 27, 6, 61, 33, 25, 2, 1, 52, 30, 23, 1, 37, 15, 18, 9, 3, 27, 54, 49, 47, 28, 34, 8, 32, 28, 54,
    #            37, 58, 25, 19, 52, 34, 12, 34, 48, 53, 8, 34, 1, 35, 27, 54, 53, 48, 28, 38, 21, 51, 28, 54, 21, 36, 15,
    #            18, 9, 20, 28, 39, 21, 37, 8, 35, 56, 49, 12, 35, 0, 44, 14, 19, 16, 44, 14, 19, 36, 44, 14, 19, 24, 44,
    #            12, 19, 0, 50, 11, 3, 8, 50, 13, 50, 48, 50, 12, 35, 32, 44, 12, 35, 8, 53, 11, 3, 8, 51, 11, 3, 4, 56,
    #            11, 3, 4, 52, 14, 18, 48, 49, 13, 3, 16, 44, 12, 19, 0, 50, 11, 3, 4, 48, 12, 2, 48, 57, 13, 50, 48, 50,
    #            12, 51, 4, 44, 12, 35, 8, 54, 11, 3, 8, 49, 11, 3, 4, 54, 11, 3, 8, 50, 11, 3, 4, 52, 13, 50, 48, 49, 13,
    #            3, 32, 44, 14, 19, 28, 44, 14, 19, 32, 44, 12, 35, 8, 57, 11, 3, 8, 50, 13, 2, 48, 50, 12, 51, 0, 44, 12,
    #            19, 36, 44, 12, 35, 0, 44, 12, 19, 28, 44, 12, 19, 20, 49, 11, 3, 4, 52, 13, 34, 48, 53, 11, 3, 0, 44,
    #            12, 35, 8, 44, 12, 19, 36, 56, 11, 3, 4, 44, 12, 19, 32, 48, 15, 2, 61, 48, 24, 23, 37, 44, 27, 54, 5,
    #            36, 15, 32]
    #
    # encodedGray = [15, 3, 61, 56, 27, 22, 48, 32, 29, 38, 21, 50, 28, 54, 37, 47, 27, 35, 52, 34, 12, 18, 56, 48, 8, 34, 1,
    #                37, 27, 38, 13, 47, 25, 6, 37, 46, 25, 51, 52, 34, 21, 21, 17, 6, 11, 19, 32, 34, 15, 51, 56, 60, 28, 6,
    #                5, 57, 27, 6, 61, 33, 25, 2, 1, 52, 30, 23, 1, 37, 15, 18, 9, 7, 28, 38, 5, 57, 8, 34, 1, 51, 26, 23, 41,
    #                37, 15, 18, 8, 51, 11, 3, 4, 48, 8, 34, 1, 35, 27, 54, 53, 48, 28, 38, 21, 51, 28, 54, 21, 36, 15, 18, 9,
    #                20, 28, 39, 21, 37, 8, 35, 56, 49, 12, 35, 0, 44, 14, 19, 16, 44, 14, 19, 36, 44, 14, 19, 24, 44, 12, 19,
    #                0, 48, 11, 3, 36, 56, 11, 3, 4, 48, 12, 34, 48, 57, 13, 50, 48, 49, 12, 3, 4, 44, 14, 19, 36, 44, 12, 35,
    #                12, 49, 11, 3, 8, 50, 13, 2, 48, 50, 12, 35, 32, 44, 12, 35, 8, 54, 11, 3, 8, 51, 12, 2, 48, 50, 12, 35,
    #                20, 44, 12, 35, 8, 57, 11, 3, 8, 50, 13, 50, 48, 50, 12, 50, 48, 49, 13, 34, 48, 50, 12, 2, 48, 49, 14,
    #                2, 48, 50, 12, 34, 48, 49, 13, 50, 48, 50, 12, 18, 48, 49, 14, 18, 48, 49, 13, 19, 4, 44, 12, 19, 16,
    #                52, 11, 3, 4, 52, 14, 2, 48, 49, 13, 3, 24, 44, 12, 19, 20, 48, 11, 3, 4, 52, 13, 18, 48, 53, 11, 3,
    #                0, 44, 12, 19, 28, 44, 12, 19, 28, 51, 11, 3, 4, 44, 12, 19, 32, 48, 15, 2, 61, 48, 24, 23, 37, 44, 27,
    #                54, 5, 36, 15, 32]
    #
#     ctn = np.array(encoded)
    # ctnGray = np.array(encodedGray)
    # # print(img)
    # toHideImg = Payload(img, cLevel, None)
    # toHideContent = Payload(img=None, compressionLevel=cLevel, content=ctn)
    #
    # payloadGrayimg = Payload(img2d, cLevel, None)
    # payloadGrayctn = Payload(img=None, compressionLevel=cLevel, content=ctnGray)
    # # print(payloadGrayctn.img)
    #
    # # print(toHideImg.img)
    # # print(toHideImg.content)
    #
    # img = np.arange(30, 60).reshape(2, 5, 3)
    # img = np.uint8(img)
    # print()
    # # print(img)
    # shapeOfYou = Carrier(img)
    # l = shapeOfYou.embedPayload(toHideImg, False)
    # # shapeOfYou.extractPayload()

    # l = [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 3, 0, 0]
    # c1 = Carrier(np.array(l).reshape((2, 5, 3)))
    # c1.extractPayload()

    c = Carrier(imread("result1_9.png"))
    # c.payloadExists()
    c.extractPayload()
    # # c.embedPayload()

    # cGray = Carrier(imread("result3_3.png"))
    # pGray = Payload(img=imread("payload3.png"), compressionLevel=3)
    # val = cGray.payloadExists()
    # print(val)
    # cGray.embedPayload(payload=pGray, override=True)
    # cGray.extractPayload()

    #
    # pColor = Payload(img=imread("payload1.png"), compressionLevel=9)
    # c = Carrier(imread("carrier1.png"))
    #
    # c.embedPayload(pColor)

    # c1 = Carrier(img)
    # p1 = Payload(content=ctn)
    # ec = c1.embedPayload(p1)
    # print("Embedded Payload")
    # print(ec)
    #
    #
    # testPload = c1.extractPayload()
    # print(testPload.img)


