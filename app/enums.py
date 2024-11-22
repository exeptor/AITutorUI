from enum import Enum

class CourseStatus(Enum):
    NOT_REVIEWED_NOT_PUBLISHED = "NotReviewed-NotPublished"
    SEND_FOR_REVIEW_AND_PUBLISHING = "Send for Review and Publishing"
    REVIEWED_PUBLISHED = "Reviewed-Published"
    DISABEL_COURSE_REQUEST = "Disable Request"
    ENABLE_COURSE_REQUEST = "Enable Request"
    DISABLED = "Disabled"