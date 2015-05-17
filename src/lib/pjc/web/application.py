# -*- coding: utf-8 -*-

import json
import logging
import os
import threading
import tornado.ioloop
import tornado.web

from pjc.current_edition import Round1Score, Round2Score, Round3Score
from pjc.tournament import Tournament
from pjc.web import admin, api, tv, uimodules

__author__ = 'Eric Pascual'


class PJCWebApp(tornado.web.Application):
    """ The Web application
    """
    TOURNAMENT_DATA_FILE = 'tournament.dat'
    VERSION_FILE = 'version.txt'

    TEAMS_DATA_FILE = 'teams.csv'
    PLANNING_DATA_FILE = 'planning.csv'

    ROBOTICS_ROUND_TYPES = (Round1Score, Round2Score, Round3Score)

    # how many teams per TV display page
    TV_PAGE_SIZE = 10

    _data_home = None

    class WSHHelp(tornado.web.RequestHandler):
        """ Returns the paths defined for the application.

        Intended for help when working with curl at command line.
        """
        def get(self, *args, **kwargs):
            self.write("Defined routes :\n")
            for handler in self._handlers:
                self.write("- %s\n" % handler[0])

    def __init__(self, root, settings_override):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.INFO)

        self.log.info('starting')

        self._res_home = os.path.join(root, "static")
        self._templates_home = os.path.join(root, "templates")

        self._handlers = \
            admin.handlers + \
            tv.handlers + \
            api.handlers + \
            [
                (r"/help", self.WSHHelp),

                (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(self._res_home, 'css')}),
                (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(self._res_home, 'js')}),
                (r"/img/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(self._res_home, 'img')}),
                (r"/fonts/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(self._res_home, 'fonts')}),
                (r"/docs/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(self._res_home, 'docs')}),
                (r"/(.*)", tornado.web.StaticFileHandler, {"path": self._res_home})
            ]

        self._lock = threading.Lock()

        settings = {
            'debug': False,
            'template_path': self._templates_home,
            'ui_modules': uimodules,
        }

        self._data_home = settings_override['data_home']
        self.log.info("data home: %s", self._data_home)

        if not os.path.exists(self._data_home):
            self.log.warning('creating data home (%s) - no team data available' % self._data_home)
            os.makedirs(self._data_home)
        elif not os.path.isdir(self._data_home):
            raise ValueError('data_home : path exists and is not a directory (%s)' % self._data_home)
        else:
            self._version = self._get_version()
            self.log.info('version: %s', self._version)

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

        super(PJCWebApp, self).__init__(self._handlers, **settings)

    @property
    def version(self):
        return self._version

    def _get_version(self):
        version_file_path = os.path.join(self._data_home, self.VERSION_FILE)
        try:
            with open(version_file_path, 'rt') as fp:
                return Version(fp)
        except IOError:
            return Version()

    def _initialize_tournament(self, tournament):
        """ Initializes a tournament instance, loading the teams definition if the related configuration
        file exists
        """
        teams_file = os.path.join(self._data_home, self.TEAMS_DATA_FILE)
        if os.path.exists(teams_file):
            self.log.info('loading teams from %s' % teams_file)
            with file(teams_file, 'rt') as fp:
                tournament.load_teams_info(fp)
            self.log.info('... done')
        else:
            self.log.warn('no team file found in %s' % self._data_home)

        planning_file = os.path.join(self._data_home, self.PLANNING_DATA_FILE)
        if os.path.exists(planning_file):
            self.log.info('loading planning from %s' % planning_file)
            with file(planning_file, 'rt') as fp:
                tournament.load_teams_plannings(fp)

            self.log.info('consolidating planning')
            tournament.consolidate_planning()

            self.log.info('assigning tables and juries')
            tournament.assign_tables_and_juries()

            self.log.info('... done')

        else:
            self.log.warn('no planning file found in %s' % self._data_home)

    @property
    def _tournament_file_path(self):
        return os.path.join(self._data_home, self.TOURNAMENT_DATA_FILE)

    def _load_tournament(self, tournament, silent=False):
        self.log.info('loading tournament from %s', self._tournament_file_path)
        with file(self._tournament_file_path, 'rb') as fp:
            tournament.deserialize(json.load(fp))

    def save_tournament(self):
        """ Saves the tournament to disk.
        """
        with file(self._tournament_file_path, 'wb') as fp:
            json.dump(self._tournament.serialize(), fp, indent=4)
            self.log.info('tournament saved to %s' % self._tournament_file_path)

    def reset_tournament(self):
        """ Deletes the saved tournament and restarts with a new one
        """
        try:
            os.remove(self.TOURNAMENT_DATA_FILE)
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
        elif display == 'next_schedules':
            return 1
        else:
            return ((self.tournament.team_count(present_only=True) - 1) / self.TV_PAGE_SIZE) + 1

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


class Version(object):
    def __init__(self, fp=None):
        if fp:
            v = (fp.readline() + '.0.0').split('.')[:3]
            self.major, self.minor = [int(f) for f in v[:2]]
            self.build = v[2]
        else:
            self.major = self.minor = self.build = None

    def __str__(self):
        if self.major:
            return "%d.%d.%s" % (self.major, self.minor, self.build)
        else:
            return 'n/a'