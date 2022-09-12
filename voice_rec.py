#!/usr/bin/env python
from os import environ, path
from pocketsphinx.pocketsphinx import *
import pyaudio
import threading
import time
from queue import Queue


keywordList = ['robot', 'okay']
robot = ['robot', 'robots', 'rabbit', 'romans', "romo"]
left = ['left', 'length', 'lady', 'lifts', 'life', ' live', 'let', 'late', 'legs']
right = ['right', 'rights', 'rats', 'rest', 'read']
drop = ['drop', 'drown', 'draw', 'job', 'dot', "drama", "from", "but"]
go = ['go', 'hello']
stop = ['stop', 'stopped', 'not']


def speech_recognizer(qu):
    # Create a decoder with certain model
    MODELDIR = "pocketsphinx/model"
    DATADIR = "pocketsphinx/test/data"
    config = Decoder.default_config()
    config.set_string('-hmm', path.join(MODELDIR, 'en-us/en-us'))
    config.set_string('-lm', path.join(MODELDIR, 'en-us/en-us.lm.bin'))
    config.set_string('-dict', path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))
    # Decode streaming data.
    decoder = Decoder(config)
    decoder.start_utt()
    mic = pyaudio.PyAudio()
    in_speech_bf = False

    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024,
                      input_device_index=0)
    stream.start_stream()

    while True:
        buf = stream.read(1024, exception_on_overflow=False)
        if buf:
            decoder.process_raw(buf, False, False)
            if decoder.get_in_speech() != in_speech_bf:
                in_speech_bf = decoder.get_in_speech()
                if not in_speech_bf:
                    decoder.end_utt()
                    hypothesis = [seg.word for seg in decoder.seg()]
                    if hypothesis == ['<s>', '[SPEECH]', '</s>'] or hypothesis == ['<s>', '</s>']:
                        decoder.start_utt()
                        continue
                    else:
                        print('Hypothesis result:', decoder.hyp().hypstr)
                        phrase = decoder.hyp().hypstr
                        phrase = phrase.split()
                        qu.put(phrase)
                    decoder.start_utt()
        else:
            break
    decoder.end_utt()

'''
q = Queue()
t1 = threading.Thread(target=speech_recognizer, args=(q,))
t1.start()

while True:
    value = q.get()
    for word in value:
        print('value:', word)
'''

