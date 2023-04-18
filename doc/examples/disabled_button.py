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
<TopLevel title="TKVue Test">
    <Frame pack-fill="both" pack-expand="1" pack-padx="10" pack-pady="10">
        <Checkbutton variable="{{btn_disabled}}" text="Disable button" />
        <Button text="Click Me" command="btn_clicked" state="{{'disabled' if btn_disabled else '!disabled'}}"/>
    </Frame>
</TopLevel>
    """
    data = tkvue.Context({"btn_disabled": False})

    def btn_clicked(self):
        print('Button clicked')


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
