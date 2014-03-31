#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
import json

from pjc.tournament import *
from pjc.pjc2014 import *


__author__ = 'eric'


def secs(minutes, seconds):
    return minutes * 60 + seconds


class TestRound1Score(TestCase):
    def test_evaluate(self):
        score = Round1Score(secs(2, 10), 8, 2, 0)
        self.assertEqual(score.evaluate(), 30)
        score = Round1Score(secs(2, 20), 8, 2, 0)
        self.assertEqual(score.evaluate(), 20)
        score = Round1Score(secs(2, 30), 6, 1, 0)
        self.assertEqual(score.evaluate(), 7)
        score = Round1Score(secs(1, 40), 8, 2, 0)
        self.assertEqual(score.evaluate(), 60)
        score = Round1Score(secs(2, 30), 8, 2, 0)
        self.assertEqual(score.evaluate(), 10)
        score = Round1Score(secs(2, 30), 8, 1, 0)
        self.assertEqual(score.evaluate(), 9)


class TestRound2Score(TestCase):
    def test_evaluate(self):
        score = Round2Score(secs(2, 10), 8, 2, 0, 2, 0)
        self.assertEqual(score.evaluate(), 40)
        score = Round2Score(secs(2, 20), 8, 2, 0, 2, 0)
        self.assertEqual(score.evaluate(), 30)
        score = Round2Score(secs(2, 30), 6, 1, 0, 1, 0)
        self.assertEqual(score.evaluate(), 12)
        score = Round2Score(secs(1, 00), 8, 2, 0, 0, 2)
        self.assertEqual(score.evaluate(), 0)
        score = Round2Score(secs(2, 10), 8, 2, 0, 1, 1)
        self.assertEqual(score.evaluate(), 10)
        score = Round2Score(secs(2, 20), 8, 2, 1, 2, 0)
        self.assertEqual(score.evaluate(), 19)


class TestRound3Score(TestCase):
    def test_evaluate(self):
        score = Round3Score(secs(2, 10), 6, 0)
        self.assertEqual(score.evaluate(), 26)
        score = Round3Score(secs(1, 40), 5, 1)
        self.assertEqual(score.evaluate(), 4)
        score = Round3Score(secs(2, 20), 4, 0)
        self.assertEqual(score.evaluate(), 4)
        score = Round3Score(secs(1, 40), 6, 0)
        self.assertEqual(score.evaluate(), 56)
        score = Round3Score(secs(2, 29), 6, 0)
        self.assertEqual(score.evaluate(), 7)
        score = Round3Score(secs(2, 00), 2, 0)
        self.assertEqual(score.evaluate(), 2)


class TestRound(TestCase):
    SCORES = [
        Round1Score(secs(1, 30), 8, 2, 0),
        Round1Score(secs(1, 40), 8, 2, 0),
        Round1Score(secs(1, 40), 8, 2, 0),
        Round1Score(secs(2, 20), 6, 1, 0),
        Round1Score(secs(1, 0), 8, 2, 0),
        Round1Score(secs(2, 30), 6, 1, 0),
        Round1Score(secs(2, 0), 8, 2, 1)
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
    TEAMS = [
        Team('Team 1', ScholarLevel.TERMINALE),
        Team('Team 2', ScholarLevel.TERMINALE),
        Team('Team 3', ScholarLevel.TERMINALE),
        Team('Team 4', ScholarLevel.SECONDE),
        Team('Team 5', ScholarLevel.TERMINALE)
    ]

    SCORES_ROBOTICS = [
        [
            (1, Round1Score(secs(1, 30), 8, 2, 0)),
            (2, Round1Score(secs(1, 40), 8, 2, 0)),
            (3, Round1Score(secs(2, 20), 6, 2, 1)),
            (4, Round1Score(secs(1, 00), 8, 2, 0)),
            (5, Round1Score(secs(2, 00), 8, 2, 0))
        ],
        [
            (1, Round2Score(secs(1, 30), 8, 2, 0, 2, 0)),
            (2, Round2Score(secs(1, 40), 8, 2, 0, 2, 0)),
            (3, Round2Score(secs(2, 20), 6, 1, 0, 1, 0)),
            (4, Round2Score(secs(1, 00), 8, 2, 0, 0, 2)),
            (5, Round2Score(secs(2 ,30), 8, 2, 0, 1, 1))
        ],
        [
            (1, Round3Score(secs(1, 30), 6, 0)),
            (2, Round3Score(secs(1, 40), 5, 1)),
            (4, Round3Score(secs(2, 20), 4, 0))
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
        self.assertEqual(self._tournament.team_count, len(self.TEAMS))

    def test_get_completion_status(self):
        status = self._tournament.get_completion_status()
        self.assertTrue(all(status.robotics[0]))
        self.assertTrue(all(status.robotics[1]))
        self.assertFalse(all(status.robotics[2]))
        self.assertFalse(status.robotics[2][2])
        self.assertFalse(status.robotics[2][4])
        self.assertTupleEqual(status.research, (True, False, True, True, True))

    def test_get_global_result(self):
        print('* robotics rounds teams results : ')
        for i in xrange(1, 4):
            print("%d : %s" % (i, self._tournament.get_robotics_round(i).get_results(self._tournament.team_count)))
        print('* robotics consolidated teams results :')
        print(self._tournament.get_robotics_results())
        print('* research teams results : ')
        print(self._tournament.research_evaluations.get_results(self._tournament.team_count))
        print('* jury evaluation results : ')
        print(self._tournament.jury_evaluations.get_results(self._tournament.team_count))
        print('* teams bonus : ')
        print(self._tournament.get_teams_bonus())

        res = self._tournament.get_final_ranking()
        print('* tournament final ranking :')
        print(res)
        self.assertEqual(res, [(1, [1]), (2, [4, 5]), (4, [3]), (5, [2])])

    def test_json_persistence(self):
        with file('/tmp/tournament.json', 'wt') as fp:
            json.dump(self._tournament.as_dict(), fp, indent=4)

        with file('/tmp/tournament.json', 'rt') as fp:
            d = json.load(fp)
        t = Tournament(self._tournament._robotics_score_types)
        t.from_dict(d)

        self.assertEqual(t.planning, self._tournament.planning)
        self.assertEqual(t.teams, self._tournament.teams)

        s1 = t.research_evaluations.scores
        s2 = self._tournament.research_evaluations.scores
        self.assertEqual(len(s1), len(s1))
        for team_num, score in s2.iteritems():
            self.assertDictEqual(score.as_dict(), s2[team_num].as_dict())

        s1 = t.jury_evaluations.scores
        s2 = self._tournament.jury_evaluations.scores
        self.assertEqual(len(s1), len(s1))
        for team_num, score in s2.iteritems():
            self.assertDictEqual(score.as_dict(), s2[team_num].as_dict())

        self.assertEqual(len(t.get_robotics_rounds()), len(self._tournament.get_robotics_rounds()))
        for round1, round2 in zip(t.get_robotics_rounds(), self._tournament.get_robotics_rounds()):
            s1 = round1.scores
            s2 = round2.scores
            self.assertEqual(len(s1), len(s1))
            for team_num, score in s2.iteritems():
                self.assertDictEqual(score.as_dict(), s2[team_num].as_dict())
