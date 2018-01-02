#!/usr/bin/env python2
from __future__ import absolute_import, division, print_function

# Imports for HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import base64

# Imports for DeepSpeech
from timeit import default_timer as timer

import argparse
import sys
import scipy.io.wavfile as wav

from deepspeech.model import Model

# DeepSpeech constants
# These constants control the beam search decoder

# Beam width used in the CTC decoder when building candidate transcriptions
BEAM_WIDTH = 500

# The alpha hyperparameter of the CTC decoder. Language Model weight
LM_WEIGHT = 1.75
# The beta hyperparameter of the CTC decoder. Word insertion weight (penalty)
WORD_COUNT_WEIGHT = 1.00

# Valid word insertion weight. This is used to lessen the word insertion penalty
# when the inserted word is part of the vocabulary
VALID_WORD_COUNT_WEIGHT = 1.00


# These constants are tied to the shape of the graph used (changing them changes
# the geometry of the first layer), so make sure you use the same constants that
# were used during training

# Number of MFCC features to use
N_FEATURES = 26

# Size of the context window used for producing timesteps in the input vector
N_CONTEXT = 9

deepspeech = None

class DeepSpeech:
    def __init__(self, model, alphabet, lm=None, trie=None):
        print('Loading model from file %s' % (model), file=sys.stderr)
        model_load_start = timer()
        self.ds = Model(model, N_FEATURES, N_CONTEXT, alphabet, BEAM_WIDTH)
        model_load_end = timer() - model_load_start
        print('Loaded model in %0.3fs.' % (model_load_end), file=sys.stderr)

        if lm is not None and trie is not None:
            print('Loading language model from files %s %s' % (lm, trie), file=sys.stderr)
            lm_load_start = timer()
            self.ds.enableDecoderWithLM(alphabet, lm, trie, LM_WEIGHT, WORD_COUNT_WEIGHT, VALID_WORD_COUNT_WEIGHT)
            lm_load_end = timer() - lm_load_start
            print('Loaded language model in %0.3fs.' % (lm_load_end), file=sys.stderr)
            
    def stt(self, audio_file):
        fs, audio = wav.read(audio_file)
        audio_length = len(audio) * ( 1 / 16000)
        print('Running inference.', file=sys.stderr)
        inference_start = timer()
        stt_result = self.ds.stt(audio, fs)
        print('Return result: ', stt_result)
        inference_end = timer() - inference_start
        print('Inference took %0.3fs for %0.3fs audio file.' % (inference_end, audio_length), file=sys.stderr)
        return stt_result
        
# Handler class for the HTTP-Server
class ServerRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        print("GET request received")
        self._set_response()
        self.wfile.write("This server doesn't support GET requests.")

    def do_POST(self):
        # Get content length
        content_length = int(self.headers['Content-Length'])
        
        # Get the data
        post_data = self.rfile.read(content_length)
        
        # Save the data into a temporary file (ugly workaround for wavfile.read)
        tmp_audiofile = open('/tmp/deepspeechwav.tmp', 'w')
        tmp_audiofile.write(base64.b32decode(post_data))
        tmp_audiofile.close()
        
        print("POST request received")

        self._set_response()
        self.wfile.write(deepspeech.stt('/tmp/deepspeechwav.tmp'))


def main():
    parser = argparse.ArgumentParser(description='HTTP-Server receiving base32 encoded WAV-Audio for STT with DeepSpeech')
    parser.add_argument('model', type=str, help='Path to the model (protocol buffer binary file)')
    parser.add_argument('alphabet', type=str, help='Path to the configuration file specifying the alphabet used by the network')
    parser.add_argument('port', type=int, nargs='?', help='Port the server will listen to (defaults to 8080)')
    parser.add_argument('lm', type=str, nargs='?', help='Path to the language model binary file')
    parser.add_argument('trie', type=str, nargs='?', help='Path to the language model trie file created with native_client/generate_trie')
    args = parser.parse_args()

    global deepspeech

    if args.lm and args.trie:
        deepspeech = DeepSpeech(args.model, args.alphabet, args.lm, args.trie)
    else:
        deepspeech = DeepSpeech(args.model, args.alphabet)

    if args.port:
        http_server_port = args.port
    else:
        http_server_port = 8080
    
    run_http_server(port=http_server_port)
        
def run_http_server(server_class=HTTPServer, handler_class=ServerRequestHandler, port=8080):
    #logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Stopping httpd...\n')

main()
