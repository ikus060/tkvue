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
import tkvue


class RootDialog(tkvue.Component):
    template = """
<TopLevel title="TKVue Test">
    <Frame pack-fill="both" pack-expand="true" padding="10">
        <Checkbutton text="Show Text using 'pack' geometry" variable="{{show_pack}}" />
        <Label text="Text is Visible" visible="{{show_pack}}" />
    </Frame>
    <Frame pack-fill="both" pack-expand="true" padding="10">
        <Checkbutton text="Show Text using 'grid' geometry" variable="{{show_grid}}" grid-column="0" grid-row="0"/>
        <Label text="Text is Visible" visible="{{show_grid}}" grid-column="0" grid-row="1"/>
    </Frame>
</TopLevel>
    """
    show_pack = tkvue.state(True)
    show_grid = tkvue.state(True)


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
