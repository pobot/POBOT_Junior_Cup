#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
from datetime import datetime, timedelta
import subprocess
from tornado.web import HTTPError

from pjc.web.ui import UIRequestHandler, ProgressDisplayHandler, ScoresDisplayHandler, RankingDisplayHandler
from pjc.web.lib import parse_hhmm_time, format_hhmm_time
from pjc.tournament import ResearchEvaluationScore, JuryEvaluationScore
from pjc.web.tv import get_selectable_displays, SequencedDisplay
import pjc.pjc2014 as edition


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


class AdminHome(AdminUIHandler):

    @property
    def template_name(self):
        return "home"


class AdminProgress(AdminUIHandler, ProgressDisplayHandler):
    pass


class AdminScoresReport(AdminUIHandler, ScoresDisplayHandler):
    pass


class AdminRankingReport(AdminUIHandler, RankingDisplayHandler):
    pass


class AdminPlanningEditor(AdminUIHandler):
    FORM_FIELDS = ('rob1', 'rob2', 'rob3', 'research')

    @property
    def template_name(self):
        return "planning_editor"

    @property
    def template_args(self):
        return dict(
            zip(
                self.FORM_FIELDS,
                [format_hhmm_time(t) for t in self.tournament.planning]
            )
        )

    def post(self):
        times = [
            parse_hhmm_time(self.get_argument(name)) for name in self.FORM_FIELDS
        ]
        self.tournament.planning = times
        self.application.save_tournament()


class TVDisplaySettingsEditor(AdminUIHandler):

    @property
    def template_name(self):
        return "tvsettings_editor"

    @property
    def template_args(self):
        return {
            'selectable_displays': [
                (display_name, label, display_name in self.application.display_sequence)
                for display_name, label in get_selectable_displays()
            ],
            'display_pause': SequencedDisplay.get_delay()
        }

    def post(self):
        self.application.display_sequence = [
            d for d, _ in get_selectable_displays() if self.get_argument('seq_' + d, None)
        ]
        SequencedDisplay.set_delay(int(self.get_argument('display_pause', '5')))

        level, message = (self.get_argument('msg_' + fld) for fld in ('level', 'text'))
        self.application.tv_message = (level, message) if message else None


class SystemSettingsEditor(AdminUIHandler):

    @property
    def template_name(self):
        return "system_settings"

    @property
    def template_args(self):
        now = datetime.now()
        return {
            'current_date': now.strftime("%d/%m/%y"),
            'current_time': now.strftime("%H:%M")
        }

    def post(self):
        s_date = self.get_argument('date').split('/')
        s_time = self.get_argument('time').split(':')

        return_code = subprocess.call(["date", ''.join([s_date[1], s_date[0], s_time[0], s_time[1]])])
        if return_code != 0 :
            raise HTTPError(400, reason="code retour commande date = %d" % return_code)


def MMSS_to_seconds(s):
    minutes, seconds = s.split(':')
    return int(minutes) * 60 + int(seconds)


class ScoreEditorHandler(AdminUIHandler):
    """ The root class for all request handlers used by score editors.

    For making concrete handlers implementation as light as possible, a dynamic configuration of the instances
    is made based on the definition of the data type used to model the score. This is done in the local version of
    the `initialize()` method, using the data type provided by descendant classes.
    """

    # this attribute is set by the `@specs` decorator put on concrete classes to configure the data type of
    # their associated score data
    score_data_type = None

    @staticmethod
    def specs(score_data_type, template_name=None):
        """ Decorates concrete descendants of ScoreEditorHandler to configure the data type of associated ScoreData

        :param type score_data_type: the data type of the `ScoreData` instance manipulated the decorated editor
        :param str template_name: the name (with related path if needed) of the editor HTML template. If None, it up to the
            class to return the information as a property or an attribute named `template_name`
        """
        def decorator(clazz):
            clazz.score_data_type = score_data_type
            if template_name:
                clazz.template_name = template_name
            return clazz
        return decorator

    # these attributes will be automatically initialized at handler creation time
    ScoreTemplateData = None
    score_fields = None

    def initialize(self, *args, **kwargs):
        if not self.score_data_type:
            raise NotImplementedError('score_data_type has not be defined in handler class')

        super(ScoreEditorHandler, self).initialize()

        # Define the type of data transmitted to the template as a named tuple composed of the team number and name
        # and the fields provided by the score data type `items` attribute.
        self.ScoreTemplateData = namedtuple(
            'ScoreTemplateData', ('team_num', 'team_name') + self.score_data_type.items
        )

        # Define the list of form fields used to enter the scored points and penalties.
        # By default, it identical to the score data items.
        self.score_fields = self.score_data_type.items

    @property
    def template_name(self):
        raise NotImplementedError()

    @property
    def template_args(self):
        raise NotImplementedError()

    def post(self):
        raise NotImplementedError()


class AdminRoboticsRoundScoreEditor(ScoreEditorHandler):
    """ Abstract root class for specific robotics round scores editors.

    It implements all the processing with a data driven approach using explicit specification of the score
    components in concrete classes. This is made possible thanks to the "specs" decorator which inject these
    metadata in concrete classes. The decorator approach makes concrete editor implementation far simpler, since
    it relieves from manually overriding class attributes initialization. In addition, using the decorator and its
    named arguments makes the code auto-documented and more readable.
    """

    # this attribute is set by the `@robotics_score_editor` decorator put on concrete classes
    round_num = None

    @staticmethod
    def specs(score_data_type, round_num):
        """ Decorates concrete descendants of ScoreEditorHandler for robotics round score editors

        :param type score_data_type: the data type of the `ScoreData` instance manipulated the decorated editor
        :param int round_num: the number of the involved round, used to identify the associated HTML template
        """
        def decorator(clazz):
            clazz.score_data_type = score_data_type
            clazz.round_num = round_num
            clazz.template_name = "scores_editor/rob_%d" % round_num
            return clazz
        return decorator

    def initialize(self, *args, **kwargs):
        super(AdminRoboticsRoundScoreEditor, self).initialize(*args, **kwargs)

        # we need to override the score fields list default definition to exclude the match time
        self.score_fields = self.score_data_type.items[1:]

    @property
    def template_args(self):
        round_ = self.tournament.get_robotics_round(self.round_num)
        form_data = []
        for team_num in self.tournament.team_nums:
            team_name = self.tournament.get_team(team_num).name
            try:
                score = round_.get_team_score(team_num)
            except KeyError:
                # team did not played the round yet
                score = round_.score_type()

            # get the match duration as a "m:ss" string (no tens of minutes)
            duration = str(timedelta(seconds=score.total_time)).split(':', 1)[-1][1:]
            form_data.append(self.ScoreTemplateData(team_num, team_name, duration,*(score.as_tuple()[1:])))
        return {
            'scores': form_data
        }

    def post(self):
        round_ = self.tournament.get_robotics_round(self.round_num)
        for team_num in self.tournament.team_nums:
            total_time = MMSS_to_seconds(self.get_argument('total_time_%d' % team_num))
            if total_time:
                score = round_.score_type(
                    total_time=total_time,
                    **dict((
                        (arg, int(self.get_argument('%s_%d' % (arg, team_num))))
                        for arg in self.score_fields
                    ))
                )
                self.tournament.set_robotics_score(team_num, self.round_num, score)
            else:
                self.tournament.clear_robotics_score(team_num, self.round_num)
        self.application.save_tournament()


@AdminRoboticsRoundScoreEditor.specs(score_data_type=edition.Round1Score, round_num=1)
class AdminRoboticsRound1ScoreEditor(AdminRoboticsRoundScoreEditor):
    """ Editor for robotics rounds 1 scores."""


@AdminRoboticsRoundScoreEditor.specs(score_data_type=edition.Round2Score, round_num=2)
class AdminRoboticsRound2ScoreEditor(AdminRoboticsRoundScoreEditor):
    """ Editor for robotics rounds 2 scores."""


@AdminRoboticsRoundScoreEditor.specs(score_data_type=edition.Round3Score, round_num=3)
class AdminRoboticsRound3ScoreEditor(AdminRoboticsRoundScoreEditor):
    """ Editor for robotics rounds 3 scores."""


class EvaluationScoreEditor(ScoreEditorHandler):
    def get_evaluations(self):
        raise NotImplementedError()

    @property
    def template_args(self):
        evaluations = self.get_evaluations()
        form_data = []
        for team_num in self.tournament.team_nums:
            team_name = self.tournament.get_team(team_num).name
            try:
                score = evaluations.get_team_score(team_num)
            except KeyError:
                # team did not played the round yet
                score = evaluations.score_type()

            form_data.append(self.ScoreTemplateData(team_num, team_name, *(score.as_tuple())))
        return {
            'scores': form_data
        }

    def post(self):
        evaluations = self.get_evaluations()
        for team_num in self.tournament.team_nums:
            score = evaluations.score_type(
                **dict((
                    (arg, int(self.get_argument('%s_%d' % (arg, team_num))))
                    for arg in self.score_fields
                ))
            )
            evaluations.add_team_score(team_num, score)
        self.application.save_tournament()


@ScoreEditorHandler.specs(score_data_type=ResearchEvaluationScore, template_name="scores_editor/research")
class AdminResearchScoreEditor(EvaluationScoreEditor):
    def get_evaluations(self):
        return self.tournament.research_evaluations

    def post(self):
        shown_fld = self.score_fields[0]
        evaluation_fields = self.score_fields[1:]

        evaluations = self.get_evaluations()
        for team_num in self.tournament.team_nums:
            shown = self.get_argument('%s_%d' % (shown_fld, team_num), None) is not None
            if shown:
                score = evaluations.score_type(
                    **dict(
                        [(shown_fld, True)] +
                        [
                            (arg, int(self.get_argument('%s_%d' % (arg, team_num))))
                            for arg in evaluation_fields
                        ]
                    )
                )
                evaluations.add_team_score(team_num, score)
            else:
                evaluations.clear_team_score(team_num)
        self.application.save_tournament()


@ScoreEditorHandler.specs(score_data_type=JuryEvaluationScore, template_name="scores_editor/jury")
class AdminJuryScoreEditor(EvaluationScoreEditor):
    def get_evaluations(self):
        return self.tournament.jury_evaluations


handlers = [
    (r"/", AdminHome),
    (r"/admin/report/progress", AdminProgress),
    (r"/admin/report/scores", AdminScoresReport),
    (r"/admin/report/ranking", AdminRankingReport),
    (r"/admin/settings/planning", AdminPlanningEditor),
    (r"/admin/settings/tv_display", TVDisplaySettingsEditor),
    (r"/admin/settings/system", SystemSettingsEditor),
    (r"/admin/scores/rob1", AdminRoboticsRound1ScoreEditor),
    (r"/admin/scores/rob2", AdminRoboticsRound2ScoreEditor),
    (r"/admin/scores/rob3", AdminRoboticsRound3ScoreEditor),
    (r"/admin/scores/research", AdminResearchScoreEditor),
    (r"/admin/scores/jury", AdminJuryScoreEditor),
]

