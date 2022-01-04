"""
Entry point of the execution in this application.
"""
from shutil import which

from core.print_log import print_log
from core.process_command import process_execution

# __PACMAN_BIN = which('pacman')  # default to use the system's pacman binary

if __name__ == '__main__':
    show_log = True
    show_log_details = False
    pacman_bin = which('pacman')
    test_packages = {'62.4 MB': 'blobwars-data', '135.5 MB': 'fillets-ng-data', '268.1 MB': 'megaglest-data',
                     '437.5 MB': 'frogatto-data', '872.4 MB': 'xonotic-data', '1.3 GB': '0ad-data', }

    # print_log('# Sending request of the mirror status in JSON format.', show_log)
    # response = get('https://archlinux.org/mirrors/status/json/')
    # print_log(str(response.content), show_log_details)
    #
    # print_log('# Load the response to a JSON object.', show_log)
    # json_object: dict = loads(response.content)
    #
    # print_log('# Check if the field "urls" exists.', show_log)
    # if 'urls' not in json_object.keys():
    #     print(response.content)
    #     print('\nERROR: The field URLS, not exists in the JSON response.\n')
    #     exit(-1)
    #
    # print_log('# Check if exists at least one server.', show_log)
    # if len(json_object['urls']) < 1:
    #     print(json_object['urls'])
    #     print('\nERROR: It needs at least one server.\n')
    #     exit(-1)
    #
    # print_log('# Start to filter.', show_log)
    # json_filtered = []
    # utc_now = datetime.utcnow()
    # utc_before = utc_now - timedelta(days=5)
    # for server in json_object['urls']:
    #     if server['last_sync'] is None:
    #         continue
    #
    #     last_sync = datetime.strptime(server['last_sync'], '%Y-%m-%dT%H:%M:%SZ')
    #     if utc_before >= last_sync:
    #         continue
    #
    #     if (
    #             server['active'] is True
    #             and server['protocol'] in ['http', 'https']
    #             and server['delay'] is not None
    #             # and server['delay'] <= 252000
    #             # and server['completion_pct'] == 1.0
    #     ):
    #         print('item: ', server)
    #         json_filtered.append(server)
    #
    # print_log(f'# Total of filtered servers: {len(json_filtered)}.', show_log)

    package = test_packages['268.1 MB']
    print('package:', package)
    print()

    print_log(f'# Check if the package {package} is installed.', show_log)
    command = [pacman_bin, '--noconfirm', '-Ss', package]
    output = process_execution(command)

    if '[installed]' in output['stdout']:
        print_log(f'# Remove the package {package}.', show_log)
        command = ['sudo', pacman_bin, '--noconfirm', '-Rns', package]
        process_execution(command)

    print_log('# Clean the pacman\'s cache.', show_log)
    command = ['sudo', pacman_bin, '--noconfirm', '-Sc']
    process_execution(command)

    print_log('# Update package list and upgrade all packages afterwards.', show_log)
    command = ['sudo', pacman_bin, '-Syyu']
    process_execution(command)

    print_log(f'# Install the package: {package}.', show_log)
    command = ['sudo', pacman_bin, '--noconfirm', '-S', package]
    process_execution(command)
