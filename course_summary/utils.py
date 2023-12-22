from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.learning_sequences.api import get_course_outline
from openedx.core.djangoapps.content.learning_sequences.data import (
    ContentErrorData,
    CourseLearningSequenceData,
    CourseOutlineData,
    CourseSectionData,
    CourseVisibility,
    ExamData,
    VisibilityData
)
from datetime import timezone, datetime
from typing import List, Tuple
from xmodule.modulestore import ModuleStoreEnum  # lint-amnesty, pylint: disable=wrong-import-order
from xmodule.modulestore.django import modulestore  # lint-amnesty, pylint: disable=wrong-import-order
from opaque_keys import OpaqueKey

from enum import Enum
from opaque_keys import InvalidKeyError
import attr


def get_course_outline_data(course_id):
    try:
        course_key = CourseKey.from_string(course_id)
    except InvalidKeyError:
        raise ValueError("Could not parse course_id {}".format(course_id))

    try:
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
