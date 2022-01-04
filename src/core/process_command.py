#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Process command and get the information about it.
"""
from subprocess import Popen, PIPE
from time import time, process_time


def process_execution(command: list) -> dict:
    """
    Run a process in linux and print the output.

    :type command: list
    :param command: Linux command which want to execute with parameters.

    :rtype: dict
    :return: Dictionary with the return code, the standard output and the error output.
    """
    print('Command:', ' '.join(command))
    start_time = time()
    start_time_cpu = process_time()
    process = Popen(command, stderr=PIPE, stdout=PIPE)
    output = process.communicate()
    finish_time = time() - start_time
    finish_time_cpu = process_time() - start_time_cpu
    data = {'code': process.returncode, 'stdout': output[0].decode(), 'stderr': output[1].rstrip(b'\n').decode()}
    print('data:\n', data)
    print()
    print(f'finish_time:     {finish_time}')
    print(f'finish_time_cpu: {finish_time_cpu}')
    print()

    if data['stderr'] != '':
        print('ERROR: Cannot execute the command.')
        print('Command:', ' '.join(command))
        print(data['stderr'])
        exit(-1)

    return data
