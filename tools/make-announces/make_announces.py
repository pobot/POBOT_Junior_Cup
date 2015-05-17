#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Eric Pascual'

import os
import argparse
from textwrap import dedent
from shutil import copyfileobj

from pjc.tournament import Tournament, TeamPlanning

SCRIPT_HOME = os.path.dirname(__file__)
CHUNKS_DIR = os.path.join(SCRIPT_HOME, 'chunks')


def make_announces(tournament, out_dir):
    def cat_files(in_files, out_file):
        with open(out_file, 'wb') as out_fp:
            for in_path in in_files:
                with open(in_path, 'rb') as in_fp:
                    copyfileobj(in_fp, out_fp)
        print(out_file)

    for team in tournament.registered_teams:
        planning = team.planning
        team_chunk = "team_is_awaited_%02d.mp3" % team.num

        for i, match in enumerate(planning.matches):
            table_chunk = "table_%02d.mp3" % match.table
            time_chunk = match.time.strftime("%Hh%M") + ".mp3"

            sequence = [os.path.join(CHUNKS_DIR, n) for n in (team_chunk, table_chunk, time_chunk)]
            announce_file = os.path.join(out_dir, "team_%02d_match_%d.mp3" % (team.num, i + 1))
            cat_files(sequence, announce_file)

        jury_chunk = "jury_%02d.mp3" % planning.presentation.jury
        time_chunk = planning.presentation.time.strftime("%Hh%M") + ".mp3"
        sequence = [os.path.join(CHUNKS_DIR, n) for n in (team_chunk, jury_chunk, time_chunk)]
        announce_file = os.path.join(out_dir, "team_%02d_jury.mp3" % team.num)
        cat_files(sequence, announce_file)

if __name__ == '__main__':
    def output_dir(value):
        path = os.path.abspath(os.path.join(SCRIPT_HOME, value))
        if os.path.exists(path) and not os.path.isdir(path):
            raise argparse.ArgumentTypeError('path exists and is not a directory (%s)' % path)
        return path

    parser = argparse.ArgumentParser(
        description=dedent("""
            Vocal announces generator.

            Generates all the vocal announces corresponding to the tournament planning,
            using a collection of synthesized sentence chunks.
        """),
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-t', '--teams-file',
                        help='teams data file\n(default: "%(default)s")',
                        type=file,
                        default='teams.csv')
    parser.add_argument('-p', '--planning-file',
                        help='planning data file\n(default: "%(default)s")',
                        type=file,
                        default='planning.csv')
    parser.add_argument('-o', '--output_dir',
                        help='output directory, created if not found\n(default: "%(default)s")',
                        type=output_dir,
                        default='./announces')
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    print(
        dedent("""
        input files :
        - %s
        - %s
        """
        ).strip() % (os.path.abspath(args.teams_file.name), os.path.abspath(args.planning_file.name))
    )

    _tournament = Tournament()
    print('loading team info')
    _tournament.load_teams_info(fp=args.teams_file)
    print('loading teams plannings')
    _tournament.load_teams_plannings(fp=args.planning_file)
    _tournament.assign_tables_and_juries()
    _tournament.consolidate_planning()

    make_announces(_tournament, args.output_dir)
