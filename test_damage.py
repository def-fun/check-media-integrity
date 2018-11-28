#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script works in Linux, not tested in Windows
# First argument is the media file to clone and damage, and the second argument is the working folder to put clones to
# e.g:
# test_damage.py test_folder/files/deep/050807-124755.jpg /tmp

__author__ = "Fabiano Tarlao"
__copyright__ = "Copyright 2018, Fabiano Tarlao"
__credits__ = ["Fabiano Tarlao"]
__license__ = "GPL3"
__version__ = "0.9.3"
__maintainer__ = "Fabiano Tarlao"
__status__ = "Beta"

import shutil
import os
import random
import check_mi
import sys


def damage_file(filename, offset, size, full_noise=False):
    num_noise = 0#random.randrange(256)
    bytes = bytearray(size)
    for i in range(len(bytes)):
        bytes[i] = random.randrange(256) if full_noise else num_noise
    fh = open(filename, "r+b")
    fh.seek(offset)
    fh.write(bytes)
    fh.close()


def damage_clone(filename, dest_filename, offset, size, full_noise=False):
    shutil.copy(filename, dest_filename)
    damage_file(dest_filename, offset, size, full_noise=full_noise)


def truncate_clone(filename, dest_filename, file_size):
    shutil.copy(filename, dest_filename)
    fh = open(dest_filename, "r+b")
    fh.truncate(file_size)


def random_damage_clone(filename, dest_filename, size, full_noise=False):
    statinfo = os.stat(filename)
    file_size = statinfo.st_size
    offset = random.randrange(file_size)
    damage_clone(filename, dest_filename, offset, min(size, file_size - offset),full_noise=full_noise)


def random_truncate_clone(filename, dest_filename, max_perc):
    statinfo = os.stat(filename)
    file_size = int(statinfo.st_size * (1.0 - random.random() * (max_perc / 100.0)))
    truncate_clone(filename, dest_filename, file_size)


NUMBER_PER_CASE = 20
DAMAGE_SIZES = [4096, 16556, 256000, 2 * 1048576]
PERC_TRUNC = []


def main():
    if len(sys.argv) != 3:
        test_file = 'test_folder/files/deep/050807-124755.jpg'
        temp_folder = '/tmp'
    else:
        test_file = sys.argv[1]
        temp_folder = sys.argv[2]

    orig_statinfo = os.stat(test_file)
    dest_test_file = os.path.join(temp_folder, os.path.basename(test_file))

    random.seed = 1

    print "Original image size:", orig_statinfo.st_size
    for damage_size in DAMAGE_SIZES:
        if damage_size >= orig_statinfo.st_size:
            break

        errors_def = 0
        errors_str = 0

        for i in range(NUMBER_PER_CASE):
            random_damage_clone(test_file, dest_test_file, damage_size,full_noise=True)
            res_def = check_mi.check_file(dest_test_file, error_detect='default')
            if not res_def[0]:
                errors_def += 1
            res_str = check_mi.check_file(dest_test_file, error_detect='strong')
            if not res_str[0]:
                errors_str += 1
        print "DAMAGE SIZE[bytes] random noise", damage_size
        print "Detected damages default:", 100 * float(errors_def) / NUMBER_PER_CASE, "%"
        print "Detected damages strong (affects only video):", 100 * float(errors_str) / NUMBER_PER_CASE, "%"

        errors_def = 0
        errors_str = 0

        for i in range(NUMBER_PER_CASE):
            random_damage_clone(test_file, dest_test_file, damage_size, full_noise=False)
            res_def = check_mi.check_file(dest_test_file, error_detect='default')
            if not res_def[0]:
                errors_def += 1
            res_str = check_mi.check_file(dest_test_file, error_detect='strong')
            if not res_str[0]:
                errors_str += 1
        print "DAMAGE SIZE[bytes] all zeros", damage_size
        print "Detected damages default:", 100 * float(errors_def) / NUMBER_PER_CASE, "%"
        print "Detected damages strong (affects only video):", 100 * float(errors_str) / NUMBER_PER_CASE, "%"

    for perc in PERC_TRUNC:
        errors_def = 0
        errors_str = 0

        for i in range(NUMBER_PER_CASE):
            random_truncate_clone(test_file, dest_test_file, perc)
            res_def = check_mi.check_file(dest_test_file, error_detect='default')
            if not res_def[0]:
                errors_def += 1
            res_str = check_mi.check_file(dest_test_file, error_detect='strong')
            if not res_str[0]:
                errors_str += 1
        print "TRUNCATE SIZE %", perc
        print "Detected damages default:", 100 * float(errors_def) / NUMBER_PER_CASE, "%"
        print "Detected damages strong (affects only video):", 100 * float(errors_str) / NUMBER_PER_CASE, "%"


if __name__ == "__main__":
    main()
