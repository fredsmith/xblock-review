# pylint: disable=import-error
'''
The logic for actually grabbing review content is contained here for the
Review XBlock. This works by having a copy of the actual course a learner
is interacting with that is hidden from learners. This copied course hosts
the content we will show as review so the review content displayed has a
fresh state and can be set to ungraded so it doesn't affect the learners'
grades. There are two ways review content can be grabbed:
    On a per problem basis
    On a unit basis (this would be single view that contains multiple problems)
'''

import json
import logging
import random
from datetime import datetime

import crum
import pytz
from courseware.models import StudentModule
from enrollment.api import add_enrollment, get_enrollment, update_enrollment
from lms.djangoapps.course_blocks.api import get_course_blocks
from xmodule.modulestore.django import modulestore

from .configuration import ENROLLMENT_COURSE_MAPPING, XBLOCK_VIEW_URL_TEMPLATE

log = logging.getLogger(__name__)

# TODO: Switch to using CourseLocators and/or CourseKeys everywhere


def get_problems(num_desired, current_course_key):
    '''
    Looks through all the problems a learner has previously loaded and randomly
    selects num_desired of them. Also checks if the learner had originally
    answered it correctly or incorrectly and after how many attempts.

    Parameters:
        num_desired (int): the number of desired problems to show the learner
        current_course_key (CourseLocator): The course the learner is currently in

    Returns a list of num_desired tuples in the form (URL to display, correct, attempts)
    '''
    user = crum.get_current_user()

    enroll_user_in_review_course_if_needed(user, current_course_key)

    store = modulestore()
    course_usage_key = store.make_course_usage_key(current_course_key)
    course_blocks = get_course_blocks(user, course_usage_key)

    problem_data = []

    for block_key, state in _get_user_accessed_problem_records(user, current_course_key):
        block_key = block_key.replace(course_key=store.fill_in_run(block_key.course_key))
        if is_valid_problem(store, block_key, state, course_blocks):
            correct, attempts = get_correctness_and_attempts(state)
            review_block_key = block_key.replace(course=block_key.course+'_review')
            problem_data.append((review_block_key, correct, attempts))
            delete_state_of_review_problem(user, current_course_key, review_block_key)

    if len(problem_data) < num_desired:
        return []

    problems_to_show = random.sample(problem_data, num_desired)
    problem_information = []
    for review_block_key, correct, attempts in problems_to_show:
        problem_information.append((XBLOCK_VIEW_URL_TEMPLATE + str(review_block_key), correct, attempts))
    return problem_information


def get_vertical(current_course_key):
    '''
    Looks through all the problems a learner has previously loaded and
    finds their parent vertical. Then randomly selects a single vertical
    to show the learner.

    Parameters:
        current_course_key (CourseLocator): The course the learner is currently in

    Returns a url (str) with the vertical id to render for review.
    '''
    user = crum.get_current_user()

    enroll_user_in_review_course_if_needed(user, current_course_key)

    store = modulestore()
    course_usage_key = store.make_course_usage_key(current_course_key)
    course_blocks = get_course_blocks(user, course_usage_key)

    vertical_data = set()

    for block_key, state in _get_user_accessed_problem_records(user, current_course_key):
        block_key = block_key.replace(course_key=store.fill_in_run(block_key.course_key))
        if is_valid_problem(store, block_key, state, course_blocks):
            vertical = course_blocks.get_parents(block_key)[0]
            sequential = course_blocks.get_parents(vertical)[0]

            # This is in case the direct parent of a problem is not a vertical,
            # we want to keep looking until we find the parent vertical to display.
            # For example, you may see:
            # sequential -> vertical -> split_test -> problem
            # OR
            # sequential -> vertical -> vertical -> problem
            # OR
            # sequential -> vertical -> conditional_block -> problem
            while sequential.block_type != 'sequential':
                vertical = sequential
                sequential = course_blocks.get_parents(vertical)[0]
            review_vertical_key = vertical.replace(course=vertical.course+'_review')
            vertical_data.add(review_vertical_key)

            review_block_key = block_key.replace(course=block_key.course+'_review')
            delete_state_of_review_problem(user, current_course_key, review_block_key)

    if not vertical_data:
        return []

    vertical_to_show = random.sample(vertical_data, 1)[0]
    return XBLOCK_VIEW_URL_TEMPLATE + str(vertical_to_show)


def _get_user_accessed_problem_records(user, current_course_key):
    '''
    Generator that yields each applicable record from the Courseware Student
    Module. Each record corresponds to a problem the user has loaded
    in the original course.

    Parameters:
        user (django.contrib.auth.models.User): User object for the current user
        current_course_key (CourseLocator): The course the learner is currently in

    Returns:
        record.module_state_key (opaque_keys.edx.locator.BlockUsageLocator):
            The locator for the problem
        state (dict): The state of the problem
    '''
    problem_filter = {'student_id': user.id, 'course_id': current_course_key, 'module_type': 'problem'}
    for record in StudentModule.objects.filter(**problem_filter):
        state = json.loads(record.state)
        # The key 'selected' shows up if a problem comes from a
        # library content module. These cause issues so we skip this.
        # Issue: Library content contains problems but the CSM brings up
        # the library content and not the problems within
        if 'selected' not in state:
            yield record.module_state_key, state


def enroll_user_in_review_course_if_needed(user, current_course_key):
    '''
    If the user is not enrolled in the review version of the course,
    they are unable to see any of the problems. This ensures they
    are enrolled so they can see review problems.

    Parameters:
        user (User): the current user interacting with the review XBlock
        current_course_key (CourseLocator): The course the learner is currently in
    '''
    enrollment_course_id = ENROLLMENT_COURSE_MAPPING[str(current_course_key)]
    enrollment_status = get_enrollment(user.username, enrollment_course_id)
    if not enrollment_status:
        add_enrollment(user.username, enrollment_course_id)
    elif not enrollment_status['is_active']:
        update_enrollment(user.username, enrollment_course_id, is_active=True)


def delete_state_of_review_problem(user, current_course_key, review_block_key):
    '''
    Deletes the state of a review problem so it can be used infinitely
    many times.

    Parameters:
        user (User): the current user interacting with the review XBlock
        current_course_key (CourseLocator): The course the learner is currently in
        # TODO update params
    '''
    review_course = current_course_key.replace(course=current_course_key.course+'_review')
    try:
        module_to_delete = StudentModule.objects.get(
            student_id=user.id,
            course_id=review_course,
            module_state_key=review_block_key
        )
        module_to_delete.delete()
    except StudentModule.DoesNotExist:
        # The record will not exist in the StudentModule if the learner has not
        # seen it as a review problem yet so we just want to skip since there
        # is no state to delete
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


def is_valid_problem(store, block_key, state, course_blocks):
    '''
    Checks a problem to see if it is valid to show to the learner. The
    reason to have this is so learners don't try to cheat by using the
    review problems to find out the correct answer and then using it to
    answer the actual problem.

    Required condition to be valid:
        The problem is accessible to the learner (checked through the block
            structure in the course)

    Possible conditions to be valid (at least 1 must be true):
        1) Ungraded (it's ungraded originally so showing it again is okay)
        2) Correctly answered (the learner has already correctly answered
            the problem so it should be fine to show them again.)
        3) All attempts have been used. (If all attempts on the actual problem
            have been used, then it's safe to show them)
        4) It is past the due date

    Parameters:
        store (xmodule.modulestore.mixed.MixedModuleStore): Modulestore
            for grabbing the instance of a problem from the locator key
        block_key (opaque_keys.edx.locator.BlockUsageLocator): The locator for the problem
        state (dict): The state of the problem

    Returns True if the problem is valid, False otherwise
    '''
    if block_key not in course_blocks:
        return False

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
