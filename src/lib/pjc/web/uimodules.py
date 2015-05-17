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

    def get_template_args(self, application, *args, **kwargs):
        """ Returns the keyword arguments to be passed to the body template as a dictionary.

        :rtype: dict
        """
        return {}

    def make_template_path(self):
        name = self.template_name
        if not name.endswith('.html'):
            name += '.html'
        return os.path.join(self.TEMPLATE_DIRECTORY, name)

    def render(self, application, *args, **kwargs):
        return self.render_string(
            self.make_template_path(),
            **self.get_template_args(application, *args, **kwargs)
        )


class AdminPageTitle(UIModuleBase):
    @property
    def template_name(self):
        return "admin_page_title"

    def render(self, title, *args, **kwargs):
        return self.render_string(
            self.make_template_path(),
            title=title
        )


class TVDisplayPageTitle(UIModuleBase):
    @property
    def template_name(self):
        return "display_page_title"

    def render(self, title, page_count=1, page_num=1, *args, **kwargs):
        return self.render_string(
            self.make_template_path(),
            title=title,
            page_count=page_count,
            page_num=page_num
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

    def get_template_args(self, application, page_num=1, tv_display=False):
        tournament = application.tournament
        times = tournament.planning
        planning = self.Planning(*[t.strftime("%H:%M") for t in times])

        now = datetime.datetime.now()
        current_time = now.time()

        status_rob, status_research, _ = tournament.get_completion_status()

        # transposes the robotics status table, so that lines are teams
        status_rob = zip(*status_rob)

        # builds the progress display data structure, made of a list of team status tuples, each one containing
        # the tree-state status of the robotics rounds and the research presentation.
        progress = []
        for team in tournament.teams(present_only=True):
            planning_times = team.planning.times
            robotics = [
                self.DONE if s
                else self.LATE if current_time > limit
                else self.NOT_DONE
                for s, limit in zip(status_rob[team.num-1], planning_times[:3])    # robotics_limits)
            ]
            research = self.DONE if status_research[team.num-1] \
                else self.LATE if current_time > planning_times[-1] \
                else self.NOT_DONE
            progress.append(self.Status(team.num, team.name, robotics[0], robotics[1], robotics[2], research))

        return {
            "planning": planning,
            "progress": paginate(progress, page_num, application.TV_PAGE_SIZE) if tv_display else progress,
            'tv_display': tv_display
        }


class NextSchedules(UIModuleBase):
    Schedule = namedtuple('Schedule', 'team_num team_name what detail')

    ITEM_LABELS = ['Epreuve 1', 'Epreuve 2', 'Epreuve 3', 'Exposé']

    @property
    def template_name(self):
        return "next_schedules"

    def get_template_args(self, application, tv_display=False, *args, **kwargs):
        # now = (datetime.datetime.now() - datetime.timedelta(hours=3, minutes=15)).time()
        now = datetime.datetime.now().time()
        next_appts = sorted([
            (time, team, team.planning.times.index(time))
            for team in application.tournament.teams(present_only=True)
            for time in team.planning.times if time >= now
        ], key=itemgetter(0, 1))

        def emergency(t):
            t_s, now_s = (_t.hour * 3600 + _t.minute * 60 + _t.second for _t in (t, now))
            dt = (t_s - now_s) / 60
            if dt > 10:
                return ''
            elif dt > 5:
                return 'text-warning'
            else:
                return 'text-danger'

        if tv_display:
            # if we are building the list for the TV displays, we keep only the first slots,
            # and try to make the list the most "natural" by not "truncating" the last one

            # start with the first 6
            default_count = 6
            wrk_appts = next_appts[:default_count]

            # if they are more items for the last listed slot, append them
            # (it will fit the display, since at the most we'll add only 2 more)
            if len(next_appts) > len(wrk_appts):
                last_slot = wrk_appts[-1][0]
                for appt in next_appts[default_count:]:
                    if appt[0] == last_slot:
                        wrk_appts.append(appt)
                    else:
                        break

            next_appts = wrk_appts

        schedules = [
            self.Schedule(
                team.num,
                team.name,
                self.ITEM_LABELS[item_index],
                team.planning[item_index]
            )
            for when, team, item_index in next_appts
        ]
        return {
            'schedules': schedules,
            'emergency_class': emergency
        }


class ScoresTable(UIModuleBase):
    """ Current scores table
    """
    ScoreDataItem = namedtuple('ScoreDataItem', 'team score')
    TeamItem = namedtuple('TeamItem', 'num name bonus')

    @property
    def template_name(self):
        return "scores"

    def get_template_args(self, application, page_num=1, tv_display=False):
        tournament = application.tournament
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
            "scores_data": paginate(scores_data, page_num, application.TV_PAGE_SIZE) if tv_display else scores_data
        }


class RankingTable(UIModuleBase):
    """ Current ranking table
    """

    ResultItem = namedtuple('ResultItem', 'rank teams')

    @property
    def template_name(self):
        return "ranking"

    def get_template_args(self, application, page_num=1, tv_display=False):
        tournament = application.tournament
        page_size = application.TV_PAGE_SIZE if tv_display else 99999

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
        if current_rank is not None:
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

