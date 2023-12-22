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


class RootDialog(tkvue.Component):
    template = """
<TopLevel geometry="350x250" title="TKVue Test">
    <Frame pack-fill="both" pack-expand="true" padding="10">
        <Label text="Label with tooltip">
            <Tooltip text="Tooltip text for label" />
        </Label>

        <Button text="Button with tooltip">
            <Tooltip text="{{tooltip_value}}" />
        </Button>

        <Label text="Tooltip with width">
            <Tooltip width="50" text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum" />
        </Label>
    </Frame>
</TopLevel>
    """
    tooltip_value = tkvue.state("Tooltip value to be displayed")

    def __init__(self, master=None):
        super().__init__(master)
        s = ttk.Style(master=self.root)
        s.configure('tooltip.TLabel', background='#ffffe0')


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
