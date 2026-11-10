"""python pp/mix.py shorts/SLUG/mix.json : voice + music + sound effects -> shorts/SLUG/mix.wav.
Voice dominant and compressed, music 14-18 dB under it and ducked by it, effects never more than +3 dB over the voice,
gentle bus compression and limiter, one static gain to -9 LUFS, true peak -1 dBTP. Needs ffmpeg on PATH.
Relative paths (the argument and every path inside mix.json) are relative to the kit root.

mix.json:
{
  "length": 61.2,                                  // seconds, = (last frame + 1) / fps
  "voice": "shorts/x/voice.mp3", "voice_delay": 0.0,
  "music": "shorts/x/music.wav", "music_db": -16,  // optional
  "sfx": [["shorts/x/sfx/whoosh.wav", 0.43, -6], ...]   // file, start in seconds, gain dB
}
Prints the measured loudness and true peak: aim -9 LUFS, peak <= -1 dBTP."""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitpath

R = kitpath.KIT
path = sys.argv[1] if os.path.isabs(sys.argv[1]) else f'{R}/{sys.argv[1]}'
M = json.load(open(path))
out = os.path.join(os.path.dirname(path), 'mix.wav')


def lufs(f, af=''):
    r = subprocess.run(['ffmpeg', '-i', f, '-af', (af + ',' if af else '') + 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])


# a static gain first, so the voice reaches the compressor at a steady -12 LUFS whatever the TTS level: the mix then lands near -9
gain = -12.0 - lufs(f"{R}/{M['voice']}")
ins, chains, buses = ['-i', f"{R}/{M['voice']}"], [], []
d = int(M.get('voice_delay', 0) * 1000)
pre = f'volume={gain:.2f}dB,highpass=f=80,acompressor=threshold=0.05:ratio=4:attack=5:release=100:makeup=3'
# the compressor takes about 6 dB off: a second static gain brings the voice to -10 LUFS, the limiter keeps its peaks at -3 dBFS
gain2 = -10.0 - lufs(f"{R}/{M['voice']}", pre)
chains.append(f'[0:a]aresample=48000,{pre},volume={gain2:.2f}dB,adelay={d}|{d},alimiter=limit=0.7:level=false,asplit=2[v][vsc]')
buses.append('[v]')
k = 1
if M.get('music'):
    ins += ['-stream_loop', '-1', '-i', f"{R}/{M['music']}"]
    chains.append(f"[{k}:a]aresample=48000,volume={M.get('music_db', -16)}dB[mu]")
    chains.append('[mu][vsc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[mud]')
    buses.append('[mud]')
    k += 1
else:
    chains.append('[vsc]anullsink')
for i, (f, t, g) in enumerate(M.get('sfx', [])):
    ins += ['-i', f'{R}/{f}']
    ms = int(t * 1000)
    chains.append(f'[{k}:a]aresample=48000,volume={g}dB,alimiter=limit=0.7:level=false,adelay={ms}|{ms}[s{i}]')
    buses.append(f'[s{i}]')
    k += 1
L = M['length']
chains.append(f"{''.join(buses)}amix=inputs={len(buses)}:normalize=0:duration=longest,acompressor=threshold=0.25:ratio=2:attack=10:release=150,"
              f"aresample=192000,alimiter=limit=0.84:level=false,aresample=48000,atrim=0:{L},afade=t=out:st={L - 0.3}:d=0.3[out]")
raw = out[:-4] + '_raw.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(chains), '-map', '[out]', '-ac', '2', '-c:a', 'pcm_f32le', raw], check=True)
# one static gain to -9 LUFS and an oversampled limiter at -1 dBTP
g = -9.0 - lufs(raw)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', f'volume={g:.2f}dB,aresample=192000,alimiter=limit=0.891:level=false,aresample=48000',
                '-c:a', 'pcm_s16le', out], check=True)
os.remove(raw)
r = subprocess.run(['ffmpeg', '-i', out, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
i = re.findall(r'I:\s+(-?[\d.]+) LUFS', r)
p = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)
print('OK', out, 'integrated', i[-1] if i else '?', 'LUFS, true peak', p[-1] if p else '?', 'dBTP')
