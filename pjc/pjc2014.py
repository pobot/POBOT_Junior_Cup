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
    items = RoboticsScore.items + ('_alignments', '_dockings', '_hits')

    _alignments = 0
    _dockings = 0
    _hits = 0

    def __init__(self, total_time, alignments, dockings, hits):
        super(Round1Score, self).__init__(total_time)
        self._alignments = alignments
        self._dockings = dockings
        self._hits = hits

    @classmethod
    def max_action_credits(cls):
        return 10

    def evaluate_action_credits(self):
        return self._alignments + self._dockings - self._hits


class Round2Score(Round1Score):
    """ Concrete score sub-class for round 2.

    It counts:
      - buoys and beacons alignment crossings
      - successful dockings
      - successful channel selection
      - penalties for moved buoys or wrong channel selection
      - time bonus when mission fulfilled
    """
    items = Round1Score.items + ('_channels_ok', '_channels_ko')

    _channels_ok = 0
    _channels_ko = 0

    def __init__(self, total_time, alignments, dockings, hits, channels_ok, channels_ko):
        super(Round2Score, self).__init__(total_time, alignments, dockings, hits)
        self._channels_ok = channels_ok
        self._channels_ko = channels_ko

    @classmethod
    def max_action_credits(cls):
        return 20

    def evaluate_action_credits(self):
        return super(Round2Score, self).evaluate_action_credits() + 5 * (self._channels_ok - self._channels_ko)


class Round3Score(RoboticsScore):
    """ Concrete score sub-class for round 3.

    It counts:
      - buoys correctly stored
      - penalties for buoys stored on the wrong side
      - time bonus when mission fulfilled
    """
    items = RoboticsScore.items + ('_buoys_ok', '_buoys_wrong')

    _buoys_ok = 0
    _buoys_wrong = 0

    def __init__(self, total_time, buoys_ok, buoys_wrong):
        super(Round3Score, self).__init__(total_time)
        self._buoys_ok = buoys_ok
        self._buoys_wrong = buoys_wrong

    @classmethod
    def max_action_credits(cls):
        return 6

    def evaluate_action_credits(self):
        return self._buoys_ok - self._buoys_wrong