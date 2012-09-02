import os
import string
import subprocess
import sys

# Reliable quoting, taken as-is from `pipes` standard module.
# There is a slight chance it may work on non-Unix platforms, but
# I wouldn't count on it. Either way tests will show.

_safechars = frozenset(string.ascii_letters + string.digits + '@%_-+=:,./')

def quote(file):
    """Return a shell-escaped version of the file string."""
    for c in file:
        if c not in _safechars:
            break
    else:
        if not file:
            return "''"
        return file
    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + file.replace("'", "'\"'\"'") + "'"

class ExecuteError(RuntimeError):
    pass

def execute(command, env=None, split_lines=False, ignore_errors=False,
            errors_to_ignore=(), stdin='', cwd=None, capture_output=True):
    """Utility function to execute a command and return the output.
       It's basically a little saner version of subprocess.call.

       :param command: a string or a list; command to be executed
       :param env: environment dictionary
       :param split_lines: On True, the result lines are returned separated
       :param ignore_errors: On False, throw an exception if the command
            returned a non-zero return code.
       :param errors_to_ignore: tuple of return codes not to be interpreted as
            errors
       :param stdin: a string passed to the subprocess
       :param cwd: working directory to temporarily chdir to
       :param capture_output: if False, output will be passed to stdout/stderr

       :returns: the standard output of the subprocess in a string
    """

    if env:
        env.update(os.environ)
    else:
        env = os.environ.copy()

    # We don't want gettext to get in the way, so let's disable it altogether
    env['LC_ALL'] = 'C'
    env['LANG'] = 'C'

    # Although there is some kind of support for "sequence" commands in the
    # subprocess module, it works kinda wonky. If you want to investigate,
    # comment the following two lines and see the tests blow up.
    if isinstance(command, (list, tuple)):
        command = ' '.join(quote(x) for x in command)

    # I'm not quite sure this is necessary. I leave it mostly
    # as I don't have a development-ready Windows box to test it.
    if sys.platform.startswith('win'):
        close_fds = False
    else:
        close_fds = True

    original_cwd = os.getcwd()
    try:
        if cwd:
            os.chdir(cwd)
        if capture_output:
            p = subprocess.Popen(command, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    shell=True, close_fds=close_fds, env=env)
        else:
            p = subprocess.Popen(command, stdin=subprocess.PIPE,
                    shell=True, close_fds=close_fds, env=env)

        stdout, _ = p.communicate(stdin)
        rc = p.returncode
    finally:
        os.chdir(original_cwd)

    if split_lines:
        stdout = stdout.splitlines()
    if rc and not ignore_errors and rc not in errors_to_ignore:
        raise ExecuteError('Failed to execute command: %s\n%s' % \
            (command, stdout))

    return stdout

