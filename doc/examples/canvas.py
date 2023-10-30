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

import tkvue


class RootDialog(tkvue.Component):
    template = """
<TopLevel geometry="450x450" title="TKVue Test">
    <Button text="Click Me" pack-expand="1" />
    <Canvas pack-fill="both" pack-expand="1"  bg="white">
        <CanvasText text="Hello" anchor="nw"/>
    </Canvas>
</TopLevel>
    """
    data = tkvue.Context(
        {
            "bg": os.path.normpath(os.path.join(__file__, '../bg.png')),
        }
    )


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()