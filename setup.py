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
    install_requires=[
        'calmap==0.0.6',
        'matplotlib==1.5.3',
        'pandas==0.18.1',
        'peewee==2.8.3',
        'pytz',
        'slackbot==0.4.1',
        'tabulate==0.7.5',
    ],
)
