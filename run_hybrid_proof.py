"""Offline six-frame native proof with a nonblocking shared render lock.

SPDX-License-Identifier: MIT. Python 3 + Pillow; Blender and a Korean-capable font
are explicit user inputs. No fonts or production scenes are redistributed.
"""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compose(out, font_path, font_index):
    from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat
    native = json.loads((out / 'native-report.json').read_text())
    frames, checks = [], []
    for kind in ('abstract', 'concrete'):
        images = []
        for row in native[kind]['frames']:
            path = out / row['file']
            assert sha(path) == row['sha256']
            image = Image.open(path).convert('RGB')
            assert image.size == (1280, 720)
            draw = ImageDraw.Draw(image)
            # Opaque bands first, text last; never paint over a previously drawn label.
            draw.rectangle((0, 0, 1280, 85), fill='#101820')
            draw.rectangle((0, 630, 1280, 720), fill='#101820')
            texts = [{'text': row['title'], 'xy': [640, 43], 'size': 31},
                     {'text': row['footer'], 'xy': [640, 670], 'size': 27}]
            texts += [{**label, 'size': 29} for label in row['labels']]
            boxes = []
            for entry in texts:
                font = ImageFont.truetype(str(font_path), entry['size'], index=font_index)
                # Reject a font presenting all Korean text as missing-glyph boxes.
                missing = bytes(font.getmask('\U0010ffff'))
                for char in entry['text']:
                    if '\uac00' <= char <= '\ud7a3':
                        assert bytes(font.getmask(char)) != missing, ('missing Hangul glyph', char)
                x, y = entry['xy']
                box = draw.textbbox((x, y), entry['text'], font=font, anchor='mm', stroke_width=1)
                assert 20 <= box[0] < box[2] <= 1260 and 10 <= box[1] < box[3] <= 710, box
                for other in boxes:
                    assert min(box[2], other[2]) <= max(box[0], other[0]) or min(box[3], other[3]) <= max(box[1], other[1]), (box, other)
                boxes.append(box)
                draw.text((x, y), entry['text'], font=font, anchor='mm', fill='#f3f1e9',
                          stroke_width=1, stroke_fill='#101820')
            composed = out / ('labelled-' + row['file'])
            image.save(composed)
            # Re-open and fully decode the exact output.
            with Image.open(composed) as decoded:
                decoded.load()
                assert decoded.size == (1280, 720)
            images.append(Image.open(path).convert('RGB'))
            frames.append({'file': composed.name, 'sha256': sha(composed), 'text_boxes': boxes})
        delta = sum(ImageStat.Stat(ImageChops.difference(images[0], images[-1])).mean) / 3
        assert delta > .1, (kind, delta)
        checks.append({'shot': kind, 'native_start_end_mean_pixel_delta': delta})
    sheet = Image.new('RGB', (1920, 720), '#101820')
    for i, frame in enumerate(frames):
        with Image.open(out / frame['file']) as image:
            sheet.paste(image.resize((640, 360), Image.Resampling.LANCZOS), ((i % 3) * 640, (i // 3) * 360))
    sheet.save(out / 'contact-sheet.png')
    root = Path(__file__).resolve().parent
    source_names = ('blender/hybrid_stage.py', 'blender/demo_hybrid.py',
                    'blender/narrative_props.py', 'run_hybrid_proof.py')
    report = {'status': 'PASS', 'source_sha256': {name: sha(root / name) for name in source_names},
              'native_frame_count': len(frames), 'composed_frame_count': len(frames),
              'font': {'filename': font_path.name, 'index': font_index, 'sha256': sha(font_path)},
              'frames': frames, 'motion_samples': checks, 'contact_sheet_sha256': sha(out / 'contact-sheet.png'),
              'checks': ['native file hashes', 'PNG full decode', '1280x720', 'screen text bounds/nonoverlap',
                         'Hangul not missing-glyph boxes', 'sampled pixel change', 'native connector/actor/camera assertions'],
              'limits': ['six sampled stills, not a continuous animation', 'no full-user QA or aesthetic approval',
                         'no natural foot-lock IK or contact/grasp validation', 'fit covers supplied sampled extrema only']}
    (out / 'proof-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print('HYBRID_PROOF_PASS ' + json.dumps({'frames': len(frames), 'motion': checks}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender', required=True, type=Path)
    parser.add_argument('--font', required=True, type=Path)
    parser.add_argument('--font-index', type=int, default=0)
    parser.add_argument('--lock', required=True, type=Path, help='shared production render lock; never use a separate lock to bypass it')
    parser.add_argument('--out', required=True, type=Path, help='fresh output directory; refuses existing paths')
    args = parser.parse_args()
    with args.lock.open('a+') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('RENDER_NOT_RUN: shared lock busy', file=sys.stderr)
            return 73
        if args.out.exists():
            parser.error('output already exists; select a fresh directory')
        if not args.blender.is_file() or not args.font.is_file():
            parser.error('Blender executable and font must be existing files')
        args.out.mkdir(parents=True)
        root = Path(__file__).resolve().parent
        command = [str(args.blender.resolve()), '--background', '--factory-startup', '--disable-autoexec',
                   '--python-exit-code', '1', '--python', str(root / 'blender' / 'demo_hybrid.py'),
                   '--', '--out', str(args.out.resolve())]
        with (args.out / 'blender.log').open('w') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False)
        if result.returncode:
            print('NATIVE_FAILED: inspect blender.log', file=sys.stderr)
            return result.returncode
        compose(args.out, args.font, args.font_index)
    return 0


if __name__ == '__main__':
    sys.exit(main())
