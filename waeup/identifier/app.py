#
#    waeup.identifier - identifiy WAeUP Kofa students biometrically
#    Copyright (C) 2014  Uli Fouquet, WAeUP Germany
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import os
import re
import socket
import subprocess
import threading
from subprocess import Popen, PIPE
from waeup.identifier.config import get_config, CONF_KEYS
from waeup.identifier.webservice import (
    get_url_from_config, store_fingerprint
)


#: The set of chars allowed in filenames we handle.
#: Last char must not be slash.
VALID_FILENAME = re.compile('^[a-zA-Z0-9/\._\-]+$')

#: How often do we look for new data while executing commands?
POLL_INTERVAL = 0.1


def check_path(path):
    """Check a given path.

    `path` must exist, be valid, and be executable. The returned path
    will be a 'normalized' with illegal chars stripped.

    Illegal chars are considered all except ``[a-zA-Z0-9_.-]`` as
    written in the `VALID_FILENAME` regular expression.

    If the path does not exist, contains illegal chars, or is not
    executable, a `ValueError` is raised.
    """
    if path is None:
        raise ValueError("Path must be a string, not None.")
    path = os.path.abspath(path)
    if not VALID_FILENAME.match(path):
        raise ValueError("Path contains illegal chars: %s" % path)
    if not (os.path.isfile(path) and os.access(path, os.X_OK)):
        raise ValueError("Not a valid executable path: %s" % path)
    return path


def fpscan(path, args=[]):
    """Call fpscan binary in `path` and return output.

    `args` gives the arguments to be passed to the executable `path`.

    Returns tuple ``(<RETURNCODE>, <OUT_DATA>, <ERR_DATA>)`` whith
    ``<RETURNCODE>`` being the subprocess return code, while
    ``<OUT_DATA>`` and ``<ERR_DATA>`` contain the subprocess output on
    stdout and stderr repsectively.

    Both, ``<OUT_DATA>`` and ``<ERR_DATA>`` are UTF-8 encoded strings.
    """
    cmd = [path] + args
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    return p.returncode, out.decode('utf-8'), err.decode('utf-8')


def detect_scanners(fpscan_path):
    """Detect available fingerprint scanners with `fpscan`.

    We use `fpscan` to find and work with available fingerprint
    scanners.
    """
    path = check_path(fpscan_path)
    status, out, err = fpscan(path)
    if status != 0:   # detection failed
        return []
    elif out == '0\n':  # detection worked but no scanners found
        return []
    result = [x for x in out.split('\n')
              if len(x) and not x.startswith(' ')]
    return result


def scan(fpscan_path, device):
    """Perform a fingerprint scan.
    """
    path = check_path(fpscan_path)
    status, out, err = fpscan(path, ['-s', '-d', str(device)])
    if status != 0:  # scan failed
        raise ValueError('Scan failed: %s' % err)
    return


class BackgroundCommand(threading.Thread):
    def __init__(self, cmd, timeout=None, callback=None):
        """A system  command run in background.

        Run system command in background. The command results like
        output, returncode, etc., can be retrieved after command
        completion.

        Normally, you will tell `BackgroundCommand` what command
        should be run in a list like ``['/bin/ls', '-l']``. You might
        optionally give a timeout and/or a callback function to call
        when the command finished. Then you start the whole process
        calling the `start()` method. Please use `start()` and not
        `run()` because only with `start()` the command is run in a
        concurrent thread.

        After `timeout` seconds the command will be killed if it still
        runs and the `callback` function will be called.

        `BackgroundCommand` provides the three attributes

        * `stdout_data`

        * `stderr_data`

        * `returncode`

        that will provide the streamed output of the run command and
        its exit code.

        Furthermore you can ask for `timed_out`, a boolean, to check
        whether the command was killed (due to timeout) and/or
        `is_alive()`, a method to see whether the command already
        finished.

        `cmd` is a list containing the command to execute and
        parameters. You can also pass in a single string as `cmd`.

        `timeout`, if given, is a float setting the amount of seconds
        after which the command execution should be aborted. By
        default there is no timeout.

        `callback`, if given, is called when new output from the
        executed binary (stdout or stderr) is available. The callback
        is called with the `BackgroundCommand` instance as only
        argument. Naturally, there is no default callback function.
        """
        super(BackgroundCommand, self).__init__()
        if not isinstance(cmd, list):
            cmd = [cmd, ]
        self.p = None
        self.cmd = cmd
        self.timeout = timeout
        self.callback = callback
        self._timer = None
        self.returncode = None
        self.stdout_data = None
        self.stderr_data = None
        self.is_killed = False

    def run(self):
        """Code run in a separate thread.

        Run command in a subprocess, set timer and set command results
        (exitcode, output, etc.).

        Do not use this method directly. Use `start()` instead,
        because `start()` will properly call this method in a
        concurrent thread.
        """
        # override base
        self.p = subprocess.Popen(
            self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if self.timeout is not None:
            # start watchdog that aborts when we need too much time
            self._timer = threading.Timer(self.timeout, self._kill)
            self._timer.daemon = True
            self._timer.start()
        self.stdout_data, self.stderr_data = self.p.communicate()
        self.returncode = self.p.returncode
        if self.callback is not None:
            if self._timer is not None:
                self._timer.cancel()
            self.callback(self)
        return

    def _kill(self):
        """Kill any running thread.

        For internal use only. This is the emergency break invoked
        after `timeout` seconds.
        """
        if self._timer is not None:
            self._timer.cancel()
        if self.p.returncode is not None:
            return
        self.p.kill()
        self.is_killed = True
        self.join()
        if self.callback is not None:
            self.callback(self)

    def wait(self):
        """Wait until command terminates.

        Returns returncode, stdout data, and stderr data as a tuple.
        """
        while self.is_alive():
            pass
        return self.returncode, self.stdout_data, self.stderr_data


class FPScanCommand(BackgroundCommand):
    def __init__(self, path, params=[], timeout=None, callback=None):
        """Execute `fsscan` as background command.

        `path` must be an existing binary path. `params` is a list of
        options to use when calling fsscan.
        """
        cmd = [path, ] + params
        if not os.path.exists(path):
            raise IOError("No such path: %s" % (path, ))
        super(FPScanCommand, self).__init__(
            cmd, timeout=timeout, callback=callback)


class FPScanApplication(object):

    detected_scanners = []
    chosen_scanner = None

    def __init__(self):
        """The main application.
        """
