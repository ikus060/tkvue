# Copyright (C) 2023 IKUS Software. All rights reserved.
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA
import os
import tkinter.ttk as ttk

import tkvue

tkvue.configure_tk(theme="clam")


class RootDialog(tkvue.Component):
    template = """
<TopLevel title="TKVue example" geometry="500x500">
    <label text="Using grid geometry manager it's possible to create complex interface" padding="10"/>
    <Frame fill="both" expand="1" columnconfigure-weight="1 1" rowconfigure-weight="1 1">
        <Button text="sticky=we" column=0 row=0 sticky="we"/>
        <Button text="sticky=nw" column=1 row=0 sticky="nw"/>
        <Button text="c" column=0 row=1 />
        <Button text="sticky=nsew" column=1 row=1 sticky="nsew"/>
    </Frame>
</TopLevel>
    """
    icon_path = tkvue.state(os.path.normpath(os.path.join(__file__, '../python_icon.png')))

    def __init__(self, master=None):
        super().__init__(master)
        s = ttk.Style(master=self.root)
        # This make the button blue.
        s.configure(
            'TButton',
            foreground='#ffffff',
            background='#0f62fe',
            bordercolor='#0f62fe',
            darkcolor='#0f62fe',
            lightcolor='#0f62fe',
        )
        s.map(
            'TButton',
            background=[('disabled', '#525252'), ('hover !disabled', '#0353e9'), ('pressed !disabled', '#002d9c')],
        )


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
