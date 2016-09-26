from fabric.api import cd, env, local, put, run, task
from fabric.colors import green, yellow
from fabric.contrib.files import exists

env.use_ssh_config = True


@task
def pack():
    """Package repository contents."""
    local('python setup.py sdist --formats=gztar', capture=False)


@task
def deploy():
    """Deploy to the server (expects pythonanywhere.com)."""
    dist = local('python setup.py --fullname', capture=True).strip()
    put('dist/{}.tar.gz'.format(dist), '/tmp/timekeeper.tar.gz')
    run('mkdir -p /var/www/bots/timekeeper')
    if not exists('$WORKON_HOME/timekeeper'):
        run('mkvirtualenv timekeeper --python=/usr/bin/python3.5')
    with cd('/var/www/bots/timekeeper'):
        run('tar zxvf /tmp/timekeeper.tar.gz --strip 1')
        run('rm -f /tmp/timekeeper.tar.gz')
        run('workon timekeeper && pip install -e .')
    print(green('Deployment successfully completed. Please manually start timekeeper on your console.'))
    print(yellow("Don't forget to export SLACK_API_TOKEN and TIMEKEEPER_ERRORS_TO environment variables before running."))


@task
def clean():
    """Remove built files."""
    local('python setup.py clean --all', capture=False)
