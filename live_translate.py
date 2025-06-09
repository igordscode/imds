import argparse
import queue
import sys
import threading
from pathlib import Path

import numpy as np
import sounddevice as sd
import whisper
from argostranslate import package, translate

SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_DURATION = 5  # seconds of audio per transcription


def install_argos_package(pkg_path: Path):
    """Install Argos Translate package if not already installed."""
    installed = [p.path for p in package.get_installed_packages()]
    if str(pkg_path) not in installed:
        package.install_from_path(str(pkg_path))


def setup_translator():
    installed_languages = translate.get_installed_languages()
    pt_lang = next((lang for lang in installed_languages if lang.code == "pt"), None)
    es_lang = next((lang for lang in installed_languages if lang.code == "es"), None)
    if not pt_lang or not es_lang:
        raise RuntimeError("Portuguese or Spanish language package not installed")
    return pt_lang.get_translation(es_lang)


def main(model_size: str, argos_pkg: str):
    install_argos_package(Path(argos_pkg))
    translator = setup_translator()
    model = whisper.load_model(model_size)

    audio_queue: queue.Queue[np.ndarray] = queue.Queue()
    stop_event = threading.Event()

    def audio_callback(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        audio_queue.put(indata.copy())

    def capture_audio():
        with sd.InputStream(channels=CHANNELS, samplerate=SAMPLE_RATE, callback=audio_callback):
            stop_event.wait()

    capture_thread = threading.Thread(target=capture_audio)
    capture_thread.start()

    buffer = np.empty((0, CHANNELS), dtype=np.float32)
    try:
        while True:
            chunk = audio_queue.get()
            buffer = np.concatenate((buffer, chunk))
            if len(buffer) / SAMPLE_RATE >= BLOCK_DURATION:
                audio_data = buffer.copy()
                buffer = np.empty((0, CHANNELS), dtype=np.float32)

                audio_data = audio_data.flatten()
                result = model.transcribe(audio_data, language="pt", fp16=False)
                text = result.get("text", "").strip()
                if text:
                    translated = translator.translate(text)
                    with open("legenda.txt", "a", encoding="utf-8") as f:
                        f.write(translated + "\n")
                    print(f"PT: {text}\nES: {translated}\n")
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        capture_thread.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live Portuguese to Spanish subtitles")
    parser.add_argument("--model", default="base", help="Whisper model size to use (tiny, base, small, medium, large)")
    parser.add_argument("--argos", required=True, help="Path to Argos Translate pt_es.argosmodel file")
    args = parser.parse_args()
    main(args.model, args.argos)
