"""Helpers for constructing Figranium automation actions."""

import threading
import time
from typing import Any, Literal, Mapping, MutableMapping, Optional, cast

from .types import Action, CaptchaType, ClickType, HttpMethod

_sequence = 0
_sequence_lock = threading.Lock()


def variable(name: str) -> str:
    """Create a Figranium variable template such as ``{$query}``."""
    if not name.strip():
        raise ValueError("Variable name must not be empty")
    return "{$" + name + "}"


def _next_action_id(action_type: str) -> str:
    global _sequence
    with _sequence_lock:
        _sequence = (_sequence + 1) % (2**53 - 1)
        sequence = _sequence
    timestamp = _base36(int(time.time() * 1000))
    return f"act_{action_type}_{timestamp}_{_base36(sequence)}"


def _base36(value: int) -> str:
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    if value == 0:
        return "0"
    result = ""
    while value:
        value, remainder = divmod(value, 36)
        result = alphabet[remainder] + result
    return result


def action(input: Mapping[str, Any]) -> Action:
    """Copy an action mapping and add an ID when one is not supplied."""
    result: MutableMapping[str, Any] = dict(input)
    action_type = result.get("type")
    if not isinstance(action_type, str) or not action_type:
        raise ValueError("Action type must not be empty")
    result.setdefault("id", _next_action_id(action_type))
    return cast(Action, dict(result))


def _with_base(action_type: str, base: Optional[Mapping[str, Any]], **values: Any) -> Action:
    payload = {
        **(base or {}),
        "type": action_type,
        **{key: value for key, value in values.items() if value is not None},
    }
    return action(payload)


LiteralTypeMode = Literal["replace", "append"]


class Actions:
    """Factory methods for commonly used actions from ``AGENT_SPEC.md``."""

    def navigate(self, url: str, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("navigate", base, value=url)

    def click(self, selector: str, click_type: ClickType = "single", *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("click", base, selector=selector, clickType=None if click_type == "single" else click_type)

    def check(self, selector: str, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("check", base, selector=selector)

    def uncheck(self, selector: str, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("uncheck", base, selector=selector)

    def drag_and_drop(self, selector: str, target_selector: str, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("drag_and_drop", base, selector=selector, targetSelector=target_selector)

    def reload(self, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("reload", base)

    def select(self, selector: str, value: str, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("select", base, selector=selector, value=value)

    def type(self, selector: str, value: str, mode: LiteralTypeMode = "replace", *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("type", base, selector=selector, value=value, typeMode=mode)

    def wait(self, seconds: float, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("wait", base, value=str(seconds))

    def wait_for(self, selector: str, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("wait_selector", base, selector=selector)

    def press(self, key: str, selector: Optional[str] = None, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("press", base, key=key, selector=selector)

    def javascript(self, script: str, var_name: Optional[str] = None, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("javascript", base, value=script, varName=var_name)

    def hover(self, selector: str, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("hover", base, selector=selector)

    def screenshot(self, name: Optional[str] = None, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("screenshot", base, value=name)

    def set(self, var_name: str, value: str, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("set", base, varName=var_name, value=value)

    def merge(self, var_name: str, value: str, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("merge", base, varName=var_name, value=value)

    def get_content(self, selector: Optional[str] = None, var_name: Optional[str] = None, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("get_content", base, selector=selector, varName=var_name)

    def request(self, url: str, *, method: Optional[HttpMethod] = None, headers: Optional[str] = None, body: Optional[str] = None, var_name: Optional[str] = None, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("http_request", base, value=url, method=method, headers=headers, body=body, varName=var_name)

    def if_(self, condition: Mapping[str, Any], *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("if", base, **condition)

    def while_(self, condition: Mapping[str, Any], *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("while", base, **condition)

    def else_(self, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("else", base)

    def end(self, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("end", base)

    def do_nothing(self, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("do_nothing", base)

    def repeat(self, count: int, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("repeat", base, value=str(count))

    def stop(self, status: str = "success", *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("stop", base, value=status)

    def start(self, task_id: str, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("start", base, value=task_id)

    def solve_captcha(self, *, captcha_type: Optional[CaptchaType] = None, selector: Optional[str] = None, var_name: Optional[str] = None, timeout: Optional[int] = None, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("solve_captcha", base, captchaType=captcha_type, selector=selector, varName=var_name, timeout=timeout)

    def wait_for_captcha(self, *, captcha_type: Optional[CaptchaType] = None, selector: Optional[str] = None, var_name: Optional[str] = None, timeout: Optional[int] = None, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("wait_captcha", base, captchaType=captcha_type, selector=selector, varName=var_name, timeout=timeout)

    def upload(self, *, selector: Optional[str] = None, cabinet_id: Optional[str] = None, mark_as_uploaded: Optional[bool] = None, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("upload", base, selector=selector, cabinetId=cabinet_id, markAsUploaded=mark_as_uploaded)

    def finalize_uploads(self, *, base: Optional[Mapping[str, Any]] = None) -> Action:
        return _with_base("finalize_uploads", base)


actions = Actions()
