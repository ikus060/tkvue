# Copyright (C) 2023 IKUS Software. All rights reserved.
# IKUS Software inc. PROPRIETARY/CONFIDENTIAL.
# Use is subject to license terms.
import asyncio
import contextlib
import functools
import logging
import os
import sys
import threading
import tkinter
from html.parser import HTMLParser
from tkinter import ttk

try:
    from gettext import gettext
except ImportError:

    def gettext(message):
        return message


EMPTY_GLOBALS = {}


def _eval_func(expr, context):
    """
    Create a function to execute eval() within the given context
    """
    assert isinstance(expr, str), 'expect an expression'
    func = functools.partial(eval, expr, EMPTY_GLOBALS, context)
    func.__expr__ = expr
    return func


# Local data for watcher tracking.
local = threading.local()
local.tracking = []

# When this module is loaded. Make sure default Tkinter doesn't get created.
tkinter.NoDefaultRoot()

# Default logger.
logger = logging.getLogger('tkvue')

# Component registry
_components = {}

# Widget registry
_widgets = {}

# Attribute registry
_attrs = {}

# Register all ttk widget
for a in dir(ttk):
    cls = getattr(ttk, a)
    if isinstance(cls, type) and issubclass(cls, tkinter.Widget):
        _widgets[a.lower()] = cls

# Register Canvas
_widgets['canvas'] = tkinter.Canvas

# Map python types to tkinter variable class.
_VARTYPES = {
    int: tkinter.IntVar,
    float: tkinter.DoubleVar,
    bool: tkinter.BooleanVar,
    str: tkinter.StringVar,
}

_default_basename = None
_default_classname = "Tkvue"
_default_screenname = None
_default_icons = None
_default_theme = None
_default_theme_source = None
_default_theme_callback = None


def _computed_expression(expr, context):
    """
    Return an observable object for the given expression.
    """
    assert isinstance(expr, str), 'expect an expression'
    # Lookup exact expression in context.
    # If observable, return it directly
    try:
        obj = context.get(expr.strip())
        if _is_observable(obj):
            return obj
    except KeyError:
        pass
    # Otherwise, create an observable using eval
    return computed_property(_eval_func(expr, context))


def attr(attr_name, widget_cls=None):
    """
    Function decorator to register an special attribute definition for a Widget.

    ```
    @tkvue.attr('foo', ttk.Widget)
    def foo(widget, value):
        widget.some_call(value)
    ```

    Could also be used with component:

    ```
    class MyWidget(tkvue.component):

        @tkvue.attr('foo')
        def foo(widget, value):
            widget.some_call(value)
    ```"""
    if isinstance(widget_cls, type):
        widget_cls = [widget_cls]

    def decorate(func):
        assert callable(func), '@tkvue.attr() required a callable function'
        if isinstance(widget_cls, (list, tuple)):
            # Register each attributes
            for cls in widget_cls:
                _attrs.setdefault(attr_name, {})[cls] = func
        else:
            # Most likely @tkvue.attr() on class method.
            assert (
                '.' in func.__qualname__
            ), '@tkvue.attr(attr_name) can only be used on class method, otherwise you must define widget_cls explicitly.'
            # The widget class cannot be retrieve at class initialization.
            func._tkvue_attr_name = attr_name
        return func

    return decorate


def widget(widget_name):
    """
    Function decorator to register a widget.
    """

    def decorate(cls):
        _widgets[widget_name] = cls
        # Collect _tkvue_attr_name
        attrs = {}
        for key in dir(cls):
            member = getattr(cls, key)
            attr_name = getattr(member, '_tkvue_attr_name', False)
            if attr_name:
                attrs[attr_name] = member
        if attrs:
            cls._tkvue_attrs = attrs
        return cls

    return decorate


def _is_observable(obj):
    """
    Return true if the object is observable with subscribe() and also return a value
    """
    return obj is not None and hasattr(obj, 'subscribe') and hasattr(obj, 'value')


class Observable:
    def accessed(self):
        """Should be called when the observable get accessed"""
        for obj in local.tracking:
            self.subscribe(obj._dependency_change)
            obj._dependencies.append(self)

    def subscribe(self, func):
        """Adding subscriber on the current state."""
        assert callable(func), 'subscriber must be callable: %s' % func
        if not getattr(self, '_subscribers', False):
            self._subscribers = []
        self._subscribers.append(func)

    def unsubscribe(self, func):
        """Removing associated subscribers."""
        if getattr(self, '_subscribers', False):
            self._subscribers.remove(func)

    def _notify(self, new_value):
        if getattr(self, '_subscribers', False):
            for func in list(self._subscribers):
                try:
                    func(new_value)
                except Exception:
                    logger.exception("exception when notifying subscriber: %s" % func)

    @contextlib.contextmanager
    def track_dependencies(self):
        """
        Used to enable tracking of dependencies.
        """
        assert callable(
            getattr(self, '_dependency_change', False)
        ), 'implemmentation of _dependency_change() is required to enable tracking'
        # Clear previous dependencies
        if getattr(self, '_dependencies', False):
            for d in list(self._dependencies):
                d.unsubscribe(self._dependency_change)
        self._dependencies = []
        # Enable tracking
        local.tracking.append(self)
        try:
            yield self
        finally:
            # Disable tracking
            local.tracking.remove(self)


class computed_property(Observable):
    """
    Class decorator
    """

    _tkvue_expose = True

    def __init__(self, func) -> None:
        assert callable(func), 'computed_property required a function'
        self._func = func

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        func = functools.partial(self._func, instance)
        return_instance = computed_property(func)
        instance.__dict__[self._name] = return_instance
        return return_instance

    def subscribe(self, func):
        super().subscribe(func)
        # If dirty, we need to compute the value to register dependencies
        if getattr(self, '_dirty', True):
            self.value

    @property
    def value(self):
        # Return cached value if available
        if not getattr(self, '_dirty', True):
            self.accessed()
            return self._value
        # Compute new value
        with self.track_dependencies():
            try:
                return_value = self._func()
            except Exception:
                raise Exception(
                    'error during evaluation of computed_property: %s' % getattr(self._func, '__expr__', self._func)
                )
        self._dirty = False
        self._value = return_value
        return return_value

    def _dependency_change(self, unused_new_value):
        """When our dependencies get updated, make our self dirty and notify our watchers."""
        self._dirty = True
        # Compute new value and notify subscribers
        if getattr(self, '_subscribers', False):
            new_value = self.value
            self._notify(new_value)


class state(Observable):
    """
    Create a state().
    """

    _tkvue_expose = True

    def __init__(self, initial_value) -> None:
        assert hasattr(initial_value, "__hash__"), "unhashable type '%s'" % type(initial_value)
        self._value = initial_value

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return_instance = state(self._value)
        instance.__dict__[self._name] = return_instance
        return return_instance

    @property
    def value(self):
        self.accessed()
        # TODO We may need to wrap list and dict.
        return self._value

    @value.setter
    def value(self, new_value):
        assert hasattr(new_value, "__hash__"), "unhashable type '%s'" % type(new_value)
        old_value = self._value
        self._value = new_value
        if old_value != new_value:
            self._notify(new_value)


def command(obj):
    """
    Expose the class function to the context. This should be used as annotation on Component's function.

    class MyComponent(tkvue.Component):
        @tkvue.command()
        def on_click(self):
            print("button click")
    """
    assert callable(obj), 'tkvue.command() required a function'
    obj._tkvue_expose = True
    return obj


def configure_tk(
    basename=None,
    classname="Tk",
    screenname=None,
    icon=[],
    theme=None,
    theme_source=None,
    theme_callback=None,
):
    """
    Use to configure default instance of Tkinter created by tkvue.

    basename: Text displayed in Dock
    classname: Text displayed in Dock
    screenname: unknown
    icon: list of default icon associated with the application
    theme: name of theme to load
    theme_source: optional tcl script to be loaded
    theme_callback: a function to further customize the theme
    """
    assert theme_source is None or os.path.isfile(theme_source)

    # Disable Tkinter default root creation
    tkinter.NoDefaultRoot()
    global _default_basename, _default_classname, _default_screenname, _default_icons, _default_theme, _default_theme_source, _default_theme_callback
    _default_basename = basename
    _default_classname = classname
    _default_screenname = screenname
    _default_icons = icon
    _default_theme = theme
    _default_theme_source = theme_source
    _default_theme_callback = theme_callback


@widget('toplevel')
def create_toplevel(master=None):
    """Used to create a TopLevel window."""

    global _default_basename, _default_classname, _default_screenname, _default_icons, _default_theme, _default_theme_source, _default_theme_callback
    if master is None:
        root = tkinter.Tk(
            baseName=_default_basename,
            className=_default_classname,
            screenName=_default_screenname,
        )
        root.report_callback_exception = lambda exc, val, tb: logger.exception("exception in Tkinter callback")
        if _default_theme_source:
            root.call("source", _default_theme_source)
        if _default_theme:
            root.call("ttk::setTheme", _default_theme)
        if _default_theme_callback:
            _default_theme_callback(root)
        if _default_icons:
            root.iconphoto(True, *_default_icons)
    else:
        root = tkinter.Toplevel(master)

    def _update_bg(event):
        # Skip update if event is not raised for TopLevel widget.
        if root != event.widget:
            return
        # Update TopLevel background according to TTK Style.
        style_name = getattr(root, '_tkvue_toplevel_style', 'TFrame')
        bg = ttk.Style(master=root).lookup(style_name, "background")
        root.configure(background=bg)

    root.bind("<<ThemeChanged>>", _update_bg)

    return root


def extract_tkvue(fileobj, keywords, comment_tags, options):
    """Extract messages from .html files.

    :param fileobj: the file-like object the messages should be extracted
                    from
    :param keywords: a list of keywords (i.e. function names) that should
                     be recognized as translation functions
    :param comment_tags: a list of translator tags to search for and
                         include in the results
    :param options: a dictionary of additional options (optional)
    :return: an iterator over ``(lineno, funcname, message, comments)``
             tuples
    :rtype: ``iterator``
    """
    encoding = options.pop("encoding", "utf-8")

    class ExtractorParser(HTMLParser):
        def __init__(self):
            self.messages = []
            super().__init__()

        def handle_starttag(self, tag, attrs):
            for name, value in attrs:
                if name in ["text", "title"] and not value.startswith("{{"):
                    self.messages.append((self.lineno, "gettext", value, []))

    extractor = ExtractorParser()
    extractor.feed(fileobj.read().decode(encoding))
    for entry in extractor.messages:
        yield entry


class _Context:
    def __init__(self, initial_data={}, parent=None):
        """Create a new root context"""
        # Make sure only callable and Observable are included.
        for key, obj in initial_data.items():
            if not callable(obj) and not _is_observable(obj):
                raise ValueError(
                    'context only support observable objects state() and computed_property(): %s = %s' % (key, obj)
                )
        self._map = initial_data.copy()
        self._parent = parent

    def __getitem__(self, key):
        """Used by `eval()` to resolve variable name. Unwrap the value."""
        if key not in self._map and self._parent:
            return self._parent.__getitem__(key)
        obj = self._map[key]
        if callable(obj):
            return obj
        return obj.value

    def __setitem__(self, key, value):
        """Used by eval() to set variable value"""
        # Dispatch setter to parent context
        if key not in self._map and self._parent:
            self._parent.__setitem__(key, value)
            return
        # Get previous value for comparaison
        obj = self._map[key]
        if not hasattr(obj, "value"):
            raise ValueError("cannot set computed attribute")
        obj.value = value

    def get(self, key):
        """Return the real object"""
        if key not in self._map and self._parent:
            return self._parent.__getitem__(key)
        return self._map[key]


def _create_command(expr, context):
    """
    Command may only be define when creating widget.
    So let process this attribute before creating the widget.
    """
    assert expr.startswith("{{") and expr.endswith("}}"), (
        "command's value should we wrap in curly braquet {{ funcation_name() }}: " + expr
    )
    expr = expr[2:-2].strip()
    # May need to adjust this to detect expression.
    if "(" in expr or "=" in expr:
        func = _eval_func(expr, context)
    else:
        try:
            func = context.get(expr)
            if func is None or not callable(func):
                raise ValueError('`command` attribute must define a function name or a function call: ' + expr)
        except KeyError:
            raise ValueError('cannot find function name for command attribute: ' + expr)
    return func


def _configure(widget, key, value):
    """Stack all configuration if widget is not registered to minimize number of tk.call"""
    # If widget is registered, simply call configure.
    if getattr(widget, '_tkvue_register', False):
        widget.configure({key: value})
    else:
        # Otherwise, store the values
        if not getattr(widget, '_tkvue_configure', False):
            widget._tkvue_configure = dict()
        widget._tkvue_configure[key] = value


@attr("id", tkinter.Widget)
def _configure_id_noop(widget, value):
    """No-op for `id` attribute already handle at creation of widget."""
    pass


@attr("command", tkinter.Widget)
def _configure_command(widget, value):
    """Assign function to command"""
    assert value is None or callable(value), "expect a callable function for command"
    _configure(widget, 'command', value)


@attr("visible", tkinter.Widget)
def _configure_visible(widget, value):
    widget._tkvue_visible = value
    # Do nothing if the widget is not yet registered.
    if getattr(widget, '_tkvue_register', False):
        # Show / Hide widget
        geo = getattr(widget, '_tkvue_geo', 'pack')
        assert geo in ['pack', 'place', 'grid']
        if value:
            # Check which geometry manager is used by this widget. Default to 'pack'
            attrs = getattr(widget, '_tkvue_geo_attrs', {})
            getattr(widget, geo)(attrs)
        else:
            forget_func = getattr(widget, '%s_forget' % geo)
            forget_func()


GEO_ATTRS = {
    'pack': ('side', 'padx', 'pady', 'ipadx', 'ipady', 'fill', 'expand', 'anchor'),
    'grid': ('column', 'columnspan', 'ipadx', 'ipady', 'padx', 'pady', 'row', 'rowspan', 'sticky'),
    'place': ('x', 'y', 'relx', 'rely', 'anchor', 'width', 'height', 'relwidth', 'relheight', 'bordermode'),
}
for geo, keys in GEO_ATTRS.items():
    for key in keys:

        @attr("%s-%s" % (geo, key), tkinter.Widget)
        def _configure_geo(widget, value, geo=geo, key=key):
            # Check if another Geometry manager was used.
            if getattr(widget, '_tkvue_geo', geo) != geo:
                raise ValueError('widget can only use a single geometry manager: %s' % geo)
            # Store the vlaue within the widget metadata
            widget._tkvue_geo = geo
            if getattr(widget, '_tkvue_geo_attrs', None) is None:
                widget._tkvue_geo_attrs = {}
            widget._tkvue_geo_attrs[key] = value
            # If registered, call the geometry manager
            if getattr(widget, '_tkvue_register', False):
                getattr(widget, geo)(widget._tkvue_geo_attrs)


for cfg in ['columnconfigure', 'rowconfigure']:
    for key in ['minsize', 'pad', 'weight']:

        @attr("%s-%s" % (cfg, key), tkinter.Widget)
        def _grid_configure(widget, value, cfg=cfg, key=key):
            assert ',' not in value, "values must be separated by spaces, not by comma (,)"
            values = value.split(' ')
            func = getattr(widget, cfg)
            for idx, val in enumerate(values):
                func(idx, **{key: val})


@attr("geometry", (tkinter.Tk, tkinter.Toplevel))
def _configure_geometry(widget, value):
    """
    Configure geometry on TopLevel
    """
    widget.geometry(value)


@attr("resizable", (tkinter.Tk, tkinter.Toplevel))
def _configure_resizable(widget, value):
    assert isinstance(value, str), f"{value} should be a string value: <width> <height>"
    widget.resizable(*value.partition(' ')[0::2])


@attr("title", (tkinter.Tk, tkinter.Toplevel))
def _configure_title(widget, value):
    assert isinstance(value, str), f"{value} should be a string"
    widget.title(gettext(value))


@attr("text", tkinter.Widget)
def _configure_text(widget, value):
    _configure(widget, 'text', gettext(value))


@attr("selected", (ttk.Button, ttk.Checkbutton))
def _configure_selected(widget, value):
    widget.state(["selected" if value else "!selected", "!alternate"])


@attr("style", (tkinter.Tk, tkinter.Toplevel))
def _configure_toplevel_style(widget, style_name):
    # Update TopLevel background according to TTK Style.
    bg = ttk.Style(master=widget).lookup(style_name, "background")
    widget.configure(background=bg)
    widget._tkvue_toplevel_style = style_name


@attr("image", ttk.Widget)
def _configure_image(widget, image_path):
    """
    Configure the image attribute of a Label or a Button.
    Support animated gif image.
    """

    def _next_frame():
        widget.frame = (widget.frame + 1) % len(widget.frames)
        if widget.winfo_ismapped():
            widget.configure(image=widget.frames[widget.frame])
        # Register next animation.
        widget._tkvue_event_id = widget.tk.call('after', 100, next_frame_command_name)

    def _stop_animation(unused=None):
        if getattr(widget, "_tkvue_func_id", None):
            widget.unbind("<Destroy>", widget._tkvue_func_id)
            del widget._tkvue_func_id

        if getattr(widget, "_tkvue_event_id", None):
            widget.after_cancel(widget._tkvue_event_id)
            del widget._tkvue_event_id

    def _start_animation(unused=None):
        if not getattr(widget, "_tkvue_event_id", None):
            widget._tkvue_event_id = widget.tk.call('after', 100, next_frame_command_name)
        if not getattr(widget, "_tkvue_func_id", None):
            widget._tkvue_func_id = widget.bind("<Destroy>", _stop_animation)

    # Manually register the function to avoid creating-deleting commands.
    next_frame_command_name = widget._register(_next_frame)
    # Convert image _path to string (support PosixPath)
    image_path = str(image_path) if image_path else image_path
    # Create a new image
    if not image_path:
        # Remove image
        widget.frames = []
    elif image_path.endswith(".gif"):
        widget.frames = []
        while True:
            try:
                image = tkinter.PhotoImage(
                    master=widget,
                    file=image_path,
                    format="gif -index %i" % len(widget.frames),
                )
                widget.frames.append(image)
            except tkinter.TclError:
                # An error is raised when the index is out of range.
                break
    elif image_path in widget.image_names():
        widget.frames = [image_path]
    elif f"{image_path}_00" in widget.image_names():
        widget.frames = sorted([name for name in widget.image_names() if name.startswith(f"{image_path}_")])
    else:
        widget.frames = [tkinter.PhotoImage(master=widget, file=image_path)]

    # Update widget image with first frame.
    widget.frame = 0
    widget.configure(image=widget.frames[0] if widget.frames else '')

    if len(widget.frames) > 1:
        _start_animation()
    else:
        _stop_animation()


@attr("wrap", ttk.Label)
def _configure_wrap(widget, wrap):
    # Support Text wrapping
    if wrap.lower() in ["true", "1"]:
        widget.bind(
            "<Configure>",
            lambda e: widget.configure(wraplength=widget.winfo_width()),
            add="+",
        )


@attr("theme", tkinter.Tk)
def _configure_theme(widget, value):
    # Defined on TopLevel
    ttk.Style(master=widget).theme_use(value)


@attr('values', ttk.Combobox)
def _configure_values(widget, value):
    """Support itterable in addition to list and tuple."""
    if hasattr(value, '__iter__'):
        value = list(value)
    widget.configure({'values': value})


def _real_widget(widget):
    """
    Return Component's inner widget or the widget itself.
    """
    return widget.root if isinstance(widget, Component) else widget


@widget("tooltip")
class ToolTip(ttk.Frame):
    """
    Tooltip widget.
    """

    def __init__(self, master, text="", timeout=400, width=None, **kwargs):
        assert master, "ToolTip widget required a master widget"
        assert timeout >= 0, "timeout should be greater or equals zero (0): %s" % timeout
        assert width is None or width > 0, "timeout should be greater than zero (0): %s" % width
        super().__init__(master, **kwargs)
        self.widget = master
        self.text = text
        self.width = width
        # Initialize internal variables
        self.tipwindow = None  # tooltip window.
        self.id = None  # event id
        self.x = self.y = 0
        self.timeout = timeout  # time in milliseconds before tooltip get displayed
        # Bind events to master
        self.master.bind("<Enter>", self.enter)
        self.master.bind("<Leave>", self.leave)
        self.master.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        self.x = event.x
        self.y = event.y
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.master.after(self.timeout, self.showtip)

    def unschedule(self):
        if self.id:
            self.master.after_cancel(self.id)
        self.id = None

    def showtip(self):
        if self.tipwindow:
            return
        x = self.master.winfo_rootx() + self.x + 5
        y = self.master.winfo_rooty() + self.y + 5
        self.tipwindow = tkinter.Toplevel(self.master)
        try:
            self.tipwindow.wm_overrideredirect(True)
            # if not sys.platform.startswith('darwin'):
            # if running_mac() and ENABLE_MAC_NOTITLEBAR_PATCH:
            # self.tipwindow.wm_overrideredirect(False)
        except Exception as e:
            print("* Error performing wm_overrideredirect in showtip *", e)
        self.tipwindow.wm_geometry("+%d+%d" % (x, y))
        self.tipwindow.wm_attributes("-topmost", 1)
        if sys.platform.startswith('linux'):
            self.tipwindow.wm_attributes("-type", "tooltip")
        label = ttk.Label(
            self.tipwindow,
            text=self.text,
            justify=tkinter.LEFT,
            padding=5,
            style="tooltip.TLabel",
            width=self.width,
        )
        if self.width:
            label.bind(
                "<Configure>",
                lambda e: label.configure(wraplen=label.winfo_width()),
                add="+",
            )
        label.pack()

    def hidetip(self):
        """
        Destroy the tooltip window
        """
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None

    def pack(self, cfg={}, **kw):
        # Do nothing This widget must not be pack
        pass

    @attr('text')
    def set_text(self, value):
        self.text = value

    @attr('timeout')
    def set_timeout(self, value):
        assert int(value) >= 0, "timeout should be greater or equals to zero (0): %s" % value
        self.timeout = int(value)

    @attr('width')
    def set_width(self, value):
        assert int(value) > 0, "width should be greater then zero (0): %s" % value
        self.width = int(value)

    def bind(self, *args, **kwargs):
        self.widget.bind(*args, **kwargs)

    def event_generate(self, *args, **kwargs):
        self.widget.event_generate(*args, **kwargs)


class Loop:
    """
    Pseudo widget used to handle for loops.
    """

    def __init__(self, tree, for_expr, master, context, widget_factory):
        assert tree
        assert " in " in for_expr, "for attribute should have the following form: {{ <target> in <list> }}" + for_expr
        assert for_expr.startswith("{{") and for_expr.endswith("}}"), (
            "for attribute should we wrap in curly braquet {{ <target> in <list> }}: " + for_expr
        )
        assert master
        assert context
        self.tree = tree.copy()
        self.tree.attrs.pop("for", "None")
        self.master = master
        self.context = context
        self.widget_factory = widget_factory
        self.idx = 0
        self.widgets = []
        # Validate expression by evaluating it.
        for_expr = for_expr[2:-2].strip()
        self.loop_target, unused, self.loop_items = for_expr.partition(" in ")
        # Register our self
        obj = _computed_expression(self.loop_items, context)
        obj.subscribe(self.update_items)
        # When our parent is destroyed, stop watching
        self.master.bind("<Destroy>", lambda event, obj=obj: obj.unsubscribe(self.update_items), add="+")
        # Children shildren
        self.update_items(obj.value)

    def create_widget(self, idx):
        child_context = _Context(
            {
                self.loop_target: computed_property(_eval_func("%s[%s]" % (self.loop_items, idx), self.context)),
                'loop_idx': state(idx),
            },
            parent=self.context,
        )
        return self.widget_factory(master=self.master, tree=self.tree, context=child_context)

    def update_items(self, items):
        assert hasattr(items, '__len__'), "for loop doesn't support type %s, make sure `%s` return a list()" % (
            type(items),
            self.loop_items,
        )
        # We may need to create new widgets.
        while self.idx < len(items):
            widget = self.create_widget(self.idx)
            # Make sure to pack widget at the right location.
            self.widgets.append(widget)
            self.idx += 1
        # We may need to delete widgets
        while self.idx > len(items):
            self.widgets.pop(-1).destroy()
            self.idx -= 1


@widget('scrolledframe')
class ScrolledFrame(ttk.Frame):
    """
    Let provide our own Scrolled frame supporting styled background color.
    """

    def __init__(self, master, *args, **kw):
        ttk.Frame.__init__(self, master, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = ttk.Scrollbar(self, orient=tkinter.VERTICAL)
        min_height = self.vscrollbar.winfo_reqheight()
        self.canvas = tkinter.Canvas(
            self,
            borderwidth=0,
            highlightthickness=0,
            yscrollcommand=self.vscrollbar.set,
            height=min_height,
        )
        self.canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
        self.vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = ttk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=tkinter.NW)
        self.interior.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._configure_canvas)
        self.canvas.bind("<Enter>", self._bind_to_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_from_mousewheel)
        # Update background with inital values.
        self.bind("<<ThemeChanged>>", self._update_bg)
        self._update_bg()

    # track changes to the canvas and frame width and sync them,
    # also updating the scrollbar
    def _update_scroll_region(self, event):
        # Update the scroll region when the interior widget is resized.
        # Since we only scroll on y axis, take the width from canvas and height from interior.
        self.canvas.config(scrollregion=(0, 0, self.interior.winfo_width(), self.interior.winfo_reqheight()))
        # Show/hide scroll bar as needed
        if self.canvas.winfo_height() > self.interior.winfo_reqheight():
            self.vscrollbar.forget()
        else:
            self.vscrollbar.pack(fill=tkinter.Y, side=tkinter.RIGHT, expand=tkinter.FALSE)

    def _configure_canvas(self, event):
        # The current width of the canvas
        canvas_width = self.canvas.winfo_width()
        # The interior widget's requested width
        interior_width = self.interior.winfo_width()
        # update the inner frame's width to fill the canvas
        if canvas_width != interior_width:
            self.canvas.itemconfigure(self.interior_id, width=canvas_width)
        else:
            if self.canvas.winfo_height() > self.interior.winfo_reqheight():
                self.vscrollbar.forget()
            else:
                self.vscrollbar.pack(fill=tkinter.Y, side=tkinter.RIGHT, expand=tkinter.FALSE)

    def _on_mousewheel(self, event):
        # Skip scroll if canvas is bigger then content.
        if self.canvas.yview() == (0.0, 1.0):
            return
        # Pick scroll directio dependinds of event <Button-?> or delta value <MouseWheel>
        if event.num == 5 or event.delta < 0:
            scroll = 1
        elif event.num == 4 or event.delta > 0:
            scroll = -1
        self.canvas.yview_scroll(scroll, "units")

    def _bind_to_mousewheel(self, event):
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # On Windows

    def _unbind_from_mousewheel(self, event):
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
        self.canvas.unbind_all("<MouseWheel>")  # On Windows

    def _update_bg(self, event=None):
        """Propagate the style of parent widget to canvas and interior widget."""
        style_name = self.cget('style') or 'TFrame'
        if style_name != getattr(self, '_tkvue_prev_style_name', False):
            bg = ttk.Style(master=self).lookup(style_name, "background")
            self.canvas.configure(bg=bg)
            self.interior.configure(style=style_name)
            self._tkvue_prev_style_name = style_name

    def configure(self, cnf=None, **kw):
        """Ovewrite configure to update style of canvas and interior."""
        super().configure(cnf, **kw)
        if 'style' in kw or (cnf and 'style' in cnf):
            self._update_bg()


class TemplateError(Exception):
    """
    Raised when trying to create the component.
    """

    pass


class Element(object):
    """
    HTML element
    """

    __slots__ = ["tag", "attrs", "children", "parent"]

    def __init__(self, tag="", attrs={}, parent=None):
        assert tag
        assert isinstance(attrs, dict)
        self.tag = tag
        self.attrs = attrs
        self.children = []
        self.parent = parent
        if parent:
            self.parent.children.append(self)

    def copy(self):
        node = Element(self.tag, self.attrs.copy())
        node.children = self.children.copy()
        return node


class Parser(HTMLParser):
    """
    HTML Parser
    """

    def __init__(self):
        self.node = self.tree = None
        super().__init__()

    def handle_starttag(self, tag, attrs):
        self.node = Element(tag, dict(attrs), self.node)
        if self.tree is None:
            self.tree = self.node

    def handle_endtag(self, tag):
        assert self.node.tag == tag, "unexpected end of tag `%s` on line %s " % (
            tag,
            self.lineno,
        )
        self.node = self.node.parent


class Component:
    template = """<Label text="default template" />"""

    def __init_subclass__(cls, **kwargs):
        """
        When creating subclass of component, we need to register the component and it's custom attributes.
        """
        if cls not in _components:
            # Register the component class
            _components[cls.__name__.lower()] = cls
            # Collect _tkvue_attr_name
            attrs = {}
            for key in dir(cls):
                member = getattr(cls, key)
                attr_name = getattr(member, '_tkvue_attr_name', False)
                if attr_name:
                    attrs[attr_name] = member
            if attrs:
                cls._tkvue_attrs = attrs
        super().__init_subclass__(**kwargs)

    def __init__(self, master=None):
        # Check if template is provided.
        assert hasattr(self, "template"), "component %s must define a template" % self.__class__.__name__
        self.root = None

        # Collect _tkvue_expose members (function or properties)
        initial_data = {}
        for key in dir(self):
            value = getattr(self, key)
            if getattr(value, '_tkvue_expose', False):
                # Get bound method or property
                initial_data[key] = value

        # Initialize a Context used to store the state.
        self._context = _Context(initial_data=initial_data)

        # Read the template
        parser = Parser()
        if isinstance(self.template, bytes):
            parser.feed(self.template.decode("utf8"))
        else:
            parser.feed(self.template)

        # Generate the widget from template.
        # Make sure to skip registration as it should be done by caller.
        self.root = self._walk(master=master, tree=parser.tree, context=self._context, skip_register=True)

        # Replace mainloop implementation for TopLevel
        if hasattr(self.root, 'mainloop'):
            self.loop = asyncio.get_event_loop_policy().get_event_loop()
            self.mainloop = self._mainloop
            self.modal = self._modal

    def _find_attr(self, widget, attr_name):
        """
        Lookup attribute registry for the proper setter function.
        """
        # Lookup @attr() declared on class
        attr_mapping = getattr(widget.__class__, '_tkvue_attrs', False)
        if attr_mapping and attr_name in attr_mapping:
            func = attr_mapping.get(attr_name)
            return functools.partial(func, widget)

        # Lookup attribute registry
        attr_mapping = _attrs.get(attr_name, False)
        if attr_mapping:
            real_widget = _real_widget(widget)
            for cls, func in attr_mapping.items():
                if isinstance(widget, cls) or isinstance(real_widget, cls):
                    return functools.partial(func, widget)
        # Otherwise default to widget configure
        return functools.partial(_configure, widget, attr_name)

    def _bind_attr(self, widget, attr_name, value, context):
        """
        This function is called for each attributes mapping. Either for dual-binding (textvariable, variable) for dynamic binding with "{{ expr }}".

        attribute name with "variable" and "command" are treated differently to accomodate tkinter behavior.

        """
        real_widget = _real_widget(widget)
        # Find the setter function for tthis attribute using the registry.
        setter = self._find_attr(widget, attr_name)
        if attr_name.endswith('command'):
            # Wrap the command value as a function
            command = _create_command(value, context)
            setter(command)
        elif value.startswith("{{") and value.endswith("}}"):
            # Truncate curly braquet {{ }}
            value = value[2:-2].strip()
            # Create an observable from the expression
            obj = _computed_expression(value, context)
            # Check if dual data binding should be put in place.
            dual = attr_name.endswith('variable')
            # Evaluate expression a first time to get the variable type.
            if dual:
                # Resolve value first, to raise any exception.
                initial_value = obj.value
                # Make sure the observable is not readonly.
                assert getattr(
                    type(obj).value, 'fset', False
                ), f'{attr_name} attribute only support dual binding and required a state(). computed_property() or expression are not supported: f{value}'
                # Create a Tkinter variable to bind with.
                VarClass = _VARTYPES.get(type(initial_value), tkinter.StringVar)
                var = VarClass(master=real_widget, value=initial_value)
                # Whenever the variable get updated, update the context
                var.trace_add("write", lambda *args, var=var: setattr(obj, 'value', var.get()))
                # The update function will update the variable value.
                update_func = var.set
            else:
                # The update function is the setter it-self.
                update_func = setter
            # Register observer
            obj.subscribe(update_func)
            # Assign the value
            if dual:
                setter(var)
            else:
                setter(obj.value)
            # Handle disposal
            widget.bind(
                "<Destroy>",
                lambda event, obj=obj, update_func=update_func: obj.unsubscribe(update_func),
                add="+",
            )
        else:
            # Plain value with evaluation.
            setter(value)

    def _create_widget(self, master, tag, attrs, context, skip_register=False):
        """
        Resolve attributes values for the given widget.
        """
        assert tag
        assert attrs is not None

        # Get widget class.
        widget_cls = _widgets.get(tag, None)
        if widget_cls is None:
            widget_cls = _components.get(tag, None)
        assert widget_cls, "cannot find widget matching tag name: " + tag

        # Create widget.
        widget = widget_cls(master=master)
        assert not isinstance(widget, Component) or getattr(
            widget, 'root'
        ), 'Component not initialized properly. Did you forget to call `super().__init__(master)` in your custom component ?'

        #
        # Assign widget to variables.
        #
        if "id" in attrs:
            assert not hasattr(self, attrs["id"]), 'widget id conflict with existing value'
            setattr(self, attrs["id"], widget)
        #
        # Process each attributes.
        #
        for attr_name, value in attrs.items():
            self._bind_attr(widget, attr_name, value, context)
        # Apply all configure at once to minimize number of tk call.
        if getattr(widget, '_tkvue_configure', False):
            widget.configure(widget._tkvue_configure)
            delattr(widget, '_tkvue_configure')
        # By default, show the widget.
        if hasattr(widget, 'pack') and not skip_register:
            widget._tkvue_register = True
            visible = getattr(widget, '_tkvue_visible', True)
            _configure_visible(widget, visible)
        return widget

    def _walk(self, master, tree, context, skip_register=False):
        assert tree
        assert context
        # Create widget to represent the node.
        attrs = tree.attrs
        # Handle for loop
        if "for" in attrs:
            widget = Loop(
                tree,
                attrs["for"],
                master=master,
                context=context,
                widget_factory=self._walk,
            )
            tree.children = []
            return None
        try:
            # Create the widget with required attributes.
            widget = self._create_widget(master, tree.tag, attrs, context, skip_register=skip_register)
        except Exception as e:
            raise TemplateError(
                str(e)
                + " for tag <%s %s>"
                % (
                    tree.tag,
                    " ".join(['%s="%s"' % (k, v) for k, v in tree.attrs.items()]),
                )
            )
        # Support ScrolledFrame with `interior`
        interior = getattr(widget, "interior", widget)
        # Create child widgets.
        for child in tree.children:
            self._walk(master=interior, tree=child, context=context)
        return widget

    def __getattr__(self, name):
        """
        Override getattr to behave like a tkinter widget.
        """
        if 'root' not in self.__dict__:
            raise AttributeError(name)
        return getattr(self.root, name)

    def get_event_loop(self):
        """
        Return the asyncio event loop to be used by component subclass to execute asynchronous operation.
        """
        return self.loop

    def _mainloop(self):
        # Register asyncio callback when tkinter event loop is starting
        self.update_asyncio_command_name = self.root._register(self._update_asyncio)
        self.root.tk.call('after', 1, self.update_asyncio_command_name)
        # Start event loop
        self.root.mainloop()

    def _update_asyncio(self):
        """
        This function run a complete iteration of asyncio.
        """
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()
        self.root.tk.call('after', 50, self.update_asyncio_command_name)

    def _modal(self):
        """
        Following tkinter documentation to make a TopLevel windows Modal.
        https://tkdocs.com/tutorial/windows.html#dialogs
        """
        self.root.protocol("WM_DELETE_WINDOW", self.destroy)  # intercept close button

        # Dialog boxes should be transient with respect to their parent,
        # so that they will always stay on top of their parent window.  However,
        # some window managers will create the window as withdrawn if the parent
        # window is withdrawn or iconified.  Combined with the grab we put on the
        # window, this can hang the entire application.  Therefore we only make
        # the dialog transient if the parent is viewable.
        if self.root.master:
            toplevel = self.root.master.winfo_toplevel()
            if toplevel.winfo_viewable():
                self.root.transient(toplevel)  # dialog window is related to main
                self.root.tk.eval('tk::PlaceWindow %s widget %s' % (self.root, toplevel))
        self.root.wait_visibility()  # can't grab until window appears, so we wait
        self.root.grab_set()  # ensure all input goes to our window
        self.root.wait_window()
