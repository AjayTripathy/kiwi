import os.path
from fabric.api import *
from fabric.colors import *

env.letter = 'k'
env.project_path = '/srv/kiwi/'
env.dj = 'p' + env.letter

env.user = 'eugene'
env.hosts = ['173.255.211.96']
key = '/Users/ebaum/.ssh/eugene_rsa'
env.branch = local('git branch | grep -e ^* | sed -E s/^.\ //', capture=True)
if os.path.isfile(key):
    env.key_filename = [key]

def runserver():
    local('./kiwi.py')

def setup():
    local('sudo pip install -r requirements.txt')

def deploy():
    sudo('')
    print(red('\nstarting...'))
    #local('git pull origin '+env.branch)
    #local('git push')
    with cd(env.project_path):
        run('git pull origin '+env.branch)
        print(red('\nupdating daemons...'))
        sudo('supervisorctl reread')
        sudo('supervisorctl update')
        print(red('\nrestarting server...'))
        sudo('supervisorctl restart ' + env.dj)
        print(red('\nKIWI KIWI KIWI'))

def clean():
    local('rm `find . -type f -iname "*pyc"`')

