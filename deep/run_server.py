'''
Created on Jul 15, 2017

@author: gcampagn
'''

import os
import sys
import numpy as np
import tensorflow as tf
import tornado.ioloop
from concurrent.futures import ThreadPoolExecutor

from util.seq2seq import Seq2SeqEvaluator
from util.loader import unknown_tokens, load_data
from model import load, create_model

from server.application import Application, LanguageContext

def load_language(app, tag, input_words, embedding_matrix, config, model_type, model_dir):
    graph = tf.Graph()
    session = tf.Session(graph)
    
    with graph.as_default():
        with session.as_default():
            model = create_model(config, model_type, embedding_matrix)
            model.build()
            loader = tf.train.Saver()
            loader.restore(session, os.path.join(model_dir, 'best'))
    app.add_language(tag, LanguageContext(tag, session, config, input_words, model))
    print('Loaded language ' + tag)

def run():
    if len(sys.argv) < 4:
        print("** Usage: python3 " + sys.argv[0] + " <<Model: bagofwords/seq2seq>> <<Input Vocab>> <<Word Embeddings>>")
        sys.exit(1)
    
    np.random.seed(42)
    config, words, reverse, embedding_matrix = load(benchmark='tt', input_words=sys.argv[2], embedding_file=sys.argv[3])
    consumed = config.apply_cmdline(sys.argv[4:]) 
    
    thread_pool = ThreadPoolExecutor(thread_name_prefix='query-thread-')
    app = Application(thread_pool)
    
    for language, model_directory in map(lambda x : x.split(':'), sys.argv[4+consumed:]):
        load_language(app, language, words, embedding_matrix, config, model_type=sys.argv[1], model_dir=model_directory)

    app.listen(8400)
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    run()