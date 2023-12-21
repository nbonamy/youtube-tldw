#!/usr/bin/env python3

import os
import consts
import litellm
import requests
from langchain.llms import Ollama
from langchain.schema.document import Document
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import HumanMessage, SystemMessage
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.chat_models import ChatOllama
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma

class Summarizer:

  def __init__(self, config):
    self.config = config

  def list_models(self):
    url = f'{self.config.ollama_url()}/api/tags'
    return requests.get(url).json()

  def summarize(self, captions, model, method, verbosity):

    if method == 'embeddings':
      return self._summarize_through_embeddings(model, captions, verbosity)
    elif method == 'prompt':
      return self._summarize_through_prompt(model, captions, verbosity)
    else:
      raise Exception('Unknown method')


  def _summarize_through_embeddings(self, ollama_model, document, verbosity):

    # ollama
    ollama = Ollama(base_url=self.config.ollama_url(), model=ollama_model)

    # split
    print('splitting')
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    all_splits = [Document(page_content=x) for x in text_splitter.split_text(document)]

    # create embeddings
    print('creating embeddings')
    oembed = OllamaEmbeddings(base_url=self.config.ollama_url(), model=ollama_model)
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=oembed)

    # now query
    print('retrieving')
    question = 'Summarize the text highlighting main topics'
    qachain = RetrievalQA.from_chain_type(ollama, retriever=vectorstore.as_retriever(search_kwargs={"k": 1}))
    return qachain({"query": question})['result']

  def _summarize_through_prompt(self, model, document, verbosity):
    return self._summarize_through_prompt2(model, document, verbosity)
  
  def _summarize_through_prompt1(self, model, document, verbosity):
    print('prompting')
    litellm.set_verbose=True
    response = litellm.completion(
      api_base=self.config.ollama_url(),
      model=f'ollama/{model}',
      stream=True,
      messages=[
        { "role": "system", "content": "you specialize in summarizing youtube videos captions. you do so by extracting key topics from captions. you provide a summary and can create youtube links specifying the timestamp matching the topic when relevant.", },
        #{ "role": "user", "content": document, },
        { "role": "user", "content": "summarize previous text", }
      ],
    )
    for chunk in response:
      print(chunk['choices'][0]['delta'])

  def _summarize_through_prompt2(self, ollama_model, document, verbosity):

    # system prompt
    system_prompt = f'Generate a detailed summary of the transcript provided below. Provide key highlights and detailed insights. Use present tense.'
    if verbosity == consts.VERBOSITY_CONCISE:
      system_prompt = f'Generate a concise summary of the transcript provided below. Use present tense.'

    # prompting
    print('prompting')
    stream_handler = StreamHandler()
    chat_model = ChatOllama(model=ollama_model, callbacks=[stream_handler], verbose=True)
    human_message = HumanMessage(content=document)
    system_message = SystemMessage(content=system_prompt)
    messages = [system_message, human_message]
    chat_model(messages)

    # done
    return stream_handler.text.strip()

class StreamHandler(BaseCallbackHandler):
  def __init__(self):
    self.text = ''

  def on_llm_new_token(self, token: str, **kwargs) -> None:
    self.text += token
