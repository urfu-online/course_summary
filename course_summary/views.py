from django.views.decorators.csrf import ensure_csrf_cookie
from common.djangoapps.util.views import ensure_valid_course_key
from opaque_keys.edx.keys import CourseKey
from lms.djangoapps.courseware.courses import get_course_with_access
from lms.djangoapps.courseware.access import has_access
from django.shortcuts import render
from xmodule.modulestore.django import modulestore
from openedx.core.djangoapps.models.course_details import CourseDetails
from cms.djangoapps.coursegraph.tasks import serialize_item, coerce_types

from cms.djangoapps.contentstore.rest_api.v1.serializers import (
    CourseDetailsSerializer,
    CourseGradingSerializer,
    CourseGradingModelSerializer,
)
from cms.djangoapps.contentstore.utils import get_course_grading
from cms.djangoapps.models.settings.course_grading import CourseGradingModel
import attr
from .utils import get_course_outline_data, get_course_outline_data_dict
from django.conf import settings
from datetime import timezone
from xmodule.modulestore import ModuleStoreEnum
from cms.djangoapps.contentstore.outlines import _make_section_data
from lms.djangoapps.course_blocks.api import get_course_blocks
from openedx.core.djangoapps.content.block_structure.api import (
    get_block_structure_manager,
)


from openedx.core.djangoapps.content.learning_sequences.data import (
    ContentErrorData,
    CourseLearningSequenceData,
    CourseOutlineData,
    CourseSectionData,
    CourseVisibility,
    ExamData,
    VisibilityData,
)
from openedx.features.course_experience.utils import get_course_outline_block_tree


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

    items = modulestore().get_items(course_key)
    for item in items:
        fields, block_type = serialize_item(item)

        for field_name, value in fields.items():
            fields[field_name] = coerce_types(value)

    course_details = CourseDetails.fetch(course_key)
    course_details_serializer = CourseDetailsSerializer(course_details)

    course_grading = CourseGradingModel.fetch(course_key)
    course_grading_serializer = CourseGradingModelSerializer(course_grading)

    # collected_block_structure = get_block_structure_manager(course_key).get_collected()

    store = modulestore()

    with store.branch_setting(ModuleStoreEnum.Branch.published_only):
        course_block = store.get_course(course_key, depth=0, lazy=False)

        sections = course_outline_data.sections

        # course_assets = store.get_all_asset_metadata(course_key, maxresults=-1, asset_type=None)

        course_blocks = get_course_outline_block_tree(request, course_id, None)

    return render(
        request,
        "course_summary/base.html",
        {
            # "course_outline_data_dict": get_course_outline_data_dict(course_id),  # attr.asdict(course_outline_data),
            "course": course,
            "staff_access": staff_access,
            # "items": items,
            "course_details": course_details,
            "course_details_data": course_details_serializer.data,
            "course_grading": course_grading,
            "course_grading_data": course_grading_serializer.data,
            # "collected_block_structure": collected_block_structure,
            "course_block": course_block,
            "course_outline_data": course_outline_data,
            "sections": sections,
            "course_blocks": course_blocks,
        },
    )


@ensure_csrf_cookie
@ensure_valid_course_key
def summary1(request, course_id):
    """
    Display the course's summary, or 404 if there is no such course.
    Assumes the course_id is in a valid format.
    """

    course_key = CourseKey.from_string(course_id)

    course = get_course_with_access(request.user, "load", course_key)
    staff_access = bool(has_access(request.user, "staff", course))
    outline_data = get_course_outline_data(course_id)
    items = modulestore().get_items(course_id)
    for item in items:
        fields, block_type = serialize_item(item)

        for field_name, value in fields.items():
            fields[field_name] = coerce_types(value)

    return render(
        request,
        "course_summary/base.html",
        {
            "course_outline_data": outline_data,
            "course_outline_data_dict": get_course_outline_data_dict(
                course_id
            ),  # attr.asdict(course_outline_data),
            "course": course,
            "course_dict": course.__dict__,
            "staff_access": staff_access,
        },
    )
