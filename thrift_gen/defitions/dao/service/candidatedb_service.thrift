namespace java com.moseeker.thrift.gen.dao.service
namespace py thrift_gen.gen.dao.service

include "../../common/struct/common_struct.thrift"
include "../struct/candidatedb_struct.thrift"

service CandidateDBDao {
    //查询HR标记的候选人信息
	candidatedb_struct.CandidateRemarkDO getCandidateRemark(1:common_struct.CommonQuery query)
	list<candidatedb_struct.CandidateRemarkDO> listCandidateRemarks(1:common_struct.CommonQuery query) throws (1:candidatedb_struct.CURDException e)
    candidatedb_struct.CandidateRemarkDO saveCandidateRemark(1:candidatedb_struct.CandidateRemarkDO candidateRemark) throws (1:candidatedb_struct.CURDException e)
    candidatedb_struct.CandidateRemarkDO updateCandidateRemark(1:candidatedb_struct.CandidateRemarkDO candidateRemark) throws (1:candidatedb_struct.CURDException e)
    list<candidatedb_struct.CandidateRemarkDO> updateCandidateRemarks(1:list<candidatedb_struct.CandidateRemarkDO> candidateRemarks) throws (1:candidatedb_struct.CURDException e)
    void deleteCandidateRemark(1: i32 id) throws (1:candidatedb_struct.CURDException e)

	candidatedb_struct.CandidateCompanyDO getCandidateCompany(1:common_struct.CommonQuery query)
	list<candidatedb_struct.CandidateCompanyDO> listCandidateCompanys(1:common_struct.CommonQuery query)
	candidatedb_struct.CandidateCompanyDO saveCandidateCompanys(1:candidatedb_struct.CandidateCompanyDO candidateCompany)
	candidatedb_struct.CandidateCompanyDO updateCandidateCompanys(1:candidatedb_struct.CandidateCompanyDO candidateCompany)
	void deleteCandidateCompany(1:i32 id)

    candidatedb_struct.CandidatePositionDO getCandidatePosition(1:common_struct.CommonQuery query)
    list<candidatedb_struct.CandidatePositionDO> listCandidatePositions(1:common_struct.CommonQuery query)
    list<candidatedb_struct.CandidatePositionDO> listCandidatePositionsByPositionIDUserID(1: list<map<i32, i32>> companyPositionIds)
    candidatedb_struct.CandidatePositionDO updateCandidatePosition(1: candidatedb_struct.CandidatePositionDO candidatePosition)
    void deleteCandidatePositions(1: i32 userId, 2: i32 positionId)

    candidatedb_struct.CandidatePositionShareRecordDO getCandidatePositionShareRecord(1:common_struct.CommonQuery query)
    list<candidatedb_struct.CandidatePositionShareRecordDO> listCandidatePositionShareRecord(1:common_struct.CommonQuery query)
    candidatedb_struct.CandidatePositionShareRecordDO updateCandidatePositionShareRecord(1: candidatedb_struct.CandidatePositionShareRecordDO candidatePositionShareRecord)
    void deleteCandidatePositionShareRecord(1: i32 id)

    candidatedb_struct.CandidateRecomRecordDO getCandidateRecomRecord(1:common_struct.CommonQuery query)
    list<candidatedb_struct.CandidateRecomRecordDO> listCandidateRecomRecords(1:common_struct.CommonQuery query)
    candidatedb_struct.CandidateRecomRecordDO updateCandidateRecomRecords(1: candidatedb_struct.CandidateRecomRecordDO candidateRecomRecord)
    void deleteCandidateRecomRecords(1: i32 id)

    candidatedb_struct.CandidateShareChainDO getCandidateShareChain(1:common_struct.CommonQuery query)
    list<candidatedb_struct.CandidateShareChainDO> listCandidateShareChain(1:common_struct.CommonQuery query)
    candidatedb_struct.CandidateShareChainDO updateCandidateShareChain(1: candidatedb_struct.CandidateShareChainDO candidateShareChain)
    void deleteCandidateShareChain(1: i32 id)

    candidatedb_struct.CandidateSuggestPositionDO getCandidateSuggestPosition(1:common_struct.CommonQuery query)
    list<candidatedb_struct.CandidateSuggestPositionDO> listCandidateSuggestPosition(1:common_struct.CommonQuery query)
    candidatedb_struct.CandidateSuggestPositionDO updateCandidateSuggestPosition(1: candidatedb_struct.CandidateSuggestPositionDO candidateSuggestPosition)
    void deleteCandidateSuggestPosition(1: i32 id)
}
