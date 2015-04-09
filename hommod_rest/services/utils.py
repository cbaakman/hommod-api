#!/usr/bin/python

from hashlib import md5

from flask import current_app as flask_app

from time import time

import os
import tarfile
from glob import glob


def parseFasta(text):

    d = {}
    currentID = None
    for line in text.split('\n'):
        if line.startswith('>'):
            currentID = line.split()[0]
            d[currentID] = ''
        else:
            d[currentID] += line.strip()

    return d


def extract_info(tar_path):

    info = {}

    tf = tarfile.open(tar_path, 'r')

    infopath = os.path.join(
        os.path.splitext(os.path.basename(tar_path))[0], 'selected-targets.txt')
    if infopath in tf.getnames():
        for line in tf.extractfile(infopath):
            if line.startswith('template:'):
                info['template'] = line.split(':')[1].strip()

    tf.close()

    return info


def extract_alignment(tar_path):

    alignment = {}

    tf = tarfile.open(tar_path, 'r')

    fastapath = os.path.join(os.path.splitext(os.path.basename(tar_path))[0],
                             'align.fasta')
    if fastapath in tf.getnames():
        alignment = parseFasta(tf.extractfile(fastapath).read())

    tf.close()

    return alignment


def extract_model(tar_path):

    contents = ''
    tf = tarfile.open(tar_path, 'r')

    pdbpath = os.path.join(os.path.splitext(os.path.basename(tar_path))[0],
                           'target.pdb')
    if pdbpath in tf.getnames():
        contents = tf.extractfile(pdbpath).read()

    tf.close()

    return contents


def list_models_of(sequence, species, position):

    h = md5(sequence).hexdigest()

    l = []
    for f in glob(
        os.path.join(flask_app.config['MODELDIR'],
                     '%s-%s-3%s-*%s-%s_%s_*-*.tgz' %
                     (h[:8], h[8:12], h[13:16], h[17:20], h[20:], species))):

        age = time() - os.path.getmtime(f)
        if age >= flask_app.config['MAX_MODEL_DAYS']*24*60*60:
            continue

        name = os.path.splitext(os.path.basename(f))[0]
        ran = name.split('_')[-1].split('-')

        start = int(ran[0])
        end = int(ran[1])

        if position >= start and position <= end:
            l.append(f)

    return l