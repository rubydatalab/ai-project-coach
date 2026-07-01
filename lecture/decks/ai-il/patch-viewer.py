# -*- coding: utf-8 -*-
"""viewer.html 슬라이드 iframe에 스크립트·팝업 권한 추가.

build-viewer는 각 슬라이드를 sandbox="allow-same-origin"으로만 감싼다 → 슬라이드 안의
JS(명령어 '복사' 버튼)와 새 탭 링크(다운로드 링크)가 전부 막힌다. 이 스크립트가
allow-scripts·allow-popups를 더해 되살린다. **build-viewer를 돌린 뒤 매번 실행**한다(멱등).
실행: python patch-viewer.py
"""
import os

VIEWER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "viewer.html")
OLD = 'sandbox="allow-same-origin"'
NEW = 'sandbox="allow-same-origin allow-scripts allow-popups allow-popups-to-escape-sandbox"'

with open(VIEWER, encoding="utf-8") as f:
    s = f.read()

n = s.count(OLD)
if n:
    s = s.replace(OLD, NEW)
    with open(VIEWER, "w", encoding="utf-8") as f:
        f.write(s)
    print("patched %d slide iframe(s): copy buttons + links enabled" % n)
else:
    print("already patched (or nothing to patch)")
