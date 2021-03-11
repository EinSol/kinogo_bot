
import grequests
import requests
import math
import os


def get_file(file_name, url, chunk_size=52428800):
    print('Start downloading')

    response = requests.get(url, stream=True)
    expected_size = int(response.headers['Content-Length'])

    regular_workers_count = math.floor(expected_size / 1024 / 1024 / 100)
    extra_worker_bytes = expected_size - regular_workers_count * 1024 * 1024 * 100

    stop_byte = 0

    headers = list()
    print('Get chunks')
    for x in range(regular_workers_count):
        print('chunks')
        if x == 0:
            start_byte = chunk_size * x
        else:
            start_byte = (chunk_size * x) + 1
        stop_byte = chunk_size * (x + 1)

        headers.append({'Range': f'bytes={start_byte}-{stop_byte}'})

    if extra_worker_bytes > 0 and expected_size > chunk_size:
        headers.append({'Range': f'bytes={stop_byte + 1}-{expected_size}'})
    else:
        headers.append({'Range': f'bytes{stop_byte}-{expected_size}'})

    rs = (grequests.get(url, headers=h) for h in headers)

    downloads = grequests.map(rs)
    rs.close()
    print('download chunks')
    with open(f'{file_name}.mp4', 'wb') as f:
        for download in downloads:
            f.write(download.content)

    print('combine chunks')

    path = os.path.abspath(f'{file_name}.mp4')
    size = ((os.path.getsize(path)) / 1024) / 1024

    if size > 2048:
        print('File is to big')
        split_in_half(f'{file_name}.mp4')
        path1 = os.path.abspath(f'{file_name}.mp4')
        path2 = os.path.abspath(f'{file_name}.mp4')
        print('Successfully downloaded (big film)')
        return [path1, path2]
    else:
        print('Successfully downloaded')
        return [path]


def split_in_half(file_name):
    print('Splitting file...')
    console_response = os.popen(f'ffmpeg -i {file_name} 2>&1 | grep "Duration"').read()

    length = console_response.split(' ')[3].replace(',', '').split('.')[0]
    splitted_length = length.split(':')
    converted_length = int(splitted_length[0]) * 60 * 60 + int(splitted_length[1]) * 60 + int(splitted_length[2])
    half_point_seconds = int(converted_length / 2)
    formatted_half_point = f'{int(half_point_seconds / 60 /60)}:{int((half_point_seconds / 60) % 60)}:{half_point_seconds % 60}'

    os.popen(f'ffmpeg -ss 00:00:00 -t {formatted_half_point} -i {file_name} -acodec copy -vcodec copy {"part1_" + file_name}').read()
    os.popen(f'ffmpeg -ss {formatted_half_point} -t {length} -i {file_name} -acodec copy -vcodec copy {"part2_" + file_name}').read()

