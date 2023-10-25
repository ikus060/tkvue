<p align="center">
<a href="LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/tkvue"></a>
<a href="https://gitlab.com/ikus-soft/tkvue/pipelines"><img alt="Build" src="https://gitlab.com/ikus-soft/tkvue/badges/master/pipeline.svg"></a>
<a href="https://sonar.ikus-soft.com/dashboard?id=tkvue"><img alt="Quality Gate Minarca Client" src="https://sonar.ikus-soft.com/api/project_badges/measure?project=tkvue&metric=alert_status"></a>
<a href="https://sonar.ikus-soft.com/dashboard?id=tkvue"><img alt="Coverage" src="https://sonar.ikus-soft.com/api/project_badges/measure?project=tkvue&metric=coverage"></a>
</p>

# TKVue

Declarative Tkinter UI using makup language with reactive data binding.

## Description

TKVue bring familiar advantages in web development to traditional development. This project allow you to create modern graphical user interface written in Python using Tkinter library.

TKVue provide a declarative language to build user interface with Markup language.

```xml
<Label text="Hello world!" />
```

TKVue provide databinding to quickly make your graphical user interface dynamic.

```xml
<ComboBox pack-side="left" pack-expand="1" values="['zero', 'one', 'two', 'three']" textvariable="{{ myvariable }}" />
<Label text="{{ myvariable }}" />
```

TKVue provide a babel entry point to support internationalization.

`babel.cfg`:

```xml
[tkvue: **/templates/**.tkml]
```

## Installation

TKVue is available on pypi and can be installed using `pip`.

```sh
pip install tkvue
```

## Usage

Once installed you may take a look at various examples available:

<https://gitlab.com/ikus-soft/tkvue/-/tree/master/doc/examples>

Help is welcome to write proper documentation about how to use TKVue.

## Support

If you need help or experience problem while using TKvue, open a ticket in [Gitlab](https://gitlab.com/ikus-soft/tkvue/-/issues/new).

## Result

Once you have customize the Tkinter themes, the result could be astonishing. Here the result of [Minarca](https://minarca.org) interface build using TKVue.

![Minarca Agent graphical user interface build with TKVue](https://gitlab.com/ikus-soft/tkvue/-/raw/master/doc/8result-welcome.png)

## Translation

Tkvue provide a babel extention to extract static text from xml template.

You must configure babel to use the right plugin to extract the values from the templates.

babel.cfg:

```ini
[tkvue: **/templates/**.tkml]
```

Then You may use babel and other gettext tools to complete the translation using the `.po` file.

```sh
python setup.py extract_messages
```

## See Also

Other Tkinter-related projects worth mentioning:

* [witkets](https://www.leandromattioli.com.br/witkets): Create Tkinter interface using XML similar to TKVue
* [ttkbootstrap](https://ttkbootstrap.readthedocs.io/): Theme extension for tkinter inspire by Bootstrap

## Changelog

## 2.1.6 ()

* Add support `@tkvue.computed()` annotation to register attribute dynamically
* Add support Python 3.12
* Ajust asyncio event loop to keep it running when mainloop() exit
* Add support Grid Geometry manager
* Add support `@tkvue.attr()` annotation to register attribute dynamically for custom component
* Add support `style` attribute on `TopLevel` to inherit background color
* Add `loop_idx` variable when using `for` attribute

## 2.1.5 (2023-10-18)

* Fix infinit recursion depth when root is not yet defined

## 2.1.4 (2023-07-26)

* Update background of ScrolledFrame when style is configure
* Register "wrap" attribute only for Label

## 2.1.3 (2023-07-25)

* Define minimum height for ScrolledFrame.

## 2.1.2 (2023-07-13)

* Fix display of scrollbar in ScrolledFrame when resize on Y axis.

## 2.1.1 (2023-07-12)

* Fix display of scrollbar on initialization.

## 2.1.0 (2023-04-20)

* Add many examples for self documentation
* Provide the `@tkvue.widget` annotation to register a new widget.
* Provide the `@tkvue.attr` annotation to register the custom attributes of the widget.

## 2.0.3 (2023-02-26)

* Support `resizable` attribute on TopLevel [not_resizable.py](https://gitlab.com/ikus-soft/tkvue/-/blob/master/src/tkvue/examples/not_resizable.py)
* Support `theme` attribute on TopLevel [theme.py](https://gitlab.com/ikus-soft/tkvue/-/blob/master/src/tkvue/examples/theme.py)

## 2.0.2 (2023-02-08)

* Add example to demonstrate usage of variables [dynamic.py](https://gitlab.com/ikus-soft/tkvue/-/blob/master/src/tkvue/examples/dynamic.py)
* Add example to demonstrate usage of `visible=` attribute to show or hide widget [dynamic_visible.py](https://gitlab.com/ikus-soft/tkvue/-/blob/master/src/tkvue/examples/dynamic_visible.py)
* Add example to demonstrate usage of `for=` attribute to create list of widget [dynamic_loop.py](https://gitlab.com/ikus-soft/tkvue/-/blob/master/src/tkvue/examples/dynamic_loop.py)
* Add example to demonstrate style customization [color.py](https://gitlab.com/ikus-soft/tkvue/-/blob/master/src/tkvue/examples/color.py)

### 2.0.1 (2023-01-16)

* Support assignment of `None` to `<Label image="..." >` to hide image [animated_gif.py](https://gitlab.com/ikus-soft/tkvue/-/blob/master/src/tkvue/examples/animated_gif.py)
* Add example to demonstrate usage of `<Progressbar>` [progressbar.py](https://gitlab.com/ikus-soft/tkvue/-/blob/master/src/tkvue/examples/progressbar.py)

### 2.0.0 (2022-12-13)

* Implement mainloop using asyncio to avoid multi-threading #1
* Increase default offset when displaying `<Tooltip>` to avoid flikering when user hover a widget
* `<ScrolledFrame>` inherit the background color from the style
* Show or hide scroll bar of `<ScrolledFrame>` when needed
* Pin version of black, isort and flake8
* Add support for `place` geometry manager

### 1.0.1 (2022-11-09)

* Fix license badge
* Declare babel entry point for translation
* Add combobox example
* Use private gitlab runner for running test

### 1.0.0 (2022-04-06)

* Initial version of TKVue writting for Minarca project
