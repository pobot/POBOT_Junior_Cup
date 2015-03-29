#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" POBOT Junior Cup Web application.
"""
from pjc.web.application import PJCWebApp

__author__ = 'eric'

import os
import logging
import json

import pjc.web.application


APP_NAME = 'pjc-mc'

if __name__ == '__main__':
    import argparse

    logging.basicConfig(
        format="%(asctime)s.%(msecs).3d [%(levelname).1s] %(name)s > %(message)s",
        datefmt='%H:%M:%S'
    )

    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)

    # automatic selection of appropriate default data directory depending on running user
    default_data_home = '/var/lib/' + APP_NAME if os.getuid() == 0 else os.path.expanduser('~/.' + APP_NAME)

    try:
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument(
            '-D', '--debug',
            help='activates debug mode',
            dest='debug',
            action='store_true')
        parser.add_argument(
            '-d', '--data-home',
            help='data storage directory path',
            dest='data_home',
            default=default_data_home)
        seq_arg = parser.add_argument(
            '--display-sequence',
            help='TV display sequence (as a JSON array of page names)',
            dest='display_sequence',
            default='["progress", "scores"]')
        cli_args = parser.parse_args()

        if cli_args.debug:
            log.warn('debug mode activated')

        # expands the display_sequence if the keyword "all" has been used (debug mode only)
        if cli_args.display_sequence == "all":
            if cli_args.debug:
                displays = [d for d, _ in pjc.web.tv.get_selectable_displays()]
                cli_args.display_sequence = json.dumps(displays)
                log.warn('"--display-sequence all" option used. Sequence expanded to : %s' % displays)
            else:
                parser.exit(1, "'--display-sequence all' is allowed in debug mode only.")

        # build the Web app settings dictionary from the CLI args
        cli_settings = dict([
            (k, getattr(cli_args, k)) for k in dir(cli_args) if not k.startswith('_')
        ])

        log.info("command line arguments : %s", cli_settings)

        _here = os.path.dirname(__file__)
        _web_root = os.path.join(_here, '../lib/pjc/web')

        app = PJCWebApp(_web_root, cli_settings)
        app.start()

    except Exception as e:
        log.exception('unexpected error - aborting')

    else:
        log.info('terminated')