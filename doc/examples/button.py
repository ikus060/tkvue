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

import pkg_resources

import tkvue

tkvue.configure_tk(theme="clam")


class RootDialog(tkvue.Component):
    template = """
<TopLevel title="TKVue Test">
<label text="With TTK Widgets, you may need to create several styles to customize the appearance of the buttons." padding="10"/>
    <Frame pack-fill="both" pack-expand="1" pack-side="left">
        <label text="Default button" />
        <Button id="label" text="Click Me" pack-pady="0 15"/>

        <label text="style=left.TButton" />
        <Button id="label" text="Click Me" style="left.TButton" pack-pady="0 15"/>

        <label text="style=right.TButton" />
        <Button id="label" text="Click Me" style="right.TButton" pack-pady="0 15"/>

        <label text="style=blue.TButton" />
        <Button id="label" text="Click Me" style="blue.TButton" pack-pady="0 15"/>

        <label text="style=blue.TButton compound=right" />
        <Button id="label" text="Click Me" style="blue.TButton" image="{{icon_path}}" compound="right" pack-pady="0 15"/>

    </Frame>
    <Frame pack-fill="both" pack-expand="1" pack-side="left">
        <label text="compound=none" />
        <Button id="label" text="Click Me" image="{{icon_path}}" compound="none" pack-pady="0 15"/>
        
        <label text="compound=bottom" />
        <Button id="label" text="Click Me" image="{{icon_path}}" compound="bottom" pack-pady="0 15"/>
        
        <label text="compound=top" />
        <Button id="label" text="Click Me" image="{{icon_path}}" compound="top" pack-pady="0 15"/>
        
        <label text="compound=left" />
        <Button id="label" text="Click Me" image="{{icon_path}}" compound="left" pack-pady="0 15"/>
        
        <label text="compound=right" />
        <Button id="label" text="Click Me" image="{{icon_path}}" compound="right" pack-pady="0 15"/>
        
        <label text="compound=center" />
        <Button id="label" text="Click Me" image="{{icon_path}}" compound="center" pack-pady="0 15"/>
        
    </Frame>
</TopLevel>
    """
    data = tkvue.Context({"icon_path": pkg_resources.resource_filename(__name__, "python_icon.png")})

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
