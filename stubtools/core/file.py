# -*- coding: utf-8 -*-
# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-08 11:30:11
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-11-09 11:09:31
# --------------------------------------------

import os

def write_file(file_path, data, create_path=True):
    full_path = os.path.abspath(file_path)          # Make it a full path to reduce issues in parsing direcotry from file
    file_directory = os.path.dirname(full_path)

    # Check the directory exists
    if not os.path.exists(file_directory):
        # Create the full path if needed
        os.makedirs(file_directory)

    FILE = open(full_path, "w")
    FILE.write(data)
    FILE.close()
