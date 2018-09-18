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


class Candidate(object):
    """
    Attributes:
     - id
     - presenteeUserId
     - presenteeName
     - presenteeFriendId
     - presenteeFriendName
     - presenteeLogo
     - isRecom
     - viewNumber
     - insterested
    """

    thrift_spec = (
        None,  # 0
        (1, TType.I32, 'id', None, None, ),  # 1
        (2, TType.I32, 'presenteeUserId', None, None, ),  # 2
        (3, TType.STRING, 'presenteeName', 'UTF8', None, ),  # 3
        (4, TType.I32, 'presenteeFriendId', None, None, ),  # 4
        (5, TType.STRING, 'presenteeFriendName', 'UTF8', None, ),  # 5
        (6, TType.STRING, 'presenteeLogo', 'UTF8', None, ),  # 6
        (7, TType.I32, 'isRecom', None, None, ),  # 7
        (8, TType.I32, 'viewNumber', None, None, ),  # 8
        (9, TType.BOOL, 'insterested', None, None, ),  # 9
    )

    def __init__(self, id=None, presenteeUserId=None, presenteeName=None, presenteeFriendId=None, presenteeFriendName=None, presenteeLogo=None, isRecom=None, viewNumber=None, insterested=None,):
        self.id = id
        self.presenteeUserId = presenteeUserId
        self.presenteeName = presenteeName
        self.presenteeFriendId = presenteeFriendId
        self.presenteeFriendName = presenteeFriendName
        self.presenteeLogo = presenteeLogo
        self.isRecom = isRecom
        self.viewNumber = viewNumber
        self.insterested = insterested

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
                if ftype == TType.I32:
                    self.presenteeUserId = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.STRING:
                    self.presenteeName = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.I32:
                    self.presenteeFriendId = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.STRING:
                    self.presenteeFriendName = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 6:
                if ftype == TType.STRING:
                    self.presenteeLogo = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 7:
                if ftype == TType.I32:
                    self.isRecom = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 8:
                if ftype == TType.I32:
                    self.viewNumber = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 9:
                if ftype == TType.BOOL:
                    self.insterested = iprot.readBool()
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
        oprot.writeStructBegin('Candidate')
        if self.id is not None:
            oprot.writeFieldBegin('id', TType.I32, 1)
            oprot.writeI32(self.id)
            oprot.writeFieldEnd()
        if self.presenteeUserId is not None:
            oprot.writeFieldBegin('presenteeUserId', TType.I32, 2)
            oprot.writeI32(self.presenteeUserId)
            oprot.writeFieldEnd()
        if self.presenteeName is not None:
            oprot.writeFieldBegin('presenteeName', TType.STRING, 3)
            oprot.writeString(self.presenteeName.encode('utf-8') if sys.version_info[0] == 2 else self.presenteeName)
            oprot.writeFieldEnd()
        if self.presenteeFriendId is not None:
            oprot.writeFieldBegin('presenteeFriendId', TType.I32, 4)
            oprot.writeI32(self.presenteeFriendId)
            oprot.writeFieldEnd()
        if self.presenteeFriendName is not None:
            oprot.writeFieldBegin('presenteeFriendName', TType.STRING, 5)
            oprot.writeString(self.presenteeFriendName.encode('utf-8') if sys.version_info[0] == 2 else self.presenteeFriendName)
            oprot.writeFieldEnd()
        if self.presenteeLogo is not None:
            oprot.writeFieldBegin('presenteeLogo', TType.STRING, 6)
            oprot.writeString(self.presenteeLogo.encode('utf-8') if sys.version_info[0] == 2 else self.presenteeLogo)
            oprot.writeFieldEnd()
        if self.isRecom is not None:
            oprot.writeFieldBegin('isRecom', TType.I32, 7)
            oprot.writeI32(self.isRecom)
            oprot.writeFieldEnd()
        if self.viewNumber is not None:
            oprot.writeFieldBegin('viewNumber', TType.I32, 8)
            oprot.writeI32(self.viewNumber)
            oprot.writeFieldEnd()
        if self.insterested is not None:
            oprot.writeFieldBegin('insterested', TType.BOOL, 9)
            oprot.writeBool(self.insterested)
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


class CandidateList(object):
    """
    Attributes:
     - positionId
     - positionName
     - candidates
    """

    thrift_spec = (
        None,  # 0
        (1, TType.I32, 'positionId', None, None, ),  # 1
        (2, TType.STRING, 'positionName', 'UTF8', None, ),  # 2
        (3, TType.LIST, 'candidates', (TType.STRUCT, (Candidate, Candidate.thrift_spec), False), None, ),  # 3
    )

    def __init__(self, positionId=None, positionName=None, candidates=None,):
        self.positionId = positionId
        self.positionName = positionName
        self.candidates = candidates

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
                    self.positionId = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRING:
                    self.positionName = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.LIST:
                    self.candidates = []
                    (_etype3, _size0) = iprot.readListBegin()
                    for _i4 in range(_size0):
                        _elem5 = Candidate()
                        _elem5.read(iprot)
                        self.candidates.append(_elem5)
                    iprot.readListEnd()
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
        oprot.writeStructBegin('CandidateList')
        if self.positionId is not None:
            oprot.writeFieldBegin('positionId', TType.I32, 1)
            oprot.writeI32(self.positionId)
            oprot.writeFieldEnd()
        if self.positionName is not None:
            oprot.writeFieldBegin('positionName', TType.STRING, 2)
            oprot.writeString(self.positionName.encode('utf-8') if sys.version_info[0] == 2 else self.positionName)
            oprot.writeFieldEnd()
        if self.candidates is not None:
            oprot.writeFieldBegin('candidates', TType.LIST, 3)
            oprot.writeListBegin(TType.STRUCT, len(self.candidates))
            for iter6 in self.candidates:
                iter6.write(oprot)
            oprot.writeListEnd()
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


class CandidateListParam(object):
    """
    Attributes:
     - postUserId
     - clickTime
     - recoms
     - companyId
    """

    thrift_spec = (
        None,  # 0
        (1, TType.I32, 'postUserId', None, None, ),  # 1
        (2, TType.STRING, 'clickTime', 'UTF8', None, ),  # 2
        (3, TType.LIST, 'recoms', (TType.I32, None, False), None, ),  # 3
        (4, TType.I32, 'companyId', None, None, ),  # 4
    )

    def __init__(self, postUserId=None, clickTime=None, recoms=None, companyId=None,):
        self.postUserId = postUserId
        self.clickTime = clickTime
        self.recoms = recoms
        self.companyId = companyId

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
                    self.postUserId = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRING:
                    self.clickTime = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.LIST:
                    self.recoms = []
                    (_etype10, _size7) = iprot.readListBegin()
                    for _i11 in range(_size7):
                        _elem12 = iprot.readI32()
                        self.recoms.append(_elem12)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.I32:
                    self.companyId = iprot.readI32()
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
        oprot.writeStructBegin('CandidateListParam')
        if self.postUserId is not None:
            oprot.writeFieldBegin('postUserId', TType.I32, 1)
            oprot.writeI32(self.postUserId)
            oprot.writeFieldEnd()
        if self.clickTime is not None:
            oprot.writeFieldBegin('clickTime', TType.STRING, 2)
            oprot.writeString(self.clickTime.encode('utf-8') if sys.version_info[0] == 2 else self.clickTime)
            oprot.writeFieldEnd()
        if self.recoms is not None:
            oprot.writeFieldBegin('recoms', TType.LIST, 3)
            oprot.writeListBegin(TType.I32, len(self.recoms))
            for iter13 in self.recoms:
                oprot.writeI32(iter13)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.companyId is not None:
            oprot.writeFieldBegin('companyId', TType.I32, 4)
            oprot.writeI32(self.companyId)
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


class RecommendResult(object):
    """
    Attributes:
     - id
     - positionName
     - presenteeName
     - nextOne
     - recomTotal
     - recomIndex
     - recomIgnore
     - clickTime
    """

    thrift_spec = (
        None,  # 0
        (1, TType.I32, 'id', None, None, ),  # 1
        (2, TType.STRING, 'positionName', 'UTF8', None, ),  # 2
        (3, TType.STRING, 'presenteeName', 'UTF8', None, ),  # 3
        (4, TType.BOOL, 'nextOne', None, None, ),  # 4
        (5, TType.I32, 'recomTotal', None, None, ),  # 5
        (6, TType.I32, 'recomIndex', None, None, ),  # 6
        (7, TType.I32, 'recomIgnore', None, None, ),  # 7
        (8, TType.STRING, 'clickTime', 'UTF8', None, ),  # 8
    )

    def __init__(self, id=None, positionName=None, presenteeName=None, nextOne=None, recomTotal=None, recomIndex=None, recomIgnore=None, clickTime=None,):
        self.id = id
        self.positionName = positionName
        self.presenteeName = presenteeName
        self.nextOne = nextOne
        self.recomTotal = recomTotal
        self.recomIndex = recomIndex
        self.recomIgnore = recomIgnore
        self.clickTime = clickTime

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
                    self.positionName = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.STRING:
                    self.presenteeName = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.BOOL:
                    self.nextOne = iprot.readBool()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.I32:
                    self.recomTotal = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 6:
                if ftype == TType.I32:
                    self.recomIndex = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 7:
                if ftype == TType.I32:
                    self.recomIgnore = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 8:
                if ftype == TType.STRING:
                    self.clickTime = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
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
        oprot.writeStructBegin('RecommendResult')
        if self.id is not None:
            oprot.writeFieldBegin('id', TType.I32, 1)
            oprot.writeI32(self.id)
            oprot.writeFieldEnd()
        if self.positionName is not None:
            oprot.writeFieldBegin('positionName', TType.STRING, 2)
            oprot.writeString(self.positionName.encode('utf-8') if sys.version_info[0] == 2 else self.positionName)
            oprot.writeFieldEnd()
        if self.presenteeName is not None:
            oprot.writeFieldBegin('presenteeName', TType.STRING, 3)
            oprot.writeString(self.presenteeName.encode('utf-8') if sys.version_info[0] == 2 else self.presenteeName)
            oprot.writeFieldEnd()
        if self.nextOne is not None:
            oprot.writeFieldBegin('nextOne', TType.BOOL, 4)
            oprot.writeBool(self.nextOne)
            oprot.writeFieldEnd()
        if self.recomTotal is not None:
            oprot.writeFieldBegin('recomTotal', TType.I32, 5)
            oprot.writeI32(self.recomTotal)
            oprot.writeFieldEnd()
        if self.recomIndex is not None:
            oprot.writeFieldBegin('recomIndex', TType.I32, 6)
            oprot.writeI32(self.recomIndex)
            oprot.writeFieldEnd()
        if self.recomIgnore is not None:
            oprot.writeFieldBegin('recomIgnore', TType.I32, 7)
            oprot.writeI32(self.recomIgnore)
            oprot.writeFieldEnd()
        if self.clickTime is not None:
            oprot.writeFieldBegin('clickTime', TType.STRING, 8)
            oprot.writeString(self.clickTime.encode('utf-8') if sys.version_info[0] == 2 else self.clickTime)
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


class RecommmendParam(object):
    """
    Attributes:
     - id
     - realName
     - company
     - position
     - mobile
     - recomReason
     - companyId
     - postUserId
     - clickTime
     - gender
     - email
    """

    thrift_spec = (
        None,  # 0
        (1, TType.I32, 'id', None, None, ),  # 1
        (2, TType.STRING, 'realName', 'UTF8', None, ),  # 2
        (3, TType.STRING, 'company', 'UTF8', None, ),  # 3
        (4, TType.STRING, 'position', 'UTF8', None, ),  # 4
        (5, TType.STRING, 'mobile', 'UTF8', None, ),  # 5
        (6, TType.STRING, 'recomReason', 'UTF8', None, ),  # 6
        (7, TType.I32, 'companyId', None, None, ),  # 7
        (8, TType.I32, 'postUserId', None, None, ),  # 8
        (9, TType.STRING, 'clickTime', 'UTF8', None, ),  # 9
        (10, TType.BYTE, 'gender', None, None, ),  # 10
        (11, TType.STRING, 'email', 'UTF8', None, ),  # 11
    )

    def __init__(self, id=None, realName=None, company=None, position=None, mobile=None, recomReason=None, companyId=None, postUserId=None, clickTime=None, gender=None, email=None,):
        self.id = id
        self.realName = realName
        self.company = company
        self.position = position
        self.mobile = mobile
        self.recomReason = recomReason
        self.companyId = companyId
        self.postUserId = postUserId
        self.clickTime = clickTime
        self.gender = gender
        self.email = email

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
                    self.realName = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.STRING:
                    self.company = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.STRING:
                    self.position = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.STRING:
                    self.mobile = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 6:
                if ftype == TType.STRING:
                    self.recomReason = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 7:
                if ftype == TType.I32:
                    self.companyId = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 8:
                if ftype == TType.I32:
                    self.postUserId = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 9:
                if ftype == TType.STRING:
                    self.clickTime = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 10:
                if ftype == TType.BYTE:
                    self.gender = iprot.readByte()
                else:
                    iprot.skip(ftype)
            elif fid == 11:
                if ftype == TType.STRING:
                    self.email = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
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
        oprot.writeStructBegin('RecommmendParam')
        if self.id is not None:
            oprot.writeFieldBegin('id', TType.I32, 1)
            oprot.writeI32(self.id)
            oprot.writeFieldEnd()
        if self.realName is not None:
            oprot.writeFieldBegin('realName', TType.STRING, 2)
            oprot.writeString(self.realName.encode('utf-8') if sys.version_info[0] == 2 else self.realName)
            oprot.writeFieldEnd()
        if self.company is not None:
            oprot.writeFieldBegin('company', TType.STRING, 3)
            oprot.writeString(self.company.encode('utf-8') if sys.version_info[0] == 2 else self.company)
            oprot.writeFieldEnd()
        if self.position is not None:
            oprot.writeFieldBegin('position', TType.STRING, 4)
            oprot.writeString(self.position.encode('utf-8') if sys.version_info[0] == 2 else self.position)
            oprot.writeFieldEnd()
        if self.mobile is not None:
            oprot.writeFieldBegin('mobile', TType.STRING, 5)
            oprot.writeString(self.mobile.encode('utf-8') if sys.version_info[0] == 2 else self.mobile)
            oprot.writeFieldEnd()
        if self.recomReason is not None:
            oprot.writeFieldBegin('recomReason', TType.STRING, 6)
            oprot.writeString(self.recomReason.encode('utf-8') if sys.version_info[0] == 2 else self.recomReason)
            oprot.writeFieldEnd()
        if self.companyId is not None:
            oprot.writeFieldBegin('companyId', TType.I32, 7)
            oprot.writeI32(self.companyId)
            oprot.writeFieldEnd()
        if self.postUserId is not None:
            oprot.writeFieldBegin('postUserId', TType.I32, 8)
            oprot.writeI32(self.postUserId)
            oprot.writeFieldEnd()
        if self.clickTime is not None:
            oprot.writeFieldBegin('clickTime', TType.STRING, 9)
            oprot.writeString(self.clickTime.encode('utf-8') if sys.version_info[0] == 2 else self.clickTime)
            oprot.writeFieldEnd()
        if self.gender is not None:
            oprot.writeFieldBegin('gender', TType.BYTE, 10)
            oprot.writeByte(self.gender)
            oprot.writeFieldEnd()
        if self.email is not None:
            oprot.writeFieldBegin('email', TType.STRING, 11)
            oprot.writeString(self.email.encode('utf-8') if sys.version_info[0] == 2 else self.email)
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


class RecomRecordResult(object):
    """
    Attributes:
     - id
     - title
     - presenteeName
     - clickTime
     - recom
    """

    thrift_spec = (
        None,  # 0
        (1, TType.I32, 'id', None, None, ),  # 1
        (2, TType.STRING, 'title', 'UTF8', None, ),  # 2
        (3, TType.STRING, 'presenteeName', 'UTF8', None, ),  # 3
        (4, TType.STRING, 'clickTime', 'UTF8', None, ),  # 4
        (5, TType.BYTE, 'recom', None, None, ),  # 5
    )

    def __init__(self, id=None, title=None, presenteeName=None, clickTime=None, recom=None,):
        self.id = id
        self.title = title
        self.presenteeName = presenteeName
        self.clickTime = clickTime
        self.recom = recom

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
                    self.title = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.STRING:
                    self.presenteeName = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.STRING:
                    self.clickTime = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.BYTE:
                    self.recom = iprot.readByte()
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
        oprot.writeStructBegin('RecomRecordResult')
        if self.id is not None:
            oprot.writeFieldBegin('id', TType.I32, 1)
            oprot.writeI32(self.id)
            oprot.writeFieldEnd()
        if self.title is not None:
            oprot.writeFieldBegin('title', TType.STRING, 2)
            oprot.writeString(self.title.encode('utf-8') if sys.version_info[0] == 2 else self.title)
            oprot.writeFieldEnd()
        if self.presenteeName is not None:
            oprot.writeFieldBegin('presenteeName', TType.STRING, 3)
            oprot.writeString(self.presenteeName.encode('utf-8') if sys.version_info[0] == 2 else self.presenteeName)
            oprot.writeFieldEnd()
        if self.clickTime is not None:
            oprot.writeFieldBegin('clickTime', TType.STRING, 4)
            oprot.writeString(self.clickTime.encode('utf-8') if sys.version_info[0] == 2 else self.clickTime)
            oprot.writeFieldEnd()
        if self.recom is not None:
            oprot.writeFieldBegin('recom', TType.BYTE, 5)
            oprot.writeByte(self.recom)
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


class SortResult(object):
    """
    Attributes:
     - count
     - rank
     - hongbao
    """

    thrift_spec = (
        None,  # 0
        (1, TType.I32, 'count', None, None, ),  # 1
        (2, TType.I32, 'rank', None, None, ),  # 2
        (3, TType.I32, 'hongbao', None, None, ),  # 3
    )

    def __init__(self, count=None, rank=None, hongbao=None,):
        self.count = count
        self.rank = rank
        self.hongbao = hongbao

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
                    self.count = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.I32:
                    self.rank = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.I32:
                    self.hongbao = iprot.readI32()
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
        oprot.writeStructBegin('SortResult')
        if self.count is not None:
            oprot.writeFieldBegin('count', TType.I32, 1)
            oprot.writeI32(self.count)
            oprot.writeFieldEnd()
        if self.rank is not None:
            oprot.writeFieldBegin('rank', TType.I32, 2)
            oprot.writeI32(self.rank)
            oprot.writeFieldEnd()
        if self.hongbao is not None:
            oprot.writeFieldBegin('hongbao', TType.I32, 3)
            oprot.writeI32(self.hongbao)
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
