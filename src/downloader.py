#!/usr/bin/env python3

import os
import re
import tempfile
from yt_dlp import YoutubeDL

class Downloader:

  def __init__(self, config):
    self.config = config

  def get_info(self, url):
    ydl_opts = {
      'verbose': False,
      #'listsubtitles': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
      return ydl.extract_info(url, download=False)

  def download_captions(self, url, lang=None):
    captions_filename = self._download_captions(url, lang)
    captions = self._load_and_cleanup_captions(captions_filename)
    os.remove(captions_filename)
    return captions

  def _download_captions(self, url, lang=None):

    # get temp directory with system call
    tmp_dir = tempfile.gettempdir()

    # default lang
    if lang is None or lang == '':
      lang = 'en'

    # basic options
    ydl_opts = {
      'verbose': False,
      'skip_download': True,
      'writesubtitles': True,
      'writeautomaticsub': True,
      'subtitleslangs': [lang],
      'outtmpl': f'{tmp_dir}/%(id)s.%(ext)s',
    }

    # extract video id
    video_id = url if '=' not in url else url.split('=')[1]

    # download captions
    with YoutubeDL(ydl_opts) as ydl:
      ydl.download(url)
      return f'{tmp_dir}/{video_id}.{lang}.vtt'

  def _load_and_cleanup_captions(self, filename):

    # read to memory
    with open(filename, 'r') as f:
      contents = f.read()

    # remove timestamp lines
    contents = re.sub(r'\d\d:\d\d:\d\d\.\d\d\d --> .*\n', '', contents)
    
    # now remove timestamps like <00:20:03.039><c>
    contents = re.sub(r'<\d\d:\d\d:\d\d\.\d\d\d><c>', '', contents)
    contents = re.sub(r'</c>', '', contents)
    contents = re.sub(r'\n+', '\n', contents)

    # now combine lines
    captions = ''
    previous_line = ''
    for line in contents.split('\n'):
      line = line.strip()
      if line != '' and previous_line != line:
        captions += line + ' '
        previous_line = line
    
    # done
    return captions

