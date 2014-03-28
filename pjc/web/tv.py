#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module gathers request handlers for features related to the information screen displays.
"""

from collections import namedtuple
import json
from operator import itemgetter
import datetime
import tornado.web
import httplib

from pjc.tournament import Tournament
from pjc.web.ui import UIRequestHandler, ProgressDisplayHandler, ScoresDisplayHandler

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

    @classmethod
    def get_delay(cls):
        """ Defines the delay before showing next display.

        Override in subclasses if you need a different delay for a given display.
        """
        return 5;

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
    pass


class TVRanking(SequencedDisplayHandler):
    """ Request handler for displaying the tournament final ranking.
    """
    ResultItem = namedtuple('ResultItem', 'team score')

    @property
    def template_name(self):
        return "ranking"

    @property
    def template_args(self):
        def get_names(teams_nums):
            return (self.tournament.get_team(num).name for num in teams_nums)

        ranking = [
            self.ResultItem(rank, get_names(teams))
            for rank, teams in self.tournament.get_final_ranking()
        ]
        return {
            'ranking': ranking
        }


class TVProgress(SequencedDisplayHandler, ProgressDisplayHandler):
    """ Request handler for displaying the tournament progression.

    Used the progression report generator shared with the administration application.
    """
    pass


class TVMessage(SequencedDisplayHandler):
    """ Request handler for the notification messages display and management.

    Supported verbs are :

        - GET : the display request
        - PUT : set the message to be displayed and its level
        - DELETE : remove the current message
    """
    REL_PATH = 'message'

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
        self._update_display_sequence()

    def delete(self):
        del self.application.tv_message
        self._update_display_sequence()

    def _update_display_sequence(self, msg):
        """ Updates the display sequence depending on the presence of a message to be displayed.
        """
        if self.application.tv_message:
            if self.REL_PATH not in self.application.display_sequence:
                self.application.display_sequence.insert(0, self.REL_PATH)
        else:
            if self.REL_PATH in self.application.display_sequence:
                self.application.display_sequence.remove(self.REL_PATH)


class TVStart(tornado.web.RequestHandler):
    """ Request handler for the display main entry point.

    It will redirect to the first page of the sequence, of issue a 404 error if no sequence is defined.
    """

    def get(self):
        if self.application.display_sequence:
            self.redirect("/tv/%s" % self.application.display_sequence[0])
        else:
            self.send_error(httplib.NOT_FOUND)


handlers = [
    (r"/tv/scores", TVScores),
    (r"/tv/results", TVRanking),
    (r"/tv/message", TVMessage),
    (r"/tv/progress", TVProgress),
    (r"/tv[/]?", TVStart),
]
