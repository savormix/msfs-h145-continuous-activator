import json
import os
import os.path
import sys
import time

from argparse import ArgumentParser
from base64 import standard_b64decode
from datetime import datetime
from json import JSONDecodeError

from requests import Session
from requests.exceptions import RequestException, Timeout

CHECK_INTERVAL: float = 300
TIMEOUT_COOLDOWN: float = 5


def _get_expiry(encoded_license: str) -> float:
    meta_start = encoded_license.find('.') + 1
    meta = json.loads(standard_b64decode(encoded_license[meta_start:encoded_license.find('.', meta_start)]))
    return meta['exp'] / 1000


def _format_expiry(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).isoformat()


def _main() -> None:
    parser = ArgumentParser(description='Activates HPG H145 and keeps activating it once it is about to expire.')
    parser.add_argument('--package', metavar='dir', help='Path to the directory with Activator.exe')
    cmd_args = parser.parse_args()
    activation_dir = None
    if cmd_args.package is None:
        opt_file_path = os.path.join(os.getenv('APPDATA'), 'Microsoft Flight Simulator', 'UserCfg.opt')
        with open(opt_file_path, 'rt', encoding='utf-8') as opt_file:
            for line in opt_file:
                line = line.strip()
                if not line.startswith('InstalledPackagesPath'):
                    continue
                path_start = line.find('"') + 1
                activation_dir = os.path.join(line[path_start:line.rfind('"')], 'Community', 'hpg-airbus-h145',
                                              'HPGH145')
    else:
        activation_dir = os.path.join(cmd_args.package, 'HPGH145')

    print('H145 activation directory: "{}"'.format(activation_dir or '<UNKNOWN>'))

    if activation_dir is None:
        parser.print_usage()
        sys.exit(1)

    try:
        with open(os.path.join(activation_dir, 'keycode.txt'), 'rt', encoding='us-ascii') as key_file:
            key = key_file.read().strip()
        current_expiry = 0
    except FileNotFoundError:
        print('License key file missing. Please activate once using Activator.exe')
        sys.exit(1)
    try:
        with open(os.path.join(activation_dir, 'license.txt'), 'rt', encoding='us-ascii') as license_file:
            current_expiry = _get_expiry(license_file.read())
        print('H145 activation expires on {} (local time)'.format(_format_expiry(current_expiry)))
    except (FileNotFoundError, JSONDecodeError):
        print('H145 activation expiry unknown')

    with Session() as session:
        session.params = {
            'key': key
        }
        while True:
            now = time.time()
            if now < current_expiry - CHECK_INTERVAL:
                time.sleep(CHECK_INTERVAL)
                continue
            try:
                response = session.get('https://hpg-online-software-service.azurewebsites.net/api/Activate')
                if response.status_code == 400:
                    print('Not a valid license key: "{}"'.format(key))
                    sys.exit(1)
                if response.status_code != 200:
                    print('Unknown activation response: {}'.format(response.status_code))
                    raise Timeout()
                license_content = response.text
                with open(os.path.join(activation_dir, 'license.txt'), 'wt', encoding='us-ascii') as license_file:
                    license_file.write(license_content)
                current_expiry = _get_expiry(license_content)
                print('H145 has been activated, will expire on {} (local time)'.format(_format_expiry(current_expiry)))
            except Timeout:
                time.sleep(TIMEOUT_COOLDOWN)
                continue
            except RequestException as e:
                print(e)
            time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    _main()
