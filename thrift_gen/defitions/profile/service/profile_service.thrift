# file: profile_service.thrift

include "../struct/profile_struct.thrift"
include "../../common/struct/common_struct.thrift"
namespace java com.moseeker.thrift.gen.profile.service
namespace py thrift_gen.gen.profile.service

/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */

service WholeProfileServices {
    common_struct.Response getResource(1:i32 userId, 2:i32 profileId, 3:string uuid);
    common_struct.Response postResource(1:string profile, 2:i32 user_id);
    common_struct.Response importCV(1:string profile, 2:i32 user_id);
    common_struct.Response verifyRequires(1:i32 userId, 2:i32 positionId);
    //创建简历
    common_struct.Response createProfile(1:string profile);
    //更新简历
    common_struct.Response improveProfile(1:string profile);
    common_struct.Response moveProfile(1:i32 destUserId, 2:i32 originUserId);
}

service ProfileServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(2:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.Profile> resources);
    common_struct.Response putResources(1: list<profile_struct.Profile> resources);
    common_struct.Response delResources(1: list<profile_struct.Profile> resources);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.Profile profile);
    common_struct.Response putResource(1: profile_struct.Profile profile);
    common_struct.Response delResource(1: profile_struct.Profile profile);
    common_struct.Response getCompleteness(1:i32 user_id, 2: string uuid, 3: i32 profile_id);
    common_struct.Response reCalculateUserCompleteness(1:i32 userId, 2:string mobile);
    common_struct.Response reCalculateUserCompletenessBySettingId(1:i32 id);
}

service AttachmentServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(1:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.Attachment> attachments);
    common_struct.Response putResources(1: list<profile_struct.Attachment> attachments);
    common_struct.Response delResources(1: list<profile_struct.Attachment> attachments);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.Attachment attachment);
    common_struct.Response putResource(1: profile_struct.Attachment attachment);
    common_struct.Response delResource(1: profile_struct.Attachment attachment);
}

service AwardsServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(1:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.Awards> awards);
    common_struct.Response putResources(1: list<profile_struct.Awards> awards);
    common_struct.Response delResources(1: list<profile_struct.Awards> awards);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.Awards awards);
    common_struct.Response putResource(1: profile_struct.Awards awards);
    common_struct.Response delResource(1: profile_struct.Awards awards);
}

service BasicServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(1:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.Basic> basics);
    common_struct.Response putResources(1: list<profile_struct.Basic> basics);
    common_struct.Response delResources(1: list<profile_struct.Basic> basics);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.Basic basic);
    common_struct.Response putResource(1: profile_struct.Basic basic);
    common_struct.Response delResource(1: profile_struct.Basic basic);
    common_struct.Response reCalculateBasicCompleteness(1: i32 userId);
}

service CredentialsServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(1:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.Credentials> credentials);
    common_struct.Response putResources(1: list<profile_struct.Credentials> credentials);
    common_struct.Response delResources(1: list<profile_struct.Credentials> credentials);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.Credentials credential);
    common_struct.Response putResource(1: profile_struct.Credentials credential);
    common_struct.Response delResource(1: profile_struct.Credentials credential);
}

service EducationServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(1:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.Education> educations);
    common_struct.Response putResources(1: list<profile_struct.Education> educations);
    common_struct.Response delResources(1: list<profile_struct.Education> educations);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.Education education);
    common_struct.Response putResource(1: profile_struct.Education education);
    common_struct.Response delResource(1: profile_struct.Education education);
}

service ProfileImportServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(1:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.ProfileImport> profileImports);
    common_struct.Response putResources(1: list<profile_struct.ProfileImport> profileImports);
    common_struct.Response delResources(1: list<profile_struct.ProfileImport> profileImports);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.ProfileImport profileImport);
    common_struct.Response putResource(1: profile_struct.ProfileImport profileImport);
    common_struct.Response delResource(1: profile_struct.ProfileImport profileImport);
}

service IntentionServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(1:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.Intention> intentions);
    common_struct.Response putResources(1: list<profile_struct.Intention> intentions);
    common_struct.Response delResources(1: list<profile_struct.Intention> intentions);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.Intention intention);
    common_struct.Response putResource(1: profile_struct.Intention intention);
    common_struct.Response delResource(1: profile_struct.Intention intention);
}

service LanguageServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(1:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.Language> languages);
    common_struct.Response putResources(1: list<profile_struct.Language> languages);
    common_struct.Response delResources(1: list<profile_struct.Language> languages);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.Language language);
    common_struct.Response putResource(1: profile_struct.Language language);
    common_struct.Response delResource(1: profile_struct.Language language);
}

service CustomizeResumeServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(1:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.CustomizeResume> Others);
    common_struct.Response putResources(1: list<profile_struct.CustomizeResume> Others);
    common_struct.Response delResources(1: list<profile_struct.CustomizeResume> Others);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.CustomizeResume Other);
    common_struct.Response putResource(1: profile_struct.CustomizeResume Other);
    common_struct.Response delResource(1: profile_struct.CustomizeResume Other);
}

service ProjectExpServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(1:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.ProjectExp> projectExps);
    common_struct.Response putResources(1: list<profile_struct.ProjectExp> projectExps);
    common_struct.Response delResources(1: list<profile_struct.ProjectExp> projectExps);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.ProjectExp projectExp);
    common_struct.Response putResource(1: profile_struct.ProjectExp projectExp);
    common_struct.Response delResource(1: profile_struct.ProjectExp projectExp);
}

service SkillServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(1:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.Skill> skills);
    common_struct.Response putResources(1: list<profile_struct.Skill> skills);
    common_struct.Response delResources(1: list<profile_struct.Skill> skills);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.Skill skill);
    common_struct.Response putResource(1: profile_struct.Skill skill);
    common_struct.Response delResource(1: profile_struct.Skill skill);
}

service WorkExpServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(1:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.WorkExp> workExps);
    common_struct.Response putResources(1: list<profile_struct.WorkExp> workExps);
    common_struct.Response delResources(1: list<profile_struct.WorkExp> workExps);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.WorkExp workExp);
    common_struct.Response putResource(1: profile_struct.WorkExp workExp);
    common_struct.Response delResource(1: profile_struct.WorkExp workExp);
}

service WorksServices {
    common_struct.Response getResources(1:common_struct.CommonQuery query);
    common_struct.Response getPagination(1:common_struct.CommonQuery query);
    common_struct.Response postResources(1: list<profile_struct.Works> works);
    common_struct.Response putResources(1: list<profile_struct.Works> works);
    common_struct.Response delResources(1: list<profile_struct.Works> works);

    common_struct.Response getResource(1:common_struct.CommonQuery query);
    common_struct.Response postResource(1: profile_struct.Works works);
    common_struct.Response putResource(1: profile_struct.Works works);
    common_struct.Response delResource(1: profile_struct.Works works);
}
