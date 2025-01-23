import os
import re
import sys
import argparse

from utils import is_directory, list_directories, input_positive_number
from naming import rename_tv_show_files

TV_SHOWS_FOLDER = 'TV Shows'

def is_properly_named(name):
    pattern = r'.+ \(\d{4}\)$'
    return bool(re.match(pattern, name))

def main(args):
    tv_shows_path = os.path.normpath(os.path.join(args.library_path, TV_SHOWS_FOLDER))
    tv_show_paths = list_directories(tv_shows_path)
    invalid_tv_shows = list(filter(lambda x: not is_properly_named(x), tv_show_paths))
    if len(invalid_tv_shows) != 0:
        print('[Invalid TV show names]')
        for invalid_tv_show in invalid_tv_shows:
            print(f' - {os.path.basename(invalid_tv_show)}')
        print()
    valid_tv_shows = list(filter(is_properly_named, tv_show_paths))
    if len(valid_tv_shows) != 0:
        print('[TV shows]')
        for tv_show_path in valid_tv_shows:
            print(f' - {os.path.basename(tv_show_path)}')
            season = 1
            start_episode = 1
            if args.interactive:
                season = input_positive_number('Enter season')
                start_episode = input_positive_number('Enter start episode')
            return_code = rename_tv_show_files(tv_show_path, season, start_episode, args.interactive)
            if return_code != 0:
                return return_code
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Unifies TV series files for Kodi'
    )
    parser.add_argument('--library_path', type=is_directory, default='Z:/')
    parser.add_argument('--interactive', action='store_true', help='Allows to enter season and start episode')
    args = parser.parse_args()
    sys.exit(main(args))