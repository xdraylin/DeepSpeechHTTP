# DeepSpeechHTTP
Simple Python HTTP-Server performing STT via HTTP-POST with DeepSpeech as backend.

Setup
  - Install DeepSpeech via pip
  - Execute dshttp.py with the required parameters

Usage
  - Encode the source WAV-formatted audio file (16kHz sampling rate) with base32
  - Post the encoded file to the server, eg. with curl -X POST -d @base_encoded_file.b32 server:8080
