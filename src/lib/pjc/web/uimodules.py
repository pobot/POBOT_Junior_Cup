#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
import datetime
import os.path
from operator import itemgetter

from tornado.web import UIModule

from pjc.tournament import Tournament


__author__ = 'eric'


class UIModuleBase(UIModule):
    """ Base class for tournament UI modules implementation.

    Shares the rendering process common operations so that concrete module implementations
    have no boiler plate code to repeat over and over.
    """
    TEMPLATE_DIRECTORY = "uimodules"

    @property
    def template_name(self):
        """ Returns the name (without extension and path) of the body template.

        To be overridden by subclasses.
        """
        raise NotImplementedError()

    def get_template_args(self, application, **kwargs):
        """ Returns the keyword arguments to be passed to the body template as a dictionary.

        :rtype: dict
        """
        return {}

    def make_template_path(self):
        name = self.template_name
        if not name.endswith('.html'):
            name += '.html'
        return os.path.join(self.TEMPLATE_DIRECTORY, name)

    def render(self, application, *args):
        return self.render_string(
            self.make_template_path(),
            **self.get_template_args(application, *args)
        )


class AdminPageTitle(UIModuleBase):
    @property
    def template_name(self):
        return "admin_page_title"

    def render(self, title):
        return self.render_string(
            self.make_template_path(),
            title=title
        )


class TVDisplayPageTitle(UIModuleBase):
    @property
    def template_name(self):
        return "display_page_title"

    def render(self, title):
        return self.render_string(
            self.make_template_path(),
            title=title
        )


def paginate(data, page_num=1, page_size=0):
    if page_size:
        start = page_size * (page_num - 1)
        end = start + page_size
        return data[start:end]
    else:
        return data


class ProgressTable(UIModuleBase):
    """ Tournament progress table
    """
    Planning = namedtuple('Planning', 'rob1 rob2 rob3 research')
    Status = namedtuple('Status', 'team_num team_name rob1 rob2 rob3 research')

    # tournament item statuses
    DONE, NOT_DONE, LATE = range(3)

    @property
    def template_name(self):
        return "progress"

    def get_template_args(self, application, page_num=1):
        tournament = application.tournament
        times = tournament.planning
        planning = self.Planning(*[t.strftime("%H:%M") for t in times])
        page_size = application.TV_PAGE_SIZE

        now = datetime.datetime.now()
        today = now.date()
        planning_limits = [
            datetime.datetime.combine(today, t)
            for t in times
        ]
        robotics_limits = planning_limits[:3]
        research_limit = planning_limits[3]

        status_rob, status_research, _ = tournament.get_completion_status()

        # transposes the robotics status table, so that lines are teams
        status_rob = zip(*status_rob)

        # builds the progress display data structure, made of a list of team status tuples, each one containing
        # the tree-state status of the robotics rounds and the research presentation.
        progress = []
        for team_num in tournament.team_nums:
            team_name = tournament.get_team(team_num).name
            robotics = [
                self.DONE if s
                else self.LATE if now > limit
                else self.NOT_DONE
                for s, limit in zip(status_rob[team_num-1], robotics_limits)
            ]
            research = self.DONE if status_research[team_num-1] \
                else self.LATE if now > research_limit \
                else self.NOT_DONE
            progress.append(self.Status(team_num, team_name, robotics[0], robotics[1], robotics[2], research))

        return {
            "planning": planning,
            "progress": paginate(progress, page_num, page_size)
        }


class ScoresTable(UIModuleBase):
    """ Current scores table
    """
    ScoreDataItem = namedtuple('ScoreDataItem', 'team score')
    TeamItem = namedtuple('TeamItem', 'num name bonus')

    @property
    def template_name(self):
        return "scores"

    def get_template_args(self, application, page_num=1):
        tournament = application.tournament
        page_size = application.TV_PAGE_SIZE
        scores = tournament.get_compiled_scores()
        scores_data = [
            self.ScoreDataItem(
                self.TeamItem(team_num, team.name, team.bonus),
                # returns a CompiledScore with 0s replaced by blank strings
                Tournament.CompiledScore(*(item if item is not None else '' for item in score))
            )
            for team_num, team, score in [
                (team_num, tournament.get_team(team_num), score)
                for team_num, score in sorted(scores.items(), key=itemgetter(0))
            ]
        ]
        return {
            "scores_data": paginate(scores_data, page_num, page_size)
        }


class RankingTable(UIModuleBase):
    """ Current ranking table
    """

    ResultItem = namedtuple('ResultItem', 'rank teams')

    @property
    def template_name(self):
        return "ranking"

    def get_template_args(self, application, page_num=1):
        tournament = application.tournament
        page_size = application.TV_PAGE_SIZE

        def get_names(teams_nums):
            return (tournament.get_team(num).name for num in teams_nums)

        start = page_size * (page_num - 1)
        end = start + page_size

        result = []

        current_rank = None
        current_teams = []

        exploded = []
        for rank, teams in tournament.get_final_ranking():
            ranks = [rank] * len(teams)
            exploded.extend(zip(ranks, teams))

        for rank, team in exploded[start:end]:
            if rank != current_rank:
                if current_rank:
                    result.append(self.ResultItem(current_rank, get_names(current_teams)))
                    current_teams = []
                current_rank = rank
            current_teams.append(team)
        result.append(self.ResultItem(current_rank, get_names(current_teams)))

        return {
            'ranking': result
        }


class FormButtons(UIModuleBase):
    @property
    def template_name(self):
        return "form_buttons"

    def render(self, *args):
        return self.render_string(
            self.make_template_path()
        )
