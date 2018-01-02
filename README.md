# DeepSpeechHTTP
Simple Python HTTP-Server performing STT via HTTP-POST with DeepSpeech as backend.

Setup
  - Install DeepSpeech via pip
  - Execute dshttp.py with the required parameters, eg.
      ```
      dshttp.py models/output_graph.pb models/alphabet.txt 8080 models/lm.binary models/trie
      ```

Usage
  - Encode the source WAV-formatted audio file (16kHz sampling rate) with base32
  - Post the encoded file to the server, eg. with curl -X POST -d @base_encoded_file.b32 server:8080
  - Server will return the result of STT as response
