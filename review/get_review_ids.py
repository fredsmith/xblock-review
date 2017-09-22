'''
Description
'''

import logging

from courseware.models import StudentModule
from opaque_keys.edx.locator import CourseLocator
from opaque_keys.edx.keys import UsageKey
from enrollment.api import get_enrollment, add_enrollment, update_enrollment
import crum
import random
import json

log = logging.getLogger(__name__)

REVIEW_COURSE_MAPPING = {
    # Sandbox
    'course-v1:DillonX+DAD301+2017_T3': 'DillonX+DAD302+2017_T3'
}
ENROLLMENT_COURSE_MAPPING = {
    # Sandbox
    'course-v1:DillonX+DAD301+2017_T3': 'course-v1:DillonX+DAD302+2017_T3'
}
TEMPLATE_URL = 'https://dillon-dumesnil.sandbox.edx.org/xblock/block-v1:{course_id}+type@problem+block@{problem_id}'


def get_records(num_desired, current_course):
    '''
    Doc String
    '''
    user = crum.get_current_user()

    # If the user is not enrolled in the review version of the course,
    # they are unable to see any of the problems. This ensures they
    # are enrolled so they can see review problems.
    enrollment_course_id = ENROLLMENT_COURSE_MAPPING[str(current_course)]
    enrollment_status = get_enrollment(user.username, enrollment_course_id)
    if not enrollment_status:
        add_enrollment(user.username, enrollment_course_id)
    elif not enrollment_status['is_active']:
        update_enrollment(user.username, enrollment_course_id, is_active=True)
    
    problem_ids = []
    # Each record corresponds to a problem the user has loaded
    # in the original course
    for record in StudentModule.objects.filter(**{'student_id': user.id, 'course_id': current_course, 'module_type': 'problem'}):
        # Actual logic regarding the record should go here
        state = json.loads(record.state)

        # record.module_state_key takes the form: 
        # block-v1:{course_id}+type@problem+block@{problem_id}
        problem_id = str(record.module_state_key).split("@")[-1]
        problem_ids.append(problem_id)

    if len(problem_ids) < num_desired:
        return []

    problems_to_show = random.sample(problem_ids, num_desired)
    review_course_id = REVIEW_COURSE_MAPPING[str(current_course)]
    urls = []
    for problem in problems_to_show:
        urls.append(TEMPLATE_URL.format(course_id=review_course_id, problem_id=problem))
    return urls
