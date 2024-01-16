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
<TopLevel title="TKVue Test" geometry="900x720">
    <Frame>
        <Spinbox textvariable="{{ scaling }}" />
    </Frame>
    <Frame id="preview">
        <Label text="Configuration" style="pixel.TLabel" pack-side="left"/>
        <Label text="Configuration" style="point.TLabel" pack-side="left"/>
    </Frame>
</TopLevel>
    """

    scaling = tkvue.state("")

    def __init__(self, master=None):
        super().__init__(master)
        self.scaling.value = self.root.tk.call('tk', 'scaling')
        s = ttk.Style(master=self.root)
        s.configure('pixel.TLabel', font=['TkDefaultFont', '-60'], background='#ffffff', padding=0)
        s.configure('point.TLabel', font=['TkDefaultFont', '60'], background='#ffffff', padding=0)

        self.scaling.subscribe(self._update_scaling)

    def _update_scaling(self, new_value):
        if new_value:
            self.root.tk.call('tk', 'scaling', new_value)
        self.preview.forget()
        self.preview.pack()

    @tkvue.command
    def _enabled_date(self, d):
        return d % 3


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
