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

import asyncio

import tkvue


class RootDialog(tkvue.Component):
    template = """
<TopLevel geometry="250x250" title="TKVue Test">
    <Frame pack-fill="both" pack-expand="true" padding="10">
        <Progressbar orient="horizontal" mode="indeterminate" value="{{progress}}" pack-fill="x"/>
        <Progressbar orient="horizontal" mode="determinate"  value="{{progress}}" pack-fill="x"/>
    </Frame>
</TopLevel>
    """
    data = tkvue.Context(
        {
            "progress": 20,
        }
    )

    def __init__(self, master=None):
        super().__init__(master)
        self.root.after(1, lambda: asyncio.get_running_loop().create_task(self._update()))

    async def _update(self):
        while self.root.winfo_exists():
            self.data['progress'] = (self.data['progress'] + 1) % 100
            # Sleep 500ms
            await asyncio.sleep(0.05)


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
