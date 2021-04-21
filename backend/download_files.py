import requests
import os



#
# def get_file(file_name, url, chunk_size=52428800):
#     print('Start downloading')
#     file_name = file_name.replace(' ', '_').replace('(', '').replace(')', '')
#     r = requests.get(url, stream=True)
#
#     with open(f"{file_name}.mp4", "wb") as Pypdf:
#
#         for chunk in r.iter_content(chunk_size=1024):
#
#             if chunk:
#                 Pypdf.write(chunk)
#
#     path = os.path.abspath(f'{file_name}.mp4')
#     size = ((os.path.getsize(path)) / 1024) / 1024
#
#     if size > 2048:
#         print('File is to big')
#         split_in_half(f'{file_name}.mp4')
#         path1 = os.path.abspath(f'{"part1_"+file_name}.mp4')
#         path2 = os.path.abspath(f'{"part2_"+file_name}.mp4')
#         print('Successfully downloaded (big film)')
#         return [path1, path2]
#     else:
#         print('Successfully downloaded')
#         return [path]


def download_file(file_name, url, chunk_size=1024*32):
    file_name = file_name.replace(' ', '_').replace('(', '').replace(')', '')

    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(f'{file_name}.mp4', 'wb') as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
    path = os.path.abspath(f'{file_name}.mp4')
    size = ((os.path.getsize(path)) / 1024) / 1024

    if size > 2048:
        print('File is to big')
        split_in_half(f'{file_name}.mp4')
        path1 = os.path.abspath(f'{"part1_" + file_name}.mp4')
        path2 = os.path.abspath(f'{"part2_" + file_name}.mp4')
        print('Successfully downloaded (big film)')
        os.remove(path)
        return [path1, path2]
    else:
        print('Successfully downloaded')
        return [path]


def split_in_half(file_name):
    print('Splitting file...')
    print(os.system('pwd'))
    print(file_name)
    console_response = os.popen(f'ffmpeg -i ./{file_name} 2>&1 | grep "Duration"').read()

    length = console_response.split(' ')[3].replace(',', '').split('.')[0]
    splitted_length = length.split(':')
    converted_length = int(splitted_length[0]) * 60 * 60 + int(splitted_length[1]) * 60 + int(splitted_length[2])
    half_point_seconds = int(converted_length / 2)
    formatted_half_point = f'{int(half_point_seconds / 60 / 60)}:{int((half_point_seconds / 60) % 60)}:{half_point_seconds % 60}'

    os.popen(
        f'ffmpeg -ss 00:00:00 -t {formatted_half_point} -i {file_name} -acodec copy -vcodec copy {"part1_" + file_name}').read()
    os.popen(
        f'ffmpeg -ss {formatted_half_point} -t {length} -i {file_name} -acodec copy -vcodec copy {"part2_" + file_name}').read()

