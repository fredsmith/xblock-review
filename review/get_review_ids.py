# pylint: disable=import-error
'''
The logic for actually grabbing review content is contained here for the
Review xBlock. This works by having a copy of the actual course a learner
is interacting with that is hidden from learners. This copied course hosts
the content we will show as review so the review content displayed has a
fresh state and can be set to ungraded so it doesn't affect the learners'
grades. There are two ways review content can be grabbed:
    On a per problem basis
    On a unit basis (this would be single view that contains multiple problems)
'''

import logging

from datetime import datetime
import json
import random
from courseware.models import StudentModule
from enrollment.api import get_enrollment, add_enrollment, update_enrollment
from lms.djangoapps.course_blocks.api import get_course_blocks
from xmodule.modulestore.django import modulestore
import crum
import pytz

from .configuration import REVIEW_COURSE_MAPPING, ENROLLMENT_COURSE_MAPPING, TEMPLATE_URL

log = logging.getLogger(__name__)

# TODO: Switch to using CourseLocators and/or CourseKeys everywhere


def get_problems(num_desired, current_course):
    '''
    Looks through all the problems a learner has previously loaded and randomly
    selects num_desired of them. Also checks if the learner had originally
    answered it correctly or incorrectly and after how many attempts.

    Parameters:
        num_desired (int): the number of desired problems to show the learner
        current_course (CourseLocator): The course the learner is currently in

    Returns a list of num_desired tuples in the form (URL to display, correct, attempts)
    '''
    user = crum.get_current_user()

    enroll_user(user, current_course)
    store = modulestore()

    problem_data = []

    for block_key, state in get_records(user, current_course):
        if is_valid_problem(store, block_key, state):
            correct, attempts = get_correctness_and_attempts(state)
            problem_id = block_key.block_id
            problem_data.append((problem_id, correct, attempts))

    if len(problem_data) < num_desired:
        return []

    problems_to_show = random.sample(problem_data, num_desired)
    review_course_id = REVIEW_COURSE_MAPPING[str(current_course)]
    urls = []
    for problem, correct, attempts in problems_to_show:
        urls.append((TEMPLATE_URL.format(course_id=review_course_id,
                    type='problem', xblock_id=problem), correct, attempts))
    return urls


def get_vertical(current_course):
    '''
    Looks through all the problems a learner has previously loaded and
    finds their parent vertical. Then randomly selects a single vertical
    to show the learner.

    Parameters:
        current_course (CourseLocator): The course the learner is currently in

    Returns a url (str) with the vertical id to render for review.
    '''
    user = crum.get_current_user()

    enroll_user(user, current_course)

    store = modulestore()
    course_usage_key = store.make_course_usage_key(current_course)
    course_blocks = get_course_blocks(user, course_usage_key)

    vertical_data = set()

    for block_key, state in get_records(user, current_course):
        if is_valid_problem(store, block_key, state):
            parent = course_blocks.get_parents(block_key)[0]
            vertical_id = parent.block_id
            vertical_data.add(vertical_id)

    if not vertical_data:
        return []

    vertical_to_show = random.sample(vertical_data, 1)[0]
    review_course_id = REVIEW_COURSE_MAPPING[str(current_course)]
    return (TEMPLATE_URL.format(course_id=review_course_id,
                                type='vertical', xblock_id=vertical_to_show))


def get_records(user, current_course):
    '''
    Generator that yields each applicable record from the Courseware Student
    Module. Each record corresponds to a problem the user has loaded
    in the original course.

    Parameters:
        user (django.contrib.auth.models.User): User object for the current user
        current_course (CourseLocator): The course the learner is currently in

    Returns:
        record.module_state_key (opaque_keys.edx.locator.BlockUsageLocator):
            The locator for the problem
        state (dict): The state of the problem
    '''
    problem_filter = {'student_id': user.id, 'course_id': current_course, 'module_type': 'problem'}
    for record in StudentModule.objects.filter(**problem_filter):
        state = json.loads(record.state)
        # The key 'selected' shows up if a problem comes from a
        # library content module. These cause issues so we skip this.
        # Issue: Library content contains problems but the CSM brings up
        # the library content and not the problems within
        if 'selected' not in state:
            yield record.module_state_key, state


def enroll_user(user, current_course):
    '''
    If the user is not enrolled in the review version of the course,
    they are unable to see any of the problems. This ensures they
    are enrolled so they can see review problems.

    Parameters:
        user (User): the current user interacting with the review xBlock
        current_course (CourseLocator): The course the learner is currently in
    '''
    enrollment_course_id = ENROLLMENT_COURSE_MAPPING[str(current_course)]
    enrollment_status = get_enrollment(user.username, enrollment_course_id)
    if not enrollment_status:
        add_enrollment(user.username, enrollment_course_id)
    elif not enrollment_status['is_active']:
        update_enrollment(user.username, enrollment_course_id, is_active=True)


def delete_state_of_review_problem(user, current_course, problem_id):  # pylint: disable=unused-argument
    '''
    Deletes the state of a review problem so it can be used infinitely
    many times.

    Parameters:
        user (User): the current user interacting with the review xBlock
        current_course (CourseLocator): The course the learner is currently in
        problem_id (str?): The problem id whose state should be cleared
    '''
    pass


def get_correctness_and_attempts(state):
    '''
    From the state of a problem from the Courseware Student Module,
    determine if the learner correctly answered it initially and
    the number of attempts they had for the original problem

    Parameter:
        state (dict): The state of a problem

    Returns a tuple of (correct, attempts)
        correct (Bool): True if correct, else False
        attempts (int): 0 if never attempted, else number of times attempted
    '''
    correct = (state['score']['raw_earned'] == state['score']['raw_possible'])

    if 'attempts' in state:
        attempts = state['attempts']
    else:
        attempts = 0

    return (correct, attempts)


def is_valid_problem(store, block_key, state):
    '''
    Checks a problem to see if it is valid to show to the learner. The
    reason to have this is so learners don't try to cheat by using the
    review problems to find out the correct answer and then using it to
    answer the actual problem.
    Conditions to be valid:
        1) Ungraded (it's ungraded originally so showing it again is okay)
        2) Correctly answered (the learner has already correctly answered
            the problem so it should be fine to show them again.)
        3) All attempts have been used. (If all attempts on the actual problem
            have been used, then it's safe to show them)
        4) It is past the due date

    Parameters:
        store (lms.djangoapps.ccx.modulestore.CCXModulestoreWrapper): Modulestore
            for grabbing the instance of a problem from the locator key
        block_key (opaque_keys.edx.locator.BlockUsageLocator): The locator for the problem
        state (dict): The state of the problem

    Returns True if the problem is valid, False otherwise
    '''
    problem = store.get_item(block_key)
    if not problem.graded:
        return True
    if state['score']['raw_earned'] == state['score']['raw_possible']:
        return True
    if 'attempts' in state:
        if state['attempts'] == problem.max_attempts:
            return True
    if problem.due is not None:
        now = datetime.utcnow()
        now = now.replace(tzinfo=pytz.utc)
        if now > problem.due:
            return True
    return False
