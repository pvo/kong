# vim: tabstop=4 shiftwidth=4 softtabstop=4

"""
Installation script for Kong's testing virtualenv
"""

import os
import stat
import string
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
VENV = os.path.join(ROOT, '.kong-venv')
PIP_REQUIRES = os.path.join(ROOT, 'tools', 'pip-requires')


def die(message, *args):
    print >> sys.stderr, message % args
    sys.exit(1)


def whereis(executable):
    """
    Detect whereis a binary and make sure it's executable we can execute.
    """
    for d in string.split(os.environ['PATH'], \
                              os.pathsep):
        f = os.path.join(d, executable)
        if os.path.isfile(f):
            try:
                st = os.stat(f)
            except OSError:
                continue
            if stat.S_IMODE(st[stat.ST_MODE]) & 0111:
                return True
    return False


def run_command(cmd, redirect_output=True, check_exit_code=True):
    """
    Runs a command in an out-of-process shell, returning the
    output of that command.  Working directory is ROOT.
    """
    if redirect_output:
        stdout = subprocess.PIPE
    else:
        stdout = None

    proc = subprocess.Popen(cmd, cwd=ROOT, stdout=stdout)
    output = proc.communicate()[0]
    if check_exit_code and proc.returncode != 0:
        die('Command "%s" failed.\n%s', ' '.join(cmd), output)
    return output


HAS_EASY_INSTALL = bool(whereis("easy_install"))
HAS_VIRTUALENV = bool(whereis("virtualenv"))


def check_dependencies():
    """Make sure virtualenv is in the path."""

    if not HAS_VIRTUALENV:
        print 'not found.'
        # Try installing it via easy_install...
        if HAS_EASY_INSTALL:
            print 'Installing virtualenv via easy_install...',
            if not run_command(['easy_install', 'virtualenv']):
                die('ERROR: virtualenv not found.\n\n'
                    'Glance development requires virtualenv, please install'
                    ' it using your favorite package management tool')
            print 'done.'
    print 'done.'


def create_virtualenv(venv=VENV):
    """Creates the virtual environment and installs PIP only into the
    virtual environment
    """
    print 'Creating venv...',
    run_command(['virtualenv', '-q', '--no-site-packages', VENV])
    print 'done.'
    print 'Installing pip in virtualenv...',
    if not run_command(['tools/with_venv.sh', 'easy_install', 'pip']).strip():
        die("Failed to install pip.")
    print 'done.'


def install_dependencies(venv=VENV):
    print 'Installing dependencies with pip (this can take a while)...'

    # Install greenlet by hand - just listing it in the requires file does not
    # get it in stalled in the right order
    venv_tool = 'tools/with_venv.sh'
    run_command([venv_tool, 'pip', 'install', '-E', venv, '-r', PIP_REQUIRES],
                redirect_output=False)

    # Tell the virtual env how to "import glance"
    pthfile = os.path.join(venv, "lib", "python2.6", "site-packages",
                                 "glance.pth")
    f = open(pthfile, 'w')
    f.write("%s\n" % ROOT)


def print_help():
    help = """
 Kong testing environment setup is complete.

 Kong testing uses virtualenv to track and manage Python dependencies
 while in development and testing.

 To activate the Kong virtualenv for the extent of your current shell
 session you can run:

 $ source .kong-venv/bin/activate

 Or, if you prefer, you can run commands in the virtualenv on a case by case
 basis by running:

 $ tools/with_venv.sh <your command>

 Also, make test will automatically use the virtualenv.
    """
    print help


def main(argv):
    check_dependencies()
    create_virtualenv()
    install_dependencies()
    print_help()

if __name__ == '__main__':
    main(sys.argv)
