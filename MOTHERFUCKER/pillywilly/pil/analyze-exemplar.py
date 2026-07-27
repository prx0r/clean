#!/usr/bin/env python3

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import warnings
warnings.filterwarnings('ignore', message='Image.Image.getdata is deprecated')

from PIL import Image

ROOT = Path('/root/projects/blog')
EXEMPLARS_DIR = ROOT / 'exemplars' / 'gold-standards'
FABLECUT_DIR = Path('/root/projects/FableCut')
ANALYZE_JS = FABLECUT_DIR / 'analyze.js'

VISION_API_KEY = os.environ.get("VISION_API_KEY", "AIzaSyA7-ZK5BGBxDwGCGx1Wiro0fB7NfX68KIc")
VISION_URL = f'https://vision.googleapis.com/v1/images:annotate?key={VISION_API_KEY}'

CF_TOKEN = os.environ.get("CF_API_TOKEN", "")
CF_ACCOUNT = "954612afb5a97bb15dddcdc70176813d"
CF_WHISPER_URL = f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/@cf/openai/whisper-large-v3-turbo'


def log(msg):
    print(f'  {msg}', flush=True)


def run(cmd, timeout=300):
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr[:500]}")
    return result.stdout


def get_video_info(video_path):
    info = json.loads(run([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format',
        '-of', 'json', str(video_path)
    ]))
    v = next((s for s in info.get('streams', []) if s['codec_type'] == 'video'), {})
    a = next((s for s in info.get('streams', []) if s['codec_type'] == 'audio'), {})
    dur = float(info.get('format', {}).get('duration', v.get('duration', 0)))
    fps = 0
    if v.get('avg_frame_rate') and v['avg_frame_rate'] != '0/0':
        n, d = v['avg_frame_rate'].split('/')
        if int(d) > 0:
            fps = int(n) / int(d)
    return {
        'duration': round(dur, 3),
        'fps': round(fps, 2),
        'width': v.get('width', 0),
        'height': v.get('height', 0),
        'has_audio': a.get('codec_type') == 'audio',
    }


def detect_shots_fablecut(video_path, threshold=None):
    log('Running FableCut shot analysis...')
    abs_path = str(Path(video_path).resolve())
    cmd = ['node', str(ANALYZE_JS), abs_path, '--no-music']
    if threshold is not None:
        cmd.append(f'--threshold={threshold}')
    analysis = json.loads(run(cmd))
    log(f'  Detected {len(analysis["shots"])} shots, {len(analysis["cuts"])} cuts')
    return analysis


def extract_keyframe(video_path, time_sec, output_path):
    cmd = [
        'ffmpeg', '-y', '-ss', str(time_sec), '-i', str(video_path),
        '-vframes', '1', '-q:v', '3', str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, timeout=30)
    return output_path if output_path.exists() else None


def extract_frames_batch(video_path, start, end, output_dir, prefix, fps=2):
    dur = max(0.5, end - start)
    out_pattern = str(output_dir / f'{prefix}_%03d.jpg')
    cmd = [
        'ffmpeg', '-y', '-ss', str(start), '-t', str(dur),
        '-i', str(video_path), '-vf', f'fps={fps}', str(out_pattern)
    ]
    subprocess.run(cmd, capture_output=True, timeout=60)
    frames = sorted(output_dir.glob(f'{prefix}_*.jpg'))
    return frames


def call_vision(image_data):
    body = {
        "requests": [{
            "image": {"content": base64.b64encode(image_data).decode()},
            "features": [{"type": "LABEL_DETECTION", "maxResults": 20}],
        }]
    }
    req = urllib.request.Request(
        VISION_URL,
        data=json.dumps(body).encode(),
        headers={'Content-Type': 'application/json'}
    )
    for attempt in range(3):
        try:
            resp = urllib.request.urlopen(req, timeout=30)
            result = json.loads(resp.read())
            return result.get("responses", [{}])[0]
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(1.5 ** (attempt + 1))
                continue
            return {"error": f"HTTP {e.code}: {str(e)[:100]}"}
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
                continue
            return {"error": str(e)[:100]}


def label_keyframe(keyframe_path):
    data = keyframe_path.read_bytes()
    if len(data) > 10 * 1024 * 1024:
        return []
    vision = call_vision(data)
    if 'error' in vision:
        log(f'  Vision API error: {vision["error"]}')
        return []
    return [l['description'] for l in vision.get('labelAnnotations', [])]


def transcribe_via_cf(video_path):
    wav_path = None
    for ext in ['.wav', '.mp3', '.m4a']:
        p = Path(str(video_path).rsplit('.', 1)[0] + ext)
        if p.exists():
            wav_path = p
            break
    if not wav_path:
        wav_path = Path(str(video_path) + '.wav')

    info = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-of', 'json', str(video_path)]))
    duration = float(info.get('format', {}).get('duration', 0))

    all_segments = []
    chunk_sec = 120

    for chunk_start in range(0, int(duration) + 1, chunk_sec):
        chunk_end = min(chunk_start + chunk_sec, duration)
        wav = Path(tempfile.mkdtemp()) / f'chunk_{chunk_start}.wav'
        subprocess.run([
            'ffmpeg', '-y', '-ss', str(chunk_start),
            '-t', str(chunk_end - chunk_start),
            '-i', str(video_path),
            '-ar', '16000', '-ac', '1', str(wav)
        ], capture_output=True, timeout=120)

        with open(wav, 'rb') as f:
            audio_b64 = base64.b64encode(f.read()).decode()

        req = urllib.request.Request(
            CF_WHISPER_URL,
            data=json.dumps({'audio': audio_b64, 'word_timestamps': True}).encode(),
            headers={
                'Authorization': f'Bearer {CF_TOKEN}',
                'Content-Type': 'application/json'
            }
        )
        for attempt in range(3):
            try:
                resp = urllib.request.urlopen(req, timeout=60)
                result = json.loads(resp.read())
                if result.get('success'):
                    segs = result['result'].get('segments', [])
                    for s in segs:
                        s['start'] = round(s['start'] + chunk_start, 3)
                        s['end'] = round(s['end'] + chunk_start, 3)
                        if s.get('words'):
                            for w in s['words']:
                                w['start'] = round(w['start'] + chunk_start, 3)
                                w['end'] = round(w['end'] + chunk_start, 3)
                    all_segments.extend(segs)
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(2)
                    continue
                log(f'  CF Whisper chunk error: {e}')

        Path(wav).unlink(missing_ok=True)
        Path(wav.parent).rmdir()

    all_segments.sort(key=lambda s: s['start'])
    log(f'  {len(all_segments)} transcript segments (CF Whisper)')
    return all_segments


_STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'nor', 'yet', 'so', 'for',
    'in', 'on', 'at', 'by', 'to', 'of', 'up', 'as', 'is', 'it', 'be',
    'he', 'she', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'theirs',
    'this', 'that', 'these', 'those',
    'what', 'when', 'where', 'which', 'who', 'whom', 'why', 'how',
    'all', 'each', 'both', 'few', 'many', 'some', 'any', 'every', 'most',
    'no', 'not', 'none', 'nothing', 'neither',
    'here', 'there', 'everywhere', 'anywhere', 'nowhere',
    'then', 'than', 'into', 'onto', 'upon', 'with', 'within', 'without',
    'after', 'before', 'between', 'under', 'through', 'during', 'across',
    'among', 'around', 'beyond', 'toward', 'until', 'since', 'because',
    'although', 'while', 'whereas', 'however', 'therefore', 'moreover',
    'further', 'furthermore', 'nevertheless', 'nonetheless', 'accordingly',
    'consequently', 'otherwise', 'instead', 'meanwhile', 'likewise',
    'indeed', 'surely', 'truly', 'certainly', 'absolutely', 'definitely',
    'essentially', 'basically', 'ultimately', 'eventually', 'rather',
    'quite', 'almost', 'nearly', 'just', 'very', 'too', 'also', 'even',
    'still', 'already', 'yet', 'again', 'often', 'ever', 'never',
    'always', 'usually', 'sometimes', 'rarely', 'seldom', 'maybe',
    'perhaps', 'possibly', 'probably', 'certainly', 'definitely',
    'such', 'same', 'own', 'other', 'another', 'much', 'more', 'less',
    'well', 'back', 'out', 'off', 'down', 'over', 'new', 'old',
    'one', 'two', 'three', 'first', 'second', 'last', 'next',
    'did', 'was', 'were', 'been', 'being', 'have', 'has', 'had',
    'does', 'doing', 'get', 'got', 'make', 'made', 'take', 'took',
    'come', 'came', 'give', 'gave', 'know', 'known', 'see', 'seen',
    'think', 'thought', 'want', 'need', 'find', 'found', 'tell', 'told',
    'ask', 'asked', 'show', 'shown', 'try', 'tried', 'leave', 'left',
    'call', 'called', 'keep', 'kept', 'let', 'put', 'set', 'begin',
    'start', 'end', 'bring', 'brings', 'brought', 'go', 'goes', 'went',
    'gone', 'say', 'says', 'said', 'dr', 'mr', 'mrs', 'ms', 'st',
}

def extract_proper_nouns(text):
    words = re.findall(r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
    seen = set()
    for w in words:
        w = w.strip()
        parts = w.split()
        if len(w) <= 2 or w.lower() in _STOP_WORDS:
            continue
        parts = [p for p in parts if p.lower() not in _STOP_WORDS and len(p) > 1]
        w = ' '.join(parts)
        if len(w) > 2:
            seen.add(w)
    return sorted(seen, key=len, reverse=True)


def align_transcript(segments, shots):
    aligned = []
    for shot in shots:
        start, end = shot['start'], shot['end']
        matching = [
            s for s in segments
            if s.get('start', 0) < end and s.get('end', 0) > start
        ]
        texts = [s['text'].strip() for s in matching]
        narration = ' '.join(t for t in texts if t)
        proper = extract_proper_nouns(narration)
        aligned.append({
            'narration': narration,
            'proper_nouns': proper,
        })
    return aligned


def analyze_motion(video_path, start, end, temp_dir):
    dur = max(0.5, end - start)

    frames = extract_frames_batch(video_path, start, end, temp_dir, f'mot_{start:.0f}', fps=1)

    if len(frames) < 2:
        return {'has_motion': False, 'motion_uniformity': 1.0}

    diffs = []
    for i in range(1, min(len(frames), 6)):
        a = frames[i - 1].read_bytes()
        b = frames[i].read_bytes()
        if len(a) < 1000 or len(b) < 1000:
            continue
        diff = abs(len(a) - len(b)) / max(len(a), len(b))
        diffs.append(diff)

    if not diffs:
        return {'has_motion': False, 'motion_uniformity': 1.0}

    avg_diff = sum(diffs) / len(diffs)
    variance = sum((d - avg_diff) ** 2 for d in diffs) / len(diffs) if len(diffs) > 1 else 0
    uniformity = 1.0 - min(1.0, variance * 5)
    has_motion = avg_diff > 0.05

    return {
        'has_motion': has_motion,
        'motion_uniformity': round(uniformity, 2),
    }


def analyze_frame_diffs(video_path, start, end, temp_dir):
    dur = end - start
    num_samples = min(8, max(3, int(dur)))

    frames = extract_frames_batch(video_path, start, end, temp_dir, f'fd_{start:.0f}', fps=num_samples / max(dur, 1))

    if len(frames) < 3:
        return {'type': 'unknown', 'complexity': 0}

    grays = []
    for s in frames[:num_samples]:
        try:
            img = Image.open(s).convert('L').resize((32, 32))
            grays.append(list(img.getdata()))
        except Exception:
            grays.append([0] * 1024)

    frame_diffs = []
    for i in range(1, len(grays)):
        diff = sum(abs(a - b) for a, b in zip(grays[i - 1], grays[i])) / len(grays[0])
        frame_diffs.append(diff)

    if not frame_diffs:
        return {'type': 'unknown', 'complexity': 0}

    mean_diff = sum(frame_diffs) / len(frame_diffs)
    max_diff = max(frame_diffs)
    std_diff = (sum((d - mean_diff) ** 2 for d in frame_diffs) / len(frame_diffs)) ** 0.5

    if mean_diff < 2.0:
        shot_type = 'ken_burns_still'
    elif std_diff < 2.0:
        shot_type = 'video_footage'
    elif max_diff > 15:
        shot_type = 'text_overlay'
    else:
        shot_type = 'video_footage'

    complexity = round(min(100, mean_diff * 3 + std_diff * 2), 1)

    return {'type': shot_type, 'complexity': complexity}


def analyze_video(video_path, threshold=None):
    video_path = Path(video_path)
    if not video_path.exists():
        print(f'Error: Video file not found: {video_path}')
        sys.exit(1)

    info = get_video_info(video_path)
    log(f'Video: {video_path.name}')
    log(f'  Duration: {info["duration"]}s, {info["fps"]}fps, {info["width"]}x{info["height"]}')

    analysis = detect_shots_fablecut(video_path, threshold)
    shots = analysis.get('shots', [])
    if not shots:
        print('Error: No shots detected')
        return None

    with tempfile.TemporaryDirectory(prefix='exemplar_') as tmp:
        tmp_dir = Path(tmp)

        log('Extracting keyframes and running vision labeling...')
        for i, shot in enumerate(shots):
            mid = (shot['start'] + shot['end']) / 2
            kf_path = tmp_dir / f'kf_{i:04d}.jpg'
            extract_keyframe(video_path, mid, kf_path)
            shot['_keyframe'] = kf_path if kf_path.exists() else None

            if shot['_keyframe'] and shot['_keyframe'].exists():
                shot['vision_labels'] = label_keyframe(shot['_keyframe'])
            else:
                shot['vision_labels'] = []

            if (i + 1) % 10 == 0:
                log(f'  Labeled {i + 1}/{len(shots)} shots')

        log(f'  Labeled {len(shots)}/{len(shots)} shots')

        log('Analyzing motion and classifying shots...')
        for i, shot in enumerate(shots):
            motion = analyze_motion(video_path, shot['start'], shot['end'], tmp_dir)
            fd = analyze_frame_diffs(video_path, shot['start'], shot['end'], tmp_dir)
            shot['has_motion'] = motion['has_motion']
            shot['motion_uniformity'] = motion['motion_uniformity']
            shot['type'] = fd['type']
            shot['_complexity'] = fd['complexity']

        log('Transcribing audio via Cloudflare Whisper...')
        segments = transcribe_via_cf(video_path)

        log('Aligning transcript with shots...')
        aligned = align_transcript(segments, shots)

        log('Building output...')
        output_shots = []
        for i, (shot, align) in enumerate(zip(shots, aligned)):
            output_shots.append({
                'shot_number': shot['index'],
                'start_sec': shot['start'],
                'end_sec': shot['end'],
                'duration_sec': round(shot['end'] - shot['start'], 3),
                'type': shot['type'],
                'energy': shot.get('energy'),
                'vision_labels': shot.get('vision_labels', []),
                'narration': align['narration'],
                'proper_nouns': align['proper_nouns'],
                'has_motion': shot['has_motion'],
                'motion_uniformity': shot['motion_uniformity'],
            })

        result = {
            'source': str(video_path),
            'name': video_path.stem,
            'analyzed_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'duration': info['duration'],
            'fps': info['fps'],
            'width': info['width'],
            'height': info['height'],
            'has_audio': info['has_audio'],
            'total_shots': len(output_shots),
            'shots': output_shots,
        }

        log(f'Done: {len(output_shots)} shots analyzed')
        return result


def main():
    parser = argparse.ArgumentParser(description='Analyze gold standard exemplar videos')
    parser.add_argument('--video', required=True, help='Path to video file')
    parser.add_argument('--output', help='Path to output JSON file')
    parser.add_argument('--name', help='Name for --save mode')
    parser.add_argument('--save', action='store_true', help='Save to gold-standards directory')
    parser.add_argument('--threshold', type=float, default=None,
                        help='Scene cut threshold for FableCut (default: adaptive 0.30->0.20->0.12). Lower for smooth/ken-burns videos.')
    args = parser.parse_args()

    result = analyze_video(args.video, args.threshold)
    if result is None:
        sys.exit(1)

    if args.save:
        name = args.name or Path(args.video).stem
        output_path = EXEMPLARS_DIR / f'{name}-analysis.json'
        EXEMPLARS_DIR.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2))
        print(f'Saved analysis to {output_path}')
    elif args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2))
        print(f'Saved analysis to {output_path}')
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
