"""python pp/words.py VOICE.wav WORDS.json [model] [language] : word timings of a voice-over with faster-whisper.
Writes [{"w": word, "s": start_s, "e": end_s}, ...], the format short.py reads for the captions.
model: default small (try medium or large-v3 for accuracy), language: default en. GPU if CUDA works, else CPU.
Needs: pip install faster-whisper. Read the result and fix misheard words by hand (keep the timings)."""
import json
import sys

from faster_whisper import WhisperModel

src, dst = sys.argv[1], sys.argv[2]
name = sys.argv[3] if len(sys.argv) > 3 else 'small'
lang = sys.argv[4] if len(sys.argv) > 4 else 'en'


def run(device, compute):
    model = WhisperModel(name, device=device, compute_type=compute)
    segs, _ = model.transcribe(src, language=lang, word_timestamps=True, vad_filter=False)
    return [{'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)} for seg in segs for w in seg.words]


try:
    words = run('cuda', 'float16')
except Exception as e:      # missing CUDA libraries only fail at transcription time
    print('GPU unavailable, using the CPU:', str(e)[:120])
    words = run('cpu', 'int8')
with open(dst, 'w', encoding='utf-8') as f:
    json.dump(words, f, indent=1, ensure_ascii=False)
print(f"{len(words)} words, {words[-1]['e'] if words else 0:.2f} s -> {dst}")
