#
# Autogenerated by Thrift Compiler (0.10.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py:tornado
#

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
import sys

from thrift.transport import TTransport


class CampaignHeadImageDO(object):
    """
    Attributes:
     - id
     - imageUrl
     - hrefUrl
     - createTime
     - updateTime
    """

    thrift_spec = (
        None,  # 0
        (1, TType.I32, 'id', None, None, ),  # 1
        (2, TType.STRING, 'imageUrl', 'UTF8', None, ),  # 2
        (3, TType.STRING, 'hrefUrl', 'UTF8', None, ),  # 3
        (4, TType.STRING, 'createTime', 'UTF8', None, ),  # 4
        (5, TType.STRING, 'updateTime', 'UTF8', None, ),  # 5
    )

    def __init__(self, id=None, imageUrl=None, hrefUrl=None, createTime=None, updateTime=None,):
        self.id = id
        self.imageUrl = imageUrl
        self.hrefUrl = hrefUrl
        self.createTime = createTime
        self.updateTime = updateTime

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, (self.__class__, self.thrift_spec))
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.I32:
                    self.id = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRING:
                    self.imageUrl = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.STRING:
                    self.hrefUrl = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.STRING:
                    self.createTime = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.STRING:
                    self.updateTime = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, (self.__class__, self.thrift_spec)))
            return
        oprot.writeStructBegin('CampaignHeadImageDO')
        if self.id is not None:
            oprot.writeFieldBegin('id', TType.I32, 1)
            oprot.writeI32(self.id)
            oprot.writeFieldEnd()
        if self.imageUrl is not None:
            oprot.writeFieldBegin('imageUrl', TType.STRING, 2)
            oprot.writeString(self.imageUrl.encode('utf-8') if sys.version_info[0] == 2 else self.imageUrl)
            oprot.writeFieldEnd()
        if self.hrefUrl is not None:
            oprot.writeFieldBegin('hrefUrl', TType.STRING, 3)
            oprot.writeString(self.hrefUrl.encode('utf-8') if sys.version_info[0] == 2 else self.hrefUrl)
            oprot.writeFieldEnd()
        if self.createTime is not None:
            oprot.writeFieldBegin('createTime', TType.STRING, 4)
            oprot.writeString(self.createTime.encode('utf-8') if sys.version_info[0] == 2 else self.createTime)
            oprot.writeFieldEnd()
        if self.updateTime is not None:
            oprot.writeFieldBegin('updateTime', TType.STRING, 5)
            oprot.writeString(self.updateTime.encode('utf-8') if sys.version_info[0] == 2 else self.updateTime)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
