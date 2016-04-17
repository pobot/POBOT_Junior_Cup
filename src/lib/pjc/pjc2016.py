# -*- coding: utf-8 -*-

""" Module gathering the specialized implementations for 2016 edition rules
"""

from .tournament import RoboticsScore

__author__ = 'eric'


class Round1Score(RoboticsScore):
    """ Concrete score sub-class for round 1.

    It counts:
      - the number of blocks successfully collected
      - the time bonus when mission fulfilled
    """
    items = RoboticsScore.items + ('collected',)
    collected = 0

    def __init__(self, total_time=0, collected=0):
        super(Round1Score, self).__init__(total_time)
        self.collected = collected

    @classmethod
    def max_action_credits(cls):
        """ The max action credits corresponds to the number of blocks which
        are collected at the end of a successful mission.
        """
        return 8

    def evaluate_action_credits(self):
        return self.collected


class Round2Score(RoboticsScore):
    """ Concrete score sub-class for round 2.

    It counts:
      - the number of blocks successfully installed
      - the number of empty areas at the end of the match
      - the number of areas with same color blocks
      - the time bonus when mission fulfilled
    """
    items = RoboticsScore.items + ('installed', 'empty_areas', 'homogeneous_areas')
    installed = 0
    empty_areas = 0
    homogeneous_areas = 0

    def __init__(self, total_time=0, installed=0, empty_areas=0, homogeneous_areas=0):
        super(Round2Score, self).__init__(total_time)
        self.installed = installed
        self.empty_areas = empty_areas
        self.homogeneous_areas = homogeneous_areas

    @classmethod
    def max_action_credits(cls):
        """ The max action credits corresponds to :
          - 8 valid blocks
          - no empty area
          - 3 homogeneous ares
        """
        return 11

    def evaluate_action_credits(self):
        malus = self.empty_areas if self.installed > 4 else 0
        return self.installed - malus + self.homogeneous_areas


class Round3Score(RoboticsScore):
    """ Concrete score sub-class for round 3.

    It counts:
      - the installed block position WRT the line (fully inside, partly inside, outside)
      - the number of "cable" elements moved outside the line
      - the time bonus when mission fulfilled
    """
    items = RoboticsScore.items + ('position', 'moved')

    OUTSIDE, PARTLY_INSIDE, FULLY_INSIDE = range(3)
    placement_points = [0, 5, 10]

    position = 0

    def __init__(self, total_time=0, position=FULLY_INSIDE, moved=0):
        super(Round3Score, self).__init__(total_time)
        self.position = position
        self.moved = moved

    @classmethod
    def max_action_credits(cls):
        """ The max action credits corresponds to the block fully inside the line, and no
        surrounding block moved outside.
        """
        return cls.placement_points[cls.FULLY_INSIDE]

    def evaluate_action_credits(self):
        return self.placement_points[self.position] - self.moved
