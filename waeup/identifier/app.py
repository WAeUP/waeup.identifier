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
import string
import subprocess
import threading
from kivy.app import App
from kivy.clock import mainthread
from kivy.config import Config
from kivy.logger import Logger
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.textinput import TextInput
from subprocess import Popen, PIPE
from waeup.identifier.config import (
    get_json_settings, get_default_settings, get_conffile_location,
)
from waeup.identifier.webservice import store_fingerprint, get_url


# Enable virtualkeyboard
if not Config.get('kivy', 'keyboard_mode'):
    Config.set('kivy', 'keyboard_mode', 'systemandmulti')

#: The set of chars allowed in filenames we handle.
#: Last char must not be slash.
VALID_FILENAME = re.compile('^[a-zA-Z0-9/\._\-]+$')

#: A valid student id looks like this
#: Two or three uppercase ASCIIs followed by at least five digits
RE_STUDENT_ID = re.compile('^[A-Z]{2,3}[0-9]{5,}$')


#: How often do we look for new data while executing commands?
POLL_INTERVAL = 0.1


#: Directory where we store images
IMAGES_PATH = os.path.join(os.path.dirname(__file__), 'images')


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
        """Execute `fpscan` as background command.

        `path` must be an existing binary path. `params` is a list of
        options to use when calling fpscan.
        """
        cmd = [path, ] + params
        if not os.path.exists(path):
            raise IOError("No such path: %s" % (path, ))
        super(FPScanCommand, self).__init__(
            cmd, timeout=timeout, callback=callback)


def call_in_background(callable, args=(), kwargs={}, callback=None):
    def run(*args, **kwargs):
        result = callable(*args, **kwargs)
        callback(result)
    thread = threading.Thread(
        target=run, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread


class StudentIdInput(TextInput):
    """A `TextInput` turning input into upper case.

    Apart from that we allow only `[A-Z0-9]` as chars.
    """
    def insert_text(self, substring, from_undo=False):
        s = substring.upper()
        s = ''.join(
            [c for c in s if c in string.ascii_letters + string.digits])
        return super(StudentIdInput, self).insert_text(s, from_undo=from_undo)


class FPScanPopup(Popup):
    """A popup in the `FPScanApp` application.

    You can set your own `title`, `message` and `button_text`, but
    consider to define derived classes and set the texts in the
    accompanied `kv` file.

    All popups in `FPScanApp` should use this popup class to share look
    and feel.
    """
    def __init__(self, title=None, message=None, button_text=None, *args):
        result = super(FPScanPopup, self).__init__(*args)
        if title is not None:
            self.title = title
        if message is not None:
            self.f_message = message
        if button_text is not None:
            self.f_btn_text = button_text
        return result


class PopupInvalidFPScanPath(FPScanPopup):
    """Popup emitting error message if `fpscan` not found.

    The output texts can be set in the accompanied ``fpscan.kv``.
    """
    pass


class PopupNoScanDevice(FPScanPopup):
    """Popup showing a warning: no scanner found
    """
    pass


class PopupScanFailed(FPScanPopup):
    """Popup signalling failed scan.
    """


class PopupUploadSuccessful(FPScanPopup):
    """Popup signalling successful fingerprint data upload.
    """


class FPScanApp(App):
    """The main application.
    """
    detected_scanners = []
    chosen_scanner = None
    icon = '%s/waeupicon.png' % IMAGES_PATH
    prevent_scanning = BooleanProperty(True)
    popup_text = StringProperty('')
    cmd_running = None
    scan_canceled = False
    mode = StringProperty('main')
    old_mode = 'main'

    def build(self):
        from kivy.uix.settings import Settings
        self.settings_cls = Settings
        Logger.debug("waeup.identifier: Icon path set to %s" % self.icon)
        result = super(FPScanApp, self).build()
        self.screen_manager = self.get_screen_manager()
        return result

    def get_application_config(self):
        """Get path of app configuration file.

        We lookup a file `.waeupident.ini` in user home.
        """
        path = get_conffile_location()
        Logger.debug("waeup.identifier: expect config file in %s" % path)
        return super(FPScanApp, self).get_application_config(path)

    def get_screen_manager(self):
        """Get the screen manager responsible for the main screen.

        There must be at most one screen manager in the widget tree.
        """
        for widget in self.root.walk():
            if isinstance(widget, ScreenManager):
                return widget

    def get_widget_by_id(self, kv_id):
        """Lookup widget with kv id `kv_id`.

        Return widget if found, none else.
        """
        for widget in self.root.walk():
            if kv_id in widget.ids:
                return widget.ids[kv_id]

    def build_config(self, config):
        for key, conf_dict in get_default_settings():
            config.setdefaults(key, conf_dict)

    def build_settings(self, settings):
        settings.add_json_panel(
            "Identifier", self.config, data=get_json_settings())

    def on_config_change(self, config, section, key, value):
        """Configuration changed.

        `config` is a ConfigParser instance , while `section`, `key` and
        `value` denote the changed value.
        """
        Logger.info(
            "waeup.identifier: config change: {0}, {1}, {2}, {3}".format(
                config, section, key, value))

    def on_stud_id_entered(self, instance):
        """A student id was entered.
        """
        entered_text = instance[0].text
        prevent = RE_STUDENT_ID.match(entered_text) is None
        self.prevent_scanning = prevent
        if entered_text and prevent:
            popup = FPScanPopup(
                title="Invalid Student Id",
                message="The entered student id is not valid"
                )
            popup.open()
        self.root.f_student_id = entered_text
        Logger.debug("waeup.identifier: stud_id changed: %s" % entered_text)

    def on_mode(self, instance, value):
        """This should be called whenever `mode` changes.
        """
        Logger.debug(
            "waeup.identifier: mode change %r -> %r" % (self.old_mode, value))
        stud_id_label = self.get_widget_by_id('label_stud_id')
        self.root.f_student_id = ''
        if value == "scan":
            self.root.btn_scan_text = 'Scan'
            self.root.prevent_scanning = True
            stud_id_label.text = "Student ID:\n[color=999]of student to register[/color]"
        elif value == "verify":
            self.root.btn_scan_text = 'Verify'
            self.root.prevent_scanning = True
            stud_id_label.text = "Student ID:\n[color=999]of student to verify[/color]"
        self.old_mode = value

    def scan_pressed(self, instance):
        Logger.debug("waeup.identifier: 'scan' pressed")
        self.mode = "scan"
        self.screen_manager.current = 'screen_scan'

    def kill_running_cmd(self):
        """Kill any running subprocess.
        """
        if self.cmd_running is None:
            return
        Logger.debug("waeup.identifier: kill running subprocess...")
        self.cmd_running.callback = None
        self.cmd_running._kill()
        Logger.debug("waeup.identifier: done.")
        self.cmd_running = None

    def verify_pressed(self, instance):
        Logger.debug("waeup.identifier: 'verify' pressed")
        self.mode = "verify"
        self.screen_manager.current = 'screen_scan'

    def quit_pressed(self, instance):
        Logger.debug("waeup.identifier: 'quit' pressed")
        self.kill_running_cmd()
        self.stop()

    def cancel_scan(self, instance):
        Logger.debug("waeup.identifier: user canceled scan")
        self.kill_running_cmd()
        self.scan_canceled = True
        self.mode = "main"

    def start_scan_pressed(self, instance):
        Logger.debug("waeup.identifier: start scan")
        self._scan_button = instance[0]
        path = self.config.get('fpscan', 'fpscan_path')
        Logger.debug("waeup.identifier: `fpscan` at %s" % path)
        if not os.path.isfile(path):
            Logger.debug("waeup.identifier: fpscan path is invalid.")
            PopupInvalidFPScanPath().open()
            return
        scanners = detect_scanners(path)
        Logger.debug(
            "waeup.identifier: detected scanners. result %s" % scanners)
        if not scanners:
            Logger.debug("waeup.identifier: no scanner detected. Aborted.")
            PopupNoScanDevice().open()
            return
        self.cmd_running = FPScanCommand(
            path=path, params=['-s'], callback=self.scan_finished)
        self._scan_button_old_text = self._scan_button.text
        self._scan_button.text = "Please touch scanner..."
        self._scan_button.disabled = True
        Logger.debug(
            'waeup.identifier: initialized scan, awaiting finger touch')
        self.cmd_running.start()

    @mainthread
    def scan_finished(self, *args):
        """A scan has been finished.

        This is a callback function which might be called from a
        separate thread. Therefore it is decorated with `mainthread`.
        """
        Logger.info("waeup.identifier: scan finished.")
        self.cmd_running = None
        if self.scan_canceled:
            self.scan_canceled = False
            return
        self._scan_button.text = self._scan_button_old_text
        self._scan_button.disabled = False
        path = os.path.join(os.getcwd(), "data.fpm")
        if not os.path.isfile(path):
            # Scan failed
            Logger.warn("waeup.identifier: no such file: %s" % path)
            PopupScanFailed().open()
            return
        self.upload_fingerprint(path)

    def upload_fingerprint(self, path):
        """Do the actual upload.

        `path` is the path to the `.fpm` file to be uploaded.
        """
        student_id = self.root.f_student_id
        Logger.info(
            "waeup.identifier: uploading fingerprint for '%s'" % student_id)
        username = self.config.get('Server', 'waeup_user')
        password = self.config.get('Server', 'waeup_passwd')
        netloc = self.config.get('Server', 'waeup_url')
        url = get_url(netloc, username, password)
        call_in_background(
            callable=store_fingerprint,
            args=(url, student_id, 1, path),
            callback=self.upload_finished)

    @mainthread
    def upload_finished(self, upload_result):
        """Callback for fingerprint file upload.
        """
        Logger.info(
            "waeup.identifier: fingerprint upload finished: %r" %
            upload_result)
        if upload_result is not True:
            # upload failed
            FPScanPopup(
                title="Data upload failed",
                message="Fingerprint upload failed.\nError message:\n%s" %
                upload_result).open()
            return
        # upload succeeded
        PopupUploadSuccessful().open()
        screen_mgr = self.get_screen_manager()
        screen_mgr.transition.direction = "right"
        screen_mgr.current = "screen_main"
        self.mode = 'main'
