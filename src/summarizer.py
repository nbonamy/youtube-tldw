#!/usr/bin/env python3

import os
import utils
import consts
import asyncio
import requests
from langchain.llms import Ollama
from langchain.schema.document import Document
from langchain.callbacks.base import BaseCallbackHandler, AsyncCallbackHandler
#from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import HumanMessage, SystemMessage
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.chat_models import ChatOllama
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma

def token_generator(callback_handler):
  for token in callback_handler.tokens:
    print(token)
    yield token

class Summarizer:

  def __init__(self, config):
    self.config = config
    self.ollama = None
    self.vectorstore = None

  def list_models(self) -> dict:
    url = f'{self.config.ollama_url()}/api/tags'
    return requests.get(url).json()

  def summarize(self, captions, model, method, verbosity, lang) -> dict:
    if method == 'embeddings':
      return self._summarize_through_embeddings(model, captions, verbosity, lang)
    elif method == 'prompt':
      return self._summarize_through_prompt(model, captions, verbosity, lang)
    else:
      raise Exception('Unknown method')

  def ask_through_embeddings(self, question) -> dict:

    # check
    if self.vectorstore is None:
      raise Exception('Must summarize first')
    
    # now query
    print('[summarize] retrieving')
    qachain = RetrievalQA.from_chain_type(self.ollama, retriever=self.vectorstore.as_retriever(search_kwargs={"k": 1}))
    qachain({"query": question})
    
    # done
    return self.stream_handler.output()

  def _summarize_through_embeddings(self, ollama_model, document, verbosity, lang)-> dict:

    # ollama
    self.stream_handler = StreamHandler(callback)
    self.ollama = Ollama(base_url=self.config.ollama_url(), model=ollama_model, callbacks=[self.stream_handler])

    # split
    print('[summarize] splitting text')
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    all_splits = [Document(page_content=x) for x in text_splitter.split_text(document)]

    # create embeddings
    print('[summarize] creating embeddings')
    oembed = OllamaEmbeddings(base_url=self.config.ollama_url(), model=ollama_model)
    self.vectorstore = Chroma.from_documents(documents=all_splits, embedding=oembed)

    # now query
    return self.ask_through_embeddings(self._system_prompt(lang, verbosity))

  def _summarize_through_prompt(self, model, document, verbosity, lang)-> dict:

    # messages
    system_message = SystemMessage(content=self._system_prompt(lang, verbosity))
    human_message = HumanMessage(content=document)
    messages = [system_message, human_message]
    
    # now run it
    print('[summarize] prompting')
    stream_handler = StreamHandler()
    chat_model = ChatOllama(base_url=self.config.ollama_url(), model=model, callbacks=[stream_handler])
    chat_model.apredict_messages(messages)

    # done
    print('[summarize] done')
    return token_generator(stream_handler)

  def _system_prompt(self, lang, verbosity) -> str:

    # french
    if lang.startswith('fr'):
      if verbosity == consts.VERBOSITY_CONCISE:
        return 'Générer un résumé concis (1 paragraphe, 250 mots maximum) en français de la transcription fournie ci-dessous. Utilisez le présent.'
      elif verbosity == consts.VERBOSITY_DETAILED:
        return 'Genérer un résumé détaillé en français de la transcription fournie ci-dessous. Fournir les points clés et les informations détaillées. Utilisez le présent.'
      else:
        raise Exception('Unknown verbosity')

    # default english
    if verbosity == consts.VERBOSITY_CONCISE:
      return 'Generate a concise summary (1 paragraph, 250 words max) of the transcript provided below. Use present tense.'
    elif verbosity == consts.VERBOSITY_DETAILED:
      return 'Generate a detailed summary of the transcript provided below. Provide key highlights and detailed insights. Use present tense.'
    else:
      raise Exception('Unknown verbosity')

class StreamHandler(BaseCallbackHandler):
  
  def __init__(self):
    self.reset()

  def reset(self):
    self.created = utils.now()
    self.text = None
    self.start = None
    self.end = None
    self.tokens = []

  def on_chat_model_start(self, serialized: dict, prompts: dict, **kwargs) -> None:
    print('[summarize] chat starting')
    self.reset()
      
  def on_llm_start(self, serialized: dict, prompts: dict, **kwargs) -> None:
    print('[summarize] llm starting')
    self.reset()
  
  def on_llm_new_token(self, token: str, **kwargs) -> None:
    print(token)
    self.tokens.append(token)
    if self.text is None:
      self.text = token
      self.start = utils.now()
      self.end = utils.now()
    else:
      self.text += token
      self.end = utils.now()
    
  def time_1st_token(self) -> float:
    return self.start - self.created

  def tokens_per_sec(self)  -> float:
    return self.tokens.length / (self.end - self.start) * 1000

  def output(self) -> dict:
    return {
      'text': self.text.strip(),
      'performance': {
        'tokens': self.tokens.length,
        'time_1st_token': int(self.time_1st_token()),
        'tokens_per_sec': round(self.tokens_per_sec(), 2)
      }
    }
