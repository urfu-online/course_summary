"""
URLs for course_summary.
"""
from django.conf import settings
from django.urls import re_path  # pylint: disable=unused-import
from django.views.generic import TemplateView  # pylint: disable=unused-import
from .views import summary, summary_docx

urlpatterns = [
    # TODO: Fill in URL patterns and views here.
    # re_path(r'', TemplateView.as_view(template_name="course_summary/base.html")),
    re_path(fr'^{settings.COURSE_ID_PATTERN}$', summary, name="course-summary"),
    re_path(fr'^{settings.COURSE_ID_PATTERN}/docx', summary_docx, name="summary-docx"),
]
