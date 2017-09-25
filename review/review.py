"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from xblock.core import XBlock
from xblock.fields import String, Scope
from xblock.fragment import Fragment

from get_review_ids import get_records

import logging

log = logging.getLogger(__name__)

# Make '_' a no-op so we can scrape strings. Using lambda instead of
#  `django.utils.translation.ugettext_noop` because Django cannot be imported in this file
_ = lambda text: text


class ReviewXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: define your own fields.
    display_name = String(
        display_name=_("Display Name"),
        help=_("The display name for this component."),
        scope=Scope.settings,
        default=_("Review"),
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_html(self):
        url_list = get_records(5, self.course_id)
        if len(url_list) != 5:
            html = self.resource_string("static/html/no_review.html")
        else:
            html = self.resource_string("static/html/review.html")
            html = html.format(self=self,
                            PROBLEM_URL_0=url_list[0],
                            PROBLEM_URL_1=url_list[1],
                            PROBLEM_URL_2=url_list[2],
                            PROBLEM_URL_3=url_list[3],
                            PROBLEM_URL_4=url_list[4])
        return html

    def student_view(self, context=None):
        """
        The primary view of the ReviewXBlock, shown to students
        when viewing courses.
        """
        html = self.get_html()
        frag = Fragment(html)
        frag.add_css(self.resource_string("static/css/review.css"))
        frag.add_javascript(self.resource_string("static/js/src/review.js"))
        frag.initialize_js('ReviewXBlock')
        return frag

    def studio_view(self, context):
        return self.student_view(context)

    @property
    def non_editable_metadata_fields(self):
        """
        """
        return
