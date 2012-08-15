from fabric.api import *
from fabric.contrib.project import rsync_project

env.key_filename = "/home/britta/.ssh/nopwd.access"
env.hosts = ["www@collin.rogowski.de"]

def test():
    local('./manage.py test timeline/tests.py --with-coverage --cover-package=babytimeline.timeline --cover-erase -s', capture=False)
    local('./manage.py test --with-freshen --with-coverage --cover-package=babytimeline.timeline -s', capture=False)

def testonly():
    local('./manage.py test timeline/tests.py -s -a only', capture=False)
    local('./manage.py test --with-freshen -s --tags only', capture=False)

def backupdb():
    local('./manage.py dumpdata -e contenttypes --indent 2 > backup.json')

def backup():
    with cd('babytimeline/app/babytimeline'):
        run('~/babytimeline/babytimeline/bin/python manage.py dumpdata -e contenttypes --indent 2 > /tmp/live.json')
        run('tar -cjf /tmp/userdata.tbz user_files')
        get('/tmp/live.json', '~/Dropbox/backups')
        get('/tmp/userdata.tbz', '~/Dropbox/backups')

def pack():
    local('tar -cjf /tmp/btl.tar.bz2 .')

def putremote():
    put('/tmp/btl.tar.bz2', '/tmp/')

def deploy():
    pack()
    putremote()
    with cd('babytimeline/app/babytimeline'):
        run('rm -rf *')
        run('tar -xjf /tmp/btl.tar.bz2')
        run('rm local_settings.py*')
#        run('pip install -r requirements.txt')

def rsync():
    exclude = ["local_settings.*", "*.pdf", ".coverage", "*.pyc", "babytimeline.*"]
    rsync_project(remote_dir = "babytimeline/app/", exclude=exclude, extra_opts="-e 'ssh -i /home/britta/.ssh/nopwd.access'")

def restart():
    with cd('babytimeline'):
        run("find -name '*.pyc' | xargs rm")
        run('./restart.sh')

def logs():
    run('tail -100 babytimeline/logs/btl-exceptions')
