from datetime import timezone

import attr
from cms.djangoapps.contentstore.outlines import _make_section_data

from cms.djangoapps.contentstore.rest_api.v1.serializers import (
    CourseDetailsSerializer,
    CourseGradingModelSerializer,
    CourseGradingSerializer,
)
from cms.djangoapps.contentstore.utils import get_course_grading
from cms.djangoapps.coursegraph.tasks import coerce_types, serialize_item
from cms.djangoapps.models.settings.course_grading import CourseGradingModel
from common.djangoapps.util.views import ensure_valid_course_key
from django.conf import settings

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from docx import Document
from lms.djangoapps.course_blocks.api import get_course_blocks
from lms.djangoapps.courseware.access import has_access
from lms.djangoapps.courseware.courses import get_course_with_access
from opaque_keys.edx.keys import CourseKey
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
from openedx.core.djangoapps.models.course_details import CourseDetails
from openedx.features.course_experience.utils import get_course_outline_block_tree
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore

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
def summary_docx(request, course_id):
    """
    Display the course's summary, or 404 if there is no such course.
    Assumes the course_id is in a valid format.
    """

    course_key = CourseKey.from_string(course_id)

    course = get_course_with_access(request.user, "load", course_key)
    if not bool(has_access(request.user, "staff", course)):
        return HttpResponseForbidden()

    store = modulestore()
    course_outline_data = get_course_outline_data(course_id)

    with store.branch_setting(ModuleStoreEnum.Branch.published_only):
        course_blocks = get_course_outline_block_tree(request, course_id, None)

    document = Document()
    document.add_heading(course_outline_data.title, 0)
    document.add_paragraph(str(course_blocks))

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    response[
        "Content-Disposition"
    ] = f"attachment; filename={course_outline_data.title}__summary.docx"
    document.save(response)

    return response
