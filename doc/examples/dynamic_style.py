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
<TopLevel title="TKVue Test">
    <Frame pack-fill="both" pack-expand="1" pack-side="left">
        <label text="Click button to change style" />
        <Button id="label" text="Click Me" pack-pady="0 15" style="{{'blue.TButton' if is_blue else 'TButton'}}" command="_toggle_style"/>
    </Frame>
</TopLevel>
    """

    is_blue = tkvue.state(False)

    def __init__(self, master=None):
        super().__init__(master)
        s = ttk.Style(master=self.root)
        # This make the button blue.
        s.configure(
            'blue.TButton',
            foreground='#ffffff',
            background='#0f62fe',
            bordercolor='#0f62fe',
            darkcolor='#0f62fe',
            lightcolor='#0f62fe',
            focuscolor='#ffffff',
            focusthickness=3,
            padding=10,
            anchor="w",
            justify="centered",
        )
        s.map(
            'blue.TButton',
            background=[('disabled', '#525252'), ('hover !disabled', '#0353e9'), ('pressed !disabled', '#002d9c')],
        )

    @tkvue.command
    def _toggle_style(self):
        self.is_blue.value = not self.is_blue.value


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
