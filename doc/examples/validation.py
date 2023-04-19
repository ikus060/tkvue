# Copyright (C) 2023 IKUS Software inc. All rights reserved.
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
<TopLevel geometry="320x261" title="Modal" >
    <Frame pack-side="top" pack-fill="both" pack-expand="1" padding="10 10">
        <Frame pack-fill="x" padding="0 3">
            <Label text="User name:" pack-side="left" width="15"/>
            <Entry textvariable="{{username}}" pack-fill="x" pack-side="left" />
        </Frame>
        <Frame pack-fill="x" padding="0 3">
            <Label text="Password:" pack-side="left" width="15" />
            <Entry textvariable="{{password}}" show="•" pack-fill="x" pack-side="left" />
        </Frame>
        <Frame pack-side="bottom" pack-anchor="se" padding="0 3">
            <Button text="OK" pack-side="left" width="10" pack-fill="both" pack-padx="0 8" state="{{'disabled' if not valid else '!disabled'}}" />
            <Button text="Cancel" pack-side="left" width="10" pack-fill="both"/>
        </Frame>
    </Frame>
</TopLevel>
    """
    data = tkvue.Context(
        {"username": "", "password": "", "valid": tkvue.computed(lambda data: data.username and data.password)}
    )

    def btn_clicked(self):
        print('Button clicked')


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
