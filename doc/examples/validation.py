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
<TopLevel geometry="320x261" title="Modal" >
    <Frame side="top" fill="both" expand="1" padding="10 10">
        <Frame fill="x" padding="0 3">
            <Label text="User name:" side="left" width="15"/>
            <Entry textvariable="{{username}}" fill="x" side="left" />
        </Frame>
        <Frame fill="x" padding="0 3">
            <Label text="Password:" side="left" width="15" />
            <Entry textvariable="{{password}}" show="•" fill="x" side="left" />
        </Frame>
        <Label text="is valid" visible="{{valid}}" />
        <Frame side="bottom" anchor="se" padding="0 3">
            <Button text="OK" side="left" width="10" fill="both" padx="0 8" state="{{'disabled' if not valid else '!disabled'}}" />
            <Button text="Cancel" side="left" width="10" fill="both"/>
        </Frame>
    </Frame>
</TopLevel>
    """
    username = tkvue.state('')
    password = tkvue.state('')

    @tkvue.computed_property
    def valid(self):
        return self.username.value and self.password.value

    @tkvue.command
    def btn_clicked(self):
        print('Button clicked')


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
