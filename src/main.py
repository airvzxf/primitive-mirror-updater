"""
Entry point of the execution in this application.
"""
from csv import DictWriter
from datetime import datetime, timedelta
from json import loads
from shutil import which

from requests import get

from core.print_log import print_log
from core.process_command import process_execution

if __name__ == '__main__':
    show_log = True
    show_log_details = False

    print_log('# Sending request of the mirror status in JSON format.', show_log)
    response = get('https://archlinux.org/mirrors/status/json/')
    print_log(str(response.content), show_log_details)

    print_log('# Load the response to a JSON object.', show_log)
    json_object: dict = loads(response.content)

    print_log('# Check if the field "urls" exists.', show_log)
    if 'urls' not in json_object.keys():
        print(response.content)
        print('\nERROR: The field URLS, not exists in the JSON response.\n')
        exit(-1)

    print_log('# Check if exists at least one server.', show_log)
    if len(json_object['urls']) < 1:
        print(json_object['urls'])
        print('\nERROR: It needs at least one server.\n')
        exit(-1)

    print_log('# Start to filter the servers.', show_log)
    mirror_list = []
    utc_now = datetime.utcnow()
    utc_before = utc_now - timedelta(days=5)
    for server in json_object['urls']:
        if server['last_sync'] is None:
            continue

        last_sync = datetime.strptime(server['last_sync'], '%Y-%m-%dT%H:%M:%SZ')
        if utc_before >= last_sync:
            continue

        if (
                server['active'] is True
                and server['protocol'] == 'https'
                and server['delay'] is not None
                and server['delay'] <= 259200
                # and server['completion_pct'] == 1.0
        ):
            mirror_list.append(server)

    print_log('# List of the filtered servers.', show_log)
    print_log(str(mirror_list), show_log)

    print_log(f'# Total of filtered servers: {len(mirror_list)}.', show_log)

    with open('filtered-mirror-list.csv', 'w') as output_file:
        csv_headers = mirror_list[0].keys()
        dict_writer = DictWriter(output_file, csv_headers)
        dict_writer.writeheader()
        dict_writer.writerows(mirror_list)
        print_log('# The filtered servers are stored in the file: ./filtered-mirror-list.json', show_log)

    print_log('# Shows the original server in the mirror list.', show_log)
    command = ['cat', '/etc/pacman.d/mirrorlist']
    process_execution(command)

    print_log('# Backup the mirror list.', show_log)
    command = ['sudo', 'cp', '/etc/pacman.d/mirrorlist', '/etc/pacman.d/mirrorlist.primitive-backup']
    process_execution(command, display_output=False)

    test_packages = {'62.4 MB': 'blobwars-data', '135.5 MB': 'fillets-ng-data', '268.1 MB': 'megaglest-data',
                     '437.5 MB': 'frogatto-data', '872.4 MB': 'xonotic-data', '1.3 GB': '0ad-data', }
    download_at = '437.5 MB'
    package = test_packages[download_at]
    server_information = []
    print_log(f'# The package is {package} with {download_at}', show_log_details)

    error_log_file = 'primitive-error.log'
    open(error_log_file, 'w').close()

    csv_headers = [
        'Server',
        'Sync Time',
        'Sync CPU',
        'Install Time',
        'Install CPU',
        'Registered UTC Time',
        'Last Sync',
        'Completion PCT',
        'Delay',
        'Duration Avg',
        'Duration Std Dev',
        'Score',
        'Country',
        'ISOs',
        'IPv4',
        'IPv6',
        'Details',
    ]

    with open('primitive-mirror-list.csv', 'w') as output_file:
        dict_writer = DictWriter(output_file, csv_headers)
        dict_writer.writeheader()
        print_log('# The information is started to stored in the file: ./primitive-mirror-list.csv', show_log)

    for server in mirror_list:
        url = server['url']

        print_log(f'# Set the server to the mirror list:\n{url}', show_log)
        command = ['sudo', 'bash', '-c', f'echo "Server = {url}\$repo/os/\$arch" > /etc/pacman.d/mirrorlist']
        process_execution(command, display_output=False)

        print_log('# Shows the server in the mirror list.', show_log)
        command = ['cat', '/etc/pacman.d/mirrorlist']
        process_execution(command)

        print_log(f'# Check if the package {package} is installed.', show_log)
        pacman_bin = which('pacman')
        command = [pacman_bin, '--noconfirm', '-Ss', package]
        output = process_execution(command, display_output=False)

        if '[installed]' in output['stdout']:
            print_log(f'# Remove the package {package}.', show_log)
            command = ['sudo', pacman_bin, '--noconfirm', '-Rns', package]
            process_execution(command, display_output=False)

        print_log('# Clean the pacman\'s cache.', show_log)
        command = ['sudo', pacman_bin, '--noconfirm', '-Sc']
        process_execution(command, display_output=False)

        print_log('# Update the package databases.', show_log)
        command = ['sudo', pacman_bin, '-Syy']
        synchronization = process_execution(command, display_output=False, terminate_on_error=False)
        if synchronization['error']:
            with open(error_log_file, 'a') as output_file:
                output_file.write('# --------------------------------------\n\n')
                output_file.write(f'Server: {url}\n')
                output_file.write('Process: Synchronization\n')
                output_file.write(f'Error:\n{synchronization["stderr"]}\n')
                output_file.write('\n')
            continue
        else:
            print_log(f'Finished in {synchronization["finish_time"]}', show_log)

        print_log(f'# Download the package: {package}.', show_log)
        command = ['sudo', pacman_bin, '--noconfirm', '--downloadonly', '-S', package]
        installation = process_execution(command, display_output=False, terminate_on_error=False)
        if installation['error']:
            with open(error_log_file, 'a') as output_file:
                output_file.write('# --------------------------------------\n\n')
                output_file.write(f'Server: {url}\n')
                output_file.write('Process: Installation\n')
                output_file.write(f'Error:\n{installation["stderr"]}\n')
                output_file.write('\n')
            continue
        else:
            print_log(f'Finished in {installation["finish_time"]}', show_log)

        information = {
            'Server': server['url'],
            'Sync Time': synchronization['finish_time'],
            'Sync CPU': synchronization['finish_time_cpu'],
            'Install Time': installation['finish_time'],
            'Install CPU': installation['finish_time_cpu'],
            'Registered UTC Time': datetime.utcnow().isoformat(),
            'Last Sync': server['last_sync'],
            'Completion PCT': server['completion_pct'],
            'Delay': server['delay'],
            'Duration Avg': server['duration_avg'],
            'Duration Std Dev': server['duration_stddev'],
            'Score': server['score'],
            'Country': server['country'],
            'ISOs': server['isos'],
            'IPv4': server['ipv4'],
            'IPv6': server['ipv6'],
            'Details': server['details'],
        }
        server_information.append(information)

        with open('primitive-mirror-list.csv', 'a', newline='') as output_file:
            dict_writer = DictWriter(output_file, csv_headers)
            dict_writer.writerow(information)
            print_log('# The information is stored in the file: ./primitive-mirror-list.csv', show_log)

        # if url == 'https://mirror.umd.edu/archlinux/':
        #     break

        process_execution(['sleep', '5'], display_output=False)

    print_log(f'# Servers Information:\n{server_information}', show_log)
