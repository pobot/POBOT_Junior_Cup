#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from collections import namedtuple

from pjc.web.ui import UIRequestHandler, ProgressDisplayHandler, ScoresDisplayHandler

__author__ = 'eric'


class AdminUIHandler(UIRequestHandler):
    """ Base class for administration UI.

     It is a specialized UIRequestHandler class, specifying the location of the templates.
    """
    @property
    def template_dir(self):
        """ Returns the path of the directory where templates are stored.
        """
        return 'admin'


class AdminProgress(AdminUIHandler, ProgressDisplayHandler):
    """ Administration application home page.

    Displays the competition progression, using the progression report generator shared with
    the administration application.
    """
    pass


class AdminScoresReport(AdminUIHandler, ScoresDisplayHandler):
    pass


class AdminPlanningEditor(AdminUIHandler):
    # TODO to be continued

    @property
    def template_name(self):
        return "planning_editor"

    @property
    def template_args(self):
        return {
            "application": self.application
        }



handlers = [
    (r"/", AdminProgress),
    (r"/admin/progress", AdminProgress),
    (r"/admin/scores", AdminScoresReport),
    (r"/admin/planning", AdminPlanningEditor),
]

