import argparse
import requests
import sys
from urllib.parse import urlencode

BASE_URL = 'https://api.themoviedb.org/3/{}'
SEARCH_SHOW_URL = BASE_URL.format('search/tv')
SHOW_URL = BASE_URL.format('tv/{}')
SEASON_URL = BASE_URL.format('tv/{}/season/{}')
TMDB_PARAMS = {'api_key': 'f090bb54758cabf231fb605d3e3e0468'}

def request(url, params=None):
    if params:
        url = url + '?' + urlencode(params)
    return requests.get(url).json()

def search_show(query, year=None):
    params = TMDB_PARAMS.copy()
    params['query'] = query
    if year is not None:
        params['year'] = str(year)
    return request(SEARCH_SHOW_URL, params)

def load_epsides_info(show_id):
    show_url = SHOW_URL.format(show_id)
    params = TMDB_PARAMS.copy()
    show_info = request(show_url, params=params)
    season_map = {}
    for season in show_info.get('seasons', []):
        season_url = SEASON_URL.format(show_id, season.get('season_number', 0))
        season_info = request(season_url, params=params)
        season_map[str(season.get('season_number', 0))] = season_info
    episode_list = []
    show_info['seasons'] = []
    for _, value in season_map.items():
        show_info['seasons'].append(value)
    for season in show_info.get('seasons', []):
        episode_list.extend(season.get('episodes', []))
    return episode_list

def main(args):
    response = search_show(args.name, args.year)
    results = response['results']
    results_count = len(results)
    if results_count == 0:
        print('No results found')
    else:
        show_index = 0
        if results_count != 1:
            print('Several results found:')
            for i, result in enumerate(results):
                print('{}. {}'.format(i + 1, result['name']))
            show_index = int(input('Enter show number: ')) - 1
        show = response['results'][show_index]
        episodes = load_epsides_info(show['id'])
        for episode in episodes:
            episode_name = episode['name']
            episode_number = episode['episode_number']
            season_number = episode['season_number']
            print('S{}E{}: {}'.format(season_number, episode_number, episode_name))
    return 0
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Shows series information from TBDB'
    )
    parser.add_argument('--name', type=str, required=True)
    parser.add_argument('--year', type=int, required=False, default=0)
    args = parser.parse_args()
    sys.exit(main(args))