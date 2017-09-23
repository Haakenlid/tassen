# -*- coding: utf-8 -*-
"""
Utilities for synchronising staging files between home server, S3 and database
"""
import glob
import os
import time
from datetime import datetime, timedelta

from django.conf import settings

# import logging

IMAGES_DIR = 'IMAGES'
PDF_DIR = 'PDF'
BYLINE_DIR = 'BYLINE'


def timestamp(delta, fallback):
    """Calculates seconds since epoch of current time minus delta.
    If delta is out of range, calculates timestamp of fallback datetime
    instead.
    """
    try:
        dt = datetime.now() - delta
    except (OverflowError):
        # date out of bounds
        dt = fallback
    return int(time.mktime(dt.timetuple()))


def new_staging_files(
    staging_subdirectory,
    fileglob='*.*',
    min_age=timedelta.min,
    max_age=timedelta.max
):
    """Check for new or updated files in staging area."""
    directory = os.path.join(settings.STAGING_ROOT, staging_subdirectory)
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    all_files = glob.glob(fileglob)
    min_mtime = timestamp(min_age, fallback=datetime.max)
    max_mtime = timestamp(max_age, fallback=datetime.min)
    files = [
        file for file in all_files
        if min_mtime > os.path.getmtime(file) > max_mtime
    ]
    return directory, sorted(files)


def new_staging_images(**kwargs):
    """Check for new or updated images in staging area"""
    arguments = dict(
        staging_subdirectory=IMAGES_DIR,
        fileglob='*.jpg',
    )
    arguments.update(kwargs)
    return new_staging_files(**arguments)


def new_staging_byline_images(**kwargs):
    """Check for new or updated byline images in staging area"""
    arguments = dict(
        staging_subdirectory=BYLINE_DIR,
        fileglob='*.jpg',
        max_age=timedelta(days=1),
    )
    arguments.update(kwargs)
    return new_staging_files(**arguments)


def new_staging_pdf_files(**kwargs):
    """Check for new or updated pdf files in staging area"""
    arguments = dict(
        staging_subdirectory=PDF_DIR,
        fileglob='UNI1*VER*000.pdf',
        max_age=timedelta(days=100),
    )
    arguments.update(kwargs)
    return new_staging_files(**arguments)
