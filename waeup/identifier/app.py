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
    N, W, S, E, StringVar, Frame, Button, Label, Entry, Menu,
    )


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

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.entry_feet.focus()
        self.create_menubar()
        self.master.bind('<Return>', self.calculate)
        self.pack()

    def cmd_file(self):
        print("CMD FILE clicked")

    def create_menubar(self):
        self.menubar = Menu(self)
        self.master['menu'] = self.menubar
        menu_file = Menu(self.menubar, tearoff=0)
        menu_file.add_command(label="My Cmd 1", command=self.cmd_file)
        menu_file.add_command(label="Quit", command=self.master.quit)
        self.menubar.add_cascade(label="File", menu=menu_file)
        self.master.config(menu=self.menubar)