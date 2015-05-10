#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Module gathering the specialized implementations for 2015 edition rules
"""

import sys

from .tournament import RoboticsScore

__author__ = 'eric'


class Round1Score(RoboticsScore):
    """ Concrete score sub-class for round 1.

    It counts:
      - the number of sections successfully traveled
      - time bonus when mission fulfilled
    """
    items = RoboticsScore.items + ('sections',)
    sections = 0

    def __init__(self, total_time=0, sections=0):
        super(Round1Score, self).__init__(total_time)
        self.sections = sections

    @classmethod
    def max_action_credits(cls):
        """ The max action credits corresponds to the number of sections which
        should be travelled at the end of a successful mission. The robots
        have to travel the track 3 times, and the track is divided into 4 sections,
        hence the result (12).
        """
        return 12

    def evaluate_action_credits(self):
        return self.sections


class Round2Score(Round1Score):
    """ Concrete score sub-class for round 2.

    The count rules are the same as for round 1.
    """


class Round3Score(RoboticsScore):
    """ Concrete score sub-class for round 3.

    It counts:
      - the number of passengers correctly transported
    """
    items = RoboticsScore.items + ('passengers',)

    passengers = 0

    def __init__(self, total_time=0, passengers=0):
        super(Round3Score, self).__init__(total_time)
        self.passengers = passengers

    @classmethod
    def max_action_credits(cls):
        """There is no fixed objective here, since the score is based on
        how many passengers have ben transported at the end of the round
        time.
        """
        return sys.maxint

    def evaluate_action_credits(self):
        return self.passengers