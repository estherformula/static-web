# FAQ (자주 묻는 질문)

EstherPack iOS 의 FAQ 화면(`faq_data.tsv` 기반 네이티브 구현)을 그대로
정적 HTML 로 옮긴 페이지입니다.

- 공개 URL: https://estherformula.github.io/static-web/faq/
- 화면 구조: **제목(목록) → 내용(상세)** 2뎁스 / 모바일 최적화

## 구성

| 파일 | 설명 |
|---|---|
| `faq_data.tsv` | 원본 데이터. 탭 구분 3컬럼: `그룹\t질문\t답변` (iOS 와 동일 포맷) |
| `build.py` | `faq_data.tsv` → `index.html` 변환 스크립트 |
| `index.html` | 빌드 결과물 (정적 HTML). 직접 수정하지 말 것 |

## 내용 변경 / 리퍼블리싱

1. `faq_data.tsv` 를 새 내용으로 교체한다. (iOS 의 `faq_data.tsv` 와 같은 포맷)
2. 아래 명령으로 다시 빌드한다.

   ```bash
   python3 build.py
   ```

3. 생성된 `index.html` 을 커밋/푸시한다.

> 답변(`a` 컬럼) 의 `<br>` 은 줄바꿈으로 변환되며, 그 외 `< >` 등은
> iOS 와 동일하게 리터럴 텍스트로 표시됩니다.
