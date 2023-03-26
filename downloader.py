# -*- coding: utf-8 -*-

"""Script to request mp3 of file from youtube API

Author : Kyosse

Date of creation : 23/03/2023

Last modification : 26/03/2023
"""
from googleapiclient.discovery import build
import youtube_dl
import os
import re


def is_valid_youtube_url(url: str) -> bool:
    """Check if a string is a valid YouTube URL.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    # Regular expression for matching YouTube URLs
    regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"

    # Check if the URL matches the regex
    return bool(re.match(regex, url))

def is_playlist(url: str) -> list:
    """Fonction that verify if the video linked is in a playlist and return 
    a list that contain : a boolean (True if the video is in a playlist), the video id,
    and the playlist id if there is one. 

    Args:
        url (str): url of the video to verify.

    Returns:
        list: List that contain a boolean (True if the video is in a playlist), the video id,
                and the playlist id if there is one. [Bool, video_id, playlist_id].
    """
    url_split: list = url.replace('&','|').replace('?', '|').split('|')
    values: list = [False, None, None]
    if len(url_split) == 1:
        undefined_id = url_split[0].split('/')[-1]
        if 'PL' in undefined_id:
            values = [True, None, undefined_id]
        else:
            values = [False, undefined_id, None]
    else:
        for element in url_split:
            if 'v=' in element:
                values[1] = element.lstrip('v=')
            elif 'list=' in element:
                values[0] = True
                values[2] = element.lstrip('list=')
    return values

def get_video_from_playlist(build: object, playlist_id: str) -> list:
    """Fonction that returns a list with the title and id of each video in the playlist corresponds to the parameter playlist_id.

    Args:
        build (object): class for API selection.
        playlist_id (str): id of the playlist looking for.

    Returns:
        list: List of tuple containing the title and id of a video. 
    """
    playlist_video_id: list = []
    next_page_token: str = None

    while True:
        # Request about the element inside the playlist
        playlistitems_list_request = build.playlistItems().list(
            playlistId=playlist_id,
            part='snippet',
            maxResults=50,
            pageToken=next_page_token 
        )
        playlistitems_list_response = playlistitems_list_request.execute()

        # Add to a list information about each video in the playlist
        for playlist_item in playlistitems_list_response['items']:
            title = playlist_item['snippet']['title']
            video_id = playlist_item['snippet']['resourceId']['videoId']
            playlist_video_id.append((title, video_id))
        
        # Check if there are more videos in the playlist, and retrieve them if so
        next_page_token = playlistitems_list_response.get('nextPageToken')
        if not next_page_token:
            break

    return playlist_video_id

def path_exist() -> str:
    """Fonction that ask a path and verify that it exist.

    Returns:
        str: Path string.
    """
    path: str = input("Directory where you want to download the songs (absolut path or from user directory) : ")
    if not ((path[0] == '/') or (path[0] == '~') or (path[1] == ':')): # Check for Unix/Windows absolute path or user shortcute path 
        path = os.path.abspath(os.path.expanduser(os.path.join('~', path)))
        print("ok")
    if not os.path.exists(path):
        print(f"Error: Could not find directory {path} | Downloading instead in '~/Downloads'")
        path = os.path.abspath(os.path.expanduser(os.path.join('~', 'Downloads')))
    return path

def format_bytes(size):
    """Converts the given size in bytes to the appropriate unit (KB, MB, GB, etc.).

    Args:
        size (int): The size to convert, in bytes.

    Returns:
        str: The converted size with unit.
    """
    power = 2**10
    n = 0
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}"

def download_progress_info(dico: dict):
    """Callback fonction to get the progress information of the current download.

    Args:
        dico (dict): Dictionary containing information about the progress of the download.
    """
    total_size: int = dico['total_bytes']
    if 'eta' in dico:
        downloaded_size: int = dico['downloaded_bytes']
        porcentage: float = (downloaded_size / total_size) * 100
        print(porcentage)
        print(f"|{porcentage:.1f}% - Time remaning : {dico['eta']}s - {format_bytes(downloaded_size)}/{format_bytes(total_size)} at {format_bytes(dico['speed'])}/s")
        print(dico['status'])
    elif dico['status'] == ('finished' or 'error'):
        print(f"finished")

def download_video_mp3(video_id: str, path: str):
    """Fonction that download the mp3 files from a ytb video.

    Args:
        video_id (str): the id of the downloaded video.
        path (str): Directory where the video files should be download.
    """
    # Set the URL of the video you want to download
    video_url = 'https://www.youtube.com/watch?v=' + video_id
    print(video_url)
    # Set the options for downloading the video

    ydl_opts = {
    'format': 'bestaudio/best',
    'embed-thumbnail': True,
    'add-metadata': True,
    'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
    'progress_hooks': [download_progress_info],
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }]
    }

    # Create a downloader object and download the video
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


if __name__ == "__main__":
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--key-api", help="API key")
    arg = parser.parse_args(sys.argv[1:])

    api_key = arg.key_api #YOUR_API_KEY
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    playlist_id = 'PLAQ9e4hp5ItvgZjsfz0IGtSw-LaW5kUK4'

    video_ids = get_video_from_playlist(youtube, playlist_id)
    print(*video_ids, sep='\n')
    download_path: str = path_exist()
    for element in video_ids:
        download_video_mp3(element[1], download_path)
    print(path_exist())