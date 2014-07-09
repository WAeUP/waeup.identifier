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
from tkinter import (
    N, W, S, E, StringVar, Frame, Button, Label, Entry, Menu, SUNKEN,
    messagebox, simpledialog, ACTIVE, LEFT, BOTH, LabelFrame, X, Y, BOTTOM
    )
from tkinter.simpledialog import Dialog


class PreferencesDialog(Dialog):

    def __init__(self, parent, title=None, values={}):
        """Initialize a preferences dialog.

        `parent` -- a parent window (the application window)

        `title` -- the dialog title.

        `values` -- a dict of values to store in preferences. Use this
                    dict to get/set values.
        """
        self.val_fpscan_path = StringVar()
        self.val_waeup_url = StringVar()
        self.val_waeup_user = StringVar()
        self.val_waeup_passwd = StringVar()
        self.values = values
        super(PreferencesDialog, self).__init__(parent, title)

    def body(self, master):
        """Override body creation.
        """
        body = Frame(master)

        base_box = LabelFrame(
            body, text="Basic Options", padx=5, pady=5, takefocus=1)
        Label(base_box, text="Path to fpscan:  ").grid(sticky=W)
        w = Entry(base_box, width=30, textvariable=self.val_fpscan_path)
        w.grid(row=0, column=1, sticky=E)

        waeup_box = LabelFrame(
            body, text="WAeUP Portal", padx=5, pady=5, takefocus=1)
        Label(waeup_box, text="URL of WAeUP Portal:  ").grid(sticky=W)
        w = Entry(waeup_box, width=30, textvariable=self.val_waeup_url)
        w.grid(row=0, column=1, sticky=E+W, pady=2)
        Label(waeup_box, text="WAeUP Username: ").grid(sticky=W, row=1)
        w = Entry(waeup_box, width=15, textvariable=self.val_waeup_user)
        w.grid(row=1, column=1, sticky=E+W, pady=2)
        Label(waeup_box, text="Portal Password: ").grid(sticky=W, row=2)
        w = Entry(waeup_box, width=20, textvariable=self.val_waeup_passwd)
        w.grid(row=2, column=1, sticky=E+W, pady=2)


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
        pass  # override


class FPScanApplication(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.body = Frame(self)
        Label(self.body, text="WAeUP Identifier", anchor="nw").pack(
            fill=X, expand=1, padx=5, pady=5, ipadx=0, ipady=0)
        Label(self.body, text="12 ").pack(fill=BOTH, expand=1)
        self.body.pack(expand=1, fill=BOTH, pady=0)

        self.footer_bar = Label(
            self, text="ready.", relief=SUNKEN, anchor="sw", height=1)
        self.footer_bar.pack(
            expand=1, fill=X, pady=2, padx=1, side=BOTTOM, anchor="sw")

        self.create_menubar()
        #self.master.bind('<Return>', self.calculate)
        self.master.bind('<Control-q>', self.cmd_quit)
        self.master.title('WAeUP Identifier')
        self.pack(expand=1, fill=BOTH)

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
        result = PreferencesDialog(
            self, title='Preferences')
        return

    def create_menubar(self):
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
            label="Preferences", command=self.cmd_prefs, underline=0)
        self.menubar.add_cascade(
            label="Edit", menu=self.menu_edit, underline=0)
        # help menu
        self.menu_help = Menu(self.menubar, tearoff=0, name='help')
        self.menu_help.add_command(
            label="About WAeUP Identifier", command=self.cmd_about)
        self.menubar.add_cascade(
            label="Help", menu=self.menu_help, underline=0)
        self.master.config(menu=self.menubar)
