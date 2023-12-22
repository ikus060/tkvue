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
import tkinter.ttk as ttk

import tkvue

tkvue.configure_tk(theme="clam")


class RootDialog(tkvue.Component):
    template = """
<TopLevel title="TKVue example" geometry="500x500">
    <label text="Using pack geometry manager it's possible to control widgets position and size" padding="10"/>
    <Frame pack-fill="x">
        <label text="Fixed size using width=" />
        <Button text="width=45" style="left.TButton" pack-pady="0 15" width="45"/>
    </Frame>

    <Frame pack-fill="x" >
        <label text="Stacked on the left" />
        <Button text="pack-side=left" pack-pady="0 15" pack-padx="0 5" pack-side="left"/>
        <Button text="pack-side=left" pack-pady="0 15" pack-padx="0 5" pack-side="left"/>
        <Button text="pack-side=left" pack-pady="0 15" pack-padx="0 5" pack-side="left"/>
    </Frame>

    <Frame pack-fill="both" pack-expand="1">
        <label text="Take all vertical space" />
        <Button text="pack-fill=x" pack-pady="0 15" pack-fill="x"/>

        <label text="Take all horizontal space" />
        <Button text="pack-fill=y pack-expand=1" pack-pady="0 15" pack-fill="y"  pack-expand="1"/>

        <label text="Take all vertical & horizontal space" />
        <Button text="pack-fill=both pack-expand=1" pack-pady="0 15" pack-fill="both"  pack-expand="1"/>

    </Frame>
</TopLevel>
    """

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
