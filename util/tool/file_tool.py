# coding=utf-8

import struct


def typeList():
  return {
    "FFD8FF": "JPEG", #jpg
    "89504E47": "PNG", #png
    "47494638": "GIF",    # gif
    "49492A00": "TIFF", #tif
    "424D": "Windows Bitmap",  #bmp
    "41433130": "CAD", #dwg
    "38425053": "Adobe Photoshop",#psd
    "7B5C727466": "Rich Text Format",#rtf
    "3C3F786D6C": "XML", #xml
    "68746D6C3E": "HTML", #html
    "44656C69766572792D646174653A": "Email", #eml
    "CFAD12FEC5FD746F": "Outlook Express", #dbx
    "2142444E": "Outlook",  # pst
    "D0CF11E0": "MS Word/Excel",  # xls.or.doc
    "5374616E64617264204A": "MS Access" #mdb
  }

# 字节码转16进制字符串
def bytes2hex(bytes):
    num = len(bytes)
    hexstr = u""
    for i in range(num):
        t = u"%x" % bytes[i]
        if len(t) % 2:
            hexstr += u"0"
        hexstr += t
    return hexstr.upper()


# 获取文件类型
def filetype(filename):
    binfile = open(filename, 'rb')  # 必需二制字读取
    tl = typeList()
    ftype = 'unknown'
    for hcode in tl.keys():
        numOfBytes = len(hcode) / 2  # 需要读多少字节
        binfile.seek(0)  # 每次读取都要回到文件头，不然会一直往后读取
        hbytes = struct.unpack_from("B" * numOfBytes, binfile.read(numOfBytes))  # 一个 "B"表示一个字节
        f_hcode = bytes2hex(hbytes)
        if f_hcode == hcode:
            ftype = tl[hcode]
            break
    binfile.close()
    return ftype
