#!/usr/bin/env python3
"""
generate_gallery.py
===================
이 스크립트를 실행하면 images/ 폴더의 사진을 자동으로 인식해서
gallery.json 파일을 만들어 줍니다.

사용법:
  python generate_gallery.py            → 일반 실행 (사진 목록만 만들기)
  python generate_gallery.py --resize   → 사진을 최대 1920px로 줄이기
  python generate_gallery.py --sample   → 테스트용 샘플 이미지 새로 만들기
"""

import os
import json
import sys
import argparse
from pathlib import Path

# 지원하는 이미지 확장자
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'}

# 파일명 키워드 → 카테고리 자동 감지
# 예: 파일명에 'portrait'이 들어있으면 portrait 카테고리로 분류
CATEGORY_MAP = {
    'portrait': ['portrait', 'person', 'people', 'face', '인물', 'model', 'human'],
    'landscape': ['landscape', 'nature', 'sky', 'mountain', 'sea', 'forest',
                  '풍경', 'travel', 'outdoor', 'sunset', 'sunrise', 'ocean'],
    'work': ['work', 'product', 'studio', 'design', '작업', 'object', 'still'],
}


# ─────────────────────────────────────────────
#  카테고리 자동 감지
# ─────────────────────────────────────────────
def guess_category(filename: str) -> str:
    name = filename.lower()
    for cat, keywords in CATEGORY_MAP.items():
        if any(kw in name for kw in keywords):
            return cat
    return 'all'


# ─────────────────────────────────────────────
#  이미지 크기 읽기 (Pillow 필요)
# ─────────────────────────────────────────────
def get_size(path: Path):
    """(width, height) 반환. Pillow 없으면 (None, None)."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except ImportError:
        return None, None
    except Exception as e:
        print(f"   ⚠  크기 읽기 실패: {path.name} ({e})")
        return None, None


# ─────────────────────────────────────────────
#  이미지 리사이즈 (Pillow 필요)
# ─────────────────────────────────────────────
def resize_image(path: Path, max_width: int = 1920, quality: int = 85):
    """
    이미지 너비가 max_width 초과이면 줄여서 덮어씁니다.
    (width, height) 반환.
    """
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("   ⚠  Pillow가 없어 리사이즈를 건너뜁니다.")
        print("      설치: pip install Pillow")
        return get_size(path)

    try:
        with Image.open(path) as im:
            # EXIF 회전 자동 보정
            im = ImageOps.exif_transpose(im)
            w, h = im.size

            if w <= max_width:
                return w, h  # 이미 충분히 작음

            ratio = max_width / w
            new_h = int(h * ratio)
            im = im.resize((max_width, new_h), Image.LANCZOS)

            # JPEG 저장 시 알파채널 제거
            if path.suffix.lower() in ('.jpg', '.jpeg'):
                if im.mode in ('RGBA', 'LA', 'P'):
                    bg = Image.new('RGB', im.size, (255, 255, 255))
                    alpha = im.split()[-1] if im.mode in ('RGBA', 'LA') else None
                    if im.mode == 'P':
                        im = im.convert('RGBA')
                        alpha = im.split()[-1]
                    bg.paste(im, mask=alpha)
                    im = bg
                im.save(path, quality=quality, optimize=True)
            else:
                im.save(path, optimize=True)

            print(f"   ✓ 리사이즈: {w}×{h} → {max_width}×{new_h}")
            return max_width, new_h

    except Exception as e:
        print(f"   ✗ 리사이즈 실패: {path.name} ({e})")
        return get_size(path)


# ─────────────────────────────────────────────
#  샘플 SVG 이미지 생성
# ─────────────────────────────────────────────
def make_samples(images_dir: Path):
    """테스트용 SVG 샘플 이미지를 새로 만듭니다."""
    samples = [
        ('sample_portrait_01.svg', 'portrait', '포트레이트 01', 800, 1067, '#e8ddd4', '#c8b8a8'),
        ('sample_portrait_02.svg', 'portrait', '포트레이트 02', 800, 1000, '#d8ccc4', '#b8a898'),
        ('sample_landscape_01.svg', 'landscape', '풍경 01', 1200, 800, '#c4d4e8', '#a4b4c8'),
        ('sample_landscape_02.svg', 'landscape', '풍경 02', 1200, 750, '#e8e4d8', '#c0b09c'),
        ('sample_landscape_03.svg', 'landscape', '풍경 03', 1000, 667, '#b8cce0', '#a8b8c8'),
        ('sample_work_01.svg', 'work', '작업물 01', 900, 900, '#f0ece4', '#d8d0c4'),
        ('sample_work_02.svg', 'work', '작업물 02', 800, 1000, '#e4e0d8', '#f0ece6'),
        ('sample_misc_01.svg', 'all', '사진 샘플', 800, 600, '#e0d8ec', '#c8c0dc'),
    ]

    images_dir.mkdir(exist_ok=True)
    created = []

    for filename, cat, title, w, h, c1, c2 in samples:
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#g)"/>
  <text x="{w//2}" y="{int(h*0.75)}" text-anchor="middle"
        font-family="Georgia,serif" font-size="{min(w,h)//12}"
        fill="rgba(80,65,50,0.22)" font-weight="300" letter-spacing="6">
    {title}
  </text>
  <text x="{w//2}" y="{int(h*0.83)}" text-anchor="middle"
        font-family="Arial,sans-serif" font-size="{min(w,h)//20}"
        fill="rgba(80,65,50,0.15)" letter-spacing="3">
    {w} × {h}
  </text>
</svg>'''
        out = images_dir / filename
        out.write_text(svg, encoding='utf-8')
        print(f"   ✓ {filename}")
        created.append({
            'src': f'images/{filename}',
            'title': title,
            'category': cat,
            'width': w,
            'height': h
        })

    return created


# ─────────────────────────────────────────────
#  images/ 폴더 스캔
# ─────────────────────────────────────────────
def scan(images_dir: Path, do_resize: bool, max_width: int) -> list:
    """images/ 폴더의 이미지 파일을 읽어 목록을 반환합니다."""
    if not images_dir.exists():
        print(f"  '{images_dir}' 폴더가 없어서 새로 만들었습니다.")
        images_dir.mkdir(exist_ok=True)
        return []

    # 이미지 파일 수집
    files = []
    for ext in IMAGE_EXTS:
        files += list(images_dir.glob(f'*{ext}'))
        files += list(images_dir.glob(f'*{ext.upper()}'))
    files = sorted(set(files))

    # gallery.json 자체는 제외
    files = [f for f in files if f.name != 'gallery.json']

    if not files:
        return []

    result = []
    for path in files:
        name  = path.name
        stem  = path.stem
        cat   = guess_category(name)

        # SVG는 리사이즈 불필요
        if do_resize and path.suffix.lower() != '.svg':
            w, h = resize_image(path, max_width=max_width)
        else:
            w, h = get_size(path)

        entry = {
            'src': f'images/{name}',
            'title': stem.replace('_', ' ').replace('-', ' ').title(),
            'category': cat,
        }
        if w and h:
            entry['width']  = w
            entry['height'] = h

        result.append(entry)
        size_str = f'{w}×{h}' if w else '크기 미확인'
        print(f"   ✓ {name}  [{cat}]  {size_str}")

    return result


# ─────────────────────────────────────────────
#  메인
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description='photos → gallery.json 변환기',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python generate_gallery.py              일반 실행
  python generate_gallery.py --resize     사진 자동 압축 포함
  python generate_gallery.py --sample     샘플 이미지 재생성
        """
    )
    parser.add_argument('--sample', action='store_true',
                        help='테스트용 샘플 이미지를 새로 만듭니다')
    parser.add_argument('--resize', action='store_true',
                        help='이미지를 --max-width 기준으로 줄입니다 (Pillow 필요)')
    parser.add_argument('--max-width', type=int, default=1920,
                        help='리사이즈 최대 너비 (기본값: 1920)')
    parser.add_argument('--images-dir', default='images',
                        help='이미지 폴더 경로 (기본값: images)')
    args = parser.parse_args()

    images_dir = Path(args.images_dir)

    print()
    print('📷  포트폴리오 갤러리 빌더')
    print('=' * 44)

    images = []

    # 1. 샘플 생성 (옵션)
    if args.sample:
        print('\n[1/2] 샘플 이미지 생성 중...')
        make_samples(images_dir)

    # 2. 폴더 스캔
    step = '2/2' if args.sample else '1/1'
    print(f'\n[{step}] "{images_dir}" 폴더 스캔 중...')
    images = scan(images_dir, do_resize=args.resize, max_width=args.max_width)

    if not images:
        print()
        print('⚠  이미지를 찾을 수 없습니다.')
        print('   → images/ 폴더에 .jpg / .png 파일을 넣어주세요.')
        print('   → 또는  python generate_gallery.py --sample  으로 샘플을 만들어보세요.')
        sys.exit(0)

    # 3. gallery.json 저장
    out_path = images_dir / 'gallery.json'
    data = {'images': images, 'total': len(images)}
    out_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    print()
    print(f'✅  완료!  {len(images)}개 이미지 → {out_path}')
    print()
    print('다음 단계:')
    print('  python -m http.server 8080  을 실행하고')
    print('  브라우저에서  http://localhost:8080  을 열어보세요.')
    print()


if __name__ == '__main__':
    main()
