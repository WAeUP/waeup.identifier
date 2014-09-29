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
import subprocess
import threading
from subprocess import Popen, PIPE
from tkinter import (
    N, W, S, E, StringVar, IntVar, Frame, Label, Entry, Menu, SUNKEN,
    messagebox, ACTIVE, LEFT, BOTH, LabelFrame, X, BOTTOM, NORMAL, DISABLED,
    )
from tkinter.simpledialog import Dialog
from tkinter.ttk import Notebook, Progressbar, Button, Radiobutton
from waeup.identifier.config import get_config, CONF_KEYS


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

        `cmd` is a list containing the command to execute and
        parameters.

        `timeout` is a float setting the amount of time after which
        the command execution should be aborted.

        `callback`, if given, is called when new output from the
        executed binary (stdout or stderr) is available. The callback
        is called without any parameters. To see, what output
        happened, you have to query the `BackgroundCommand` used
        before.
        """
        super(BackgroundCommand, self).__init__()
        self.p = None
        self.cmd = cmd
        self.timeout = timeout
        self.callback = callback
        self._timer = None
        self._stdout = None
        self._stderr = None

    def _poll(self):
        """Poll process output. If new output was received, call back.
        """
        if self._timer is not None:
            self._timer.cancel()
            if self.callback is not None:
                self.callback()
        if self.p.returncode is None:
            self._timer = threading.Timer(POLL_INTERVAL, self._poll)
            self._timer.daemon = True
            self._timer.start()

    def stop(self):
        """Stop running subprocess, terminate any timers, etc.

        General cleanup actions.
        """
        if self._timer is not None:
            self._timer.cancel()
        if self.p is not None and self.is_alive():
            self.p.terminate()
            self.join()

    def run(self):
        # override base
        self.p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        self._poll()

    def execute(self):
        """Execute the given command, respecting timeouts.

        Run the command given on init and terminate it when `timeout`
        lapsed.
        """
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.p.terminate()  # use self.p.kill() if process needs a kill -9
            self.join()

    def wait(self):
        """Wait until command terminates.

        Returns returncode, stdout data, and stderr data as a tuple.
        """
        stdout_data, stderr_data = self.p.communicate()
        if self._timer is not None:
            self._timer.cancel()
        return self.p.returncode, stdout_data, stderr_data


class FPScanCommand(BackgroundCommand):
    def __init__(self, path, params=[], timeout=None, callback=None):
        """Execute `fsscan` as background command.

        `path` must be an existing binary path. `params` is a list of
        options to use when calling fsscan.
        """
        cmd = [path,] + params
        super(FPScanCommand, self).__init__(
            cmd, timeout=timeout, callback=callback)


class PreferencesDialog(Dialog):

    def __init__(self, parent, title=None, values={}):
        """Initialize a preferences dialog.

        `parent` -- a parent window (the application window)

        `title` -- the dialog title.

        `values` -- a dict of values to store in preferences. Use this
                    dict to get/set values.
        """
        self.values = values
        self._values = dict()
        for key in CONF_KEYS:
            self._values[key] = StringVar()
            self._values[key].set(values.get(key, ''))
        super(PreferencesDialog, self).__init__(parent, title)

    def body(self, master):
        """Override body creation.
        """
        body = Frame(master)

        base_box = LabelFrame(
            body, text="Basic Options", padx=5, pady=5, takefocus=1)
        Label(base_box, text="Path to fpscan:  ").grid(sticky=W)
        w = Entry(base_box, width=30, textvariable=self._values['fpscan_path'])
        w.grid(row=0, column=1, sticky=E)

        waeup_box = LabelFrame(
            body, text="WAeUP Portal", padx=5, pady=5, takefocus=1)
        Label(waeup_box, text="URL of WAeUP Portal:  ").grid(sticky=W)
        w = Entry(waeup_box, width=30, textvariable=self._values['waeup_url'])
        w.grid(row=0, column=1, sticky=E + W, pady=2)
        Label(waeup_box, text="WAeUP Username: ").grid(sticky=W, row=1)
        w = Entry(waeup_box, width=15, textvariable=self._values['waeup_user'])
        w.grid(row=1, column=1, sticky=E + W, pady=2)
        Label(waeup_box, text="Portal Password: ").grid(sticky=W, row=2)
        w = Entry(
            waeup_box, width=20, textvariable=self._values['waeup_passwd'],
            show='*')
        w.grid(row=2, column=1, sticky=E + W, pady=2)

        base_box.pack(fill=BOTH, expand=1)
        waeup_box.pack(fill=BOTH, expand=1)
        body.pack(fill=BOTH, expand=1)
        return body

    def buttonbox(self):
        """Override standard button box.
        """
        box = Frame(self)
        w = Button(box, text="Save", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack(fill=BOTH, expand=1)

    def validate(self):
        '''validate the data

        This method is called automatically to validate the data
        before the dialog is destroyed. By default, it always
        validates OK.
        '''
        return 1  # override

    def apply(self):
        '''process the data

        This method is called automatically to process the data,
        *after* the dialog is destroyed. By default, it does nothing.
        '''
        for key in CONF_KEYS:
            self.values[key] = self._values[key].get()


class FPScanApplication(Frame):

    detected_scanners = []
    chosen_scanner = None

    def __init__(self, master=None):
        """The main application.

        `master` is a parent widget, normally ``None``.
        """
        Frame.__init__(self, master, width=400, height=240)
        self.config = get_config()
        self.chosen_scanner = IntVar()
        self.chosen_scanner.set(-1)
        self.chosen_scanner.trace("w", self.evt_scanner_chosen)

        self.body = Notebook(self, name="body")
        self.body.enable_traversal()

        self.page_scan = Frame(self.body)
        self.page_scan_body = Frame(self.page_scan)

        self.page_identify = Frame(self.body)
        self.page_identify_body = Frame(self.page_identify)

        self.page_hardware = Frame(self.body)
        self.page_hardware_body = Frame(self.page_hardware)

        self.body.add(
            self.page_hardware,
            text="Hardware", underline=-1, padding=4)
        self.body.add(
            self.page_scan,
            text="New Fingerprint", underline=-1, padding=4)
        self.body.add(
            self.page_identify,
            text="Identify Person", underline=-1, padding=4)
        self.body.pack(expand=1, fill=BOTH, pady=0)
        #self.body.select(2)

        self.footer_bar = Label(
            self, text="ready.", relief=SUNKEN, anchor="sw", height=1)
        self.footer_bar.pack(
            expand=0, fill=X, pady=2, padx=1, side=BOTTOM, anchor="sw")

        self.draw_scan_page()
        self.draw_hardware_detect_page()
        self.create_menubar()
        self.master.bind('<Control-q>', self.cmd_quit)
        self.master.title('WAeUP Identifier')
        self.pack(expand=1, fill=BOTH)
        self.pack_propagate(0)
        self.cmd_start_detect()

    def evt_scanner_chosen(self, *args):
        self.draw_scan_page()

    def draw_scan_page(self):
        self.page_scan_body.pack_forget()
        self.page_scan_body.destroy()  # remove old body
        self.page_scan_body = Frame(self.page_scan)
        state = NORMAL
        if self.chosen_scanner.get() < 0:
            state = DISABLED
        Label(
            self.page_scan_body,
            text="Scan Fingerprint",
            anchor="nw").pack()
        btn = Button(
            self.page_scan_body,
            text="Start Scan",
            command=lambda: self.cmd_start_scan(),
            state=state,
            )
        btn.pack(pady=15)
        self.page_scan_body.pack()

    def draw_scan_running_page(self):
        self.page_scan_body.pack_forget()
        self.page_scan_body.destroy()  # remove old body
        self.page_scan_body = Frame(self.page_scan)
        state = NORMAL
        if self.chosen_scanner.get() < 0:
            state = DISABLED
        Label(
            self.page_scan_body,
            text="Scanning Fingerprint\nPlease put finger on device",
            anchor="nw").pack()
        btn = Button(
            self.page_scan_body,
            text="Abort Scan",
            command=lambda: self.cmd_start_scan(),
            state=state,
            )
        btn.pack(pady=15)
        self.page_scan_body.pack()

    def draw_hardware_detect_page(self):
        self.page_hardware_body.pack_forget()
        self.page_hardware_body.destroy()  # remove old body
        self.page_hardware_body = Frame(self.page_hardware)
        Label(
            self.page_hardware_body,
            text="Detecting fingerprint scanners, please wait...",
            anchor="nw").pack(pady=15)
        pb1 = Progressbar(
            self.page_hardware_body, mode="indeterminate")
        pb1.pack()
        pb1.start()

        detect_cancel = Button(
            self.page_hardware_body,
            text="Cancel", command=lambda: self.cmd_abort_detect())
        detect_cancel.pack(pady=15)
        self.page_hardware_body.pack()
        self.footer_bar['text'] = "Detecting scanners..."

    def draw_hardware_list_page(self):
        self.page_hardware_body.pack_forget()
        self.page_hardware_body.destroy()  # remove old body
        self.page_hardware_body = Frame(self.page_hardware)
        text = "Fingerprint scanners found:"
        if not self.detected_scanners:
            text += " None\n"
        Label(
            self.page_hardware_body,
            text=text,
            anchor="nw").pack(pady=15)
        for num, scanner in enumerate(self.detected_scanners):
            line = Frame(self.page_hardware_body)
            Radiobutton(
                line, text=scanner, variable=self.chosen_scanner, value=num
                ).pack(anchor=W)
            line.pack()
        btn = Button(
            self.page_hardware_body,
            text="Rescan",
            command=lambda: self.cmd_start_detect()
            )
        btn.pack(pady=15)
        self.page_hardware_body.pack()
        self.footer_bar['text'] = "Ready."

    def cmd_start_detect(self):
        self.draw_hardware_detect_page()
        self.chosen_scanner.set(-1)
        try:
            self.detected_scanners = detect_scanners(
                self.config['DEFAULT'].get('fpscan_path'))
        except ValueError:
            messagebox.showwarning(
                "fpscan binary missing",
                "Cannot find 'fpscan'.\n\nThis programme is needed. Please "
                "install it and set the path in preferences.")
        self.draw_hardware_list_page()
        return

    def cmd_abort_detect(self):
        self.footer_bar['text'] = "Ready."
        self.draw_hardware_list_page()
        print("Abort detection.")
        return

    def cmd_start_scan(self):
        self.footer_bar['text'] = "Scanning..."
        self.draw_scan_running_page()
        print("Start FP scan")
        return

    def cmd_file(self):
        return

    def cmd_quit(self, event=None):
        return self.master.quit()

    def cmd_about(self):
        messagebox.showinfo("About WAeUP Identifier",
                            "WAeUP Identifier, (c) 2014 WAeUP Germany")
        return

    def cmd_prefs(self):
        """Command called when a (modal) preference dialog should appear.
        """
        values = dict()
        for conf_key in CONF_KEYS:
            values[conf_key] = self.config['DEFAULT'].get(conf_key, '')
        dialog = PreferencesDialog(self, title='Preferences', values=values)
        for conf_key in CONF_KEYS:
            self.config['DEFAULT'][conf_key] = dialog.values[conf_key]
        return

    def create_menubar(self):
        """Create a menubar.
        """
        self.menubar = Menu(self)
        self.master['menu'] = self.menubar
        # file menu
        self.menu_file = Menu(self.menubar, tearoff=0)
        self.menu_file.add_command(
            label="Quit", command=self.cmd_quit, underline=0,
            accelerator="Ctrl+Q")
        self.menubar.add_cascade(
            label="File", menu=self.menu_file, underline=0)
        # edit menu
        self.menu_edit = Menu(self.menubar, tearoff=0)
        self.menu_edit.add_command(
            label="Preferences", command=self.cmd_prefs)
        self.menubar.add_cascade(
            label="Edit", menu=self.menu_edit, underline=0)
        # help menu
        self.menu_help = Menu(self.menubar, tearoff=0, name='help')
        self.menu_help.add_command(
            label="About WAeUP Identifier", command=self.cmd_about)
        self.menubar.add_cascade(
            label="Help", menu=self.menu_help, underline=0)
        self.master.config(menu=self.menubar)
