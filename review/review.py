"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from xblock.core import XBlock
from xblock.fields import Integer, String, Scope
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

    display_name = String(
        display_name=_("Display Name"),
        help=_("The display name for this component."),
        scope=Scope.settings,
        default=_("Review"),
    )

    num_desired = Integer(
        display_name=_("Number of desired review problems"),
        help=_("Defines the number of problems the review module will display "
               "to the learner."),
        default=5,
        scope=Scope.user_state_summary
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_html(self):
        url_list = get_records(self.num_desired, self.course_id)
        if len(url_list) != self.num_desired:
            html = self.resource_string("static/html/no_review.html")
        else:
            html = self.resource_string("static/html/review.html")
            html = html.format(NUMBER_DESIRED=self.num_desired)
            for i in xrange(self.num_desired):
                content = self.resource_string("static/html/review_content.html")
                content = content.format(PROBLEM_URL=self.url_list[i], INDEX=(i+1))
                html += content
            # Need to close out the div from the original review.html
            html += '</div>'
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
