#!/usr/bin/env python3

import utils
import consts
import os.path
from config import Config
from downloader import Downloader
from summarizer import Summarizer
from bottle import Bottle, request, abort, static_file

# we need this as a global so we can use it in the ask endpoint
summarizer = None

# and an app with a config
app = Bottle()
app.config.update({
  'config': Config(consts.CONFIG_PATH)
})

@app.route('/models')
def models():
  summarizer = Summarizer(app.config.get('config'))
  models = summarizer.list_models()['models']
  return {
    'models': list(map(lambda x: x['name'], models))
  }

@app.route('/info')
def info():
  downloader = Downloader(app.config.get('config'))
  video = request.query.video
  info = downloader.get_info(video)
  # info['formats'] = ''
  # info['requested_formats'] = ''
  # info['thumbnails'] = ''
  # return info
  return {
    'id': info['id'],
    'title': info['fulltitle'],
    'channel': info['channel'],
    'channel_url': info['channel_url'],
    'uploader': info['uploader'],
    'thumbnail': info['thumbnail'],
    'description': info['description'],
    'captions': list(info['automatic_captions'].keys()),
    'subtitles': list(info['subtitles'].keys()),
    'duration_string': info['duration_string'],
    'original_url': info['webpage_url'],
    'date': info['upload_date'],
  }

@app.route('/summarize')
def summarize():

  # get info
  video = request.query.video
  lang = request.query.lang
  model = request.query.model
  method = request.query.method
  verbosity = request.query.verbosity

  # default model
  global summarizer
  summarizer = Summarizer(app.config.get('config'))
  if model is None or model == '':
    models = summarizer.list_models()['models']
    model = models[0]['name']

  # default lang
  downloader = Downloader(app.config.get('config'))
  if lang is None or lang == '' or lang == 'default':
    langs = downloader.get_info(video)['subtitles']
    lang = None if len(langs) == 0 else list(langs.keys())[0]

  # current time
  start = utils.now()

  # first get captions
  print(f'[youtube] downloading captions for {video} in lang {lang}')
  captions = downloader.download_captions(video, lang)

  # time
  download_time = utils.now() - start
  start = utils.now()

  # now summarize
  print(f'[summarize] model {model}, method {method}, verbosity {verbosity}, lang {lang}')
  result = summarizer.summarize(captions, model, method, verbosity, lang)

  # time
  processing_time = utils.now() - start

  # done
  result['performance']['download_time'] = int(download_time)
  result['performance']['processing_time'] = int(processing_time)
  result['performance']['total_time'] = int(download_time + processing_time)
  return result

@app.route('/ask')
def ask():

  # must have embeddings
  if summarizer is None:
    abort(400, 'Must summarize first')
  
  # do it
  question = request.query.question
  start = utils.now()
  result = summarizer.ask_through_embeddings(f'Based om the transcript {question}')
  processing_time = utils.now() - start
  
  # done
  result['performance']['processing_time'] = int(processing_time)
  result['performance']['total_time'] = int(processing_time)
  return result

@app.route('/<filepath:path>')
def server_static(filepath):
  return static_file(filepath, root='./public')  

@app.route('/')
def server_index():
  return static_file('index.html', root='./public')

# run server
app.run(host='0.0.0.0', port=5555, debug=True)
