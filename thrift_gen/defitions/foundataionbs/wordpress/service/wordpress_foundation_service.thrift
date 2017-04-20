# file: foundation_wordpress_service.thrift

include "../struct/wordpress_foundation_strcut.thrift"

namespace java com.moseeker.thrift.gen.foundation.wordpress.service

/**
 * TODO:list what notation this dateTime represents. eg ISO-8601
 * or if its in the format like YYYY-mm-DD you mentioned.
 */
 
service WordpressService {
    wordpress_foundation_strcut.NewsletterData getNewsletter(1:wordpress_foundation_strcut.NewsletterForm newsletter); 
}

