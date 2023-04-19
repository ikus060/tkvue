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


class ModalDialog(tkvue.Component):
    template = """
<TopLevel geometry="320x261" title="Modal" >
    <Frame pack-side="top" pack-fill="both" pack-expand="1" padding="10 10">

        <Label text="Enter user account information for running this tasks." padding="0 10 0 17" wrap="1" justify="left" pack-fill="x"/>

        <!-- Username -->
        <Frame pack-fill="x" padding="0 3">
            <Label text="User name:" pack-side="left" width="15"/>
            <Entry textvariable="{{username}}" pack-fill="x" pack-side="left" />
        </Frame>

        <!-- Password -->
        <Frame pack-fill="x" padding="0 3">
            <Label text="Password:" pack-side="left" width="15" />
            <Entry textvariable="{{password}}" show="•" pack-fill="x" pack-side="left" />
        </Frame>

        <!-- Buttons -->
        <Frame pack-side="bottom" pack-anchor="se" padding="0 3">
            <Button text="OK" pack-side="left" width="10" pack-fill="both" pack-padx="0 8" command="return_event" state="{{'disabled' if not password else '!disabled'}}" />
            <Button text="Cancel" pack-side="left" width="10" pack-fill="both" command="cancel_event"/>
        </Frame>
    </Frame>
</TopLevel>
    """

    def __init__(self, master=None):
        self.data = tkvue.Context({'username': '', 'password': ''})
        super().__init__(master)
        self.root.bind('<Return>', self.return_event)
        self.root.bind('<Key-Escape>', self.cancel_event)

    def return_event(self, event=None):
        # Quit this windows
        if self.data['password']:
            self.root.destroy()
        else:
            self.root.bell()

    def cancel_event(self, event=None):
        # Remove password value
        self.data['password'] = ''
        # Close this windows
        self.root.destroy()

    def modal(self):
        """
        Following tkinter documentation to make a TopLevel windows Modal.
        https://tkdocs.com/tutorial/windows.html#dialogs
        """
        self.root.protocol("WM_DELETE_WINDOW", self.cancel_event)  # intercept close button
        if self.root.master:
            self.root.transient(self.root.master)  # dialog window is related to main
            self.root.tk.eval('tk::PlaceWindow %s widget %s' % (self.root, self.root.master))
        self.root.wait_visibility()  # can't grab until window appears, so we wait
        self.root.grab_set()  # ensure all input goes to our window
        self.root.wait_window()  # block until window is destroyed


class RootDialog(tkvue.Component):
    template = """
<TopLevel geometry="322x261" title="TKVue Test" >
    <Frame pack-fill="both" pack-expand="true" padding="10" >
        <Button text="Show modal Dialog" command="show_modal" />
        <Label text="Modal dialog return value: " />
        <Label text="{{ returnvalue }}" />
    </Frame>
</TopLevel>
    """
    data = tkvue.Context({'returnvalue': ''})

    def __init__(self, master=None):
        super().__init__(master)
        self.root.tk.eval('tk::PlaceWindow %s pointer' % (self.root))

    def show_modal(self, event=None):
        dlg = ModalDialog(self.root)
        dlg.modal()
        self.data['returnvalue'] = dlg.data['password']


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
