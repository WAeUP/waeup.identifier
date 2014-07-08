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
    messagebox, simpledialog, ACTIVE, LEFT,
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
        super(PreferencesDialog, self).__init__(parent, title)
        self.values = values


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

        box.pack()

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

    def calculate(self, *args):
        try:
            value = float(self.feet.get())
            self.meters.set((0.3048 * value * 10000.0 + 0.5) / 10000.0)
        except ValueError:
            pass

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.feet = StringVar()
        self.meters = StringVar()

        self.entry_feet = Entry(self, width=7, textvariable=self.feet)
        self.entry_feet.grid(column=2, row=2, sticky=(W, E))

        self.lbl_meters = Label(self, textvariable=self.meters)
        self.lbl_meters.grid(column=2, row=3, sticky=(W, E))

        self.btn_calc = Button(self, text="Calculate", command=self.calculate)
        self.btn_calc.grid(column=3, row=4, sticky=W)

        self.lbl_feet = Label(self, text="feet")
        self.lbl_feet.grid(column=3, row=2, sticky=W)
        self.lbl_equiv = Label(self, text="is equivalent to")
        self.lbl_equiv.grid(column=1, row=3, sticky=E)
        self.lbl_meters2 = Label(self, text="meters")
        self.lbl_meters2.grid(column=3, row=3, sticky=W)
        self.footer_bar = Label(
            self, text="ready.", relief=SUNKEN, anchor="nw")
        self.footer_bar.grid(column=0, row=5, sticky=(E, W), columnspan=4,
                           padx=0, pady=0)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.entry_feet.focus()
        self.create_menubar()
        self.master.bind('<Return>', self.calculate)
        self.master.bind('<Control-q>', self.cmd_quit)
        self.master.title('WAeUP Identifier')
        self.pack()

    def cmd_file(self):
        return

    def cmd_quit(self, event=None):
        return self.master.quit()

    def cmd_about(self):
        messagebox.showinfo("About WAeUP Identifier",
                            "WAeUP Identifier, (c) 2014 WAeUP Germany")
        return

    def cmd_prefs(self):
        result = PreferencesDialog(
        # result = simpledialog.Dialog(
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
