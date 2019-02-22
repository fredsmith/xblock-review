'''Setup for review XBlock.'''

import os

from setuptools import setup


def package_data(pkg, roots):
    '''Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    '''
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}

long_description = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='xblock-review',
    version='1.1.5',
    description='The Review XBlock is designed to act as a review tool for learners in their edX course.',
    long_description = long_description,
    license='AGPL v3',
    author='edX',
    author_email='oscm@edx.org',
    url='https://github.com/edx/xblock-review',
    packages=[
        'review',
    ],
    install_requires=[
        'django-crum',
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'review = review:ReviewXBlock',
        ]
    },
    package_data=package_data('review', ['static', 'templates']),
)
