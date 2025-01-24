import os
import re
import sys
import argparse

from utils import is_directory, list_directories, input_positive_number, get_logs_filename, ensure_exists, LogsTee
from naming import rename_tv_show_files

TV_SHOWS_FOLDER = 'TV Shows'
APP_FOLDER = '.library'
LOGS_FOLDER = 'logs'
CACHE_FILE = 'library.cache'

def is_properly_named(name):
    pattern = r'.+ \(\d{4}\)$'
    return bool(re.match(pattern, name))

def read_cache(app_folder_path):
    cache_path = os.path.join(app_folder_path, CACHE_FILE)
    if not os.path.exists(cache_path):
        return set()
    with open(cache_path, 'r') as f:
        return set(line.strip() for line in f.readlines())

def update_cache(app_folder_path, tv_shows):
    cache_path = os.path.join(app_folder_path, CACHE_FILE)
    with open(cache_path, 'a+') as f:
        f.writelines(line + '\n' for line in tv_shows)

def main(args):
    app_folder_path = os.path.join(args.library_path, APP_FOLDER)
    logs_path = os.path.join(app_folder_path, LOGS_FOLDER)
    ensure_exists(app_folder_path)
    ensure_exists(logs_path)
    logs_filename = os.path.join(logs_path, get_logs_filename())
    cache = read_cache(app_folder_path)
    tv_shows_path = os.path.normpath(os.path.join(args.library_path, TV_SHOWS_FOLDER))
    tv_show_paths = list_directories(tv_shows_path)
    invalid_tv_shows = list(filter(lambda x: not is_properly_named(x), tv_show_paths))
    if len(invalid_tv_shows) != 0:
        print('[Invalid TV show names]')
        for invalid_tv_show in invalid_tv_shows:
            print(f' - {os.path.basename(invalid_tv_show)}')
        print()
    valid_tv_shows = list(filter(is_properly_named, tv_show_paths))
    processed_tv_shows = []
    if len(valid_tv_shows) != 0:
        print('[TV shows]')
        for tv_show_path in valid_tv_shows:
            tv_show_name = os.path.basename(tv_show_path)
            if tv_show_name in cache:
                continue
            print(f' - {tv_show_name}')
            season = 1
            start_episode = 1
            if args.interactive:
                season = input_positive_number('Enter season')
                start_episode = input_positive_number('Enter start episode')
            with LogsTee(logs_filename) as tee:
                return_code = rename_tv_show_files(tv_show_path, season, start_episode, args.interactive)
            if return_code == 0:
                processed_tv_shows.append(tv_show_name)
            else:
                print(f'Renaming {tv_show_name} failed')
    if len(processed_tv_shows) != 0:
        update_cache(app_folder_path, processed_tv_shows)
    else:
        print('No new TV shows')
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Unifies TV series files for Kodi'
    )
    parser.add_argument('--library_path', type=is_directory, default='Z:/')
    parser.add_argument('--interactive', action='store_true', help='Allows to enter season and start episode')
    args = parser.parse_args()
    sys.exit(main(args))