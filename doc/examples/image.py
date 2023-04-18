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
import pkg_resources

import tkvue


class RootDialog(tkvue.Component):
    template = """
<TopLevel title="TKVue Test">
    <Frame pack-fill="both" pack-expand="1">
        <label text="compound none" />
        <Label id="label" text="gastonf" image="{{icon_path}}" compound="none"/>
        <label text="" />
        <label text="compound bottom" />
        <Label id="label" text="gastonf" image="{{icon_path}}" compound="bottom"/>
        <label text="" />
        <label text="compound top" />
        <Label id="label" text="gastonf" image="{{icon_path}}" compound="top"/>
        <label text="" />
        <label text="compound left" />
        <Label id="label" text="gastonf" image="{{icon_path}}" compound="left"/>
        <label text="" />
        <label text="compound right" />
        <Label id="label" text="gastonf" image="{{icon_path}}" compound="right"/>
        <label text="" />
        <label text="compound center" />
        <Label id="label" text="gastonf" image="{{icon_path}}" compound="center"/>
        <label text="" />
    </Frame>
</TopLevel>
    """
    data = tkvue.Context({"icon_path": pkg_resources.resource_filename(__name__, "python_icon.png")})


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
