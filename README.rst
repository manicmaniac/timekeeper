timekeeper
==========

.. image:: https://travis-ci.org/ymizushima/timekeeper.svg?branch=master
    :target: https://travis-ci.org/ymizushima/timekeeper

.. image:: https://coveralls.io/repos/github/ymizushima/timekeeper/badge.svg?branch=master
    :target: https://coveralls.io/github/ymizushima/timekeeper?branch=master

A nosy Slack bot to track your daily workload.
Tested on Python 3.5.

Usage
-----

After install and start timekeeper, say ``@timekeeper help`` on your Slack team.

Dependencies
------------

- Linux (or Docker)
- Python 3.5
- pip

Install
-------

.. code:: sh

    # Clone this repo and move into it
    git clone https://github.com/ymizushima/timekeeper.git
    cd timekeeper

    # Setup Python virtual environment
    python -mvenv env
    source env/bin/activate

    # Install dependencies
    pip install -e .

    # Configure environment variables
    export SLACK_API_TOKEN='your Slack API token here'
    export TIMEKEEPER_ERRORS_TO='your Slack username here'

    # Run the bot
    python bot.py

Docker
------

with docker-compose (recommended)

.. code:: sh

    SLACK_API_TOKEN='your Slack API token here' TIMEKEEPER_ERRORS_TO='your Slack username here' docker-compose up -d


or with docker

.. code:: sh

    # Start the built image at the first time
    docker run -d -e SLACK_API_TOKEN='your Slack API token here' -e TIMEKEEPER_ERRORS_TO='your Slack username here' --name timekeeper ymizushima/timekeeper

    # Just start the created container thereafter
    docker start timekeeper

Testing
-------

.. code:: sh

    # Install extra dependencies
    pip install tox

    # Start the test runner
    tox
