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
<TopLevel title="TKVue Test">
<label text="With TTK Widgets, you may need to create several styles to customize the appearance of the buttons." padding="10"/>
    <Frame fill="both" expand="1" side="left">
        <label text="Default button" />
        <Button text="Click Me" pady="0 15"/>

        <label text="style=left.TButton" />
        <Button text="Click Me" style="left.TButton" pady="0 15"/>

        <label text="style=right.TButton" />
        <Button text="Click Me" style="right.TButton" pady="0 15"/>

        <label text="style=blue.TButton" />
        <Button text="Click Me" style="blue.TButton" pady="0 15"/>

        <label text="style=blue.TButton compound=right" />
        <Button text="Click Me" style="blue.TButton" image="{{icon_path}}" compound="right" pady="0 15"/>

    </Frame>
    <Frame fill="both" expand="1" side="left">
        <label text="compound=none" />
        <Button text="Click Me" image="{{icon_path}}" compound="none" pady="0 15"/>
        <label text="compound=bottom" />
        <Button text="Click Me" image="{{icon_path}}" compound="bottom" pady="0 15"/>
        <label text="compound=top" />
        <Button text="Click Me" image="{{icon_path}}" compound="top" pady="0 15"/>
        <label text="compound=left" />
        <Button text="Click Me" image="{{icon_path}}" compound="left" pady="0 15"/>
        <label text="compound=right" />
        <Button text="Click Me" image="{{icon_path}}" compound="right" pady="0 15"/>
        <label text="compound=center" />
        <Button text="Click Me" image="{{icon_path}}" compound="center" pady="0 15"/>
    </Frame>
</TopLevel>
    """
    icon_path = tkvue.state(os.path.normpath(os.path.join(__file__, '../python_icon.png')))

    def __init__(self, master=None):
        super().__init__(master)
        s = ttk.Style(master=self.root)
        s.map('left.TButton', anchor='w')
        s.map('right.TButton', anchor='e')
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


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
