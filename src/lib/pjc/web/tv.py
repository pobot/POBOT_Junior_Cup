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
    """ Mixin adding the sequenced display feature.
    """
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
    """ Handler providing the content part of the displays on TV sets.

    Javascript code of the HTML page periodically uses this request to get the next content
    to put on the public address TV screens.
    """
    TEMPLATES_DIR = 'tv_display'
    display_saved_context = {}

    def get(self):
        client, port = self.request.connection.context.address

        if self.application.client_is_known(client):
            current_display = self.get_argument("current_display", None)
            current_page = int(self.get_argument("current_page", '1'))
        else:
            current_display, current_page = None, 0

        sequence = self.application.get_client_sequence(client)
        if self.application.debug:
            self.application.log.debug("seq(%s) = %s", client, sequence)
        if not sequence:
            self.send_error(httplib.NOT_FOUND)

        # handle the case where the server is restarted while a TV was displaying a message
        if current_display == "message" and not self.application.tv_message:
            current_display = None

        if not current_display:
            current_display = sequence.pop(0)

        if self.application.debug:
            self.application.log.debug("curdisp/curpage(%s) = %s/%s", client, current_display, current_page)

        if self.application.tv_message and current_display != "message":
            self.display_saved_context[client] = (current_display, current_page)
            next_display = "message"
            next_page = 1

        else:
            # restore the context as it was when the message was inserted in the sequence
            if client in self.display_saved_context:
                if self.application.debug:
                    self.application.log.debug("restoring display context for client %s", client)
                current_display, current_page = self.display_saved_context[client]
                del self.display_saved_context[client]

            if current_page < self.application.required_pages(current_display):
                next_display = current_display
                next_page = current_page + 1
            else:
                sequence.append(current_display)
                next_display = sequence.pop(0)
                next_page = 1

        if self.application.debug:
            self.application.log.debug("nextdisp/nextpage(%s) = %s/%s", client, next_display, next_page)

        html = self.render_string(
            "%s/%s.html" % (self.TEMPLATES_DIR, next_display),
            application=self.application,
            page_num=next_page,
            page_size=self.application.TV_PAGE_SIZE,
            page_count=self.application.required_pages(next_display)
        )
        self.write({
            'display_name': next_display,
            'current_page': next_page,
            'content': html,
            'delay': self._delay,
            'clock': datetime.datetime.now().strftime("%H:%M")

        })
        self.finish()


def get_selectable_displays():
    displays = (
        ('scores', 'Scores'),
        ('progress', 'Avancement'),
        ('ranking', 'Classement'),
        ('next_schedules', 'Prochains passages')
    )
    return sorted(displays, key=itemgetter(1))

handlers = [
    (r"/tv/content", TVContent),
    (r"/tv[/]?", TVStart),
]

