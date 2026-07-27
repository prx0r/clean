#!/usr/bin/env python3
"""
Spanda Renderer — custom video output for our visual language.
Takes a scene spec + audio → finished MP4.
No FableCut dependency.
"""

import json, subprocess, math, tempfile, os, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30

# ── Animation generators ──
# Each returns a list of (PIL Image) frames

def pulse_field(duration):
    """Pulsing organic field — 3 nested contours + crimson bindu."""
    nf = int(duration * FPS)
    frames = []
    for i in range(nf):
        t = i / FPS
        phase = t * 2 * math.pi / 6.4
        
        img = Image.new('RGB', (W, H), 'white')
        draw = ImageDraw.Draw(img)
        
        for j, (scale_offset, base_opacity, pw) in enumerate([
            (0, 0.22, 2.5), (0.55, 0.38, 3), (1.1, 0.72, 4)
        ]):
            s = 0.99 + 0.03 * math.sin(phase + scale_offset)
            op = base_opacity + 0.06 * math.sin(phase + scale_offset)
            r = (180 + j * 60) * s
            grey = int(255 * (1 - min(op, 1)))
            draw.ellipse([W//2-r, H//2-r, W//2+r, H//2+r],
                        outline=(grey, grey, grey), width=pw)
        
        # Centre bindu
        cs = 0.75 + 0.5 * (0.5 + 0.5 * math.sin(phase))
        co = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(phase - 0.5))
        cr = 8 * cs
        alpha = int(255 * min(co, 1))
        draw.ellipse([W//2-cr, H//2-cr, W//2+cr, H//2+cr], fill=(139, 30, 30))
        
        frames.append(img)
    return frames

def wheel_hub(duration):
    """Central hub with rotating wheel and spokes."""
    nf = int(duration * FPS)
    frames = []
    cx, cy = W//2, H//2
    for i in range(nf):
        t = i / FPS
        angle = t * 2 * math.pi / 22  # 22s per rotation
        
        img = Image.new('RGB', (W, H), 'white')
        draw = ImageDraw.Draw(img)
        
        # Outer ring
        draw.ellipse([cx-330, cy-330, cx+330, cy+330], outline='#111', width=4)
        
        # Spokes that rotate
        for s in range(3):
            a = angle + s * 2 * math.pi / 3
            x1 = cx + 30 * math.cos(a)
            y1 = cy + 30 * math.sin(a)
            x2 = cx + 320 * math.cos(a)
            y2 = cy + 320 * math.sin(a)
            draw.line([x1, y1, x2, y2], fill='#777' if s else '#111', width=3)
        
        # Hub
        draw.ellipse([cx-22, cy-22, cx+22, cy+22], fill='#111')
        draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill='#8b1e1e')
        
        frames.append(img)
    return frames

def aperture_breath(duration):
    """Circle aperture opening and closing like a breath."""
    nf = int(duration * FPS)
    frames = []
    for i in range(nf):
        t = i / FPS
        phase = (t % 5) / 5  # 5s cycle
        scale = 0.72 + 0.33 * (0.5 - 0.5 * math.cos(phase * 2 * math.pi))
        
        img = Image.new('RGB', (W, H), 'white')
        draw = ImageDraw.Draw(img)
        
        r = 205 * scale
        draw.ellipse([W//2-r, H//2-r, W//2+r, H//2+r], outline='#111', width=4)
        
        # Gate opening
        gate = 0.2 + 0.8 * (0.5 + 0.5 * math.sin(phase * 2 * math.pi))
        gate_w = 205 * gate
        draw.arc([W//2-205, H//2-205, W//2+205, H//2+205], -90 + gate * 90, 90 - gate * 90, fill='#8b1e1e', width=4)
        draw.arc([W//2-205, H//2-205, W//2+205, H//2+205], 180 - gate * 90, 180 + gate * 90, fill='#8b1e1e', width=4)
        
        frames.append(img)
    return frames

def render_scene(scene_type, duration):
    """Dispatch to the right animation generator."""
    generators = {
        "pulse-field": pulse_field,
        "wheel-hub": wheel_hub,
        "aperture-breath": aperture_breath,
    }
    gen = generators.get(scene_type)
    if gen:
        return gen(duration)
    else:
        # Fallback: blank with white
        nf = int(duration * FPS)
        return [Image.new('RGB', (W, H), 'white') for _ in range(nf)]

def render_video(project_spec, output_path):
    """Full render pipeline: generate frames → encode → mix audio."""
    tmp = Path(tempfile.mkdtemp())
    
    # Render each scene
    video_segments = []
    for scene in project_spec["scenes"]:
        print(f"  Rendering {scene['type']} ({scene['duration']:.1f}s)...", flush=True)
        frames = render_scene(scene["type"], scene["duration"])
        
        # Write to rawvideo pipe
        seg_path = tmp / f"seg_{scene['start']:.0f}.mp4"
        nf = len(frames)
        h = int(nf * 0.6)
        
        # Convert frames to bytes
        raw = b''.join(f.tobytes() for f in frames)
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'rawvideo', '-vcodec', 'rawvideo',
            '-s', f'{W}x{H}', '-pix_fmt', 'rgb24', '-r', str(FPS),
            '-i', '-',
            '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
            str(seg_path)
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.stdin.write(raw)
        proc.stdin.close()
        proc.wait()
        video_segments.append(seg_path)
    
    # Concatenate video segments
    concat_file = tmp / "concat.txt"
    with open(concat_file, "w") as f:
        for seg in video_segments:
            f.write(f"file '{seg}'\n")
    
    raw_video = tmp / "raw_video.mp4"
    subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                    '-i', str(concat_file),
                    '-c', 'copy', str(raw_video)], capture_output=True, timeout=300)
    
    # Mix audio
    audio_inputs = []
    filter_parts = []
    for i, scene in enumerate(project_spec["scenes"]):
        if "audio" in scene:
            audio_inputs.extend(['-i', scene["audio"]])
            filter_parts.append(f'[{i+1}:a]adelay={int(scene["start"]*1000)}|{int(scene["start"]*1000)}[a{i}]')
    
    if audio_inputs:
        # Add audio
        adelay_parts = "".join(f"[a{i}]" for i in range(len(project_spec["scenes"])) if "audio" in project_spec["scenes"][i])
        amix_cmd = [
            'ffmpeg', '-y', '-i', str(raw_video), *audio_inputs,
            '-filter_complex', ';'.join(filter_parts) + f";{adelay_parts}amix=inputs={len([s for s in project_spec['scenes'] if 'audio' in s])}:duration=first[aout]",
            '-map', '0:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac',
            str(output_path)
        ]
        subprocess.run(amix_cmd, capture_output=True, timeout=300)
    else:
        shutil.copy2(raw_video, output_path)
    
    # Cleanup
    shutil.rmtree(tmp)
    print(f"\nRendered: {output_path}")
    size = os.path.getsize(output_path)
    print(f"Size: {size/1024/1024:.1f} MB")

if __name__ == "__main__":
    # Test with a simple spec
    project = {
        "scenes": [
            {"start": 0, "duration": 8, "type": "pulse-field",
             "audio": "/root/projects/FableCut/media/seg-01-hook.mp3"},
        ]
    }
    render_video(project, "/root/projects/FableCut/exports/spanda-test.mp4")
