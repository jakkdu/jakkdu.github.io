#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import time

AUTHOR = 'Insu Yun'
SITENAME = 'Insu Yun'
SITEURL = ''
PATH = 'content'

CUSTOM_CSS = 'assets/css/insu.css' + '?' + str(time.time()) # to do not cache CSS
THEME = 'themes/pelican-bootstrap3'
JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}
PLUGIN_PATHS = ['plugins']
PLUGINS = ['i18n_subsites']

STATIC_PATHS = ['assets']

TIMEZONE = 'America/New_York'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DEFAULT_PAGINATION = 10

HIDE_SIDEBAR = True

# pelican-bootstrap3 variables
DISPLAY_TAGS_ON_SIDEBAR = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
