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
        <Label text="Static text on top of scrollable" />
        <ScrolledFrame pack-fill="both" pack-expand="1" pack-side="left">
            <Label pack-fill="x" pack-expand="1" for="i in range(1,100)" text="{{ 'left %s' % i }}" />
        </ScrolledFrame>
        <ScrolledFrame pack-fill="both" pack-expand="1" pack-side="right">
            <Label pack-fill="x" pack-expand="1" for="i in range(1,5)" text="{{ 'right %s' % i }}" />
        </ScrolledFrame>
    </Frame>
</TopLevel>


    """
    data = tkvue.Context({})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
