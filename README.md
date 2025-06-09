# IMDS Subtitle Translator

This repository contains a simple Python script to capture audio from the microphone,
transcribe the speech with [Whisper](https://github.com/openai/whisper), translate
from Portuguese to Spanish using [Argos Translate](https://www.argosopentech.com/),
and write the translated lines to `legenda.txt` so they can be used in OBS as
live subtitles.

## Requirements

- Python 3.8+
- `sounddevice`
- `whisper`
- `argostranslate`
- A Portuguese &rarr; Spanish Argos Translate package (`pt_es.argosmodel`)

Install the dependencies with:

```bash
pip install sounddevice whisper argostranslate
```

Download the `pt_es.argosmodel` file from the [Argos Translate releases](https://github.com/argosopentech/argos-translate/releases)
and note its path. The script will install it on first run.

## Usage

Run the script from a terminal. Provide the path to the `.argosmodel` file
and optionally choose which Whisper model to load:

```bash
python live_translate.py --argos path/to/pt_es.argosmodel --model base
```

A file named `legenda.txt` will be updated in real time with translated
Spanish text. Add this file as a text source in OBS to display subtitles.
Press `Ctrl+C` to stop the script.

