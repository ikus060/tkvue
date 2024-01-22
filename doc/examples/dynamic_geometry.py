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
<TopLevel title="TKVue Test" geometry="{{ '%sx%s' % (win_width, win_height) }}" >
    <Frame pack="fill:both; expand:1; padx:10; pady:10">
        <Frame pack="fill:x" padding="0 3">
            <Label text="Height:" pack="side:left" width="10"/>
            <Scale variable="{{win_height}}" from="100" to="800" pack="fill:x; side:left;" />
        </Frame>

        <Frame pack="fill:x" padding="0 3">
            <Label text="Width:" pack="side:left" width="10" />
            <Scale variable="{{win_width}}" from="200" to="800" pack="fill:x; side:left;" />
        </Frame>
    </Frame>
</TopLevel>
    """
    win_width = tkvue.state(200)
    win_height = tkvue.state(100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


dlg = RootDialog()
dlg.mainloop()
