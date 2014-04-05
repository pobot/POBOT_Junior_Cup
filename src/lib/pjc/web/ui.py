#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from collections import namedtuple

from pjc.web.lib import AppRequestHandler


__author__ = 'eric'


class UIRequestHandler(AppRequestHandler):
    """ Base class for all TV displays.

    The render process uses the templates extension mechanism. This class takes care of the generic part of the
    process. In order to minimise the amount of code to be written in descendants (especially invoking super here
    and there), it implements to whole chain and relies on callbacks to provided the required parameters and data.

    To implement a concrete display, subclass this one and implement the `template_dir` and `template_name` methods for
    providing the location of the template to be used for the page rendering.

    If the template uses arguments, you can override the `template_args` method (which returns an empty dictionary
    by default), so that it returns a dictionary containing the keyword arguments to be passed to the template.
    """
    PAGES_TITLE = "POBOT Junior Cup"

    def get(self):
        _template_name = self.template_name
        if not _template_name.endswith('.html'):
            _template_name += '.html'
        self.render(
            os.path.join(self.template_dir, _template_name),
            title=self.PAGES_TITLE,
            **self.template_args
        )

    @property
    def template_dir(self):
        """ Returns the path of the directory where templates are stored.

        To be overridden by subclasses.
        """
        raise NotImplementedError()

    @property
    def template_name(self):
        """ Returns the name (without extension and path) of the body template.

        To be overridden by subclasses.
        """
        raise NotImplementedError()

    @property
    def template_args(self):
        """ Returns the keyword arguments to be passed to the body template as a dictionary.

        :rtype: dict
        """
        return {}


class ProgressDisplayHandler(UIRequestHandler):
    """ Shared request handler for displaying the tournament progress report.

    Used by TV display (`pjc.web.tv.TVProgress`) and administration (`pjc.web.admin.AdminHome`) pages.
    """
    Planning = namedtuple('Planning', 'rob1 rob2 rob3 research')
    Status = namedtuple('Status', 'team rob1 rob2 rob3 research')

    # tournament item statuses
    DONE, NOT_DONE, LATE = range(3)

    @property
    def template_name(self):
        # depending on the context (TV display or administration application), the template file will be
        # looked for in the associated directory, and thus can be customized to fit the display needs.
        return "progress"

    @property
    def template_args(self):
        return {
            "application": self.application
        }


class ScoresDisplayHandler(UIRequestHandler):
    """ Shared request handler for displaying the current scores report.

    Used by TV display (`pjc.web.tv.TVScores`) and administration (`pjc.web.admin.AdminScoreReport`) pages.
    """
    @property
    def template_name(self):
        # depending on the context (TV display or administration application), the template file will be
        # looked for in the associated directory, and thus can be customized to fit the display needs.
        return "scores"

    @property
    def template_args(self):
        return {
            "application": self.application
        }


class RankingDisplayHandler(UIRequestHandler):
    """ Shared request handler for displaying the current ranking report.

    Used by TV display (`pjc.web.tv.TVRanking`) and administration (`pjc.web.admin.AdminRankingReport`) pages.
    """
    @property
    def template_name(self):
        # depending on the context (TV display or administration application), the template file will be
        # looked for in the associated directory, and thus can be customized to fit the display needs.
        return "ranking"

    @property
    def template_args(self):
        return {
            "application": self.application
        }
