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

try:
    # Python < 3.12
    import pkg_resources

    def resource_path(fn):
        return pkg_resources.resource_filename(__package__, fn)

except ImportError:
    # Python >=3.12
    import importlib.resources

    def resource_path(fn):
        with importlib.resources.files(__package__).joinpath(fn) as p:
            return str(p)


import calendar
import os
import sys
import tkinter
import tkinter.ttk as ttk
import unittest
from contextlib import contextmanager

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
    def test_get_set_variable(self):
        var1 = tkvue.state("foo")
        var1.value = "bar"
        self.assertEqual(var1.value, "bar")

    def test_get_computed(self):
        var1 = tkvue.state(1)
        var2 = tkvue.state(2)
        sum = tkvue.computed_property(lambda: var1.value + var2.value)
        self.assertEqual(sum.value, 3)

    def test_watch_with_variable(self):
        listener = []
        var1 = tkvue.state("foo")
        var1.subscribe(listener.append)
        var1.value = "bar"
        self.assertEqual(listener, ["bar"])

    def test_watch_with_computed(self):
        listener = []
        var1 = tkvue.state(1)
        var2 = tkvue.state(1)
        sum = tkvue.computed_property(lambda: var1.value + var2.value)
        self.assertEqual(2, sum.value)
        sum.subscribe(listener.append)
        var1.value = 4
        self.assertEqual(listener, [5])

    def test_unwatch(self):
        listener = []
        var1 = tkvue.state("foo")
        var1.subscribe(listener.append)
        var1.value = "bar"
        self.assertEqual(listener, ["bar"])
        var1.unsubscribe(listener.append)
        var1.value = "foo"
        self.assertEqual(listener, ["bar"])

    def test_eval(self):
        context = tkvue._Context({"var1": tkvue.state([1, 2, 3, 4])})
        self.assertEqual(2, eval("var1[1]", None, context))

    def test_new_child(self):
        var1 = tkvue.state([1, 2, 3, 4])
        item = tkvue.computed_property(lambda: var1.value[3])
        parent = tkvue._Context({'var1': var1})
        child = tkvue._Context({'item': item}, parent=parent)
        # Item is equals to var[3] in data2
        self.assertEqual(item.value, 4)
        self.assertEqual(child['item'], 4)

    def test_setter_child(self):
        # Given a parent context
        var1 = tkvue.state("foo")
        context = tkvue._Context({'var1': var1})
        # When setting a value on the child context.
        context['var1'] = "bar"
        # Then the value is update into the parent context.
        self.assertEqual(var1.value, "bar")

    def test_computed_dependencies_updated(self):
        listener = []
        var1 = tkvue.state(True)
        var2 = tkvue.state(True)
        valid = tkvue.computed_property(lambda: var1.value or var2.value)
        valid.subscribe(listener.append)
        # When setting a value on the child context.
        var1.value = False
        var2.value = False
        # Then the value is update into the parent context.
        self.assertEqual(listener, [True, False])

    def test_computed_parent(self):
        # Given multiple parent-child context
        c = calendar.Calendar(calendar.SUNDAY)
        year = tkvue.state(2023)
        month = tkvue.state(12)
        days = tkvue.computed_property(lambda c=c: list(c.itermonthdays3(year.value, month.value)))
        parent = tkvue._Context({'year': year, 'month': month, 'days': days})
        child_idx0 = tkvue._Context(
            {'d': tkvue.computed_property(lambda: eval('days', None, parent)[0])}, parent=parent
        )
        child_idx1 = tkvue._Context(
            {'d': tkvue.computed_property(lambda: eval('days', None, parent)[1])}, parent=parent
        )
        self.assertEqual((2023, 11, 26), child_idx0['d'])
        self.assertEqual((2023, 11, 27), child_idx1['d'])
        # When updating the year and month.
        month.value = 11
        # Then child value get updated.
        self.assertEqual((2023, 10, 29), child_idx0['d'])
        self.assertEqual((2023, 10, 30), child_idx1['d'])
        # When watching index of value
        listener = []
        computed = tkvue.computed_property(lambda: eval('d[2]', None, child_idx0))
        computed.subscribe(listener.append)
        # When updating the month again
        month.value = 10
        # The listener should be called
        self.assertEqual([1], listener)

    def test_computed_raise_error(self):
        # Given a computed property that raise an error.
        obj = tkvue.state(None)
        days = tkvue.computed_property(lambda obj=obj: obj.value.test)
        # When getting computed property value
        # Then an error is raised
        with self.assertRaises(Exception):
            days.value
        # When adding computed property to context
        # Then an error is raised
        with self.assertRaises(Exception):
            tkvue._Context({'days': days})


class CustomComponent(tkvue.Component):
    template = """
    <Frame>
        <Label id="label" text="tet in component" />
    </Frame>
    """

    @tkvue.attr('mytext')
    def mytext(self, value):
        self.label.configure(text=value)


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
            <Label for="{{i in names}}" text="{{i}}" />
        </Frame>
        <label id="count1_label" text="{{count1}}" />
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
            <Checkbutton id="checkbutton" text="foo" selected="{{checkbutton_selected}}" command="{{checkbutton_invoke}}"/>
            <Checkbutton id="checkbutton2" text="leader" variable="{{checkbutton_selected}}"/>
            <Checkbutton id="checkbutton3" text="follower" selected="{{checkbutton_selected}}" command="{{funcation_call_with_args('arg1')}}"/>
        </Frame>
        <CustomComponent></CustomComponent>
    </TopLevel>
    """
    text_value = tkvue.state("foo")
    button_visible = tkvue.state(True)
    names = tkvue.state(["patrik", "annik", "michel", "denise"])
    selected_color = tkvue.state("blue")
    selected_number = tkvue.state(1)
    checkbutton_selected = tkvue.state(True)

    @tkvue.computed_property
    def count1(self):
        return len(self.names.value)

    @tkvue.command
    def checkbutton_invoke(self):
        self.checkbutton_selected.value = not self.checkbutton_selected.value

    @tkvue.command
    def funcation_call_with_args(self, value):
        self.value = value


class DialogWithImage(tkvue.Component):
    template = """
    <TopLevel>
        <Button id="button" text="Button with image" image="{{image_path}}" compound="left"/>
        <Label id="label" text="Label with image" image="{{image_path}}" compound="left"/>
    </TopLevel>
    """
    image_path = tkvue.state(None)


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
            <Tooltip id="tooltip" text="This is a tooltip" width="15" timeout="500" padding="10" />
        </Label>
    </TopLevel>
    """


class DialogWithLoop(tkvue.Component):
    template = """
    <TopLevel>
        <Label text="{{item}}" for="{{item in items}}"/>
    </TopLevel>
    """
    items = tkvue.state([])


class DialogWithCustomComponentLoop(tkvue.Component):
    template = """
    <TopLevel>
        <CustomComponent for="{{item in items}}" />
    </TopLevel>
    """
    items = tkvue.state([])


class DialogWithScrolledFrame(tkvue.Component):
    template = """
    <TopLevel geometry="500x500">
        <ScrolledFrame id="scrolled_frame" pack-fill="both" pack-expand="1">
            <Frame for="{{item in range(1,10)}}" pack-fill="x"  pack-expand="1">
                <Label pack-fill="x" pack-expand="1" text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. " wrap="1"/>
            </Frame>
        </ScrolledFrame>
    </TopLevel>
    """


class DialogWithInvalidCommand(tkvue.Component):
    template = """
    <TopLevel>
        <Checkbutton id="checkbutton" text="foo" selected="True" command="{{invalid_command}}"/>
    </TopLevel>
    """


class DialogWithBindingCommand(tkvue.Component):
    template = """
    <TopLevel>
        <Checkbutton id="checkbutton" text="foo" selected="True" command="{{my_command}}"/>
    </TopLevel>
    """

    def my_command(self):
        pass


class DialogNotResizable(tkvue.Component):
    template = """
    <TopLevel geometry="322x261" resizable="False False">
        <ScrolledFrame id="scrolled_frame">
            <Label text="{{item}}" for="{{item in range(1,25)}}"/>
        </ScrolledFrame>
    </TopLevel>
    """


class DialogWithTheme(tkvue.Component):
    template = """
    <TopLevel theme="{{ theme_value }}">
        <Button text="Push button" />
    </TopLevel>
    """
    theme_value = tkvue.state("alt")


class DialogWithPack(tkvue.Component):
    template = """
    <TopLevel>
        <Button id="btn" text="Push button" pack-side="left" pack-padx="5" pack-pady="10" pack-ipadx="2" pack-ipady="2" pack-fill="x" pack-expand="y" pack-anchor="nw"/>
        <CustomComponent pack-side="left" />
    </TopLevel>
    """


class DialogWithPlace(tkvue.Component):
    template = """
    <TopLevel>
        <Button id="btn" text="Push button" place-x="20" place-y="10" place-width="20" place-height="20"/>
        <CustomComponent place-x="40" place-y="40" />
    </TopLevel>
    """


class DialogWithGrid(tkvue.Component):
    template = """
    <TopLevel geometry="322x261">
        <Frame pack-fill="both" pack-expand="1" columnconfigure-weight="1 1">
            <Button id="btn1" text="grid-sticky=we" grid-column=0 grid-row=0 grid-sticky="we"/>
            <Button id="btn2" text="b" grid-column=1 grid-row=0 />
            <Button id="btn3" text="c" grid-column=0 grid-row=1 />
            <Button id="btn4" text="d" grid-column=1 grid-row=1 />
            <CustomComponent grid-column=0 grid-row=2 />
        </Frame>
    </TopLevel>
    """


class DialogWithCustomAttr(tkvue.Component):
    template = """
    <TopLevel>
        <CustomComponent id="mywidget" mytext="Foo" />
    </TopLevel>
    """


class DialogWithStyle(tkvue.Component):
    template = """
    <TopLevel style="default.TFrame">
        <Label text="test" />
    </TopLevel>
    """


class DialogWithLoopInLoop(tkvue.Component):
    template = """
    <TopLevel style="default.TFrame">
        <LabelFrame for="{{item in items}}" text="{{ '%s / %s' % (loop_idx, len(item)) }}">
            <Label for="{{char in item}}" text="{{ '%s: %s' % (loop_idx, char) }}" pack-padx="5"/>
        </LabelFrame>
    </TopLevel>
    """
    items = tkvue.state([])


class DialogWithCombobox(tkvue.Component):
    template = """
    <TopLevel>
        <Combobox id="combobox" values="{{values}}"/>
    </TopLevel>
    """
    values = tkvue.state(None)


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
            dlg.text_value.value = "bar"
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
            self.assertEqual("ifoo", dlg.text_value.value)
            self.assertEqual("ifoo", dlg.label.cget("text"))
            self.assertEqual("ifoo", dlg.entry.getvar(dlg.entry.cget("text")))

    @unittest.skipIf(IS_WINDOWS, "fail to reliably make this test work in CICD")
    def test_visible(self):
        # Given a dialog with a simple binding
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            self.assertTrue(dlg.button.winfo_ismapped())
            # When typing into the entry field
            dlg.button_visible.value = False
            dlg.pump_events()
            # Then the store get updated
            self.assertFalse(dlg.button.winfo_ismapped())

    def test_for_loop(self):
        # Given a dialog with a for loop
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            self.assertEqual(4, len(dlg.people.winfo_children()))
            # When Adding element to the list
            dlg.names.value = ["patrik", "annik"]
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
            self.assertEqual("red", dlg.selected_color.value)

    def test_dual_binding_select_number(self):
        # Given a dialog with a for loop
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            # When selecting an item with radio
            dlg.three.invoke()
            dlg.pump_events()
            self.assertEqual(3, dlg.selected_number.value)

    @unittest.skipIf(IS_MAC, "this fail on MacOS when running in test suite")
    def test_checkbutton_selected(self):
        # Given a dialog with checkbutton binded with `selected` attribute
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            # Due to bug in TTK, when we assign command, the state switch to 'alternate'
            self.assertEqual(dlg.checkbutton.state(), ("selected", "alternate"))
            self.assertEqual(dlg.checkbutton2.state(), ("selected",))
            # When updating checkbutton_selected value
            dlg.checkbutton_selected.value = False
            dlg.pump_events()
            # Then the widget get updated
            self.assertEqual(dlg.checkbutton.state(), tuple())
            self.assertEqual(dlg.checkbutton2.state(), tuple())
            # When updating checkbutton_selected value
            dlg.checkbutton_selected.value = True
            dlg.pump_events()
            # Then the widget get updated
            self.assertEqual(dlg.checkbutton.state(), ("selected",))
            self.assertEqual(dlg.checkbutton2.state(), ("selected",))

    @unittest.skipIf(IS_MAC, "this fail on MacOS when running in test suite")
    def test_checkbutton_selected_command(self):
        # Given a dialog with checkbutton binded with `selected` attribute
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            self.assertEqual(dlg.checkbutton2.state(), ("selected",))
            # When cliking on checkbutton
            dlg.checkbutton.focus_set()
            dlg.checkbutton.invoke()
            dlg.root.focus_set()
            dlg.pump_events()
            # Then the widget status get toggled.
            self.assertEqual(dlg.checkbutton_selected.value, False)
            self.assertEqual(dlg.checkbutton.state(), tuple())
            self.assertEqual(dlg.checkbutton2.state(), tuple())
            # When cliking on checkbutton again
            dlg.checkbutton.focus_set()
            dlg.checkbutton.invoke()
            dlg.root.focus_set()
            dlg.pump_events()
            # Then the widget status get toggled.
            self.assertEqual(dlg.checkbutton_selected.value, True)
            self.assertEqual(dlg.checkbutton.state(), ("selected",))
            self.assertEqual(dlg.checkbutton2.state(), ("selected",))

    def test_image_path(self):
        with new_dialog(DialogWithImage) as dlg:
            # Given a dialog with image
            self.assertEqual("", dlg.button.cget("image"))
            self.assertEqual("", dlg.label.cget("image"))
            # When settings image_path
            dlg.image_path.value = resource_path("python_icon.png")
            # Then Button and Label get update with an image
            self.assertTrue(dlg.button.cget("image")[0].startswith("pyimage"))
            self.assertTrue(dlg.label.cget("image")[0].startswith("pyimage"))

    def test_image_path_with_gif(self):
        with new_dialog(DialogWithImage) as dlg:
            # Given a dialog with image
            self.assertEqual("", dlg.button.cget("image"))
            self.assertEqual("", dlg.label.cget("image"))
            # When settings image_path
            dlg.image_path.value = resource_path("preloader.gif")
            # Then Button and Label get update with an image
            self.assertTrue(dlg.button.cget("image")[0].startswith("pyimage"))
            self.assertTrue(dlg.label.cget("image")[0].startswith("pyimage"))
            # Then set image to None
            dlg.image_path.value = ''

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
            dlg.items.value = [1, 2, 3, 4]
            dlg.pump_events()
            # Then widget get created
            self.assertEqual(4, len(dlg.winfo_children()))

    def test_loop_removing_items(self):
        # Given a dial with loop
        with new_dialog(DialogWithLoop) as dlg:
            dlg.items.value = [1, 2, 3, 4]
            dlg.pump_events()
            self.assertEqual(4, len(dlg.winfo_children()))
            # When removing items
            dlg.items.value = [3, 4]
            dlg.pump_events()
            # Then widget get created
            self.assertEqual(2, len(dlg.winfo_children()))

    def test_loop_custom_component(self):
        # Given a dial with loop
        with new_dialog(DialogWithCustomComponentLoop) as dlg:
            dlg.pump_events()
            self.assertEqual(0, len(dlg.winfo_children()))
            # When updating the items
            dlg.items.value = [1, 2, 3, 4]
            dlg.pump_events()
            # Then widget get created
            self.assertEqual(4, len(dlg.winfo_children()))

    def test_scrolled_frame(self):
        with new_dialog(DialogWithScrolledFrame) as dlg:
            dlg.pump_events()
            style = ttk.Style(dlg)
            style.configure('white.TFrame', background='#ffffff')
            dlg.scrolled_frame.configure({'style': 'white.TFrame'})
            dlg.pump_events()
            # Make sure the style is applied to the scrolled frame
            self.assertEqual(dlg.scrolled_frame.cget('style'), 'white.TFrame')
            # Make sure the background get applied to the inner canvas.
            self.assertEqual(dlg.scrolled_frame.canvas.cget('background'), '#ffffff')
            # Make sure the inner frame get updated too.
            self.assertEqual(dlg.scrolled_frame.interior.cget('style'), 'white.TFrame')
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

    @unittest.skip('With the new event loop this is not working')
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
            dlg.theme_value.value = 'clam'
            # Then theme get updated
            self.assertEqual('clam', ttk.Style(dlg.root).theme_use())

    def test_computed(self):
        # Given a dialog with computed attribute
        with new_dialog(Dialog) as dlg:
            dlg.pump_events()
            # Then the count value updates the labels
            self.assertEqual(dlg.count1_label.cget('text'), 4)
            self.assertEqual(dlg.count1_label.cget('text'), 4)
            # When uding the names
            dlg.names.value = ["patrik", "annik"]
            dlg.pump_events()
            # Then the label get updated too.
            self.assertEqual(dlg.count1_label.cget('text'), 2)
            self.assertEqual(dlg.count1_label.cget('text'), 2)

    @unittest.skipIf(IS_WINDOWS, "grid coordinate not working in CICD.")
    def test_pack(self):
        # Given a dialog with place-x attributes
        with new_dialog(DialogWithPack) as dlg:
            dlg.pump_events()
            # Then dialog get displayed and button coordinate are fixed
            self.assertEqual(5, dlg.btn.winfo_x())
            self.assertEqual(10, dlg.btn.winfo_y())

    def test_place(self):
        # Given a dialog with place-x attributes
        with new_dialog(DialogWithPlace) as dlg:
            dlg.pump_events()
            # Then dialog get displayed and button coordinate are fixed
            self.assertEqual(20, dlg.btn.winfo_x())
            self.assertEqual(10, dlg.btn.winfo_y())

    @unittest.skipIf(IS_WINDOWS, "grid coordinate not working in CICD.")
    def test_grid(self):
        # Given a dialog with place-x attributes
        with new_dialog(DialogWithGrid) as dlg:
            dlg.pump_events()
            # Then dialog get displayed and button coordinate are fixed
            self.assertEqual(0, dlg.btn1.winfo_x())
            self.assertEqual(0, dlg.btn1.winfo_y())
            # Then dialog get displayed and button coordinate are variable
            self.assertTrue(dlg.btn4.winfo_x() > 0)
            self.assertTrue(dlg.btn4.winfo_y() > 0)

    def test_custom_attr(self):
        # Given a dialog with a custom attribute
        with new_dialog(DialogWithCustomAttr) as dlg:
            dlg.pump_events()
            # Then our custom attribute update the internal widget
            self.assertEqual('Foo', dlg.mywidget.label.cget('text'))

    def test_toplevel_style(self):
        # Given a dialog with a custom style.
        with new_dialog(DialogWithStyle) as dlg:
            dlg.pump_events()
            self.assertNotEqual('#ffffff', dlg.root.cget('background'))
            # When updating the style
            s = ttk.Style(master=dlg.root)
            s.configure('default.TFrame', background='#ffffff')
            dlg.pump_events()
            # Then the TopLevel background get updated.
            self.assertEqual('#ffffff', dlg.root.cget('background'))

    def test_loop_in_loop(self):
        # Given a dialog with loops
        with new_dialog(DialogWithLoopInLoop) as dlg:
            # When updating the items
            dlg.items.value = ["patrik", "michel"]
            dlg.pump_events()
            # Then the widget get created
            self.assertEqual(2, len(dlg.winfo_children()))
            self.assertEqual(6, len(dlg.winfo_children()[0].winfo_children()))
            self.assertEqual(6, len(dlg.winfo_children()[1].winfo_children()))

    def test_combobox_values(self):
        # Given a dialog with a combobox
        with new_dialog(DialogWithCombobox) as dlg:
            # When updating the items
            dlg.pump_events()
            # list is supported
            values = ["some text", "some value"]
            dlg.values.value = values
            dlg.pump_events()
            self.assertEqual(dlg.combobox.cget('values'), ('some text', 'some value'))
            # Iterable is supported
            value_map = {1: "new text", 2: "new value"}
            dlg.values.value = value_map.values()
            dlg.pump_events()
            self.assertEqual(dlg.combobox.cget('values'), ('new text', 'new value'))
