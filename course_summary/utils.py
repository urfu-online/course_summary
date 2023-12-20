from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.learning_sequences.api import get_course_outline
from openedx.core.djangoapps.content.learning_sequences.data import CourseOutlineData
from opaque_keys import OpaqueKey
from datetime import datetime
from enum import Enum
import attr


def get_course_outline_data(course_id):
    try:
        course_key = CourseKey.from_string(course_id)
        outline_data = get_course_outline(course_key)
    except (ValueError, CourseOutlineData.DoesNotExist):
        return None
    else:
        return outline_data


def get_course_outline_data_dict(course_id):
    def json_serializer(_field, value, *args, **kwargs):
        if isinstance(value, OpaqueKey):
            return str(value)
        elif isinstance(value, Enum):
            return value.value
        elif isinstance(value, datetime):
            return value.isoformat()
        return value

    return attr.asdict(
        get_course_outline_data(course_id),
        recurse=True,
        value_serializer=json_serializer,
    )
