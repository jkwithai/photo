# -*- coding: utf-8 -*-
"""
generate_gallery.py
===================
images/ 폴더를 스캔해서 gallery.json을 만들고,
브라우저에서 바로 확인할 수 있게 로컬 서버를 켜줍니다.

사용법:
  python generate_gallery.py           -> JSON 생성 + 서버 실행 + 브라우저 열기
  python generate_gallery.py --no-serve -> JSON만 생성 (서버 X)
  python generate_gallery.py --resize  -> 큰 사진 자동 압축 포함
  python generate_gallery.py --deploy  -> JSON 생성 + GitHub에 배포
"""

import sys
import io
import os
import json
import argparse
import subprocess
import webbrowser
import threading
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Windows 터미널 한글/이모지 출력 안전 처리
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf-8-sig'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 지원 확장자
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'}

# 파일명 키워드 -> 카테고리 자동 분류
CATEGORY_MAP = {
    'portrait': ['portrait', 'person', 'people', 'face', 'model', 'human', '인물'],
    'landscape': ['landscape', 'nature', 'sky', 'mountain', 'sea', 'forest',
                  'travel', 'outdoor', 'sunset', 'sunrise', 'ocean', '풍경', '바다', '산', '하늘'],
    'work': ['work', 'product', 'studio', 'design', 'object', 'still', '작업', '제품'],
}

PORT = 8080


# ─────────────────────────────────────────────
def guess_category(filename: str) -> str:
    name = filename.lower()
    for cat, keywords in CATEGORY_MAP.items():
        if any(kw in name for kw in keywords):
            return cat
    return 'all'


# ─────────────────────────────────────────────
def get_size(path: Path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except ImportError:
        return None, None
    except Exception:
        return None, None


# ─────────────────────────────────────────────
def resize_image(path: Path, max_width: int = 1920, quality: int = 85):
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("  [!] Pillow 없음 - 리사이즈 건너뜀 (pip install Pillow)")
        return get_size(path)

    try:
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im)
            w, h = im.size
            if w <= max_width:
                return w, h

            ratio = max_width / w
            new_h = int(h * ratio)
            im = im.resize((max_width, new_h), Image.LANCZOS)

            if path.suffix.lower() in ('.jpg', '.jpeg'):
                if im.mode in ('RGBA', 'LA', 'P'):
                    bg = Image.new('RGB', im.size, (255, 255, 255))
                    if im.mode == 'P':
                        im = im.convert('RGBA')
                    alpha = im.split()[-1] if im.mode in ('RGBA', 'LA') else None
                    bg.paste(im, mask=alpha)
                    im = bg
                im.save(path, quality=quality, optimize=True)
            else:
                im.save(path, optimize=True)

            print(f"  [리사이즈] {path.name}: {w}x{h} -> {max_width}x{new_h}")
            return max_width, new_h
    except Exception as e:
        print(f"  [!] 리사이즈 실패: {path.name} ({e})")
        return get_size(path)


# ─────────────────────────────────────────────
def scan(images_dir: Path, do_resize: bool, max_width: int) -> list:
    if not images_dir.exists():
        images_dir.mkdir(exist_ok=True)
        return []

    files = []
    for ext in IMAGE_EXTS:
        files += list(images_dir.glob(f'*{ext}'))
        files += list(images_dir.glob(f'*{ext.upper()}'))

    files = sorted(set(files))
    files = [f for f in files if f.name != 'gallery.json']

    result = []
    for path in files:
        cat = guess_category(path.name)

        if do_resize and path.suffix.lower() != '.svg':
            w, h = resize_image(path, max_width=max_width)
        else:
            w, h = get_size(path)

        entry = {
            'src': f'images/{path.name}',
            'title': path.stem.replace('_', ' ').replace('-', ' '),
            'category': cat,
        }
        if w and h:
            entry['width'] = w
            entry['height'] = h

        result.append(entry)
        size_str = f'{w}x{h}' if w else '크기미확인'
        print(f"  [추가] {path.name}  [{cat}]  {size_str}")

    return result


# ─────────────────────────────────────────────
def start_server(directory: str, port: int):
    """백그라운드에서 로컬 서버 실행"""
    os.chdir(directory)

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # 서버 로그 숨김

    try:
        server = HTTPServer(('', port), QuietHandler)
        server.serve_forever()
    except OSError:
        pass  # 이미 포트가 열려있으면 무시


def is_port_open(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


# ─────────────────────────────────────────────
def deploy_to_github():
    """gallery.json 변경사항을 GitHub에 push"""
    print()
    print("[배포] GitHub에 업로드 중...")
    cmds = [
        ['git', 'add', 'images/gallery.json'],
        ['git', 'commit', '-m', '갤러리 이미지 업데이트'],
        ['git', 'push'],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # "nothing to commit"은 오류가 아님
            if 'nothing to commit' in result.stdout + result.stderr:
                print("  [!] 변경사항 없음 (이미 최신 상태)")
                return
            print(f"  [!] 오류: {result.stderr.strip()}")
            return
    print("  [완료] GitHub Pages 반영까지 1-2분 소요됩니다.")


# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='images/ -> gallery.json 생성기')
    parser.add_argument('--no-serve', action='store_true',
                        help='서버를 켜지 않고 JSON만 만들기')
    parser.add_argument('--resize', action='store_true',
                        help='큰 이미지 자동 압축 (pip install Pillow 필요)')
    parser.add_argument('--max-width', type=int, default=1920)
    parser.add_argument('--images-dir', default='images')
    parser.add_argument('--deploy', action='store_true',
                        help='JSON 생성 후 GitHub에 자동 배포')
    args = parser.parse_args()

    images_dir = Path(args.images_dir)

    print()
    print("===========================================")
    print("  포트폴리오 갤러리 빌더")
    print("===========================================")

    # 1. 이미지 스캔
    print()
    print(f"[1/2] '{images_dir}' 폴더 스캔 중...")
    images = scan(images_dir, do_resize=args.resize, max_width=args.max_width)

    if not images:
        print()
        print("[!] 이미지를 찾을 수 없습니다.")
        print("    images/ 폴더에 .jpg / .png 파일을 넣어주세요.")
        sys.exit(0)

    # 2. gallery.json 저장
    out_path = images_dir / 'gallery.json'
    data = {'images': images, 'total': len(images)}
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    print()
    print(f"[2/2] gallery.json 저장 완료 -> {len(images)}개 이미지")

    # GitHub 배포
    if args.deploy:
        deploy_to_github()
        print()
        print("  배포 완료! 확인: https://jkwithai.github.io/photo/")
        return

    # 로컬 서버 + 브라우저 열기
    if not args.no_serve:
        url = f"http://localhost:{PORT}"
        project_dir = str(Path(__file__).parent.resolve())

        if is_port_open(PORT):
            print()
            print(f"[서버] 이미 실행 중 -> {url}")
        else:
            t = threading.Thread(
                target=start_server,
                args=(project_dir, PORT),
                daemon=True
            )
            t.start()
            time.sleep(0.5)
            print()
            print(f"[서버] 로컬 서버 시작 -> {url}")

        webbrowser.open(url)
        print()
        print("브라우저에서 갤러리를 확인하세요!")
        print("(이 창을 닫으면 서버도 종료됩니다. 계속 보려면 열어두세요)")
        print()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print()
            print("서버를 종료합니다.")
    else:
        print()
        print("완료! 서버를 켜려면: python -m http.server 8080")
        print(f"그 다음 브라우저에서: http://localhost:{PORT}")


if __name__ == '__main__':
    main()
