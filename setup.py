import os.path
import sys

from setuptools import setup, find_packages

sys.path.insert(0, os.path.abspath('timekeeper'))
from _version import *  # noqa
sys.path.pop(0)

setup(
    name='timekeeper',
    description='A nosy Slack bot to track your daily workload.',
    long_description=open('README.rst').read(),
    version=__version__,
    py_modules=['bot', 'slackbot_settings'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=open('requirements.txt').read(),
    test_suite='tests'
)
