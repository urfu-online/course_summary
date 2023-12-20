from django.views.decorators.csrf import ensure_csrf_cookie
from common.djangoapps.util.views import ensure_valid_course_key
from opaque_keys.edx.keys import CourseKey
from lms.djangoapps.courseware.courses import get_course_with_access
from lms.djangoapps.courseware.access import has_access
from django.shortcuts import render

import attr
from .utils import get_course_outline_data, get_course_outline_data_dict


@ensure_csrf_cookie
@ensure_valid_course_key
def summary(request, course_id):
    """
    Display the course's summary, or 404 if there is no such course.
    Assumes the course_id is in a valid format.
    """

    course_key = CourseKey.from_string(course_id)

    course = get_course_with_access(request.user, "load", course_key)
    staff_access = bool(has_access(request.user, "staff", course))
    course_outline_data = get_course_outline_data(course_id)

    return render(
        request,
        "course_summary/base.html",
        {
            "course_outline_data": course_outline_data,
            "course_outline_data_dict": get_course_outline_data_dict(course_id),  # attr.asdict(course_outline_data),
            "course": course,
            "course_dict": course.__dict__,
            "staff_access": staff_access,
        },
    )
