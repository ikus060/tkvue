<p align="center">
<a href="LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/tkvue"></a>
<a href="https://gitlab.com/ikus-soft/tkvue/pipelines"><img alt="Build" src="https://gitlab.com/ikus-soft/tkvue/badges/master/pipeline.svg"></a>
<a href="https://sonar.ikus-soft.com/dashboard?id=tkvue"><img alt="Quality Gate Minarca Client" src="https://sonar.ikus-soft.com/api/project_badges/measure?project=tkvue&metric=alert_status"></a>
<a href="https://sonar.ikus-soft.com/dashboard?id=tkvue"><img alt="Coverage" src="https://sonar.ikus-soft.com/api/project_badges/measure?project=tkvue&metric=coverage"></a>
</p>

# TKvue

Declarative Tkinter UI using makup language with reactive data binding

# Translation

Tkvue provide a babael extention to extract static text from xml template.

You must configure babel to use the right plugin to extract the values from the templates.

    babel.cfg:

    [tkvue: **/templates/**.html]

Then You may use babel and other gettext tools to complete the translation using the `.po` file.

    python setup.py extract_messages
