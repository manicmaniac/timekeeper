from setuptools import setup, find_packages

setup(
    name='timekeeper',
    description='A nosy Slack bot to track your daily workload.',
    long_description=open('README.rst').read(),
    version='0.1.0',
    py_modules=['bot', 'slackbot_settings'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=open('requirements.txt').read(),
    test_suite='tests'
)
