#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Process command and get the information about it.
"""
from subprocess import Popen, PIPE
from time import time, process_time


def process_execution(command: list, display_output: bool = True, display_information: bool = False,
                      terminate_on_error: bool = True) -> dict:
    """
    Run a process in linux and print the output.

    :type command: list
    :param command: Linux command which want to execute with parameters.

    :type display_output: bool
    :param display_output: Display the standard output.

    :type display_information: bool
    :param display_information: Display the information of the command.

    :type terminate_on_error: bool
    :param terminate_on_error: Exit the application if an error occurs.

    :rtype: dict
    :return: Dictionary with the return code, the standard output and the error output.
    """
    if display_information:
        print('Command:', ' '.join(command))

    start_time = time()
    start_time_cpu = process_time()
    process = Popen(command, stderr=PIPE, stdout=PIPE)
    output = process.communicate()
    finish_time = time() - start_time
    finish_time_cpu = process_time() - start_time_cpu
    data = {'code': process.returncode, 'stdout': output[0].decode(), 'stderr': output[1].rstrip(b'\n').decode(),
            'finish_time': finish_time, 'finish_time_cpu': finish_time_cpu, }

    if display_information:
        print('data:\n', data)
        print()
        print(f'finish_time:     {finish_time}')
        print(f'finish_time_cpu: {finish_time_cpu}')
        print()

    if display_output:
        print(data["stdout"])

    data['error'] = False

    if data['stderr'] != '':
        print('ERROR: Cannot execute the command.')
        print('Command:', ' '.join(command))
        print(data['stderr'])
        data['error'] = True
        if terminate_on_error:
            exit(-1)

    return data
