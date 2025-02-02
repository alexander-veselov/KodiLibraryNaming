import sys
import os
import argparse
import codecs
import chardet

from enum import Enum
from utils import list_files, is_directory, natural_keys, input_confirmation
    
class FileType(Enum):
    VIDEO = 0
    SUBTITLES = 1
    
def determine_file_type(file):
    VIDEO_FORMATS = [
        '.mkv',
        '.avi',
        '.mp4',
        '.mov',
        '.wmv',
        '.avchd',
        '.webm',
        '.flv'
    ]
    SUBTITLE_FORMATS = [
        '.srt',
        '.ass',
        '.sub',
        '.vtt',
        '.ssa',
        '.smi'
    ]
    _, extension = os.path.splitext(file)
    extension = extension.lower()
    if extension in VIDEO_FORMATS:
        return FileType.VIDEO
    elif extension in SUBTITLE_FORMATS:
        return FileType.SUBTITLES
    else:
        raise NotImplementedError()
        
def change_encoding(filepath, source_encoding, target_encoding):
    with codecs.open(filepath, 'r', source_encoding) as f:
        data = f.read()
    with codecs.open(filepath, 'w+', target_encoding) as f:
        f.write(data)
        
def determine_encoding(filepath):
    with codecs.open(filepath, 'rb') as f:
        result = chardet.detect(f.read())
        if result['confidence'] > 0.9:
            return result['encoding']
        else:
            raise NotImplementedError('Unexpected encoding {0} (confidence: {1})'
                .format(result['encoding'], result['confidence']))
    
def process_encodings(subtitles):
    encodings = dict()
    for subtitles_file in subtitles:
        encoding = determine_encoding(subtitles_file).lower()
        encodings[subtitles_file] = encoding
    utf8_files_count = list(encodings.values()).count('utf-8')
    utf8_sig_files_count = list(encodings.values()).count('utf-8-sig')
    if utf8_files_count + utf8_sig_files_count != len(encodings.values()):
        for file, encoding in encodings.items():
            print('"{0}" [{1}]'.format(file, encoding))
        if input_confirmation('The encoding is different from UTF-8. Convert these files to UTF-8?'):
            for file, encoding in encodings.items():
                change_encoding(file, encoding, 'utf-8')

def rename_files(files, season, start_episode, interactive):
    if len(files) == 0:
        return
    rename_candidates = dict()
    _, ext = os.path.splitext(files[0])
    season_label = 'S' + str(season)
    for number, file in enumerate(files):
        dirname = os.path.dirname(file)
        new_filename = season_label + 'E' + str(start_episode + number) + ext
        new_path = os.path.join(dirname, new_filename)
        if file != new_path:
            rename_candidates[file] = new_path
    if len(rename_candidates) == 0:
        return
    for filepath, new_filepath in rename_candidates.items():
        print('"{0}"\t=>\t"{1}"'.format(filepath, new_filepath))
    if not interactive or input_confirmation('Confirm rename'):
        for filepath, new_filepath in rename_candidates.items():
            os.rename(filepath, new_filepath)

def rename_tv_show_files(path, season, start_episode, interactive):
    files = {}
    for file_type in FileType:
        files[file_type] = []
    for file in list_files(path):
        file_type = determine_file_type(file)
        files[file_type].append(file)
    for file_type in FileType:
        files[file_type].sort(key=natural_keys)
    subtitles_exist = len(files[FileType.SUBTITLES]) != 0
    if subtitles_exist:
        if len(files[FileType.VIDEO]) != len(files[FileType.SUBTITLES]):
            print('The number of videos and subtitles are different')
            return 1
        process_encodings(files[FileType.SUBTITLES])
    for file_type in FileType:
        rename_files(files[file_type], season, start_episode, interactive)
    return 0

def main(args):
    return rename_tv_show_files(args.path, args.season, args.start_episode, not args.auto_confirm)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Unifies TV series files for Kodi'
    )
    parser.add_argument('--path', type=is_directory, required=True)
    parser.add_argument('--season', type=int, required=False, default=1)
    parser.add_argument('--start_episode', type=int, required=False, default=1)
    parser.add_argument('--auto_confirm', action='store_true')
    args = parser.parse_args()
    sys.exit(main(args))