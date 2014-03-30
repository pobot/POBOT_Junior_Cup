#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import json
import datetime

from pjc.tournament import ResearchEvaluationScore, TeamEvaluationScore
from pjc.web.lib import AppRequestHandler, parse_hhmm_time


__author__ = 'eric'


class WSHTeams(AppRequestHandler):
    def put(self):
        self.tournament.load_teams(json.loads(self.request.body))
        self.application.save_tournament()

    def get(self):
        res = [
            (i + 1, (team.name, team.level))
            for i, team in enumerate(self.tournament.teams)
        ]
        self.write({"teams": res})
        self.finish()


class WSHTeamBaseHandler(AppRequestHandler):
    PATH_ARGS = AppRequestHandler.PATH_ARGS + ['team_num']


class WSHTeam(WSHTeamBaseHandler):
    def get(self, team_num):
        team = self.tournament.get_team(team_num)
        self.write({"team": team.as_dict()})
        self.finish()


class WSHRoboticsScore(WSHTeamBaseHandler):
    PATH_ARGS = WSHTeamBaseHandler.PATH_ARGS + ['round_num']

    def get(self, team_num, round_num):
        _round = self.tournament.get_robotics_round(round_num)
        try:
            score = _round.scores[team_num]
            self.write({"score": score.as_dict()})
            self.finish()
        except KeyError:
            self.set_status(httplib.NOT_FOUND, 'Round not found (%d) for team (%d)' % (round_num, team_num))

    def put(self, team_num, round_num):
        score_data = json.loads(self.request.body)
        score_type = self.tournament.get_robotics_round(round_num).score_type
        score = score_type(**score_data)
        self.tournament.set_robotics_score(team_num, round_num, score)

        self.application.save_tournament()


class WSHResearchScore(WSHTeamBaseHandler):
    def get(self, team_num):
        try:
            score = self.tournament.research_evaluations.scores[team_num]
            self.write({"score": score.as_dict()})
            self.finish()
        except KeyError:
            self.set_status(httplib.NOT_FOUND, 'Score not found for team (%d)' % team_num)

    def put(self, team_num):
        score_data = json.loads(self.request.body)
        score = ResearchEvaluationScore(**score_data)
        self.tournament.set_research_evaluation(team_num, score)
        self.application.save_tournament()


class WSHJuryScore(WSHTeamBaseHandler):
    def get(self, team_num):
        try:
            score = self.tournament.jury_evaluations.scores[team_num]
            self.write({"score": score.as_dict()})
            self.finish()
        except KeyError:
            self.set_status(httplib.NOT_FOUND, 'Score not found for team (%d)' % team_num)

    def put(self, team_num):
        score_data = json.loads(self.request.body)
        score = TeamEvaluationScore(**score_data)
        self.tournament.set_team_evaluation(team_num, score)
        self.application.save_tournament()


class WSHTournamentStatus(AppRequestHandler):
    def get(self):
        status = self.tournament.get_completion_status()
        sections = ('robotics', 'research', 'jury')
        self.write({'status': dict(zip(sections, status))})
        self.finish()


class WSHRoboticsRoundResults(AppRequestHandler):
    PATH_ARGS = ['round_num']

    def get(self, round_num):
        _round = self.tournament.get_robotics_round(round_num)
        res = _round.get_results()
        self.write({'results': res})
        self.finish()


class WSHSingleResultsHandler(AppRequestHandler):
    def get(self):
        self.write({'results': self._get_results()})
        self.finish()


class WSHRoboticsResults(WSHSingleResultsHandler):
    def _get_results(self):
        return self.tournament.get_robotics_results()


class WSHResearchResults(WSHSingleResultsHandler):
    def _get_results(self):
        return self.tournament.get_research_evaluation_results()


class WSHJuryResults(WSHSingleResultsHandler):
    def _get_results(self):
        return self.tournament.get_team_evaluation_results()


class WSHFinalResults(WSHSingleResultsHandler):
    def _get_results(self):
        return self.tournament.get_final_ranking()


class WSHTournament(AppRequestHandler):
    def delete(self, *args, **kwargs):
        self.application.reset_tournament()


class WSHPlanning(AppRequestHandler):
    def put(self):
        data = json.loads(self.request.body)
        self.tournament.planning = [
            parse_hhmm_time(hhmm) for hhmm in data
        ]
        self.application.save_tournament()

    def get(self):
        self.write(json.dumps([t.strftime("%H:%M") for t in self.tournament.planning]))


class WSHDisplaySequence(AppRequestHandler):
    def put(self):
        self.application.display_sequence = json.loads(self.request.body)

    def get(self):
        self.write(json.dumps(self.application.display_sequence))


handlers = [
    (r"/api/tv/sequence", WSHDisplaySequence),
    (r"/api/tournament/teams", WSHTeams),
    (r"/api/tournament/team/(?P<team_num>\d)+/rob/(?P<round_num>\d)+", WSHRoboticsScore),
    (r"/api/tournament/team/(?P<team_num>\d)+/research", WSHResearchScore),
    (r"/api/tournament/team/(?P<team_num>\d)+/jury", WSHJuryScore),
    (r"/api/tournament/team/(?P<team_num>\d)+", WSHTeam),
    (r"/api/tournament/results/rob/(?P<round_num>\d)+", WSHRoboticsRoundResults),
    (r"/api/tournament/results/rob", WSHRoboticsResults),
    (r"/api/tournament/results/research", WSHResearchResults),
    (r"/api/tournament/results/jury", WSHJuryResults),
    (r"/api/tournament/results", WSHFinalResults),
    (r"/api/tournament/status", WSHTournamentStatus),
    (r"/api/tournament/planning", WSHPlanning),
    (r"/api/tournament[/]?", WSHTournament),
]