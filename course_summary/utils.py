from datetime import datetime, timezone

from enum import Enum
from typing import List, Tuple

import attr
from lms.djangoapps.courseware.courses import (
    get_course_overview_with_access,
    get_course_with_access,
)
from opaque_keys import InvalidKeyError, OpaqueKey
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.learning_sequences.api import get_course_outline
from openedx.core.djangoapps.content.learning_sequences.data import (
    ContentErrorData,
    CourseLearningSequenceData,
    CourseOutlineData,
    CourseSectionData,
    CourseVisibility,
    ExamData,
    VisibilityData,
)
from xmodule.modulestore import (  # lint-amnesty, pylint: disable=wrong-import-order
    ModuleStoreEnum,
)
from xmodule.modulestore.django import (  # lint-amnesty, pylint: disable=wrong-import-order
    modulestore,
)

# def get_course()


def get_course_outline_data(course_key):
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
