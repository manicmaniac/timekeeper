from setuptools import setup

setup(
    name='timekeeper',
    description='A nosy Slack bot to track your daily workload.',
    long_description=open('README.rst').read(),
    version='0.0.2',
    py_modules=['bot', 'slackbot_settings'],
    packages=['timekeeper'],
    include_package_data=True,
    zip_safe=False,
    install_requires=open('requirements.txt').read(),
)
