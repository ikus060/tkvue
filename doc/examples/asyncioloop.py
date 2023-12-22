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

import os
from importlib.metadata import version

import aiohttp

import tkvue


class RootDialog(tkvue.Component):
    template = """
<TopLevel geometry="450x450" title="TKVue Test">
    <Frame pack-fill="both" pack-expand="true" padding="10">
        <Checkbutton text="Show animation" variable="{{show}}" />
        <Label image="{{icon_path}}" visible="{{show}}" background="#ffffff" />
    </Frame>
    <Frame>
        <Button id="check_latest_version_button" text="Check now" command="_check_latest_version" pack-side="right"
                pack-pady="5" />
        <Label text="Checking for updates..." compound="left" visible="{{checking_for_update}}"
            anchor="e" pack-fill="x" />
        <Label text="Current version is up-to-date" style="success.TLabel" compound="left"
            visible="{{is_latest is True}}" anchor="e" pack-fill="x" />
        <Label text="Update available" style="info.TLabel" compound="left"
            visible="{{is_latest is False}}" anchor="e" pack-fill="x" />
        <Label text="Cannot check for updates. Try again later." style="danger.TLabel" compound="left"
            visible="{{check_latest_version_error is not None}}" anchor="e" pack-fill="x">
            <Tooltip text="{{check_latest_version_error}}" width="50" />
        </Label>
    </Frame>
</TopLevel>
    """
    show = tkvue.state(True)
    icon_path = tkvue.state(os.path.normpath(os.path.join(__file__, '../dots.gif')))
    checking_for_update = tkvue.state(False)  # True when background thread is running.
    is_latest = tkvue.state(None)
    check_latest_version_error = tkvue.state(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root.after(3000, self._check_latest_version)

    @tkvue.command
    def _check_latest_version(self):
        self.loop.create_task(self._check_latest_version_task())

    async def _check_latest_version_task(self):
        self.checking_for_update.value = True
        self.is_latest.value = None
        self.check_latest_version_error.value = None

        # Query latest version.
        try:
            tkvue_cur_version = version("tkvue")
            async with aiohttp.ClientSession() as session:
                async with session.get('https://pypi.org/pypi/tkvue/json') as response:
                    data = await response.json()
            latest_version = data.get('info', {}).get('version', None)
            self.is_latest.value = is_latest = latest_version == tkvue_cur_version
            if not is_latest:
                # Show dialog
                pass
        except Exception as e:
            self.check_latest_version_error.value = str(e)
        finally:
            self.checking_for_update.value = False


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
