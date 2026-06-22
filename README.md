# 📷 내 사진으로 만드는 웹 포트폴리오

코딩 몰라도 OK! 사진을 폴더에 넣고, 스크립트 하나 돌리면 끝입니다.

---

## 📁 폴더 구조

```
photo/
├── index.html          ← 사이트 메인 파일
├── style.css           ← 디자인 (색상, 폰트 등)
├── script.js           ← 갤러리 동작
├── generate_gallery.py ← 사진 목록 자동 생성 스크립트
├── images/
│   ├── gallery.json    ← 스크립트가 자동으로 만들어줌
│   ├── 내사진1.jpg
│   ├── 내사진2.jpg
│   └── ...
└── README.md           ← 지금 읽고 있는 이 파일
```

---

## ✏️ 내 정보 입력하는 법

`index.html` 파일을 메모장(또는 VS Code)으로 열고, 아래 주석을 찾아 수정하세요.

| 주석 | 무엇을 바꾸면 되나 |
|------|------------------|
| `✏️ 수정 1` | 브라우저 탭 제목 (예: `홍길동 \| 포트폴리오`) |
| `✏️ 수정 2` | 헤더에 표시될 내 이름 |
| `✏️ 수정 3` | 헤더 아래 한 줄 소개 |
| `✏️ 수정 4` | About 자기소개 문단 |
| `✏️ 수정 5` | 이메일 주소 |
| `✏️ 수정 6` | Instagram 아이디 |
| `✏️ 수정 7` | GitHub 아이디 (없으면 `<li>` 태그째 삭제) |
| `✏️ 수정 8` | 푸터 이름 |

---

## 🖼️ 내 사진 넣는 법 (5단계)

### 1단계 — 사진을 `images/` 폴더에 복사

파일 이름은 한글보다 영어가 안전합니다.

```
images/
├── portrait_01.jpg
├── landscape_trip.jpg
└── work_branding.png
```

### 2단계 — 파일 이름으로 카테고리 자동 분류

파일 이름에 아래 단어가 들어있으면 자동으로 분류됩니다.

| 카테고리 | 파일명에 포함되면 되는 단어 |
|---------|--------------------------|
| 인물    | portrait, person, people, face, model, 인물 |
| 풍경    | landscape, nature, sky, mountain, sea, 풍경, travel |
| 작업물  | work, product, studio, design, 작업 |
| 전체    | 위 단어 없으면 자동으로 '전체'에 포함 |

### 3단계 — Python이 설치되어 있는지 확인

터미널(명령 프롬프트)을 열고 입력:

```bash
python --version
```

`Python 3.x.x` 가 나오면 OK. 없으면 https://python.org 에서 설치.

### 4단계 — 갤러리 목록 생성

터미널에서 이 폴더로 이동 후:

```bash
# 기본 실행 (사진 목록만 만들기)
python generate_gallery.py

# 사진이 크면 자동으로 줄이기 (Pillow 패키지 필요)
pip install Pillow
python generate_gallery.py --resize
```

### 5단계 — 로컬 서버로 확인

```bash
python -m http.server 8080
```

브라우저에서 `http://localhost:8080` 열기 → 갤러리 확인!

> **왜 서버가 필요하나요?**  
> `index.html`을 직접 더블클릭하면 보안 제한으로 사진 목록을 읽지 못합니다.  
> 위 명령어를 실행하면 PC가 잠깐 웹서버가 되어서 정상 작동합니다.

---

## 🌐 GitHub Pages로 무료 배포하는 법

인터넷에 올려서 전 세계 어디서든 볼 수 있게 만들기!

### 사전 준비
- GitHub 계정 (https://github.com 에서 무료 가입)
- Git 설치 (https://git-scm.com)

### 배포 순서

**1. GitHub에서 새 저장소(Repository) 만들기**
- GitHub 로그인 → 오른쪽 위 `+` → `New repository`
- 이름: `portfolio` (또는 원하는 이름)
- `Public` 선택 → `Create repository`

**2. 파일 올리기**

터미널에서:

```bash
# 이 폴더(photo)로 이동 후
git init
git add .
git commit -m "포트폴리오 첫 업로드"
git branch -M main
git remote add origin https://github.com/내아이디/portfolio.git
git push -u origin main
```

**3. GitHub Pages 켜기**
- GitHub 저장소 페이지에서 `Settings` 탭 클릭
- 왼쪽 메뉴에서 `Pages` 클릭
- **Source**: `Deploy from a branch` 선택
- **Branch**: `main` / `/ (root)` 선택 → `Save`

**4. 1~3분 기다리면 주소 생성!**

```
https://내아이디.github.io/portfolio/
```

이 주소를 카카오톡, 인스타 바이오, 이메일 서명에 붙여넣기 하면 됩니다. 🎉

---

## 🔄 사진 추가하는 법 (배포 이후)

1. `images/` 폴더에 사진 추가
2. `python generate_gallery.py` 실행
3. 아래 명령어로 GitHub에 업데이트 반영:

```bash
git add .
git commit -m "새 사진 추가"
git push
```

GitHub Pages가 자동으로 업데이트됩니다. (1~2분 소요)

---

## 🎨 디자인 바꾸고 싶을 때

`style.css` 파일 맨 위의 `:root { ... }` 블록을 수정하면 됩니다.

```css
:root {
  --accent: #b8956a;  ← 포인트 색상 (지금은 골드톤)
  --bg:     #f9f7f4;  ← 배경색
}
```

색상 코드는 https://htmlcolorcodes.com 에서 고를 수 있습니다.

---

## ❓ 자주 묻는 질문

**Q. 사진이 갤러리에 안 나와요.**  
A. `python generate_gallery.py`를 다시 실행했는지 확인하세요.  
   그리고 `python -m http.server 8080` 으로 서버를 켜고 열었는지 확인하세요.

**Q. 카테고리 이름을 바꾸고 싶어요.**  
A. `index.html`에서 `<button class="filter-btn" data-filter="portrait">인물</button>` 부분을 찾아 `인물`을 원하는 이름으로 바꾸세요.

**Q. 사진을 클릭해도 크게 안 보여요.**  
A. 로컬 서버(`python -m http.server 8080`)를 켜고 사용하고 있는지 확인하세요.

---

*이 포트폴리오 사이트는 HTML + CSS + JavaScript로 만들어졌습니다.*
