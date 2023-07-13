# Copyright (C) 2023 IKUS Software. All rights reserved.
# IKUS Software inc. PROPRIETARY/CONFIDENTIAL.
# Use is subject to license terms.
import asyncio
import collections
import functools
import logging
import os
import tkinter
from html.parser import HTMLParser
from itertools import chain
from tkinter import ttk

try:
    from gettext import gettext
except ImportError:

    def gettext(message):
        return message


logger = logging.getLogger(__name__)


_components = {}  # Component registry.
_widgets = {}  # Widget registry
_attrs = {}  # Attribute registry

_default_basename = None
_default_classname = "Tkvue"
_default_screenname = None
_default_icons = None
_default_theme = None
_default_theme_source = None


def attr(widget_cls, attr_name):
    """
    Function decorator to register an special attribute definition for a Widget.
    """

    def decorate(f):
        if isinstance(widget_cls, (list, tuple)):
            for c in widget_cls:
                _attrs[(c, attr_name)] = f
        else:
            _attrs[(widget_cls, attr_name)] = f
        return f

    return decorate


def widget(widget_name):
    """
    Function decorator to register a widget.
    """

    def decorate(f):
        _widgets[widget_name] = f
        return f

    return decorate


#
# Register all ttk widget
#
for a in dir(ttk):
    cls = getattr(ttk, a)
    if type(cls) == type and issubclass(cls, ttk.Widget):
        _widgets[a.lower()] = cls


def configure_tk(
    basename=None,
    classname="Tk",
    screenname=None,
    icon=[],
    theme=None,
    theme_source=None,
):
    """
    Use to configure default instance of Tkinter created by tkvue.
    """
    assert theme_source is None or os.path.isfile(theme_source)

    # Disable Tkinter default root creation
    tkinter.NoDefaultRoot()
    global _default_basename, _default_classname, _default_screenname, _default_icons, _default_theme, _default_theme_source
    _default_basename = basename
    _default_classname = classname
    _default_screenname = screenname
    _default_icons = icon
    _default_theme = theme
    _default_theme_source = theme_source


@widget('toplevel')
def create_toplevel(master=None):
    """
    Used to create a TopLevel window.
    """

    global _default_basename, _default_classname, _default_screenname, _default_icons, _default_theme, _default_theme_source
    if master is None:
        root = tkinter.Tk(
            baseName=_default_basename,
            className=_default_classname,
            screenName=_default_screenname,
        )
        root.report_callback_exception = lambda exc, val, tb: logger.exception("Exception in Tkinter callback")
        if _default_theme_source:
            root.call("source", _default_theme_source)
        if _default_theme:
            root.call("ttk::setTheme", _default_theme)
        if _default_icons:
            root.iconphoto(True, *_default_icons)
    else:
        root = tkinter.Toplevel(master)

    def _update_bg(event):
        # Skip update if event is not related to TopLevel widget.
        if root != event.widget:
            return
        # Update TopLevel background according to TTK Style.
        bg = ttk.Style(master=root).lookup("TFrame", "background")
        root.configure(bg=bg)

    root.bind("<<ThemeChanged>>", _update_bg)

    return root


def computed(func):
    """
    Create computed attributes.
    """
    assert callable(func)
    func.__computed__ = True
    return func


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


class Context(collections.abc.MutableMapping):
    def __init__(self, initial_data={}, parent=None):
        "Create a new root context"
        for key, value in initial_data.items():
            assert hasattr(value, "__hash__"), "unhashable type '%s' for key %s" % (
                type(value),
                key,
            )
        self._map = initial_data.copy()
        self._parent = parent
        self._maps = [self._map]
        self._track = None
        self._watchers = {}
        if self._parent is not None:
            self._maps += self._parent._maps

    def new_child(self, **kwargs):
        "Make a child context, inheriting enable_nonlocal unless specified"
        return self.__class__(kwargs, parent=self)

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        if key.startswith("_"):
            super().__setattr__(key, value)
        else:
            self[key] = value

    set = __setattr__

    def __getitem__(self, key):
        for m in self._maps:
            if key in m:
                break
        value = m[key]
        if hasattr(value, "__computed__"):
            return value(self)
        else:
            if self._track is not None:
                self._track.append(key)
            return value

    def __setitem__(self, key, value):
        assert hasattr(value, "__hash__"), "unhashable type '%s' for key %s" % (
            type(value),
            key,
        )
        # Dispatch setter to parent context
        if key not in self._map and self._parent:
            self._parent.__setitem__(key, value)
            return
        # Get previous value for comparaison
        prev_value = self._map[key]
        # Raise an error if the key is a computed value. Those cannot be updated.
        if hasattr(prev_value, "__computed__"):
            raise ValueError("cannot set computed attribute")
        # Save the new value.
        self._map[key] = value
        # If value changed, notify
        if prev_value != value:
            self._notify(key, value)

    def __delitem__(self, key):
        del self._map[key]

    def __len__(self):
        return sum(map(len, self._maps))

    def __iter__(self, chain_from_iterable=chain.from_iterable):
        return chain_from_iterable(self._maps)

    def __contains__(self, key, any=any):
        return any(key in m for m in self._maps)

    def __repr__(self, repr=repr):
        return " -> ".join(map(repr, self._maps))

    def _notify(self, key, new):
        # Notify watchers.
        items = list(self._watchers.items())
        for (expr, func), (dependencies, context) in items:
            # Check if dependencies matches our key
            # Also check if the watcher is still in the list since
            # the list may get updated during notification.
            if key in dependencies and (expr, func) in self._watchers:
                func(context.watch(expr, func))

    def eval(self, expr, **kwargs):
        """
        Evaluate the given expression.
        """
        if kwargs:
            return self.new_child(**kwargs).eval(expr)
        else:
            try:
                return eval(expr, None, self)
            except Exception as e:
                raise Exception("exception occured while evaluating expression `%s`" % expr) from e

    def watch(self, expr, func):
        """
        Adding watcher on the given expression.
        """
        assert expr
        assert func and hasattr(func, "__call__")
        if expr in self._map and not hasattr(self._map[expr], "__computed__"):
            dependencies = set([expr])
            v = self.get(expr)
        else:
            self._track = []
            v = self.eval(expr)
            dependencies = set(self._track)
            self._track = None
        # Register watchers on appropriate context depending where variable is declared
        context = self
        while context:
            dep = [d for d in dependencies if d in context._map]
            if dep:
                context._watchers[(expr, func)] = (dep, self)
            context = context._parent
        return v

    def unwatch(self, expr, func):
        """
        Removing associated watchers.
        """
        context = self
        while context:
            if (expr, func) in context._watchers:
                del context._watchers[(expr, func)]
            context = context._parent

    def __bool__(self):
        return True


def _configure(widget, key, value):
    widget.configure(**{key: value})


@attr((tkinter.Tk, tkinter.Toplevel), "geometry")
def _configure_geometry(widget, value):
    """
    Configure geometry on TopLevel
    """
    widget.geometry(value)


@attr((tkinter.Tk, tkinter.Toplevel), "resizable")
def _configure_resizable(widget, value):
    assert isinstance(value, str), f"{value} should be a string value: <width> <height>"
    widget.resizable(*value.partition(' ')[0::2])


@attr((tkinter.Tk, tkinter.Toplevel), "title")
def _configure_title(widget, value):
    assert isinstance(value, str), f"{value} should be a string"
    widget.title(gettext(value))


@attr(ttk.Widget, "text")
def _configure_text(widget, value):
    widget.configure(text=gettext(value))


@attr((ttk.Button, ttk.Checkbutton), "selected")
def _configure_selected(widget, value):
    widget.state(["selected" if value else "!selected", "!alternate"])


@attr(ttk.Widget, "image")
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
        widget._event_id = widget.after(150, _next_frame)

    def _stop_animation(unused=None):
        if getattr(widget, "_func_id", None):
            widget.unbind("<Destroy>", widget._func_id)
            del widget._func_id

        if getattr(widget, "_event_id", None):
            widget.after_cancel(widget._event_id)
            del widget._event_id

    def _start_animation(unused=None):
        if not getattr(widget, "_event_id", None):
            widget._event_id = widget.after(100, _next_frame)
        if not getattr(widget, "_func_id", None):
            widget._func_id = widget.bind("<Destroy>", _stop_animation)

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


@attr(ttk.Widget, "wrap")
def _configure_wrap(widget, wrap):
    # Support Text wrapping
    if wrap.lower() in ["true", "1"]:
        widget.bind(
            "<Configure>",
            lambda e: widget.configure(wraplen=widget.winfo_width()),
            add="+",
        )


@attr(tkinter.Tk, "theme")
def _configure_theme(widget, value):
    # Defined on TopLevel
    ttk.Style(master=widget).theme_use(value)


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

    def configure(self, cnf={}, **kw):
        # Text
        self.text = cnf.pop("text", kw.pop("text", self.text))
        # Timeout
        timeout = cnf.pop("timeout", kw.pop("timeout", self.timeout))
        assert timeout >= 0, "timeout should be greater or equals zero (0): %s" % timeout
        self.timeout = timeout
        # Width
        self.width = cnf.pop("width", kw.pop("width", self.width))
        # Pass other config to widget.
        super().configure(cnf, **kw)

    def cget(self, key):
        if key == "text":
            return self.text
        elif key == "timeout":
            return self.timeout
        elif key == "width":
            return self.width
        return super().cget(key)

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
        assert " in " in for_expr, "for expression must have the for <target> in <list>"
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
        self.loop_target, unused, self.loop_items = for_expr.partition(" in ")
        items = context.eval(self.loop_items)
        # Register our self
        context.watch(self.loop_items, self.update_items)
        # Children shildren
        self.update_items(items)

    def create_widget(self, idx):
        child_var = {self.loop_target: computed(lambda context: context.eval(self.loop_items)[idx])}
        child_context = self.context.new_child(**child_var)
        return self.widget_factory(master=self.master, tree=self.tree, context=child_context)

    def update_items(self, items):
        # We may need to create new widgets.
        while self.idx < len(items):
            widget = self.create_widget(self.idx)
            # Make sure to pack widget at the right location.
            # TODO Fix parent when all item get deleteds
            widget.pack(after=self.widgets[-1] if self.widgets else None)
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
        self.canvas = tkinter.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=self.vscrollbar.set)
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
        self.canvas.bind("<<ThemeChanged>>", self._update_bg)

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

    def _update_bg(self, event):
        style_name = self.cget('style') or 'TFrame'
        bg = ttk.Style(master=self.master).lookup(style_name, "background")
        self.canvas.configure(bg=bg)
        self.interior.configure(style=style_name)


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


class TkVue:
    def __init__(self, component, master):
        assert component
        assert hasattr(component, "template"), "component %s must define a template" % component.__class__.__name__

        # Keep reference to the component.
        self.component = component
        if not hasattr(self.component, "data"):
            self.component.data = Context()

        # Read the template
        parser = Parser()
        if isinstance(component.template, bytes):
            parser.feed(component.template.decode("utf8"))
        else:
            parser.feed(component.template)

        # Generate the widget from template.
        self.component.root = self._walk(master=master, tree=parser.tree, context=self.component.data)

    def _bind_attr(self, widget, value, func, context):
        if value.startswith("{{") and value.endswith("}}"):
            expr = value[2:-2]
            # Register observer
            expr_value = context.watch(expr, func)
            # Assign the value
            func(expr_value)
            # Handle disposal
            widget.bind(
                "<Destroy>",
                lambda event, expr=expr, func=func: context.unwatch(expr, func),
                add="+",
            )
        else:
            # Plain value with evaluation.
            func(value)

    def _dual_bind_attr(self, widget, value, attr, context):
        assert value.startswith("{{") and value.endswith("}}")
        expr = value[2:-2].strip()
        # Get current variable type.
        # And create appropriate variable type.
        var_type = type(context.eval(expr))
        if var_type == int:
            var = tkinter.IntVar(master=widget)
        elif var_type == float:
            var = tkinter.DoubleVar(master=widget)
        elif var_type == bool:
            var = tkinter.BooleanVar(master=widget)
        else:
            var = tkinter.StringVar(master=widget)
        # Support dual-databinding
        self._bind_attr(widget, value, lambda new_value, var=var: var.set(new_value), context)
        var.trace_add("write", lambda *args, var=var: context.set(expr, var.get()))
        # TODO trace_remove
        widget.configure({attr: var})

    def _bind_attrs(self, master, tag, attrs, context):
        """
        Resolve attributes values for the given widget.
        Then apply them using configure() and pack()
        """
        assert tag
        assert attrs is not None

        # Get widget class.
        widget_cls = _widgets.get(tag, None)
        if widget_cls is None:
            widget_cls = _components.get(tag, None)
        assert widget_cls, "cannot find widget matching tag name: " + tag

        # The "command" attribute must be pass during widget construction.
        kwargs = {}
        if "command" in attrs:
            kwargs["command"] = self._create_command(attrs["command"], context)

        #
        # Create widget.
        #
        widget = widget_cls(master=master, **kwargs)

        #
        # Assign widget to variables.
        #
        if "id" in attrs:
            setattr(self.component, attrs["id"], widget)

        # Check if args contains pack or :pack
        # If the widget doesn't need to be pack. We don't need to compute changes.
        if hasattr(widget, 'pack'):
            geo = list(set([k.split('-')[0] for k in attrs.keys() if k.startswith("pack-") or k.startswith("place-")]))
            if len(geo) > 1:
                raise ValueError('widget can only use a single geometry manager: %s' % geo)
            geo = geo[0] if geo else 'pack'
            geo_attrs = {k.split('-')[1]: v for k, v in attrs.items() if k.startswith(geo + "-")}
            if "visible" in attrs:
                self._bind_attr(
                    widget,
                    attrs["visible"],
                    lambda value, geo_attrs=geo_attrs, geo=geo: getattr(widget, geo)(geo_attrs)
                    if value
                    else widget.forget(),
                    context,
                )
            else:
                getattr(widget, geo)(geo_attrs)
        for k, v in attrs.items():
            if k in ["id", "command", "visible"] or k.startswith("pack-") or k.startswith("place-"):
                # ignore pack attribute
                continue
            elif k in ["textvariable", "variable"]:
                self._dual_bind_attr(widget, v, k, context)
            elif k == "selected":
                # Special attribute for Button, Checkbutton
                self._bind_attr(
                    widget, v, lambda value: widget.state(["selected" if value else "!selected", "!alternate"]), context
                )
            else:
                # Lookup attribute registry
                func = [func for a, func in _attrs.items() if a[1] == k if isinstance(widget, a[0])]
                if func:
                    func = functools.partial(func[0], widget)
                else:
                    # Otherwise default to widget configure
                    func = functools.partial(_configure, widget, k)
                self._bind_attr(widget, v, func, context)

        return widget

    def _create_command(self, value, context):
        """
        Command may only be define when creating widget.
        So let process this attribute before creating the widget.
        """
        if value.startswith("{{"):
            raise ValueError("cannot use binding ({{) in `command` attribute: " + value)
        available_functions = {
            k: getattr(self.component, k) for k in dir(self.component) if callable(getattr(self.component, k))
        }
        # May need to adjust this to detect expression.
        if "(" in value or "=" in value:

            def func():
                return context.eval(value, **available_functions)

        else:
            func = available_functions.get(value, None)
            if func is None or not hasattr(func, "__call__"):
                raise ValueError(
                    '`command` attribute must define a function to be called `function_name(arg1, arg2)`: ' + value
                )
        return func

    # TODO Make this function static.
    def _walk(self, master, tree, context):
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
            widget = self._bind_attrs(master, tree.tag, attrs, context)
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


class Component:
    template = """<Label text="default template" />"""

    def __init_subclass__(cls, **kwargs):
        if cls not in _components:
            _components[cls.__name__.lower()] = cls
        super().__init_subclass__(**kwargs)

    def __init__(self, master=None):
        self.root = None
        self.vue = TkVue(self, master=master)
        # Replace mainloop implementation for TopLevel
        if hasattr(self.root, 'mainloop'):
            self.mainloop = self._mainloop

    def __getattr__(self, name):
        return getattr(self.root, name)

    def get_event_loop(self):
        return asyncio.get_event_loop()

    def _mainloop(self):
        asyncio.run(self._async_mainloop())

    async def _async_mainloop(self):
        '''
        An asynchronous implementation of tkinter mainloop
        '''
        while True:
            try:
                self.root.winfo_exists()  # Throw TclError if the main Windows is destroyed
                await self._update_root()
            except tkinter.TclError:
                break
            await asyncio.sleep(0.01)

    async def _update_root(self):
        """
        This coroutine runs a complete iteration of the tkinter event loop for a
        root. It yields in between each individual event, which prevents it from
        blocking the asyncio event loop. It runs until there are no more events in
        the queue, then returns, allowing the caller to do other tasks or sleep
        afterwards. This keeps CPU load low. Generally clients will never need to
        call this function; it should only be used internally by async_mainloop.
        """
        while self.root.dooneevent(tkinter._tkinter.DONT_WAIT):
            await asyncio.sleep(0)
