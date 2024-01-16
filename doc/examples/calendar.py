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

import calendar
import datetime
import tkinter.ttk as ttk

from babel.dates import get_day_names, get_month_names

import tkvue

tkvue.configure_tk(theme="clam")


class Calendar(tkvue.Component):
    template = """
<Frame style="default.TFrame" columnconfigure-weight="1 1 1 1 1 1 1">
    <Frame style="default.TFrame" grid-columnspan="7" >
        <Button text="<" command="{{_prev}}" pack-side="left" width="3"/>
        <Button text=">" command="{{_next}}" pack-side="right" width="3"/>
        <Label text="{{ title }}" pack-side="top" pack-padx="10 10" pack-fill="both" pack-expand="1" anchor="center"/>
    </Frame>
    <Label for="{{d in weekdays}}" text="{{ d }}" grid-column="{{ loop_idx }}" grid-row="2"/>
    <Button for="{{d in dates}}" text="{{ d[2] }}" grid-column="{{ loop_idx % 7 }}" grid-row="{{ 2 + int(loop_idx / 7) }}" command="{{_select(d)}}"/>

</Frame>
    """
    year = int(datetime.datetime.today().strftime('%Y'))
    month = int(datetime.datetime.today().strftime('%m'))
    displayed_year_month = tkvue.state((year, month))
    firstweekday = tkvue.state(calendar.SUNDAY)

    def __init__(self, master=None):
        self._variable = None
        self._validatecommand = None
        super().__init__(master)

    @tkvue.attr('datevariable')
    def set_datevariable(self, value):
        """
        In order to be able to retrieve the current text from the calendar widget, you must set this option to an instance of the StringVar.
        """
        self._variable = value

    @tkvue.attr('firstweekday')
    def set_firstweekday(self, value):
        """
        Control the first day of week. Usually SUNDAY (6) or MONDAY(0).
        """
        self.firstweekday.value = value

    @tkvue.attr('validatecommand')
    def set_validatecommand(self, func):
        """
        A callback that return true or false for each visible dates of the calendar controlling the enabled state.
        """
        assert func is None or callable(func), 'validatecommand required a function or None'
        self._validatecommand = func

    @tkvue.computed_property
    def title(self):
        months = dict(get_month_names())
        month_text = months.get(self.displayed_year_month.value[1])
        return '%s %s' % (month_text, self.displayed_year_month.value[0])

    @tkvue.computed_property
    def weekdays(self):
        """
        Return translated version of day of weeks
        """
        # Get translation from babel.
        trans = dict(get_day_names('narrow'))
        # Return
        c = calendar.Calendar(self.firstweekday.value)
        return [trans.get(d) for d in c.iterweekdays()]

    @tkvue.computed_property
    def dates(self):
        """
        Liste of all dates as (year, month, day)
        """
        c = calendar.Calendar(self.firstweekday.value)
        year, month = self.displayed_year_month.value
        return list(c.itermonthdays3(year, month))

    @tkvue.command
    def _select(self, d):
        if self._variable is not None:
            self._variable.set(d)

    @tkvue.command
    def _prev(self):
        year, month = self.displayed_year_month.value
        month = month - 1
        if month < 1:
            month = 12
            year = year - 1
        if year <= 1970:
            year = 1970
        self.displayed_year_month.value = (year, month)

    @tkvue.command
    def _next(self):
        year, month = self.displayed_year_month.value
        month = month + 1
        if month > 12:
            month = 1
            year = year + 1
        self.displayed_year_month.value = (year, month)


class RootDialog(tkvue.Component):
    template = """
<TopLevel title="TKVue Test" geometry="900x720">
    <Frame style="default.TFrame" pack-fill="both" pack-expand="1" padding="10">
        <Label text="Hello World !" style="h1.TLabel" pack-padx="25" pack-pady="25"/>
        <Calendar datevariable="{{ selected_date }}" validatecommand="{{_enabled_date}}"/>
        <Label text="{{ 'Selected date: %s' % selected_date}}" />
        <Frame style="default.TFrame" pack-fill="both" pack-expand="1" pack-padx="10" pack-pady="10">
            <Button style="default.TButton" text="Continue" pack-side="right" pack-padx="5"/>
            <Button style="default.TButton" text="Cancel" pack-side="right"/>
        </Frame>
    </Frame>
</TopLevel>
    """

    selected_date = tkvue.state(None)

    def __init__(self, master=None):
        super().__init__(master)
        s = ttk.Style(master=self.root)
        s.configure('H1.TLabel', font=['Lato', '-60'], background='#ffffff')
        s.configure('default.TFrame', background='#ffffff')
        s.configure(
            'default.TButton',
            foreground='#0E2933',
            background='#B6DDE2',
            bordercolor='#ACD1D6',
            darkcolor='#B6DDE2',
            lightcolor='#B6DDE2',
            focuscolor='#0E2933',
        )
        s.map(
            'default.TButton',
            background=[('disabled', '#E9F4F6'), ('hover !disabled', '#9ABBC0'), ('pressed !disabled', '#88A5A9')],
        )
        self.root.tk.call('tk', 'scaling', '1.333333333333')

    @tkvue.command
    def _enabled_date(self, d):
        return d % 3


if __name__ == "__main__":
    dlg = RootDialog()
    dlg.mainloop()
