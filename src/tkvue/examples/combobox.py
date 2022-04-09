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
<TopLevel title="TKVue Test">
    <Frame pack-fill="both" pack-expand="1" pack-padx="10" pack-pady="10">
        <Label text="Available values: " width="20" pack-side="left"/>
        <ComboBox id="label" pack-side="left" pack-expand="1" values="{{myvalues}}" textvariable="{{selected_value}}" />
    </Frame>
</TopLevel>
    """

    def __init__(self, master=None):
        self.data = tkvue.Context({"myvalues": ["zero", "one", "two", "three"], "selected_value": "one"})
        super().__init__(master)
        # We could register an observer to get notify when the value is updated
        self.data.watch('selected_value', self.on_value_changed)

    def on_value_changed(self, new_value):
        print('new value selected: ' + new_value)


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
