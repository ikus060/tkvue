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
import sys
import tkinter
import tkinter.ttk as ttk
import unittest
from contextlib import contextmanager

import pkg_resources

import tkvue

NO_DISPLAY = not os.environ.get("DISPLAY", False)
IS_LINUX = sys.platform in ["linux", "linux2"]
IS_MAC = sys.platform == "darwin"
IS_WINDOWS = os.name == "nt"


@contextmanager
def new_dialog(cls):
    def pump_events():
        while dlg.root.dooneevent(tkinter._tkinter.ALL_EVENTS | tkinter._tkinter.DONT_WAIT):
            pass

    dlg = cls()
    dlg.pump_events = pump_events
    try:
        yield dlg
    finally:
        dlg.pump_events()
        dlg.destroy()
        dlg.pump_events()


class DataTest(unittest.TestCase):
    def setUp(self):
        self.last_value = None
        return super().setUp()

    def callback(self, value):
        self.last_value = value

    def test_get_set_variable(self):
        data = tkvue.Context({"var1": "foo"})
        data.var1 = "bar"
        self.assertEqual(data.var1, "bar")
        data.set("var1", "rat")
        self.assertEqual(data.var1, "rat")

    def test_get_computed(self):
        data = tkvue.Context(
            {
                "var1": 1,
                "var2": 2,
                "sum": tkvue.computed(lambda store: store.var1 + store.var2),
            }
        )
        self.assertEqual(data.sum, 3)

    def test_watch_with_variable(self):
        data = tkvue.Context({"var1": "foo"})
        data.watch("var1", self.callback)
        data.var1 = "bar"
        self.assertEqual(self.last_value, "bar")

    def test_watch_with_computed(self):
        data = tkvue.Context(
            {
                "var1": 1,
                "var2": 2,
                "sum": tkvue.computed(lambda store: store.var1 + store.var2),
            }
        )
        data.watch("sum", self.callback)
        data.var1 = 4
        self.assertEqual(self.last_value, 6)

    def test_watch_list(self):
        data = tkvue.Context(
            {"var1": [1, 2, 3, 4]},
        )
        data.watch("var1", self.callback)
        data.var1 = [1, 2, 3]
        self.assertEqual(self.last_value, [1, 2, 3])

    def test_unwatch(self):
        data = tkvue.Context(
            {"var1": "foo"},
        )
        data.watch("var1", self.callback)
        data.var1 = "bar"
        self.assertEqual(self.last_value, "bar")
        data.unwatch("var1", self.callback)
        data.var1 = "foo"
        self.assertEqual(self.last_value, "bar")

    def test_eval(self):
        data = tkvue.Context(
            {"var1": [1, 2, 3, 4]},
        )
        self.assertEqual(2, data.eval("var1[1]"))

    def test_watch_list_item(self):
        data = tkvue.Context(
            {"var1": [1, 2, 3, 4]},
        )
        data.watch("var1[1]", self.callback)
        data.var1 = [1, 2, 3]
        self.assertEqual(self.last_value, 2)

    def test_new_child(self):
        data = tkvue.Context(
            {"var1": [1, 2, 3, 4]},
        )
        data2 = data.new_child(item=tkvue.computed(lambda self: self.var1[3]))
        # Item doesn't exists in data
        with self.assertRaises(KeyError):
            data.item
        # Item is equals to var[3] in data2
        self.assertEqual(data2.item, 4)
        # Call to function also work.
        data2.eval("callback(item)", callback=self.callback)
        self.assertEqual(self.last_value, 4)

    def test_new_child_watch(self):
        # Given a parent context with a list
        data = tkvue.Context(
            {"var1": [1, 2, 3, 4]},
        )
        # Given a child context with computed value on parent
        child = data.new_child(item=tkvue.computed(lambda self: self.var1[1]))
        self.assertEqual(child.item, 2)
        # Given a watcher on computed value
        child.watch("item", self.callback)
        # When updating the parent
        data.var1 = [2, 3, 4]
        # Then the watcher get called.
        self.assertEqual(self.last_value, 3)

    def test_new_child_unwatch(self):
        # Given a parent context
        data = tkvue.Context(
            {"var1": "foo"},
        )
        # Given a child context with computed value on parent
        child = data.new_child(item=tkvue.computed(lambda self: self.var1 + "bar"))
        self.assertEqual(child.item, "foobar")
        # Given a watcher on computed value
        child.watch("item", self.callback)
        data.var1 = "bar"
        self.assertEqual(self.last_value, "barbar")
        # When removing watcher
        child.unwatch("item", self.callback)
        # Then updating the parent doesn't notify anymore
        data.var1 = "rat"
        self.assertEqual(self.last_value, "barbar")

    def test_setter_child(self):
        # Given a parent context
        data = tkvue.Context(
            {"var1": "foo"},
        )
        # Given a child context
        child = data.new_child()
        # When setting a value on the child context.
        child.var1 = "bar"
        # Then the value is update into the parent context.
        self.assertEqual(data.var1, "bar")

    def test_computed_dependencies_updated(self):
        # Given a parent context
        data = tkvue.Context(
            {"var1": True, "var2": True},
        )
        # Given a watching on both variables.
        data.watch("var1 or var2", self.callback)
        # When setting a value on the child context.
        data.var1 = False
        data.var2 = False
        # Then the value is update into the parent context.
        self.assertEqual(self.last_value, False)


class CustomComponent(tkvue.Component):
    template = """
    <Frame pack-fill="x" pack-expand="1">
        <Label text="tet in component" />
    </Frame>
    """


class Dialog(tkvue.Component):
    template = """
    <TopLevel geometry="500x500" title="My Dialog">
        <Frame pack-fill="x" pack-expand="1">
            <!-- Single and dual binding -->
            <Entry id="entry" textvariable="{{text_value}}" />
            <label id="label" text="{{text_value}}" />
        </Frame>
        <Frame pack-fill="x" pack-expand="1">
            <Button id="button" visible="{{button_visible}}" text="Visible" />
        </Frame>
        <Frame id="people" pack-fill="x" pack-expand="1">
            <Label for="i in names" text="{{i}}" />
        </Frame>
        <Frame pack-fill="x" pack-expand="1">
            <Radiobutton id="blue" variable="{{selected_color}}" value="blue" text="blue"/>
            <Radiobutton id="red" variable="{{selected_color}}" value="red" text="red"/>
            <Radiobutton id="green" variable="{{selected_color}}" value="green" text="green"/>
            <Combobox id="combo" textvariable="{{selected_color}}" values="blue red green" />
        </Frame>
        <Frame pack-fill="x" pack-expand="1">
            <Radiobutton id="one" variable="{{selected_number}}" value="1" text="1"/>
            <Radiobutton id="two" variable="{{selected_number}}" value="2" text="2"/>
            <Radiobutton id="three" variable="{{selected_number}}" value="3" text="3"/>
        </Frame>
        <Frame pack-fill="x" pack-expand="1">
            <Checkbutton id="checkbutton" text="foo" selected="{{checkbutton_selected}}" command="checkbutton_invoke"/>
            <Checkbutton id="checkbutton2" text="foo" variable="{{checkbutton_selected}}"/>
            <Checkbutton id="checkbutton3" text="foo" selected="{{checkbutton_selected}}" command="funcation_call_with_args('arg1')"/>
        </Frame>
        <CustomComponent></CustomComponent>
    </TopLevel>
    """

    def __init__(self, master=None):
        self.data = tkvue.Context(
            {
                "text_value": "foo",
                "button_visible": True,
                "names": ["patrik", "annik", "michel", "denise"],
                "selected_color": "blue",
                "selected_number": 1,
                "checkbutton_selected": True,
            }
        )
        super().__init__(master=master)

    def checkbutton_invoke(self):
        self.data.checkbutton_selected = not self.data.checkbutton_selected

    def funcation_call_with_args(self, value):
        self.value = value


class DialogWithImage(tkvue.Component):
    template = """
    <TopLevel>
        <Button id="button" text="Button with image" image="{{image_path}}" compound="left"/>
        <Label id="label" text="Label with image" image="{{image_path}}" compound="left"/>
    </TopLevel>
    """

    def __init__(self, master=None):
        self.data = tkvue.Context({"image_path": None})
        super().__init__(master=master)


class DialogWithTextWrap(tkvue.Component):
    template = """
    <TopLevel>
        <Label id="label1" text="Text with wrapping" wrap="0" width="5"/>
        <Label id="label2" text="Text with wrapping" wrap="1" width="5"/>
    </TopLevel>
    """


class DialogWithTooltip(tkvue.Component):
    template = """
    <TopLevel>
        <Label id="label1" text="Label with tooltip">
            <Tooltip id="tooltip" text="This is a tooltip" />
        </Label>
    </TopLevel>
    """


class DialogWithLoop(tkvue.Component):
    template = """
    <TopLevel>
        <Label id="label1" text="{{item}}" for="item in items"/>
    </TopLevel>
    """

    def __init__(self, master=None):
        self.data = tkvue.Context({"items": []})
        super().__init__(master=master)


class DialogWithScrolledFrame(tkvue.Component):
    template = """
    <TopLevel geometry="500x500">
        <ScrolledFrame id="scrolled_frame" pack-fill="both" pack-expand="1">
            <Frame for="item in range(1,10)" pack-fill="x"  pack-expand="1">
                <Label id="label1" pack-fill="x" pack-expand="1" text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. " wrap="1"/>
            </Frame>
        </ScrolledFrame>
    </TopLevel>
    """


class DialogWithInvalidCommand(tkvue.Component):
    template = """
    <Frame>
        <Checkbutton id="checkbutton" text="foo" selected="True" command="invalid_command"/>
    </Frame>
    """


class DialogWithBindingCommand(tkvue.Component):
    template = """
    <Frame>
        <Checkbutton id="checkbutton" text="foo" selected="True" command="{{my_command}}"/>
    </Frame>
    """

    def my_command(self):
        pass


class DialogNotResizable(tkvue.Component):
    template = """
    <TopLevel geometry="322x261" resizable="False False">
        <ScrolledFrame id="scrolled_frame">
            <Label id="label1" text="{{item}}" for="item in range(1,25)"/>
        </ScrolledFrame>
    </TopLevel>
    """


class DialogWithTheme(tkvue.Component):
    template = """
    <TopLevel theme="{{ theme_value }}">
        <Button text="Push button" />
    </TopLevel>
    """

    def __init__(self, master=None):
        self.data = tkvue.Context({"theme_value": 'alt'})
        super().__init__(master=master)


@unittest.skipIf(IS_LINUX and NO_DISPLAY, "cannot run this without display")
class ComponentTest(unittest.TestCase):
    def test_open_close(self):
        # Given a dialog with a geometry and a title
        with new_dialog(Dialog) as dlg:
            # When opening the dialog
            dlg.pump_events()
            # Then dialog has the right geometry
            self.assertRegex(dlg.root.winfo_geometry(), '^500x500.*')
            # Then the dialog has a title
            self.assertEqual('My Dialog', dlg.root.title())
            # Then the dialog has the default class
            self.assertEqual('Tkvue', dlg.root.winfo_class())

    def test_simple_binding(self):
        # Given a dialog with a simple binding
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            self.assertEqual("foo", dlg.label.cget("text"))
            # When updating the value of the context
            dlg.data.text_value = "bar"
            # Then the widget get updated
            self.assertEqual("bar", dlg.label.cget("text"))

    @unittest.skipIf(IS_WINDOWS, "fail to reliably force focus on windows")
    def test_dual_binding(self):
        # Given a dialog with a simple binding
        with new_dialog(Dialog) as dlg:
            dlg.root.lift()
            dlg.pump_events()
            self.assertEqual("foo", dlg.label.cget("text"))
            self.assertEqual("foo", dlg.entry.getvar(dlg.entry.cget("text")))
            # Given the root windows has focus.
            dlg.root.focus_force()
            dlg.pump_events()
            self.assertEqual(dlg.root.focus_get(), dlg.root)
            # When typing into the entry field
            dlg.entry.focus_set()
            dlg.entry.event_generate("<i>")
            dlg.pump_events()
            # Then the store get updated
            self.assertEqual("ifoo", dlg.data.text_value)
            self.assertEqual("ifoo", dlg.label.cget("text"))
            self.assertEqual("ifoo", dlg.entry.getvar(dlg.entry.cget("text")))

    @unittest.skipIf(IS_WINDOWS, "fail to reliably make this test work in CICD")
    def test_visible(self):
        # Given a dialog with a simple binding
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            self.assertTrue(dlg.button.winfo_ismapped())
            # When typing into the entry field
            dlg.data.button_visible = False
            dlg.pump_events()
            # Then the store get updated
            self.assertFalse(dlg.button.winfo_ismapped())

    def test_for_loop(self):
        # Given a dialog with a for loop
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            self.assertEqual(4, len(dlg.people.winfo_children()))
            # When Adding element to the list
            dlg.data.names = ["patrik", "annik"]
            dlg.pump_events()
            # Then the dialog get updated
            self.assertEqual(2, len(dlg.people.winfo_children()))

    def test_dual_binding_select_text(self):
        # Given a dialog with a for loop
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            # When selecting an item with radio
            dlg.red.invoke()
            dlg.pump_events()
            # Then radio button get updated
            self.assertEqual("red", dlg.data.selected_color)

    def test_dual_binding_select_number(self):
        # Given a dialog with a for loop
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            # When selecting an item with radio
            dlg.three.invoke()
            dlg.pump_events()
            # Then radio button get updated
            self.assertEqual(3, dlg.data.selected_number)

    @unittest.skipIf(IS_MAC, "this fail on MacOS when running in test suite")
    def test_checkbutton_selected(self):
        # Given a dialog with checkbutton binded with `selected` attribute
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            self.assertEqual(dlg.checkbutton.state(), ("selected",))
            self.assertEqual(dlg.checkbutton2.state(), ("selected",))
            # When updating checkbutton_selected value
            dlg.data.checkbutton_selected = False
            dlg.pump_events()
            # Then the widget get updated
            self.assertEqual(dlg.checkbutton.state(), tuple())
            self.assertEqual(dlg.checkbutton2.state(), tuple())

    @unittest.skipIf(IS_MAC, "this fail on MacOS when running in test suite")
    def test_checkbutton_selected_command(self):
        # Given a dialog with checkbutton binded with `selected` attribute
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            self.assertEqual(dlg.checkbutton.state(), ("selected",))
            self.assertEqual(dlg.checkbutton2.state(), ("selected",))
            # When cliking on checkbutton
            dlg.checkbutton.focus_set()
            dlg.checkbutton.invoke()
            dlg.root.focus_set()
            dlg.pump_events()
            # Then the widget status get toggled.
            self.assertEqual(dlg.data.checkbutton_selected, False)
            self.assertEqual(dlg.checkbutton.state(), tuple())
            self.assertEqual(dlg.checkbutton2.state(), tuple())
            # When cliking on checkbutton again
            dlg.checkbutton.focus_set()
            dlg.checkbutton.invoke()
            dlg.root.focus_set()
            dlg.pump_events()
            # Then the widget status get toggled.
            self.assertEqual(dlg.data.checkbutton_selected, True)
            self.assertEqual(dlg.checkbutton.state(), ("selected",))
            self.assertEqual(dlg.checkbutton2.state(), ("selected",))

    def test_image_path(self):
        with new_dialog(DialogWithImage) as dlg:
            # Given a dialog with image
            self.assertEqual("", dlg.button.cget("image"))
            self.assertEqual("", dlg.label.cget("image"))
            # When settings image_path
            dlg.data["image_path"] = pkg_resources.resource_filename(__name__, "python_icon.png")
            # Then Button and Label get update with an image
            self.assertTrue(dlg.button.cget("image")[0].startswith("pyimage"))
            self.assertTrue(dlg.label.cget("image")[0].startswith("pyimage"))

    def test_image_path_with_gif(self):
        with new_dialog(DialogWithImage) as dlg:
            # Given a dialog with image
            self.assertEqual("", dlg.button.cget("image"))
            self.assertEqual("", dlg.label.cget("image"))
            # When settings image_path
            dlg.data["image_path"] = pkg_resources.resource_filename(__name__, "preloader.gif")
            # Then Button and Label get update with an image
            self.assertTrue(dlg.button.cget("image")[0].startswith("pyimage"))
            self.assertTrue(dlg.label.cget("image")[0].startswith("pyimage"))
            # Then set image to None
            dlg.data["image_path"] = ''

    @unittest.skipIf(IS_WINDOWS, "Not working on Windows CICD")
    def test_text_wrap(self):
        # Given a dialog with text wrap enabled
        with new_dialog(DialogWithTextWrap) as dlg:
            dlg.pump_events()
            # Then label2 text is displayed on multiple line.
            self.assertGreater(dlg.label2.winfo_height(), dlg.label1.winfo_height() * 2)

    def test_tooltip(self):
        # Given a dialog with tooltip
        with new_dialog(DialogWithTooltip) as dlg:
            dlg.pump_events()
            # When forcing tooltip display
            dlg.tooltip.showtip()
            dlg.pump_events()
            # Then tooltip get displayed
            self.assertTrue(dlg.tooltip.tipwindow)
            # When hiding tooltip
            dlg.tooltip.hidetip()
            dlg.pump_events()
            # Then tooltip get hide
            self.assertFalse(dlg.tooltip.tipwindow)

    def test_loop(self):
        # Given a dial with loop
        with new_dialog(DialogWithLoop) as dlg:
            dlg.pump_events()
            self.assertEqual(0, len(dlg.winfo_children()))
            # When updating the items
            dlg.data["items"] = [1, 2, 3, 4]
            dlg.pump_events()
            # Then widget get created
            self.assertEqual(4, len(dlg.winfo_children()))

    def test_loop_removing_items(self):
        # Given a dial with loop
        with new_dialog(DialogWithLoop) as dlg:
            dlg.data["items"] = [1, 2, 3, 4]
            dlg.pump_events()
            self.assertEqual(4, len(dlg.winfo_children()))
            # When removing items
            dlg.data["items"] = [3, 4]
            dlg.pump_events()
            # Then widget get created
            self.assertEqual(2, len(dlg.winfo_children()))

    def test_scrolled_frame(self):
        with new_dialog(DialogWithScrolledFrame) as dlg:
            dlg.pump_events()

    @unittest.skipUnless(IS_LINUX, "fail randomly on Windows and MacOS due to race condition")
    def test_scrolled_frame_resize(self):
        with new_dialog(DialogWithScrolledFrame) as dlg:
            dlg.pump_events()
            # Make sure scrollable is working
            self.assertTrue(dlg.scrolled_frame.vscrollbar.winfo_ismapped())
            # When dialog is resize
            dlg.geometry('800x800')
            dlg.pump_events()
            # Then scrollbar is removed
            self.assertFalse(dlg.scrolled_frame.vscrollbar.winfo_ismapped())

    def test_command_invalid(self):
        # Given a dialog with an invalid command name
        # When trying to create the dialog
        # Then an exception is raised
        with self.assertRaises(tkvue.TemplateError) as ctx:
            with new_dialog(DialogWithInvalidCommand) as dlg:
                dlg.pump_events()
        self.assertIn('command', str(ctx.exception))

    def test_command_with_binding(self):
        # Given a dialog with an invalid binding
        # When trying to create the dialog
        # Then an exception is raised
        with self.assertRaises(tkvue.TemplateError) as ctx:
            with new_dialog(DialogWithBindingCommand) as dlg:
                dlg.pump_events()
        self.assertIn('command', str(ctx.exception))

    def test_command_with_arguments(self):
        # Given a dialog with a command with arguments
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            # When invoking the check button
            dlg.checkbutton3.focus_set()
            dlg.checkbutton3.invoke()
            dlg.pump_events()
            # Then function get called
            self.assertEqual('arg1', dlg.value)

    def test_mainloop(self):
        # Given a dialog
        dlg = Dialog()
        # Closing windows after .5 seconds
        dlg.root.after(500, dlg.root.destroy)
        dlg.mainloop()

    def test_resizable(self):
        # Given a dialog with resizable="False False"
        with new_dialog(DialogNotResizable) as dlg:
            dlg.pump_events()
        # Then the dialog cannot be resize

    def test_theme(self):
        # Given a dialog with theme defined
        with new_dialog(DialogWithTheme) as dlg:
            dlg.pump_events()
            # Then TopLevel get created with specific theme
            self.assertEqual('alt', ttk.Style(dlg.root).theme_use())
            # When updating the theme value
            dlg.data['theme_value'] = 'clam'
            # Then theme get updated
            self.assertEqual('clam', ttk.Style(dlg.root).theme_use())
