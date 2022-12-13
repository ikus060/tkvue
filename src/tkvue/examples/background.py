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
<TopLevel geometry="970x970" title="TKVue Test">
    <Label image="{{ bg }}" place-x="0" place-y="0" place-relwidth="1" place-relheight="1" compound="top"/>
    <Checkbutton text="Show animation" />
</TopLevel>
    """
    data = tkvue.Context(
        {
            "bg": pkg_resources.resource_filename(__name__, "bg.png"),
        }
    )


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
