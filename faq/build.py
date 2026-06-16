#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAQ 정적 HTML 빌더

EstherPack iOS 의 FAQ 화면(faq_data.tsv 기반 네이티브 구현)을 그대로
정적 HTML 로 변환한다.

사용법:
    python3 build.py

동작:
    같은 폴더의 faq_data.tsv 를 읽어 index.html 을 생성한다.
    내용 변경 시 faq_data.tsv 만 교체한 뒤 다시 실행하면(리퍼블리싱)
    동일한 형태의 정적 HTML 이 재생성된다.

TSV 포맷 (탭 구분, 3컬럼):
    그룹(group)\t질문(q)\t답변(a)
    - iOS 와 동일하게 정확히 3개 컬럼인 행만 사용한다.
    - 답변(a) 의 <br> 은 줄바꿈으로 변환하고, 그 외 텍스트는
      iOS(StyledLabel) 와 동일하게 < > 등을 리터럴 텍스트로 노출한다.
"""

import html
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TSV_PATH = os.path.join(BASE_DIR, "faq_data.tsv")
OUT_PATH = os.path.join(BASE_DIR, "index.html")


def load_groups(tsv_path):
    """iOS FaqParser 와 동일한 로직: 3컬럼 행만 채택하고 그룹 순서를 보존."""
    with open(tsv_path, "r", encoding="utf-8") as f:
        contents = f.read()

    group_titles = []
    group_items = {}

    for row in contents.split("\n"):
        cols = row.split("\t")
        if len(cols) != 3:
            continue
        group, q, a = cols
        if group not in group_titles:
            group_titles.append(group)
        group_items.setdefault(group, []).append({"group": group, "q": q, "a": a})

    return [
        {"title": t, "items": group_items[t]}
        for t in group_titles
        if group_items.get(t)
    ]


def render_answer(answer):
    """iOS: a.replacingOccurrences(of: "<br>", with: "\n").
    < > 같은 비-태그 문자는 리터럴로 보여야 하므로 전체 이스케이프 후
    <br> 만 실제 줄바꿈으로 복원한다."""
    escaped = html.escape(answer)
    return escaped.replace("&lt;br&gt;", "<br>")


def build_html(groups):
    items_flat = []
    for g in groups:
        for it in g["items"]:
            items_flat.append(it)

    # 리스트(1뎁스)
    list_parts = []
    detail_index = 0
    for gi, group in enumerate(groups):
        rows = []
        for it in group["items"]:
            q_text = html.escape(it["q"])
            rows.append(
                f'        <button class="faq-item" onclick="showDetail({detail_index})">'
                f'<span class="q">Q</span>'
                f'<span class="q-text">{q_text}</span></button>'
            )
            detail_index += 1
        group_html = (
            f'      <section class="faq-group">\n'
            f'        <h2 class="group-title">{html.escape(group["title"])}</h2>\n'
            f'        <div class="items">\n' + "\n".join(rows) + "\n        </div>\n"
            f'      </section>'
        )
        list_parts.append(group_html)
        if gi < len(groups) - 1:
            list_parts.append('      <div class="group-divider"></div>')

    list_html = "\n".join(list_parts)

    # 상세(2뎁스)
    detail_parts = []
    for idx, it in enumerate(items_flat):
        detail_parts.append(
            f'      <article class="faq-detail" id="detail-{idx}" hidden>\n'
            f'        <button class="back" onclick="showList()" aria-label="뒤로">\n'
            f'          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
            f'<path d="M15 19L8 12L15 5" stroke="#1F2A37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>\n'
            f'        </button>\n'
            f'        <span class="badge">{html.escape(it["group"])}</span>\n'
            f'        <h1 class="detail-title">{html.escape(it["q"])}</h1>\n'
            f'        <div class="detail-content">{render_answer(it["a"])}</div>\n'
            f'      </article>'
        )
    detail_html = "\n".join(detail_parts)

    return TEMPLATE.format(list_html=list_html, detail_html=detail_html)


TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <meta name="format-detection" content="telephone=no" />
  <title>자주 묻는 질문</title>
  <style>
    :root {{
      --gray900: #111927;
      --gray800: #1F2A37;
      --gray600: #4D5761;
      --gray500: #6C737F;
      --gray400: #9DA4AE;
      --gray200: #EDEFF3;
      --gray100: #F3F4F6;
    }}
    * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
    html, body {{ margin: 0; padding: 0; }}
    body {{
      font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo",
        "Malgun Gothic", "맑은 고딕", sans-serif;
      color: var(--gray800);
      background: #fff;
      -webkit-font-smoothing: antialiased;
    }}
    .wrap {{ max-width: 480px; margin: 0 auto; min-height: 100vh; }}

    /* 리스트(1뎁스) */
    .faq-group {{ padding: 12px 16px 0; }}
    .group-title {{
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      line-height: 1.4;
      color: var(--gray900);
    }}
    .items {{ margin-top: 12px; display: flex; flex-direction: column; }}
    .faq-item {{
      display: flex;
      align-items: center;
      gap: 12px;
      width: 100%;
      padding: 12px 0;
      background: none;
      border: 0;
      text-align: left;
      cursor: pointer;
      font: inherit;
    }}
    .faq-item .q {{
      flex: 0 0 auto;
      width: 12px;
      font-size: 16px;
      font-weight: 600;
      color: var(--gray400);
    }}
    .faq-item .q-text {{
      flex: 1 1 auto;
      font-size: 16px;
      font-weight: 500;
      line-height: 1.5;
      color: var(--gray800);
    }}
    .group-divider {{
      height: 1px;
      background: var(--gray200);
      margin: 20px 16px 27px;
    }}

    /* 상세(2뎁스) */
    .faq-detail {{ padding: 0 16px 60px; }}
    .back {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      margin: 8px -8px 0;
      padding: 0;
      background: none;
      border: 0;
      cursor: pointer;
    }}
    .badge {{
      display: inline-block;
      margin-top: 16px;
      padding: 3px 6px;
      border-radius: 6px;
      background: var(--gray100);
      color: var(--gray600);
      font-size: 14px;
      font-weight: 600;
      line-height: 1.4;
    }}
    .detail-title {{
      margin: 12px 0 0;
      font-size: 20px;
      font-weight: 600;
      line-height: 1.4;
      color: var(--gray800);
    }}
    .detail-content {{
      margin-top: 40px;
      font-size: 16px;
      font-weight: 500;
      line-height: 1.6;
      color: var(--gray500);
      white-space: normal;
      word-break: break-word;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div id="list">
{list_html}
    </div>
{detail_html}
  </div>

  <script>
    var listEl = document.getElementById('list');
    var currentDetail = null;

    function showDetail(idx) {{
      var el = document.getElementById('detail-' + idx);
      if (!el) return;
      listEl.hidden = true;
      el.hidden = false;
      currentDetail = el;
      window.scrollTo(0, 0);
      if (history.state === null || history.state.view !== 'detail') {{
        history.pushState({{ view: 'detail', idx: idx }}, '');
      }}
    }}

    function showList() {{
      if (history.state && history.state.view === 'detail') {{
        history.back();
      }} else {{
        renderList();
      }}
    }}

    function renderList() {{
      if (currentDetail) {{ currentDetail.hidden = true; currentDetail = null; }}
      listEl.hidden = false;
      window.scrollTo(0, 0);
    }}

    window.addEventListener('popstate', function (e) {{
      if (e.state && e.state.view === 'detail') {{
        showDetailFromState(e.state.idx);
      }} else {{
        renderList();
      }}
    }});

    function showDetailFromState(idx) {{
      var el = document.getElementById('detail-' + idx);
      if (!el) return;
      listEl.hidden = true;
      if (currentDetail && currentDetail !== el) currentDetail.hidden = true;
      el.hidden = false;
      currentDetail = el;
      window.scrollTo(0, 0);
    }}
  </script>
</body>
</html>
"""


def main():
    groups = load_groups(TSV_PATH)
    out = build_html(groups)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(out)
    total = sum(len(g["items"]) for g in groups)
    print(f"생성 완료: {OUT_PATH}")
    print(f"  그룹 {len(groups)}개 / 문항 {total}개")


if __name__ == "__main__":
    main()
