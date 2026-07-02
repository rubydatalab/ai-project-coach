"""PC 카카오톡(Windows 앱) 조작용 참고 구현.

이 파일은 "카카오톡 PC 도구 사용법" 스킬의 **참고 구현**이다.
공식 카카오 API가 아니라, 사람이 하듯 PC 카카오톡 앱 창을 직접 열고 읽고 답한다.
(DDadeA/pyautokakao 방식을 참고해, 실제 PC 카카오톡에서 검증한 창 조작 뼈대만 남겼다.)

AI 직원을 만들 때는 이 파일을 그대로 쓰거나, 채팅방 이름·판단 로직만 얹어 쓴다.
반품 처리/응대 문구 같은 **업무 판단은 여기 넣지 않는다** — 그건 직원의 업무지침이 정한다.

의존성: pywin32  (설치: pip install pywin32)
전제: 사장님이 PC 카카오톡을 켜서 직접 로그인해 둔 상태. (로그인·비밀번호는 사람이 한다.)

명령 예시:
  python kakaotalk_pc.py --status
  python kakaotalk_pc.py --room "거래처방" --read
  python kakaotalk_pc.py --room "거래처방" --result 2 --read      # 같은 이름 2번째 결과
  python kakaotalk_pc.py --room "거래처방" --message "확인했습니다" --write   # 입력칸에 써만 놓음(안 보냄)
  python kakaotalk_pc.py --room "거래처방" --message "확인했습니다" --send    # 실제 전송

안전 규칙(스킬과 동일):
- 기본은 --write(입력칸에 써놓기)까지만. **실제 전송은 --send를 명시했을 때만** 한다.
- --send 뒤에는 --read로 다시 읽어 내 메시지가 기록에 남았는지 확인한다.
"""

import argparse
import ctypes
import json
import sys
import time

import win32api
import win32clipboard
import win32con
import win32gui
from win32api import MAKELONG, SendMessage


# --- 기본 대기/창 찾기 유틸 ---------------------------------------------------

def wait(seconds: float = 0.4) -> None:
    time.sleep(seconds)


def find_window(title: str) -> int:
    return win32gui.FindWindow(None, title)


def find_child(parent: int, class_name: str, after: int = 0) -> int:
    return win32gui.FindWindowEx(parent, after, class_name, None)


def enum_visible_windows() -> list:
    windows = []

    def callback(hwnd: int, _extra: object) -> bool:
        title = win32gui.GetWindowText(hwnd)
        if title and win32gui.IsWindowVisible(hwnd):
            windows.append((hwnd, title))
        return True

    win32gui.EnumWindows(callback, None)
    return windows


# --- 텍스트/클립보드 ----------------------------------------------------------

def set_text(hwnd: int, text: str) -> None:
    # WM_SETTEXT: 입력칸에 글자를 "써놓기"만 한다. (초안 용도)
    # 주의: 이 방식으로 넣고 PostMessage Enter만 보내면 실제 전송 기록에 안 남는 경우가 있다.
    #       그래서 실제 전송은 아래 send_reply()의 클립보드 붙여넣기 + 진짜 Enter로만 한다.
    SendMessage(hwnd, win32con.WM_SETTEXT, 0, text)


def get_clipboard_text() -> str:
    win32clipboard.OpenClipboard()
    try:
        if not win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            return ""
        return win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()


def set_clipboard_text(text: str) -> None:
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()


# --- 키 입력 ------------------------------------------------------------------

def press_key(hwnd: int, key: int, seconds: float = 0.02) -> None:
    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, key, 0)
    time.sleep(seconds)
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, key, 0)


PBYTE256 = ctypes.c_ubyte * 256
USER32 = ctypes.WinDLL("user32")
GetKeyboardState = USER32.GetKeyboardState
SetKeyboardState = USER32.SetKeyboardState
GetWindowThreadProcessId = USER32.GetWindowThreadProcessId
AttachThreadInput = USER32.AttachThreadInput
MapVirtualKeyA = USER32.MapVirtualKeyA


def press_with_ctrl(hwnd: int, key: int) -> None:
    """Ctrl+<key>를 특정 창에 보낸다. (Ctrl+A, Ctrl+C로 대화 긁기용)

    카카오톡 대화 목록은 포커스를 줘야 Ctrl 조합이 먹어서, 스레드 입력 상태를
    잠시 붙였다(AttachThreadInput) 떼는 방식으로 Ctrl 눌림 상태를 만들어 보낸다.
    """
    if not win32gui.IsWindow(hwnd):
        raise RuntimeError("카카오톡 대화 영역을 찾지 못했습니다.")

    thread_id = GetWindowThreadProcessId(hwnd, None)
    current_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
    old_state = PBYTE256()
    new_state = PBYTE256()
    lparam = MAKELONG(0, MapVirtualKeyA(key, 0))

    SendMessage(hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
    AttachThreadInput(current_thread_id, thread_id, True)
    GetKeyboardState(ctypes.byref(old_state))
    new_state[win32con.VK_CONTROL] |= 128
    SetKeyboardState(ctypes.byref(new_state))
    wait(0.03)
    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, key, lparam)
    wait(0.03)
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, key, lparam | 0xC0000000)
    wait(0.03)
    SetKeyboardState(ctypes.byref(old_state))
    AttachThreadInput(current_thread_id, thread_id, False)


def real_key(key: int) -> None:
    """실제 키보드 이벤트. (전송용 진짜 Enter 등)"""
    win32api.keybd_event(key, 0, 0, 0)
    wait(0.05)
    win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)


def click_center(hwnd: int) -> None:
    """창(컨트롤) 정중앙을 실제 마우스로 클릭한다. (입력칸 포커스 주기)"""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    x = (left + right) // 2
    y = (top + bottom) // 2
    win32api.SetCursorPos((x, y))
    wait(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    wait(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


# --- 채팅방 열기 --------------------------------------------------------------

def find_chat_window(room_name: str, before_handles: set = None) -> int:
    exact = find_window(room_name)
    if exact:
        return exact

    before_handles = before_handles or set()
    for hwnd, title in enum_visible_windows():
        if hwnd in before_handles:
            continue
        if room_name in title:
            return hwnd

    for hwnd, title in enum_visible_windows():
        if room_name in title:
            return hwnd
    return 0


def open_chat(room_name: str, result_index: int = 1) -> int:
    """PC 카카오톡에서 채팅방을 검색해 연다.

    result_index: 같은 이름의 검색 결과가 여러 개일 때 몇 번째를 열지. 첫 번째=1, 두 번째=2.
    """
    kakao = find_window("카카오톡")
    if not kakao:
        raise RuntimeError("PC 카카오톡 창을 찾지 못했습니다. 카카오톡을 먼저 켜주세요.")

    press_with_ctrl(kakao, ord("F"))  # 검색창 열기
    wait(0.5)

    child = find_child(kakao, "EVA_ChildWindow")
    search_area_1 = find_child(child, "EVA_Window")
    search_area_2 = find_child(child, "EVA_Window", search_area_1)
    search_box = find_child(search_area_2, "Edit")
    if not search_box:
        raise RuntimeError("카카오톡 검색창을 찾지 못했습니다. PC 카카오톡 화면 구성이 달라졌을 수 있습니다.")

    before_handles = {hwnd for hwnd, _title in enum_visible_windows()}

    set_text(search_box, room_name)
    wait(0.8)

    for _ in range(max(0, result_index - 1)):  # 검색 결과에서 아래로 이동
        press_key(search_box, win32con.VK_DOWN)
        wait(0.15)

    press_key(search_box, win32con.VK_RETURN)  # 채팅방 열기
    wait(1.0)
    set_text(search_box, "")

    chat = find_chat_window(room_name, before_handles=before_handles)
    if not chat:
        titles = [title for _hwnd, title in enum_visible_windows() if room_name in title]
        detail = f" 열린 창 후보: {titles}" if titles else ""
        raise RuntimeError(f"'{room_name}' 채팅방을 열지 못했습니다.{detail}")
    return chat


def find_message_list(chat_hwnd: int) -> int:
    message_list = find_child(chat_hwnd, "EVA_VH_ListControl_Dblclk")
    if not message_list:
        raise RuntimeError("채팅 메시지 목록을 찾지 못했습니다.")
    return message_list


def find_input_box(chat_hwnd: int) -> int:
    edit = find_child(chat_hwnd, "RICHEDIT50W")
    if not edit:
        raise RuntimeError("답장 입력칸을 찾지 못했습니다.")
    return edit


# --- 읽기 / 답장 --------------------------------------------------------------

def read_chat(room_name: str, close_after: bool = False, result_index: int = 1) -> str:
    """채팅방을 열어 대화 내용 전체를 Ctrl+A/Ctrl+C로 긁어 문자열로 돌려준다."""
    chat = open_chat(room_name, result_index=result_index)
    message_list = find_message_list(chat)
    wait(0.5)
    press_with_ctrl(message_list, ord("A"))
    wait(0.2)
    press_with_ctrl(message_list, ord("C"))
    wait(0.4)
    text = get_clipboard_text()
    if close_after:
        win32gui.PostMessage(chat, win32con.WM_CLOSE, 0, 0)
    return text


def draft_reply(room_name: str, text: str, result_index: int = 1) -> None:
    """입력칸에 답장을 '써만' 놓는다. 전송하지 않는다. (사람이 눈으로 확인하는 단계)"""
    chat = open_chat(room_name, result_index=result_index)
    edit = find_input_box(chat)
    set_text(edit, text)
    wait(0.2)


def send_reply(room_name: str, text: str, result_index: int = 1) -> None:
    """실제 전송. 반드시 이 방식으로만 보낸다.

    검증 결과: WM_SETTEXT + PostMessage Enter는 함수는 성공해도 실제 기록에 안 남을 수 있다.
    그래서 (1) 채팅창을 앞으로 (2) 입력칸 클릭 (3) 클립보드 붙여넣기 (4) 진짜 Enter 순서로 보낸다.
    """
    chat = open_chat(room_name, result_index=result_index)
    edit = find_input_box(chat)

    win32gui.ShowWindow(chat, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(chat)
    wait(0.4)
    click_center(edit)
    wait(0.2)
    set_clipboard_text(text)
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    real_key(ord("V"))
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    wait(0.3)
    real_key(win32con.VK_RETURN)
    wait(0.3)


def status() -> dict:
    kakao = find_window("카카오톡")
    return {
        "kakaotalk_running": bool(kakao),
        "kakaotalk_window_handle": kakao,
        "kakao_related_windows": [
            {"handle": hwnd, "title": title}
            for hwnd, title in enum_visible_windows()
            if "카카오톡" in title
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="PC 카카오톡 메시지 읽기/답장 도구 (참고 구현)")
    parser.add_argument("--room", help="채팅방 이름")
    parser.add_argument("--result", type=int, default=1,
                        help="같은 이름 검색 결과에서 열 순서. 첫 번째=1, 두 번째=2")
    parser.add_argument("--status", action="store_true", help="PC 카카오톡 실행/연결 상태 확인")
    parser.add_argument("--read", action="store_true", help="채팅방 대화 읽기")
    parser.add_argument("--message", help="입력칸에 넣을 문장")
    parser.add_argument("--write", action="store_true", help="입력칸에 써만 놓기(전송 안 함)")
    parser.add_argument("--send", action="store_true", help="실제 전송 (사람이 명시할 때만)")
    parser.add_argument("--close", action="store_true", help="읽은 뒤 채팅창 닫기")
    args = parser.parse_args()

    if args.status:
        print(json.dumps(status(), ensure_ascii=False, indent=2))
        return 0

    if args.read:
        if not args.room:
            raise RuntimeError("--room 으로 채팅방 이름을 지정하세요.")
        print(read_chat(args.room, close_after=args.close, result_index=args.result))
        return 0

    if args.message is not None:
        if not args.room:
            raise RuntimeError("--room 으로 채팅방 이름을 지정하세요.")
        if args.send:
            send_reply(args.room, args.message, result_index=args.result)
        else:
            # 기본은 써놓기만 한다. --send 없으면 절대 전송하지 않는다.
            draft_reply(args.room, args.message, result_index=args.result)
        print(json.dumps(
            {"room": args.room, "message": args.message,
             "written": True, "sent": bool(args.send)},
            ensure_ascii=False, indent=2))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1)
