#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib
import tornado.web
from tornado.web import HTTPError

__author__ = 'eric'


class AppRequestHandler(tornado.web.RequestHandler):
    PATH_ARGS = []
    tournament = None

    def initialize(self):
        self.tournament = self.application.tournament

    def prepare(self):
        for arg_name in self.PATH_ARGS:
            checker = getattr(self, 'check_' + arg_name, None)
            if checker:
                self.path_kwargs[arg_name] = checker(self.path_kwargs[arg_name])

    def check_team_num(self, value):
        team_num = int(value)
        if team_num in self.tournament.team_nums:
            return team_num
        else:
            raise HTTPError(httplib.NOT_FOUND, 'Team not found (%d)' % team_num)

    def check_round_num(self, value):
        round_num = int(value)
        if self.tournament.is_valid_round_num(round_num):
            return round_num
        else:
            raise HTTPError(httplib.NOT_FOUND, 'Round not found (%d)' % round_num)


