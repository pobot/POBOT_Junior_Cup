#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Eric Pascual'

import os

from GoogleTTS import audio_extract

OUTPUT_DIR = "assets"

args = {
    'language': 'fr',
    'output': 'test.mp3'
}

chunks = {
    ("à la table. %d.", 'table'),
    ('par le jury. %d.', 'jury')
}

for i in range(1, 4):
    for chunk, mp3_name in chunks:
        args['output'] = os.path.join(OUTPUT_DIR, '%s_%02d.mp3' % (mp3_name, i))
        audio_extract(input_text=chunk % i, args=args)

for i in range(1, 22):
    args['output'] = os.path.join(OUTPUT_DIR, 'team_is_awaited_%02d.mp3' % i)
    audio_extract(input_text="L'équipe. %d. est attendue" % i, args=args)

for h in range(12, 20):
    for m in range(0, 60, 10):
        args['output'] = os.path.join(OUTPUT_DIR, '%02dh%02d.mp3' % (h, m))
        audio_extract(input_text="à .%02dh%02d" % (h, m), args=args)


