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

import aiohttp
import pkg_resources

import tkvue


class RootDialog(tkvue.Component):
    template = """
<TopLevel geometry="970x970" title="TKVue Test">
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

    def __init__(self, *args, **kwargs):
        self.data = tkvue.Context(
            {
                "show": True,
                "icon_path": pkg_resources.resource_filename(__name__, "preloader.gif"),
                'checking_for_update': False,  # True when background thread is running.
                'is_latest': None,
                'check_latest_version_error': None,
            }
        )
        super().__init__(*args, **kwargs)
        self.root.after(3000, self._check_latest_version)

    def _check_latest_version(self):
        asyncio.get_running_loop().create_task(self._check_latest_version_task())

    async def _check_latest_version_task(self):
        self.data['checking_for_update'] = True
        self.data['is_latest'] = None
        self.data['check_latest_version_error'] = None

        # Query latest version.
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.ikus-soft.com/archive/minarca/latest_version') as response:
                    value = await response.text()
            self.data['is_latest'] = is_latest = bool(value)
            if not is_latest:
                # Show dialog
                pass
        except Exception as e:
            self.data['check_latest_version_error'] = str(e)
        finally:
            self.data['checking_for_update'] = False


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
