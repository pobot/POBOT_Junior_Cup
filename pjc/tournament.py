#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'eric'

from operator import itemgetter
from collections import namedtuple
import datetime

MATCH_DURATION = 150    # secs


class Score(object):
    """ Root class implementing a team score for a round.

    It must be sub-classed to take in account the way points are counted for a given round, for instance when
    different actions give a specific point sub-count.
    """
    items = ()

    def evaluate(self):
        """ Returns the global point count, following the sub-counts aggregation rules.

         :returns int: the point count
        """
        raise NotImplementedError()

    def as_dict(self):
        return dict([(item[1:], getattr(self, item)) for item in self.items])


class RoboticsScore(Score):
    """ Specialized score for robotics rounds.

    It shares invariants, which are :
        - the round total time (in seconds)
    """
    items = ('_total_time',)
    _total_time = 0

    def __init__(self, total_time):
        """
        :param int total_time: final stopwatch value in seconds
        """
        self._total_time = total_time

    @classmethod
    def max_action_credits(cls):
        """ Returns the maximum point count corresponding to rewarded actions.

        It is used to know if the competitor has completely fulfilled the mission or not.

        It is specific to each round, and thus must be provided by sub-classes.
        """
        raise NotImplementedError()

    def evaluate_action_credits(self):
        """ Returns the total of action credits, taking in account completed actions result and penalties.

        It is specific to each round, and thus must be provided by sub-classes.
        """
        raise NotImplementedError()

    def evaluate(self):
        """ Return the total points for this round, based on time, successful actions and penalties.
        """
        advance = 0
        credit = self.evaluate_action_credits()
        if credit == self.max_action_credits():
            if self._total_time < MATCH_DURATION:
                advance = MATCH_DURATION - self._total_time
        return credit + advance


class ResearchScore(Score):
    items = ('_topic', '_research', '_presentation', '_poster')

    def __init__(self, topic, research, presentation, poster):
        self._topic, self._research, self._presentation, self._poster = topic, research, presentation, poster

    def evaluate(self):
        return sum(getattr(self, attr) for attr in self.items)


class JuryScore(Score):
    items = ('_evaluation',)

    def __init__(self, evaluation):
        self._evaluation = evaluation

    def evaluate(self):
        return sum(getattr(self, attr) for attr in self.items)


# Collating structure for scored points and ranking points
RoundScorePoints = namedtuple('RoundScorePoints', 'score rank')


class Round(object):
    """ A round collects the scores of all participating teams
    """

    # all teams detailed scores, keyed by the team number
    _scores = None

    def __init__(self, score_type):
        if score_type is None:
            raise ValueError("score_type cannot be None")

        self._scores = dict()
        self._score_type = score_type

    def add_score(self, team_number, score):
        assert isinstance(team_number, int)
        assert isinstance(score, self._score_type)
        self._scores[team_number] = score

    @property
    def scores(self):
        return self._scores

    @property
    def score_type(self):
        return self._score_type

    def get_ranking_points(self, team_count):
        """ Returns the round results as a dictionary given to ranking points for each participating team.

        See get_ranking_points() for ranking points computation method.
        """
        points = [(team_number, score.evaluate()) for team_number, score in self._scores.iteritems()]
        return get_ranking_points(points, team_count)

    def get_results(self, team_count):
        """ Returns the detailed round result as a dictionary keyed by the team number which values are pairs
         composed of the score points and the ranking points of the team.

         :param int team_count: the total team count
         :returns dict: the detailed round results
        """
        score_points = [(team_number, score.evaluate()) for team_number, score in self._scores.iteritems()]
        ranking_points = dict(get_ranking_points(score_points, team_count))
        score_points = dict(score_points)
        res = dict([
            (team_number, RoundScorePoints(score_points.get(team_number, 0), ranking_points.get(team_number, 0)))
            for team_number in xrange(1, team_count + 1)
        ])
        return res

    def get_completed_teams(self):
        """ Returns the list of teams having already played the round.

        :returns list: sorted list of team numbers
        """
        return sorted(self._scores.keys())

    def get_team_score(self, team_number):
        return self._scores[team_number]


def get_ranking_points(score_points, team_count):
    """ Returns the ranking points corresponding to a set of score points.

    Ranking points are the inverse of ranking positions. If N teams are competing, teams receive a number of points
    equal to N - P + 1, if P is their position : the first one gets N points, the second one N-1, and so on,
    until the last one which gets 1 point. In case of ex-aequo, teams sharing the same rank receive the same point
    count, and next count will skip as many units as ex-aequos.

     :param list score_points: a list of pairs, which first item is the team number and the second one the points scored
     for the related round

     :returns list; a list of pairs containing the team number and the ranking points, the best competitor being in
     first position
    """
    wrk = sorted(score_points, key=itemgetter(1), reverse=True)
    rank_points = team_count
    ex_aequo = 0
    last_score_points = None
    result = []
    for team_number, score_points in wrk:
        if score_points == last_score_points:
            ex_aequo += 1
        else:
            last_score_points = score_points
            ex_aequo = 0
        result.append((team_number, rank_points + ex_aequo))
        rank_points -= 1
    return result


class ScholarLevel(object):
    (POST_BAC,
     TERMINALE,
     PREMIERE,
     SECONDE,
     TROISIEME,
     QUATRIEME,
     CINQUIEME,
     SIXIEME,
     CM2,
     CM1
    ) = range(10)

    labels = [
        'post-BAC',
        'Terminale',
        '1ere',
        '2nde',
        '3eme',
        '4eme',
        '5eme',
        '6eme',
        'CM2',
        'CM1'
    ]

    @classmethod
    def bonus_points(cls, level):
        return level - cls.POST_BAC

    @classmethod
    def is_valid(cls, level):
        return cls.POST_BAC <= level <= cls.CM1


class Team(namedtuple('Team', 'name level')):
    def as_dict(self):
        return {
            'name': self.name,
            'level': ScholarLevel.labels[self.level],
            'bonus': ScholarLevel.bonus_points(self.level)
        }

    @property
    def bonus(self):
        return ScholarLevel.bonus_points(self.level)


class DuplicatedTeam(Exception):
    """ Raised when attempt to add and already existing team to a tournament
    """


class Tournament(object):
    """ The global tournament
    """

    def __init__(self, robotics_score_types):
        self._teams = []
        self._team_count = 0
        self._team_numbers = []
        self._robotics_rounds = [Round(score_type) for score_type in robotics_score_types]
        self._research = Round(ResearchScore)
        self._jury_evaluation = Round(JuryScore)
        self._planning = [
            datetime.time(14, 30),
            datetime.time(15, 45),
            datetime.time(19, 30),
            datetime.time(20, 30)
        ]

    @property
    def planning(self):
        return self._planning

    @planning.setter
    def planning(self, planning):
        self._planning = planning

    def add_team(self, team):
        """ Adds a team to participants.

        Since the are often used, the teams count and the assigned team numbers are updated and cached
        if successful add.

        :param Team team: the new team
        :returns int: the new teams count (is also the number given to the added team)
        :raises DuplicatedTeam: if team already present
        :raises ValueError: if scholar level is invalid
        """
        if team in self._teams:
            raise DuplicatedTeam(team.name)

        self._teams.append(team)
        self._team_count += 1
        self._team_numbers = range(1, self.team_count + 1)
        return self._team_count

    def load_teams(self, data):
        teams = []
        for name, level in data:
            teams.append(Team(name, level))

            self._teams = teams
            self._team_count = len(self._teams)
            self._team_numbers = range(1, self.team_count + 1)

    @property
    def team_count(self):
        """ The teams count.
        """
        return self._team_count

    @property
    def team_nums(self):
        """ The team numbers.
        """
        return self._team_numbers

    @property
    def teams(self):
        """ The team list sorted by team number.
        """
        return self._teams

    def get_team(self, team_num):
        if 0 < team_num <= self.team_count:
            return self._teams[team_num-1]
        else:
            raise KeyError("invalid team num (%d)" % team_num)

    @property
    def research_evaluation(self):
        return self._research

    @property
    def jury_evaluation(self):
        return self._jury_evaluation

    def get_robotics_rounds(self):
        return self._robotics_rounds

    def get_robotics_round(self, num):
        return self._robotics_rounds[num-1]

    def is_valid_round_num(self, num):
        return num in xrange(1, len(self._robotics_rounds) + 1)

    def set_robotics_score(self, team_num, round_num, score):
        """ Set the score for a robotics round and for a given team.

        :param int team_num: the team number
        :param int round_num: the round number (>= 1)
        :param Score score: the score
        """
        assert round_num in range(1, len(self._robotics_rounds) + 1)
        self._robotics_rounds[round_num - 1].add_score(team_num, score)

    def set_research_score(self, team_num, score):
        """ Set the score for the research work of a given team.

        :param int team_num: the team number
        :param Score score: the score
        """
        self._research.add_score(team_num, score)

    def set_jury_score(self, team_num, score):
        """ Set the score given by the jury.

        :param int team_num: the team number
        :param Score score: the score
        """
        self._jury_evaluation.add_score(team_num, score)

    Status = namedtuple('TournamentStatus', 'robotics research jury_eval')

    def get_completion_status(self):
        """ Returns the global completion status of the tournament, indicating which teams have completed which rounds.

        The result is a tuple containing :
            - a tuple gathering the completion of robotics rounds
            - the completion of research work presentation
            - the completion of jury evaluation

        The robotics rounds tuple contains one item per round, in tournament sequence.

        Each completion status is a tuple with one boolean per team, telling if the relevant round has been completed
        or not.
        """
        robotics = []
        for round_num, _round in enumerate(self._robotics_rounds, start=1):
            teams = _round.get_completed_teams()
            robotics.append(tuple(n in teams for n in self.team_nums))
        robotics = tuple(robotics)

        research = tuple(n in self._research.get_completed_teams() for n in self.team_nums)
        jury_evaluation = tuple(n in self._jury_evaluation.get_completed_teams() for n in self.team_nums)

        return Tournament.Status(robotics, research, jury_evaluation)

    def get_robotics_results(self):
        """ Returns the consolidated robotics rounds results.

         It is returned as a dictionary of RoundScorePoints, keyed by the team number
        """
        total_points = {}
        for _round in self._robotics_rounds:
            _res = _round.get_ranking_points(self.team_count)
            for team, points in _res:
                if team in total_points:
                    total_points[team] += points
                else:
                    total_points[team] = points

        ranking_points = dict(get_ranking_points(total_points.items(), self.team_count))
        return dict([
            (team_num, RoundScorePoints(total_points.get(team_num, 0), ranking_points.get(team_num, 0)))
            for team_num in self.team_nums
        ])

    def get_research_results(self):
        """ Returns the research work results.

        It is returned as a dictionary of RoundScorePoints, keyed by the team number
        """
        return self._research.get_results(self.team_count)

    def get_jury_results(self):
        """ Returns the jury evaluation results.

        It is returned as a dictionary of RoundScorePoints, keyed by the team number
        """
        return self._jury_evaluation.get_results(self.team_count)

    def get_teams_bonus(self):
        """ Returns the list of teams bonus.
        """
        return [ScholarLevel.bonus_points(team.level) for team in self._teams]

    CompiledScore = namedtuple('CompiledScore', 'rob1 rob2 rob3 research jury')

    def get_compiled_scores(self):
        """ Returns the compiled scores for all the teams as a dictionary keyed by the team number which
          associated value is a CompiledScore named tuple.
        """
        wrk = dict()

        def get_team_scores(team_num):
            if team_num in wrk:
                team_scores = wrk[team_num]
            else:
                team_scores = dict()
                wrk[team_num] = team_scores
            return team_scores

        for round_num, round in enumerate(self._robotics_rounds, start=1):
            for team_num, score in round.scores.iteritems():
                team_scores = get_team_scores(team_num)
                team_scores['rob%d' % round_num] = score.evaluate()
        for team_num, score in self._research.scores.iteritems():
            team_scores = get_team_scores(team_num)
            team_scores['research'] = score.evaluate()
        for team_num, score in self._jury_evaluation.scores.iteritems():
            team_scores = get_team_scores(team_num)
            team_scores['jury'] = score.evaluate()

        result = dict()
        for team_num in self.team_nums:
            if team_num in wrk:
                scores = wrk[team_num]
                result[team_num] = Tournament.CompiledScore(
                    scores.get('rob1', None),
                    scores.get('rob2', None),
                    scores.get('rob3', None),
                    scores.get('research', None),
                    scores.get('jury', None),
                )
            else:
                result[team_num] = Tournament.CompiledScore(None, None, None, None, None)
        return result



    def get_final_ranking(self):
        """ Computes and returns the tournament final ranking, as a list of tuples, containing each the rank and
        corresponding list of team numbers.
        """
        robotics = self.get_robotics_results()
        research = self.get_research_results()
        jury = self.get_jury_results()

        not_avail = RoundScorePoints(0, 0)

        global_ranking = get_ranking_points([
            (team_num,
             robotics.get(team_num, not_avail).rank +
             research.get(team_num, not_avail).rank +
             jury.get(team_num, not_avail).rank +
             ScholarLevel.bonus_points(team.level)
            )
            for team_num, team in enumerate(self._teams, start=1)
        ], self.team_count)

        # rearrange it
        result = []
        global_ranking.sort(key=itemgetter(1), reverse=True)
        rank = 1
        last_pts = None
        rank_list = None
        for team_num, pts in global_ranking:
            if pts == last_pts:
                rank_list.append(team_num)
            else:
                rank_list = [team_num]
                result.append((rank, rank_list))
                last_pts = pts
            rank += 1

        return result