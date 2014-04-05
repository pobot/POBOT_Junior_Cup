#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module gathers request handlers for features related to the information screen displays.
"""

from operator import itemgetter
import datetime
import httplib

from pjc.web.ui import UIRequestHandler


__author__ = 'eric'


class TVStart(UIRequestHandler):
    """ Request handler for the display main entry point.

    Displays the page skeleton with an empty main content. The real content will be requested by an Ajax request
    triggered by embedded Javascript in charge of managing the pages sequence.
    """

    def get(self):
        super(TVStart, self).render(
            "tv_display.html",
            title=self.PAGES_TITLE,
            application=self.application
        )


class SequencedDisplay(object):
    # default display delay
    _delay = 5

    @classmethod
    def get_delay(cls):
        """ Defines the delay before showing next display.

        Override in subclasses if you need a different delay for a given display.
        """
        return cls._delay

    @classmethod
    def set_delay(cls, delay):
        cls._delay = delay


class TVContent(UIRequestHandler, SequencedDisplay):
    TEMPLATES_DIR = 'tv_display'

    def get(self):
        if not self.application.display_sequence:
            self.send_error(httplib.NOT_FOUND)

        current_display = self.get_argument("current_display", None)
        if self.application.tv_message and current_display != "message":
            next_page = "message"
        else:
            next_page = self.application.display_sequence.pop(0)
            self.application.display_sequence.append(next_page)

        html = self.render_string(
            "%s/%s.html" % (self.TEMPLATES_DIR, next_page),
            application=self.application
        )
        self.write({
            'display_name': next_page,
            'content': html,
            'delay': self._delay,
            'clock': datetime.datetime.now().strftime("%H:%M")
        })
        self.finish()


def get_selectable_displays():
    displays = (
        ('scores', 'Scores'),
        ('progress', 'Avancement'),
        ('ranking', 'Classement')
    )
    return sorted(displays, key=itemgetter(1))

handlers = [
    (r"/tv/content", TVContent),
    (r"/tv[/]?", TVStart),
]

