#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
import json

from pjc.tournament import *
from pjc.current_edition import *


__author__ = 'eric'


def secs(minutes, seconds):
    return minutes * 60 + seconds


MAX_SECS = secs(2, 30)


def secs_saved(score):
    return MAX_SECS - score.total_time


class TestRound1Score(TestCase):
    def test_evaluate(self):
        score = Round1Score(secs(2, 10), 8)
        self.assertEqual(score.evaluate(), secs_saved(score) + 8)
        score = Round1Score(secs(2, 20), 8)
        self.assertEqual(score.evaluate(), secs_saved(score) + 8)
        score = Round1Score(secs(2, 30), 6)
        self.assertEqual(score.evaluate(), 6)
        score = Round1Score(secs(1, 40), 8)
        self.assertEqual(score.evaluate(), secs_saved(score) + 8)
        score = Round1Score(secs(2, 30), 8)
        self.assertEqual(score.evaluate(), secs_saved(score) + 8)
        score = Round1Score(secs(2, 30), 8)
        self.assertEqual(score.evaluate(), secs_saved(score) + 8)


class TestRound2Score(TestCase):
    def test_evaluate(self):
        score = Round2Score(secs(2, 10), 8, 0, 3)
        self.assertEqual(score.evaluate(), secs_saved(score) + 8 + 3)
        score = Round2Score(secs(2, 20), 8, 2, 0)
        self.assertEqual(score.evaluate(), 8 - 2)
        score = Round2Score(secs(2, 30), 6, 1, 0)
        self.assertEqual(score.evaluate(), 6 - 1)
        score = Round2Score(secs(1, 00), 8, 2, 0)
        self.assertEqual(score.evaluate(), 8 - 2)
        score = Round2Score(secs(2, 10), 8, 2, 0)
        self.assertEqual(score.evaluate(), 8 - 2)
        score = Round2Score(secs(2, 20), 8, 2, 1)
        self.assertEqual(score.evaluate(), 8 - 2 + 1)


class TestRound3Score(TestCase):
    def test_evaluate(self):
        score = Round3Score(secs(2, 10), Round3Score.FULLY_INSIDE, 0)
        self.assertEqual(score.evaluate(), secs_saved(score) + 10)
        score = Round3Score(secs(1, 40), Round3Score.FULLY_INSIDE, 1)
        self.assertEqual(score.evaluate(), 10 - 1)
        score = Round3Score(secs(2, 20), Round3Score.OUTSIDE, 0)
        self.assertEqual(score.evaluate(), 0)
        score = Round3Score(secs(1, 40), Round3Score.FULLY_INSIDE, 0)
        self.assertEqual(score.evaluate(), secs_saved(score) + 10)
        score = Round3Score(secs(2, 29), Round3Score.PARTLY_INSIDE, 0)
        self.assertEqual(score.evaluate(), 5)
        score = Round3Score(secs(2, 00), Round3Score.FULLY_INSIDE, 0)
        self.assertEqual(score.evaluate(), secs_saved(score) + 10)


class TestRound(TestCase):
    SCORES = [
        Round1Score(secs(1, 30), 8),
        Round1Score(secs(1, 40), 8),
        Round1Score(secs(1, 40), 8),
        Round1Score(secs(2, 20), 6),
        Round1Score(secs(1, 0), 8),
        Round1Score(secs(2, 30), 6),
        Round1Score(secs(2, 0), 8)
    ]

    def setUp(self):
        self._round = Round(Score)
        for i, s in enumerate(self.SCORES, start=1):
            self._round.add_team_score(i, s)

    def test_get_results(self):
        res = self._round.get_ranking_points(len(self.SCORES))

        rankings = [(5, 7), (1, 6), (2, 5), (3, 5), (7, 3), (4, 2), (6, 2)]
        self.assertEqual(res, rankings)

    def test_get_completed_teams(self):
        self.assertEqual(self._round.get_completed_teams(), range(1, len(self.SCORES) + 1))


class TestTournament(TestCase):
    DUMMY_PLANNING = TeamPlanning([datetime.time(14), datetime.time(15), datetime.time(16), datetime.time(17)])

    TEAMS = [
        Team(1, 'Team 1', 'School 1', Grade.TERMINALE, 'Grasse', 6, True, planning=DUMMY_PLANNING),
        Team(2, 'Team 2', 'School 2', Grade.QUATRIEME, 'Le Cannet', 6, True, planning=DUMMY_PLANNING),
        Team(3, 'Team 3', 'School 3', Grade.SIXIEME, 'Nice', 6, True, planning=DUMMY_PLANNING),
        Team(4, 'Team 4', 'School 4', Grade.SECONDE, 'Hasparren', 64, True, planning=DUMMY_PLANNING),
        Team(5, 'Team 5', 'School 5', Grade.TROISIEME, 'Valbonne', 6, True, planning=DUMMY_PLANNING)
    ]

    SCORES_ROBOTICS = [
        [
            (1, Round1Score(secs(1, 30), 8)),
            (2, Round1Score(secs(1, 40), 8)),
            (3, Round1Score(secs(2, 20), 6)),
            (4, Round1Score(secs(1, 00), 8)),
            (5, Round1Score(secs(2, 00), 8))
        ],
        [
            (1, Round2Score(secs(1, 30), 8, 2, 0)),
            (2, Round2Score(secs(1, 40), 8, 2, 0)),
            (3, Round2Score(secs(2, 20), 6, 1, 0)),
            (4, Round2Score(secs(1, 00), 8, 2, 0)),
            (5, Round2Score(secs(2 ,30), 8, 2, 0))
        ],
        [
            (1, Round3Score(secs(1, 30), Round3Score.FULLY_INSIDE, 0)),
            (2, Round3Score(secs(1, 40), Round3Score.PARTLY_INSIDE, 1)),
            (4, Round3Score(secs(2, 20), Round3Score.OUTSIDE, 0))
        ]
    ]

    SCORES_RESEARCH = [
        (1, ResearchEvaluationScore(True, 15, 17, 12, 18)),
        (3, ResearchEvaluationScore(True, 10, 15, 14, 17)),
        (4, ResearchEvaluationScore(False)),
        (5, ResearchEvaluationScore(True, 18, 17, 16, 14))
    ]

    JURY_EVALUATION = [
        (1, JuryEvaluationScore(18)),
        (2, JuryEvaluationScore(15)),
        (3, JuryEvaluationScore(16)),
        (4, JuryEvaluationScore(16)),
        (5, JuryEvaluationScore(16))
    ]

    def setUp(self):
        self._tournament = Tournament((Round1Score, Round2Score, Round3Score))
        for team in self.TEAMS:
            self._tournament.add_team(team)

        for round_num, scores in enumerate(self.SCORES_ROBOTICS, start=1):
            for team_num, score in scores:
                self._tournament.set_robotics_score(team_num, round_num, score)

        for team_num, score in self.SCORES_RESEARCH:
            self._tournament.set_research_evaluation(team_num, score)

        for team_num, score in self.JURY_EVALUATION:
            self._tournament.set_jury_evaluation(team_num, score)

    def test_get_teams(self):
        self.assertEqual(self._tournament.team_count(present_only=False), len(self.TEAMS))

    def test_get_completion_status(self):
        status = self._tournament.get_completion_status()
        self.assertTrue(all(status.robotics[0]))
        self.assertTrue(all(status.robotics[1]))
        self.assertFalse(all(status.robotics[2]))
        self.assertFalse(status.robotics[2][2])
        self.assertFalse(status.robotics[2][4])
        self.assertTupleEqual(status.research, (True, False, True, True, True))

    def test_get_global_result(self):
        present_teams_count = self._tournament.team_count(present_only=True)

        print('* robotics rounds teams results : ')
        for i in xrange(1, 4):
            print("%d : %s" % (
                i, self._tournament.get_robotics_round(i).get_results(present_teams_count)
            ))
        print('* robotics consolidated teams results :')
        print(self._tournament.get_robotics_results())
        print('* research teams results : ')
        print(self._tournament.research_evaluations.get_results(present_teams_count))
        print('* jury evaluation results : ')
        print(self._tournament.jury_evaluations.get_results(present_teams_count))
        print('* teams bonus : ')
        print(self._tournament._bonus.get_results(present_teams_count))

        res = self._tournament.get_final_ranking()
        print('* tournament final ranking :')
        print(res)
        self.assertEqual(res, [(1, [1]), (2, [5]), (3, [4]), (4, [3])])

    def test_json_persistence(self):
        with file('/tmp/tournament.json', 'wt') as fp:
            json.dump(self._tournament.serialize(), fp, indent=4)

        with file('/tmp/tournament.json', 'rt') as fp:
            d = json.load(fp)
        t = Tournament(self._tournament._robotics_score_types)
        t.deserialize(d)

        self.assertEqual(t.planning, self._tournament.planning)
        self.assertEqual(t.teams(), self._tournament.teams())

        s1 = t.research_evaluations.scores
        s2 = self._tournament.research_evaluations.scores
        self.assertEqual(len(s1), len(s1))
        for team_num, score in s2.iteritems():
            self.assertDictEqual(score.serialize(), s2[team_num].serialize())

        s1 = t.jury_evaluations.scores
        s2 = self._tournament.jury_evaluations.scores
        self.assertEqual(len(s1), len(s1))
        for team_num, score in s2.iteritems():
            self.assertDictEqual(score.serialize(), s2[team_num].serialize())

        self.assertEqual(len(t.get_robotics_rounds()), len(self._tournament.get_robotics_rounds()))
        for round1, round2 in zip(t.get_robotics_rounds(), self._tournament.get_robotics_rounds()):
            s1 = round1.scores
            s2 = round2.scores
            self.assertEqual(len(s1), len(s1))
            for team_num, score in s2.iteritems():
                self.assertDictEqual(score.serialize(), s2[team_num].serialize())
