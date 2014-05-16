#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" POBOT Junior Cup Web application.
"""

__author__ = 'eric'

import os
import logging
import json
import threading

import tornado.ioloop
import tornado.web
import tornado.log
from tornado.web import HTTPError

from pjc.tournament import Team, Tournament
from pjc.pjc2014 import *
import pjc.web.api
import pjc.web.tv
import pjc.web.admin
from pjc.web import uimodules


APP_NAME = 'pjc-compmgr'

_here = os.path.dirname(__file__)
_lib_root = os.path.join(_here, '../lib/pjc')


class PJCWebApp(tornado.web.Application):
    """ The Web application
    """
    TOURNAMENT_DAT = 'tournament.dat'
    TEAMS_CFG = 'teams.cfg'

    ROBOTICS_ROUND_TYPES = (Round1Score, Round2Score, Round3Score)

    # how many teams per TV display page
    TV_PAGE_SIZE = 10

    _res_home = os.path.join(_lib_root, "web/static")
    _templates_home = os.path.join(_lib_root, "web/templates")
    _data_home = None

    class WSHHelp(tornado.web.RequestHandler):
        """ Returns the paths defined for the application.

        Intended for help when working with curl at command line.
        """
        def get(self, *args, **kwargs):
            self.write("Defined routes :\n")
            for handler in PJCWebApp.handlers:
                self.write("- %s\n" % handler[0])

    handlers = \
        pjc.web.admin.handlers + \
        pjc.web.tv.handlers + \
        pjc.web.api.handlers + \
        [
            (r"/help", WSHHelp),

            (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(_res_home, 'css')}),
            (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(_res_home, 'js')}),
            (r"/img/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(_res_home, 'img')}),
            (r"/docs/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(_res_home, 'docs')})
        ]

    def __init__(self, settings_override):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.INFO)
        self.log.info('starting')

        self._lock = threading.Lock()

        settings = {
            'debug': False,
            'template_path': self._templates_home,
            'ui_modules': uimodules,
        }

        self._data_home = settings_override['data_home']
        if not os.path.exists(self._data_home):
            self.log.warning('creating data home (%s) - no team data available' % self._data_home)
            os.makedirs(self._data_home)
        elif not os.path.isdir(self._data_home):
            raise ValueError('data_home : path exists and is not a directory (%s)' % self._data_home)
        else:
            checker_path = os.path.join(self._data_home, '$$tmp')
            try:
                with file(checker_path, 'wt') as fp:
                    fp.write('test')
            except Exception:
                raise ValueError('data_home : cannot write in directory (%s)' % self._data_home)
            else:
                os.remove(checker_path)

        settings.update(settings_override)
        self.debug = settings['debug']
        if self.debug:
            self.log.setLevel(logging.DEBUG)

        self._display_sequence = json.loads(settings['display_sequence'])
        self._client_sequences = {}
        self._tv_message = None

        # try to load a previously saved tournament if any, or create a new one otherwise
        self._tournament = Tournament(self.ROBOTICS_ROUND_TYPES)
        try:
            self._load_tournament(self._tournament)
        except IOError as e:
            self.log.warn('... no previous tournament data found => initializing new one')
            self._initialize_tournament(self._tournament)
        else:
            self.log.info('... done')

        super(PJCWebApp, self).__init__(self.handlers, **settings)

    def _initialize_tournament(self, tournament):
        """ Initializes a new tournament instance, loading the teams definition if the related configuration
        file exists

        :return: a Tournament instance
        """
        teams_cfg = os.path.join(self._data_home, self.TEAMS_CFG)
        if os.path.exists(teams_cfg):
            self.log.info('loading teams configuration from %s' % teams_cfg)
            with file(teams_cfg, 'rt') as fp:
                teams_cfg = json.load(fp)
                for name, level in teams_cfg:
                    tournament.add_team(Team(name, level))
            self.log.info('... done')
        else:
            self.log.warn('no team configuration found in %s' % self._data_home)

    @property
    def _tournament_file_path(self):
        return os.path.join(self._data_home, self.TOURNAMENT_DAT)

    def _load_tournament(self, tournament, silent=False):
        self.log.info('loading tournament from %s', self._tournament_file_path)
        with file(self._tournament_file_path, 'rb') as fp:
            tournament.from_dict(json.load(fp))

    def save_tournament(self):
        """ Saves the tournament to disk.
        """
        with file(self._tournament_file_path, 'wb') as fp:
            json.dump(self._tournament.as_dict(), fp, indent=4)
            self.log.info('tournament saved to %s' % self._tournament_file_path)

    def reset_tournament(self):
        """ Deletes the saved tournament and restarts with a new one
        """
        try:
            os.remove(self.TOURNAMENT_DAT)
        except OSError:
            pass
        self._initialize_tournament(self._tournament)
        self.log.info('tournament cleared')

    def client_is_known(self, client):
        return client in self._client_sequences

    def get_client_sequence(self, client):
        with self._lock:
            if self.debug:
                self.log.debug('sequences=%s', self._client_sequences)
            key = str(client)
            try:
                sequence = self._client_sequences[key]
                if len(sequence) == 0:
                    raise KeyError()
            except KeyError:
                sequence = self._display_sequence[:]
                self._client_sequences[key] = sequence
        return sequence

    @property
    def display_sequence(self):
        return self._display_sequence

    @display_sequence.setter
    def display_sequence(self, sequence):
        with self._lock:
            self._display_sequence = sequence[:]
            self.log.info("display sequence changed to : %s", self._display_sequence)
            self._client_sequences = {}

    def required_pages(self, display):
        if display == 'ranking':
            return ((len(self.tournament.get_competing_teams()) - 1) / self.TV_PAGE_SIZE) + 1
        else:
            return ((self.tournament.team_count - 1) / self.TV_PAGE_SIZE) + 1

    @property
    def title(self):
        return "PJCWebApplication"

    @property
    def tv_message(self):
        return self._tv_message

    @tv_message.setter
    def tv_message(self, msg):
        self._tv_message = msg

    @tv_message.deleter
    def tv_message(self):
        self._tv_message = None

    @property
    def tournament(self):
        return self._tournament

    def start(self, port=8080):
        """ Starts the application
        """
        self.listen(port)
        try:
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            print # cosmetic to keep log messages nicely aligned
            self.log.info('SIGTERM caught')


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

        app = PJCWebApp(cli_settings)
        app.start()

    except Exception as e:
        log.exception('unexpected error - aborting')

    else:
        log.info('terminated')