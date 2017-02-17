include "../struct/dict_struct.thrift"
include "../../common/struct/common_struct.thrift"

namespace py thrift_gen.gen.dict.service

service CityServices {
    common_struct.Response getAllCities(1:i32 level);
    common_struct.Response getCitiesById(1:i32 id);
    common_struct.Response getResources(1:common_struct.CommonQuery query);
}

service CollegeServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
}

/*
  获取国家字典数据服务
*/
service DictCountryService {
    common_struct.Response getDictCountry();
}

/*
  获取常量字典json数据服务
*/
service DictConstanService {
    common_struct.Response getDictConstantJsonByParentCode(1:list<i32> parentCodeList);
}

/*
  行业服务接口
*/
service IndustryService {
    common_struct.Response getIndustriesByCode(1: string code);
}

/*
  职能服务接口
*/
service PositionService {
   common_struct.Response getPositionsByCode(1:string code);
}
/*
	orm层第三方职位职能查询
*/
service DictOccupationDao{
	common_struct.Response getOccupations51();
	common_struct.Response getOccupationsZPin();
	common_struct.Response getOccupation51(1:common_struct.CommonQuery query);
	common_struct.Response getOccupationZPin(1:common_struct.CommonQuery query);
}
/*
 service层第三方职位职能查询
*/
service DictOccupationService{
	common_struct.Response getDictOccupation(1:string param);
}
