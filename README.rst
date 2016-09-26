timekeeper
==========

A nosy Slack bot to track your daily workload.
Tested on Python 3.5.

Usage
-----

After install and start timekeeper, say ``@timekeeper help`` on your Slack team.

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
    python timekeeper.py

Testing
-------

.. code:: sh

    # Install extra dependencies
    pip install tox

    # Start the test runner
    tox
