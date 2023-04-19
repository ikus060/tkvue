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
<TopLevel geometry="322x261" title="TKVue Test" theme="{{theme}}">
    <Frame pack-fill="both" pack-expand="true" padding="10" >
        <Button text="Switch to Clam Theme" command="set_clam" />
    </Frame>
    <Frame pack-fill="both" pack-expand="true" padding="10">
        <Button text="Switch to Alt Theme" command="set_alt" />
    </Frame>
    <Frame pack-fill="both" pack-expand="true" padding="10">
        <Button text="Switch to Default Theme" command="set_default" />
    </Frame>
</TopLevel>
    """
    data = tkvue.Context({'theme': 'clam'})

    def set_clam(self, event=None):
        self.data['theme'] = 'clam'

    def set_alt(self, event=None):
        self.data['theme'] = 'alt'

    def set_default(self, event=None):
        self.data['theme'] = 'default'


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
