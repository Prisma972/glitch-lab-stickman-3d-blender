"""python pp/preview.py BLEND NAME START END [samples] [percent] [tag] : renders a frame range with the real finish
(motion blur included) and encodes out/NAME/NAME.mp4, no sound. For checking motion before a full render: keep it small.
BLEND is relative to the kit root (or absolute). tag = the grade of post.SCENES (default st)."""
import os
import subprocess
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitpath

R = kitpath.KIT
blend, name, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
samples = sys.argv[5] if len(sys.argv) > 5 else '6'
pct = sys.argv[6] if len(sys.argv) > 6 else '50'
tag = sys.argv[7] if len(sys.argv) > 7 else 'st'
blend = blend if os.path.isabs(blend) else f'{R}/{blend}'
O = f'{kitpath.OUT}/{name}'
subprocess.run([sys.executable, f'{R}/pp/gpulock.py', kitpath.BLENDER, '-b', blend, '-P', f'{R}/pp/render_frames.py', '--',
                f'{O}/{tag}', str(a), str(b), '1', samples, pct], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
subprocess.run([sys.executable, f'{R}/pp/test_frames.py', O, tag], stdout=subprocess.DEVNULL, check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-start_number', str(a), '-i', f'{O}/{tag}/f%04d_f.jpg', '-frames:v', str(b - a + 1),
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', f'{O}/{name}.mp4'], check=True)
print('OK', f'{O}/{name}.mp4')
