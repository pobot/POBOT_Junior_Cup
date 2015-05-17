#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

__author__ = 'eric'

from operator import itemgetter
from collections import namedtuple
import datetime
import csv

MATCH_DURATION = 150    # secs


class Score(object):
    """ Root class implementing a team score for the various parts of the competition.

    Score instances conveys basic information such as:

        * time spent by the robot to fulfill the missions during robotics matches
        * points (including penalties) scored by actions during robotics matches
        * points given by the jury when evaluating the various aspects of the research work

    It also implements the rules producing the aggregated count based on the above listed base information by providing
    the `evaluate()` method.

    It must thus be sub-classed :

        * to define the basic information used for each tournament part
        * to implement aggregation rules

    ~ Implementation note: ~

         In order to make concrete classes implementation task easier, we use introspection mechanisms. They are
         based on the following principles :

            * concrete score items are represented by attributes
            * their list must be provided by an attribute named `items`, containing the collection of above
              mentioned attributes as a tuple for instance

         Some convenience methods are provided :

            * `as_dict()` returning the score items as a dictionary
            * `as_tuple()` returning the score items as a tuple, which components are in the same sequence as the
              `items` attribute.
    """
    items = ()

    def evaluate(self):
        """ Returns the aggregated point count, following the sub-counts aggregation rules.

         :returns int: the point count
        """
        raise NotImplementedError()

    def serialize(self):
        return dict([(item, getattr(self, item)) for item in self.items])

    def as_tuple(self):
        return tuple([getattr(self, attr) for attr in self.items])


class RoboticsScore(Score):
    """ Specialized score for robotics rounds.

    It shares invariants, which are :
        - the round total time (in seconds)
    """
    items = ('total_time',)
    total_time = 0

    def __init__(self, total_time=0):
        """
        :param int total_time: final stopwatch value in seconds
        """
        super(RoboticsScore, self).__init__()
        self.total_time = total_time

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
        time_credit = 0
        actions_credit = self.evaluate_action_credits()
        if actions_credit >= self.max_action_credits():
            if self.total_time < MATCH_DURATION:
                time_credit = MATCH_DURATION - self.total_time
        return actions_credit + time_credit


class ResearchEvaluationScore(Score):
    items = ('shown', 'topic', 'research', 'presentation', 'poster')

    def __init__(self, shown=False, topic=0, research=0, presentation=0, poster=0):
        self.shown, self.topic, self.research, self.presentation, self.poster = \
            shown, topic, research, presentation, poster

    def evaluate(self):
        return sum(getattr(self, attr) for attr in self.items[1:]) if self.shown else 0;


class JuryEvaluationScore(Score):
    items = ('evaluation',)

    def __init__(self, evaluation=0):
        self.evaluation = evaluation

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

    def add_team_score(self, team_number, score):
        assert isinstance(team_number, int)
        if score:
            if not isinstance(score, self._score_type):
                raise ValueError('argument is not a %s' % self.score_type.__name__)
            self._scores[team_number] = score
        else:
            raise ValueError('score cannot be None')

    def clear_team_score(self, team_number):
        assert isinstance(team_number, int)
        try:
            del self._scores[team_number]
        except KeyError:
            pass

    @property
    def scores(self):
        return self._scores

    @property
    def score_type(self):
        """

        :rtype : type
        """
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
        """ Returns the score of the team for this round, or raises a KeyError exception of not available.
        """
        return self._scores[team_number]

    def serialize(self):
        return dict([(team_num, score.serialize()) for team_num, score in self._scores.iteritems()])


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
    (
        POST_BAC,
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
        '1ère',
        '2nde',
        '3ème',
        '4ème',
        '5ème',
        '6ème',
        'CM2',
        'CM1'
    ]

    encoding = [
        ('fac', 'iut', 'ing', '>BAC'),
        ('terminale', 'tale', 'tle', 't'),
        ('première', '1ère', '1ere', '1e'),
        ('seconde', '2nde'),
        ('troisième', '3ème', '3eme', '3e'),
        ('quatrième', '4ème', '4eme', '4e'),
        ('cinquième', '5ème', '5eme', '5e'),
        ('sixième', '6ème', '6eme', '6e'),
        ('cm2',),
        ('cm1',)
    ]

    @classmethod
    def bonus_points(cls, level):
        return level.code - cls.POST_BAC

    @classmethod
    def is_valid(cls, level):
        return cls.POST_BAC <= level <= cls.CM1

    @classmethod
    def encode(cls, level):
        lvl = level.lower()
        for code, accepted_forms in [t for t in enumerate(cls.encoding)][::-1]:
            for option in accepted_forms:
                if option in lvl:
                    return code
        raise KeyError('unrecognized level (%s)' % level)

    @classmethod
    def decode(cls, code):
        return cls.labels[code]

    def __init__(self, value):
        if isinstance(value, dict):
            self.__dict__.update(value)

        else:
            try:
                self.code = int(value)
                self.orig = None
            except (TypeError, ValueError):
                self.code = self.encode(value)
                self.orig = value
            self.label = self.labels[self.code]

    def serialize(self):
        return {
            'code': self.code,
            'label': self.label,
            'orig': self.orig,
        }


class TeamPlanning(object):
    class Match(object):
        SLOT_DURATION = datetime.timedelta(minutes=10)

        def __init__(self, time, table=None):
            self.time = time
            self.table = table

    class Presentation(object):
        SLOT_DURATION = datetime.timedelta(minutes=30)

        def __init__(self, time, jury=None):
            self.time = time
            self.jury = jury

    def __init__(self, times):
        if len(times) != 4:
            raise ValueError('parameter must be a 4 items tuples')

        match_count = 3
        self.matches = [None] * match_count
        for i, entry in enumerate(times):
            if isinstance(entry, (tuple, list)):
                time, assignment = entry
            else:
                time, assignment = entry, None

            if not isinstance(time, datetime.time):
                if isinstance(time, basestring):
                    time = datetime.datetime.strptime(time, "%H:%M").time()
                elif isinstance(time, datetime.datetime):
                    time = time.time()
                else:
                    raise ValueError('invalid planning time (%s)' % time)

            if i < match_count:
                self.matches[i] = self.Match(time, assignment)
            else:
                self.presentation = self.Presentation(time, assignment)

    def __getitem__(self, item):
        if 0 <= item < 3:
            return self.matches[item]
        elif item == 3:
            return self.presentation
        else:
            raise IndexError()

    def serialize(self):
        return [(m.time.strftime('%H:%M'), m.table) for m in self.matches] + \
               [(self.presentation.time.strftime('%H:%M'), self.presentation.jury)]

    @property
    def times(self):
        return tuple(m.time for m in self.matches) + (self.presentation.time,)

    @property
    def extent(self):
        today = datetime.date.today()
        planning_start = datetime.time.max
        planning_end = datetime.time.min

        for time in (m.time for m in self.matches):
            if time < planning_start:
                planning_start = time
            if time >= planning_end:
                end = (datetime.datetime.combine(today, time) + self.Match.SLOT_DURATION).time()
                if end > planning_end:
                    planning_end = end

        time = self.presentation.time
        if time < planning_start:
            planning_start = time
        if time >= planning_end:
            end = (datetime.datetime.combine(today, time) + self.Presentation.SLOT_DURATION).time()
            if end > planning_end:
                planning_end = end

        return planning_start, planning_end

    def __str__(self):
        return str(self.times)


class Team(object):

    def __init__(self, num, name, school, level, city, department, present, planning=None):
        self.num = int(num)
        self.name = name
        self.school = school
        self.level = level if isinstance(level, ScholarLevel) else ScholarLevel(level)
        self.city = city
        self.department = department
        self.present = present
        self.planning = planning

    @property
    def bonus(self):
        return ScholarLevel.bonus_points(self.level)

    def serialize(self):
        return {
            'name': self.name,
            'school': self.school,
            'level': self.level.serialize(),
            'city': self.city,
            'department': self.department,
            'present': self.present,
            'planning': self.planning.serialize()
        }

    def as_dict(self):
        return self.serialize().update({
            'num': self.num,
            'bonus': ScholarLevel.bonus_points(self.level),
        })

    def __repr__(self):
        return "%d - %s" % (self.num, self.name)

    def __cmp__(self, other):
        return self.num.__cmp__(other.num)


TeamCSVData = namedtuple('TeamCSVData', 'num name level school city dept')


class DuplicatedTeam(Exception):
    """ Raised when attempt to add and already existing team to a tournament
    """


class Tournament(object):
    """ The global tournament
    """
    ITEMS_DURATION = (10, 10, 10, 30)

    def __init__(self, robotics_score_types=None):
        self._robotics_score_types = robotics_score_types
        self._teams = {}
        self._robotics_rounds = \
            [Round(score_type) for score_type in robotics_score_types] if robotics_score_types \
            else []
        self._research_evaluations = Round(ResearchEvaluationScore)
        self._jury_evaluations = Round(JuryEvaluationScore)
        self._planning = [
            datetime.time(15, 00),  # time limit for round 1 matches
            datetime.time(16, 00),  # time limit for round 2 matches
            datetime.time(17, 00),  # time limit for round 3 matches
            datetime.time(17, 00)   # time limit for presentations
        ]
        self._start_time = datetime.time.min

    @property
    def planning(self):
        return self._planning

    @planning.setter
    def planning(self, planning):
        self._planning = planning

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        self._start_time = start_time

    def load_teams_info(self, fp):
        fp.seek(0)
        rdr = csv.reader(fp)
        for team_data in (TeamCSVData(*f) for f in rdr):
            level = ScholarLevel(team_data.level)
            self.add_team(Team(
                team_data.num,
                name=team_data.name,
                school=team_data.school,
                level=level,
                city=team_data.city,
                department=team_data.dept,
                present=False
            ))

    def load_teams_plannings(self, fp):
        fp.seek(0)
        rdr = csv.reader(fp)

        # first line is the header, which gives us the time slots and the X position of the planning data (-> x0)
        x0 = 0
        cells = rdr.next()
        for x0, time_slot in enumerate(cells):
            if time_slot:
                break
        time_slots = [datetime.datetime.strptime(t, "%H:%M").time() for t in cells[x0:]]

        # process team lines
        in_teams = False
        for cells in rdr:
            team_num = cells[0]
            if team_num:
                in_teams = True
                team_num = int(team_num)
                planning_cells = cells[x0:]
                slots_indices = [planning_cells.index(s) for s in ('M1', 'M2', 'M3', 'EXP')][:4]
                planning = TeamPlanning([time_slots[i] for i in slots_indices])

                self._teams[team_num].planning = planning

            elif in_teams:
                break

    def consolidate_planning(self):
        earliest_start_time = datetime.time.max
        latest_start_times = [datetime.time() for _ in range(4)]

        for team in self.registered_teams:
            for i, t in enumerate(zip(team.planning.times, latest_start_times)):
                team_time, latest_time = t
                if team_time > latest_time:
                    latest_start_times[i] = team_time
                if team_time < earliest_start_time:
                    earliest_start_time = team_time

        # advance latest start times by the duration of the corresponding items
        # so that we'll get the time at which all teams should have completed theirs
        today = datetime.date.today()   # dummy date part used for using timedeltas with time instances
        self.planning = [
            (datetime.datetime.combine(today, t) + datetime.timedelta(minutes=m)).time()
            for t, m in zip(latest_start_times, self.ITEMS_DURATION)
        ]
        self._start_time = earliest_start_time

    def assign_tables_and_juries(self):
        all_teams = self.registered_teams

        start_table = 0
        for match in range(3):
            num = start_table
            for team in all_teams:
                team.planning.matches[match].table = num + 1    # human friendly numbers start at 1
                num = (num + 1) % 3
            start_table = (start_table + 1) % 3
            
        num = 0
        for team in all_teams:
            team.planning.presentation.jury = num + 1
            num = (num + 1) % 3

    def add_team(self, team):
        """ Adds a team to participants.

        Since the are often used, the teams count and the assigned team numbers are updated and cached
        if successful add.

        :param Team team: the new team
        :returns int: the new teams count (is also the number given to the added team)
        :raises DuplicatedTeam: if team already present
        :raises ValueError: if scholar level is invalid
        """
        if team.num in self._teams:
            raise DuplicatedTeam(team)

        self._teams[team.num] = team
        return self.team_count(present_only=False)

    def deserialize_teams(self, dct):
        self._teams.clear()
        for num, details in dct.iteritems():
            planning = TeamPlanning(details['planning'])
            team = Team(
                num,
                name=details['name'],
                school=details['school'],
                level=details['level'],
                city=details['city'],
                department=details['department'],
                present=details['present'],
                planning=planning
            )
            self.add_team(team)

    def team_count(self, present_only=True):
        """ The teams count.
        """
        if present_only:
            return len(self.teams(present_only=True))
        else:
            return len(self._teams)

    def teams(self, present_only=True):
        """ The team list sorted by team number.

        :param boolean present_only: if true the result contains present teams only
        """
        if present_only:
            return sorted([t for t in self._teams.itervalues() if t.present], key=lambda t : t.num)
        else:
            return sorted(self._teams.itervalues(), key=lambda t : t.num)

    def team_nums(self, present_only=False):
        return sorted([team.num for team in self.teams(present_only=present_only)])

    @property
    def registered_teams(self):
        return self.teams(present_only=False)

    def get_team(self, team_num):
        return self._teams[team_num]

    def register_abandon(self, team_num):
        self._teams[team_num].abandon = True

    @property
    def research_evaluations(self):
        return self._research_evaluations

    @property
    def jury_evaluations(self):
        return self._jury_evaluations

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
        self._robotics_rounds[round_num - 1].add_team_score(team_num, score)

    def clear_robotics_score(self, team_num, round_num):
        assert round_num in range(1, len(self._robotics_rounds) + 1)
        self._robotics_rounds[round_num - 1].clear_team_score(team_num)

    def get_research_evaluation(self, team_num):
        return self._research_evaluations.get_team_score(team_num)

    def set_research_evaluation(self, team_num, score):
        """ Set the score for the research work of a given team.

        :param int team_num: the team number
        :param Score score: the score
        """
        self._research_evaluations.add_team_score(team_num, score)

    def clear_research_evaluation(self, team_num):
        self._research_evaluations.clear_team_score(team_num)

    def get_jury_evaluation(self, team_num):
        return self._jury_evaluations.get_team_score(team_num)

    def set_jury_evaluation(self, team_num, score):
        """ Set the score given by the jury.

        :param int team_num: the team number
        :param Score score: the score
        """
        self._jury_evaluations.add_team_score(team_num, score)

    def clear_jury_evaluation(self, team_num):
        self._jury_evaluations.clear_team_score(team_num)

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
        all_team_nums = self.team_nums(present_only=False)
        for round_num, _round in enumerate(self._robotics_rounds, start=1):
            teams = _round.get_completed_teams()
            robotics.append(tuple(n in teams for n in all_team_nums))
        robotics = tuple(robotics)

        research = tuple(n in self._research_evaluations.get_completed_teams() for n in all_team_nums)
        jury_evaluation = tuple(n in self._jury_evaluations.get_completed_teams() for n in all_team_nums)

        return Tournament.Status(robotics, research, jury_evaluation)

    def get_robotics_results(self):
        """ Returns the consolidated robotics rounds results.

         It is returned as a dictionary of RoundScorePoints, keyed by the team number
        """
        total_points = {}
        teams_count = self.team_count(present_only=False)
        for _round in self._robotics_rounds:
            _res = _round.get_ranking_points(teams_count)
            for team, points in _res:
                if team in total_points:
                    total_points[team] += points
                else:
                    total_points[team] = points

        ranking_points = dict(get_ranking_points(total_points.items(), teams_count))
        return dict([
            (team_num, RoundScorePoints(total_points.get(team_num, 0), ranking_points.get(team_num, 0)))
            for team_num in self.team_nums(present_only=False)
        ])

    def get_research_evaluation_results(self):
        """ Returns the research work evaluation results.

        It is returned as a dictionary of RoundScorePoints, keyed by the team number
        """
        return self._research_evaluations.get_results(self.team_count(present_only=False))

    def get_team_evaluation_results(self):
        """ Returns the team overall evaluation made by the jury.

        It is returned as a dictionary of RoundScorePoints, keyed by the team number
        """
        return self._jury_evaluations.get_results(self.team_count(present_only=False))

    def get_teams_bonus(self):
        """ Returns the list of teams bonus.
        """
        return [ScholarLevel.bonus_points(team.level) for team in self._teams]

    CompiledScore = namedtuple('CompiledScore', 'rob1 rob2 rob3 research jury')

    def get_compiled_scores(self):
        """ Returns the compiled scores for all the present teams as a dictionary keyed by the team number which
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
        for team_num, score in self._research_evaluations.scores.iteritems():
            team_scores = get_team_scores(team_num)
            team_scores['research'] = score.evaluate()
        for team_num, score in self._jury_evaluations.scores.iteritems():
            team_scores = get_team_scores(team_num)
            team_scores['jury'] = score.evaluate()

        result = dict()
        for team_num in [team.num for team in self.teams(present_only=True)]:
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

    def get_competing_teams(self):
        """ Returns the list of teams which have really participated to the competition.

        A team is considered to be participating if it played at least one round and has presented its
        research work.

        :returns: a list of team nums
        """
        comp_rob, comp_research, comp_jury = self.get_completion_status()
        comp_rob = zip(*comp_rob)   # transposes the matrix
        return [
            t for t, c in enumerate(
                [all((any(r), s)) for r, s in zip(comp_rob, comp_research)], start=1
            ) if c
        ]

    def get_final_ranking(self):
        """ Computes and returns the tournament final ranking, as a list of tuples, containing each the rank and
        corresponding list of team numbers.

        Only competing teams are included in the final ranking result.
        """
        competing_teams = self.get_competing_teams()

        robotics = self.get_robotics_results()
        research = self.get_research_evaluation_results()
        jury = self.get_team_evaluation_results()

        not_avail = RoundScorePoints(0, 0)

        global_ranking = get_ranking_points([
            (team_num,
             robotics.get(team_num, not_avail).rank +
             research.get(team_num, not_avail).rank +
             jury.get(team_num, not_avail).rank +
             ScholarLevel.bonus_points(team.level)  #TODO should be processed like other items to keep a constant weight whatever is the team count
            )
            for team_num, team in self._teams.iteritems() if team_num in competing_teams
        ], self.team_count(present_only=True))

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

    def serialize(self):
        d = dict()

        d['teams'] = dict([(team.num, team.serialize())for team in self._teams.values()])
        d['planning'] = [t.strftime('%H:%M') for t in self._planning]
        d['start_time'] = self._start_time.strftime('%H:%M')
        d['robotics_rounds'] = [r.serialize() for r in self._robotics_rounds]
        d['research_evaluations'] = self._research_evaluations.serialize()
        d['jury_evaluations'] = self._jury_evaluations.serialize()
        return d

    def deserialize(self, d):
        self.deserialize_teams(d['teams'])

        self.planning = [datetime.datetime.strptime(s, "%H:%M").time() for s in d['planning']]
        self.start_time = datetime.datetime.strptime(d['start_time'], "%H:%M").time()

        self._robotics_rounds = []
        rounds_dict = d['robotics_rounds']
        for round_num, score_type in enumerate(self._robotics_score_types, start=1):
            round_ = Round(score_type)
            scores = rounds_dict[round_num - 1]
            for team_num, score_dict in scores.iteritems():
                score = score_type(**score_dict)
                round_.add_team_score(int(team_num), score)
            self._robotics_rounds.append(round_)

        for team_num, score_dict in d['research_evaluations'].iteritems():
            score = ResearchEvaluationScore(**score_dict)
            self._research_evaluations.add_team_score(int(team_num), score)

        for team_num, score_dict in d['jury_evaluations'].iteritems():
            score = JuryEvaluationScore(**score_dict)
            self._jury_evaluations.add_team_score(int(team_num), score)

    def get_planning_time_span(self):
        """
        :return: the bounds of the event time extent
        :rtype: tuple of datetime.time
        """
        return self.start_time, max(self.planning)


