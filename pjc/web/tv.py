#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module gathers request handlers for features related to the information screen displays.
"""

#TODO change page chaining to Ajax based mechanism (need to handle gracefully server interruption)

from collections import namedtuple
from operator import itemgetter
import json
import tornado.web
import httplib

from pjc.web.ui import UIRequestHandler, ProgressDisplayHandler, ScoresDisplayHandler, RankingDisplayHandler

__author__ = 'eric'


class TVDisplayHandler(UIRequestHandler):
    """ Base class for all TV displays.

    It is a specialized UIRequestHandler class, specifying the location of the templates.
    """

    @property
    def template_dir(self):
        """ Returns the path of the directory where templates are stored.

        To be overridden by subclasses.
        """
        return 'tv_display'


class SequencedDisplayHandler(TVDisplayHandler):
    """ Base class for handlers related to sequenced displays.

    It specializes `TVDisplayHandler` by handling the automatic display sequencing.

    Display delay is defined by the `get_delay` which can be overridden if the default value
    must be changed for a given display.
    """

    # tells if this display can be selected in the TV display settings form
    is_selectable = True

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

    def render(self, template_name, **kwargs):
        # if a display sequence is defined, insert the appropriate header to chain the pages
        if self.application.display_sequence:
            next_page = self.application.display_sequence.pop(0)
            self.application.display_sequence.append(next_page)
            self.add_header("refresh", "%d;/tv/%s" % (self.get_delay(), next_page))
        super(SequencedDisplayHandler, self).render(template_name, **kwargs)


class TVScores(SequencedDisplayHandler, ScoresDisplayHandler):
    """ Request handler for displaying the current scores.

    Used the progression report generator shared with the administration application.
    """
    display_label = "Scores"


class TVRanking(SequencedDisplayHandler, RankingDisplayHandler):
    """ Request handler for displaying the tournament final ranking.
    """
    display_label = "Classement"


class TVProgress(SequencedDisplayHandler, ProgressDisplayHandler):
    """ Request handler for displaying the tournament progression.

    Used the progression report generator shared with the administration application.
    """
    display_label = "Avancement"


class TVMessage(SequencedDisplayHandler):
    """ Request handler for the notification messages display and management.

    Supported verbs are :

        - GET : the display request
        - PUT : set the message to be displayed and its level
        - DELETE : remove the current message
    """

    # this display is managed and cannot be manually selected
    is_selectable = False

    display_name = 'message'

    @property
    def template_name(self):
        return "message"

    @property
    def template_args(self):
        msg = self.application.tv_message
        level, content = msg if msg else ('warning', 'Aucun message à afficher')
        return {
            'level': level,
            'content': content
        }

    def put(self):
        self.application.tv_message = json.loads(self.request.body)

    def delete(self):
        del self.application.tv_message


class TVStart(tornado.web.RequestHandler):
    """ Request handler for the display main entry point.

    It will redirect to the first page of the sequence, of issue a 404 error if no sequence is defined.
    """

    def get(self):
        if self.application.display_sequence:
            self.redirect("/tv/%s" % self.application.display_sequence[0])
        else:
            self.send_error(httplib.NOT_FOUND)


def get_selectable_displays():
    displays = []
    for url, cls in [url_spec[:2] for url_spec in handlers]:
        if issubclass(cls, SequencedDisplayHandler) and cls.is_selectable:
            displays.append((url.strip('/').split('/')[-1], cls.display_label))
    return sorted(displays, key=itemgetter(1))

handlers = [
    (r"/tv/scores", TVScores),
    (r"/tv/results", TVRanking),
    (r"/tv/message", TVMessage),
    (r"/tv/progress", TVProgress),
    (r"/tv[/]?", TVStart),
]

