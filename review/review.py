# pylint: disable=import-error
""" Review XBlock """

import logging
import pkg_resources
from xblock.core import XBlock
from xblock.fields import Integer, String, Scope
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader

from .get_review_ids import get_problems, get_vertical
from .configuration import SHOW_PROBLEMS, SHOW_VERTICAL

log = logging.getLogger(__name__)
loader = ResourceLoader(__name__)


# Make '_' a no-op so we can scrape strings. Using lambda instead of
#  `django.utils.translation.ugettext_noop` because Django cannot be imported in this file
def _(text):
    return text


@XBlock.needs('i18n')
class ReviewXBlock(XBlock):
    """
    The Review XBlock helps learners review concepts from a course by redisplaying
    a handful of problems from the course with a fresh state that are ungraded and
    have unlimited attempts.
    """
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
        scope=Scope.content
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_problem_html(self):
        """
        Create the html for showing review problems by picking individual
        problems. This calls the get_problems function which will return
        self.num_desired urls to display in iFrames for the Review XBlock.
        """
        # url_list elements have the form (url, correctness, attempts)
        url_list = get_problems(self.num_desired, self.course_id)
        if len(url_list) == self.num_desired:
            review_context_dict = {'number_desired': self.num_desired}
            template = loader.render_django_template("/templates/review.html", review_context_dict)
            # Want to wrap all of the problems inside of a div
            template += '<div>\n'

            for i in xrange(self.num_desired):
                problem_url, correctness, num_attempts = url_list[i]
                prob_context_dict = {
                    'problem_url': problem_url,
                    'correctness': correctness,
                    'num_attempts': num_attempts,
                    'index': (i+1)
                }
                template += loader.render_django_template("/templates/review_content_problem.html", prob_context_dict)
            template += '</div>'
            return template

    def get_vertical_html(self):
        """
        Create the html for showing review problems by picking a single unit
        to show to a learner (which will contain 1 or more problems). This
        calls the get_vertical function which will return a single url to
        display in an iFrame for the Review XBlock.
        """
        vertical_url = get_vertical(self.course_id)
        if vertical_url:
            review_context_dict = {'number_desired': 'some'}
            template = loader.render_django_template("/templates/review.html", review_context_dict)
            # Want to wrap all of the problems inside of a div
            template += '<div>\n'
            vert_context_dict = {'vertical_url': vertical_url}
            template += loader.render_django_template("/templates/review_content_vertical.html", vert_context_dict)
            template += '</div>'
            return template

    def student_view(self, context=None):  # pylint: disable=unused-argument
        """
        The primary view of the ReviewXBlock, shown to students
        when viewing courses.
        """
        html = None
        if str(self.course_id) in SHOW_PROBLEMS:
            html = self.get_problem_html()
        elif str(self.course_id) in SHOW_VERTICAL:
            html = self.get_vertical_html()
        if not html:
            # Default html if no problems or vertical are shown
            html = loader.render_django_template("/templates/no_review.html")
        frag = Fragment(html)
        frag.add_css(self.resource_string("static/css/review.css"))
        frag.add_javascript(self.resource_string("static/js/src/review.js"))
        frag.initialize_js('ReviewXBlock')
        return frag

    def studio_view(self, context):
        return self.student_view(context)
