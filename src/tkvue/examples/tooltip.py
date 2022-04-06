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
import tkvue


class RootDialog(tkvue.Component):
    template = """
<TopLevel geometry="970x500" title="TKVue Test">
    <Frame pack-fill="both" pack-expand="true" padding="10">
        <Label text="Label with tooltip">
            <Tooltip text="Tooltip text for label" />
        </Label>

        <Button text="Button with tooltip">
            <Tooltip text="{{tooltip_value}}" />
        </Button>

        <Label text="Tooltip with width">
            <Tooltip wrap="1" width="50" text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum" />
        </Label>
    </Frame>
</TopLevel>
    """
    data = tkvue.Context({"tooltip_value": "Tooltip value to be displayed"})


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
