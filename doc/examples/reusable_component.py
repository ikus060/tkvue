# Copyright (C) 2023 IKUS Software inc. All rights reserved.
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


class ErrorFrame(tkvue.Component):
    template = """
<Frame style="error.TFrame" pack-fill="x" pack-expand="1" padding="4 1 1 1">
    <Frame style="default.TFrame" pack-fill="x" pack-expand="1" padding="10">
        <Label style="default.TLabel" text="{{text}}" pack-side="left"/>
        <Label style="default.TLabel" text="{{subtext}}" pack-side="left" />
    </Frame>
</Frame>
"""

    def __init__(self, master=None):
        self.data = tkvue.Context({"text": "Error notification", "subtext": "Subtitle text goes here."})
        super().__init__(master)

    def configure(self, cnf=None, **kw):
        if 'text' in kw:
            self.data.text = kw.pop('text')
        if 'subtext' in kw:
            self.data.subtext = kw.pop('subtext')


class RootDialog(tkvue.Component):
    template = """
<TopLevel title="TKVue Test" geometry="450x350" >
    <Frame style="default.TFrame" pack-fill="both" pack-expand="1" padding="25">

        <ErrorFrame subtext="This is the first error message."/>

        <ErrorFrame subtext="This is a second error message."/>

    </Frame>
</TopLevel>
    """
    data = tkvue.Context({"win_width": 150, "win_height": 150})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        s = ttk.Style(master=self.root)
        s.configure('default.TLabel', background='#161616', foreground='#ffffff')
        s.configure('default.TFrame', background='#161616')
        s.configure('error.TFrame', background='#fa4d56')


dlg = RootDialog()
dlg.mainloop()
