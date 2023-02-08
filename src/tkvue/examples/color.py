# Copyright (C) 2021 IKUS Software inc. All rights reserved.
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
<TopLevel title="TKVue Test" geometry="450x200">
    <Frame style="default.TFrame" pack-fill="both" pack-expand="1" padding="10">
        <Label text="Hello World !" style="H1.TLabel" pack-padx="25" pack-pady="25"/>
        <Frame style="default.TFrame" pack-fill="both" pack-expand="1" pack-padx="10" pack-pady="10">
            <Button style="default.TButton" text="Continue" pack-side="right" pack-padx="5"/>
            <Button style="default.TButton" text="Cancel" pack-side="right"/>
        </Frame>
    </Frame>
</TopLevel>
    """

    def __init__(self, master=None):
        super().__init__(master)
        s = ttk.Style(master=self.root)
        s.configure('H1.TLabel', font=['Lato', '-60'], background='#ffffff')
        s.configure('default.TFrame', background='#ffffff')
        s.configure(
            'default.TButton',
            foreground='#0E2933',
            background='#B6DDE2',
            bordercolor='#ACD1D6',
            darkcolor='#B6DDE2',
            lightcolor='#B6DDE2',
            focuscolor='#0E2933',
        )
        s.map(
            'default.TButton',
            background=[('disabled', '#E9F4F6'), ('hover !disabled', '#9ABBC0'), ('pressed !disabled', '#88A5A9')],
        )


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
