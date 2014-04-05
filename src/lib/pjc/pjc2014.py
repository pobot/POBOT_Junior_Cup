#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Module gathering the specialized implementations for 2014 edition rules
"""
from pjc.tournament import RoboticsScore

__author__ = 'eric'


class Round1Score(RoboticsScore):
    """ Concrete score sub-class for round 1.

    It counts:
      - buoys and beacons alignment crossings
      - successful dockings
      - penalties for moved buoys
      - time bonus when mission fulfilled
    """
    items = RoboticsScore.items + ('alignments', 'dockings', 'hits')

    alignments = 0
    dockings = 0
    hits = 0

    def __init__(self, total_time=0, alignments=0, dockings=0, hits=0):
        super(Round1Score, self).__init__(total_time)
        self.alignments = alignments
        self.dockings = dockings
        self.hits = hits

    @classmethod
    def max_action_credits(cls):
        return 10

    def evaluate_action_credits(self):
        return self.alignments + self.dockings - self.hits


class Round2Score(Round1Score):
    """ Concrete score sub-class for round 2.

    It counts:
      - buoys and beacons alignment crossings
      - successful dockings
      - successful channel selection
      - penalties for moved buoys or wrong channel selection
      - time bonus when mission fulfilled
    """
    items = Round1Score.items + ('channels_ok', 'channels_wrong')

    channels_ok = 0
    channels_wrong = 0

    def __init__(self, total_time=0, alignments=0, dockings=0, hits=0, channels_ok=0, channels_wrong=0):
        super(Round2Score, self).__init__(total_time, alignments, dockings, hits)
        self.channels_ok = channels_ok
        self.channels_wrong = channels_wrong

    @classmethod
    def max_action_credits(cls):
        return 20

    def evaluate_action_credits(self):
        return super(Round2Score, self).evaluate_action_credits() + 5 * (self.channels_ok - self.channels_wrong)


class Round3Score(RoboticsScore):
    """ Concrete score sub-class for round 3.

    It counts:
      - buoys correctly stored
      - penalties for buoys stored on the wrong side
      - time bonus when mission fulfilled
    """
    items = RoboticsScore.items + ('buoys_ok', 'buoys_wrong')

    buoys_ok = 0
    buoys_wrong = 0

    def __init__(self, total_time=0, buoys_ok=0, buoys_wrong=0):
        super(Round3Score, self).__init__(total_time)
        self.buoys_ok = buoys_ok
        self.buoys_wrong = buoys_wrong

    @classmethod
    def max_action_credits(cls):
        return 6

    def evaluate_action_credits(self):
        return self.buoys_ok - self.buoys_wrong