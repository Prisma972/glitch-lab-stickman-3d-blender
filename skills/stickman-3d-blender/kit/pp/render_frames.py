"""blender -b x.blend -P render_frames.py -- OUTDIR start end [step] [samples] [percent]
or     blender -b x.blend -P render_frames.py -- OUTDIR 8,19,52 [samples] [percent]
Skips frames already on disk, so a stopped render resumes."""
import bpy, sys, os, json
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]
out = a[0]
if ',' in a[1]:
    fr = [int(x) for x in a[1].split(',') if x]
    rest = a[2:]
else:
    fr = list(range(int(a[1]), int(a[2]) + 1, int(a[3]) if len(a) > 3 else 1))
    rest = a[4:]
sc = bpy.context.scene
sc.eevee.taa_render_samples = int(rest[0]) if rest else 32
sc.render.resolution_percentage = int(rest[1]) if len(rest) > 1 else 100
os.makedirs(out, exist_ok=True)
vl = sc.view_layers[0]
vl.use_pass_z = True
vl.use_pass_normal = True
vl.use_pass_vector = True
sc.render.use_motion_blur = False
im = sc.render.image_settings
im.media_type = 'MULTI_LAYER_IMAGE'
im.file_format = 'OPEN_EXR_MULTILAYER'
im.color_depth = '32'
im.exr_codec = 'ZIP'
HULL0 = {o.name: o.modifiers['PP_ink'].thickness for o in sc.objects if 'PP_ink' in o.modifiers}
for i, f in enumerate(fr):
    p = f'{out}/f{f:04d}.exr'
    if os.path.exists(p):
        continue
    sc.frame_set(f)
    # character hulls keep their width on screen, whatever the distance
    cam = sc.camera
    cp = cam.matrix_world.translation
    k = cam.data.sensor_height / (cam.data.lens * 1920)
    for o in sc.objects:
        md = o.modifiers.get('PP_ink')
        if md is None:
            continue
        px = o.get('ink_px')
        pts = [o.matrix_world @ Vector(b) for b in o.bound_box]
        d = max(0.5, (sum(pts, Vector()) / 8 - cp).length)
        sx = o.matrix_world.to_scale()[0]
        if px:
            md.thickness = px * d * k / sx
        elif not o.name.startswith(('RM_top', 'RM_apron', 'ST_endr')):
            # set lines stay finer than character lines on long lenses: capped, never widened.
            # Geometric mean of the nearest corner and the centre, so a long facade is not judged by its far end
            d = max(0.5, (d * min((q - cp).length for q in pts)) ** 0.5)
            md.thickness = min(HULL0[o.name], (5.0 if o.name.startswith('T_bx') else 3.4) * d * k / sx)
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
    cd = sc.camera.data
    json.dump(dict(focus=cd.dof.focus_distance, fstop=cd.dof.aperture_fstop if cd.dof.use_dof else None, lens=cd.lens), open(p[:-4] + '.json', 'w'))
    print(f'FRAME {f} {i + 1}/{len(fr)}', flush=True)
