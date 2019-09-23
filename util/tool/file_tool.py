# coding=utf-8


import struct


# 支持文件类型
# 用16进制字符串的目的是可以知道文件头是多少字节
# 各种文件头的长度不一样，少半2字符，长则8字符
def type_list():
    print('获取文件格式十六进制码表……')
    return {
        "FFD8FF": 'JPEG',  # .xls or.doc
        '89504E47': 'PNG',  # .docx or .xlsx or .zip or.jar or .XLSX
        "47494638": "GIF",

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
def filetype(file_content=None, filename=None, tl=type_list()):
    ftype = 'unknown'
    if filename:
        binfile = open(filename, 'rb')
        content = binfile.read(20)
    elif file_content:
        content = file_content
    else:
        return ftype
    for hcode in tl.keys():
        num_of_bytes = int(len(hcode) / 2)  # 需要读多少字节
        hbytes = struct.unpack_from("B" * num_of_bytes, content)  # 一个 "B"表示一个字节
        f_hcode = str(bytes2hex(hbytes)).upper()
        if f_hcode == hcode:
            ftype = tl[hcode]
            break
    return ftype





