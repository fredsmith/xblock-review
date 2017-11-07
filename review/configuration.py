'''
Constants are stored here for use in other parts of the xBlock.
'''

# Needed for review.py #
# Eventually, this should be part of the xBlock fields as a Boolean
SHOW_PROBLEMS = set([
    'course-v1:MITx+6.002.3x+2T2016',
    'course-v1:MITx+18.01.2x+3T2017',
    # This is here for testing purposes. Do not remove
    'DillonX/DAD101x/3T2017',
])
SHOW_VERTICAL = set([
    'course-v1:MITx+2.01x+3T2017',
    'course-v1:MITx+8.01.2x+3T2017',
])

# Needed for get_review_ids.py #
'''
The mappings here are necessary to grab the review content from a review
version of the course (a copy where problems are not graded and have
unlimited attempts).
When accessed, the key is the course the learner is currently interacting
with and the value is the corresponding review course.
'''
REVIEW_COURSE_MAPPING = {
    # Course used for testing. DO NOT REMOVE
    'DillonX/DAD101x/3T2017': 'DillonX/DAD101rx/3T2017',

    'course-v1:MITx+6.002.3x+2T2016': 'MITx+6.002.3rx+2T2016',
    'course-v1:MITx+2.01x+3T2017': 'MITx+2.01rx+3T2017',
    'course-v1:MITx+18.01.2x+3T2017': 'MITx+18.01.2rx+3T2017',
    'course-v1:MITx+8.01.2x+3T2017': 'MITx+8.01.2rx+3T2017',
}
ENROLLMENT_COURSE_MAPPING = {
    # Course used for testing. DO NOT REMOVE
    'DillonX/DAD101x/3T2017': 'DillonX/DAD101rx/3T2017',

    'course-v1:MITx+6.002.3x+2T2016': 'course-v1:MITx+6.002.3rx+2T2016',
    'course-v1:MITx+2.01x+3T2017': 'course-v1:MITx+2.01rx+3T2017',
    'course-v1:MITx+18.01.2x+3T2017': 'course-v1:MITx+18.01.2rx+3T2017',
    'course-v1:MITx+8.01.2x+3T2017': 'course-v1:MITx+8.01.2rx+3T2017',
}
TEMPLATE_URL = 'https://dillon-demo.sandbox.edx.org/xblock/block-v1:{course_id}+type@{type}+block@{xblock_id}'
