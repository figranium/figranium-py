"""Public type definitions for Figranium request and response payloads."""

from typing import Any, Dict, List, Literal, Mapping, MutableMapping, Optional, Sequence, TypedDict, Union

JsonPrimitive = Union[str, int, float, bool, None]
JsonValue = Union[JsonPrimitive, List["JsonValue"], Dict[str, "JsonValue"]]
JsonObject = Dict[str, JsonValue]
UnknownRecord = Dict[str, Any]

TaskMode = Literal["scrape", "agent", "headful"]
TaskOutcome = Literal["success", "error", "stopped", "crashed", "anti_bot"]
VariableType = Literal["string", "number", "boolean"]
ExtractionFormat = Literal["json", "csv"]
HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
CaptchaType = Literal["recaptcha_v2", "recaptcha_v3", "hcaptcha", "turnstile"]
CabinetItemStatus = Literal["pending", "uploaded"]
AiProvider = Literal["gemini", "openai", "claude", "ollama"]
Theme = Literal["dark", "light", "solarized-light", "solarized-dark"]


class TaskVariable(TypedDict, total=False):
    type: VariableType
    value: Any
    autoCreated: bool


class StealthConfig(TypedDict, total=False):
    allowTypos: bool
    idleMovements: bool
    overscroll: bool
    deadClicks: bool
    fatigue: bool
    naturalTyping: bool
    cursorGlide: bool
    randomizeClicks: bool


class Schedule(TypedDict, total=False):
    enabled: bool
    frequency: Literal["interval", "hourly", "daily", "weekly", "monthly"]
    intervalMinutes: int
    hour: int
    minute: int
    daysOfWeek: List[int]
    dayOfMonth: int
    cron: str
    lastRun: int
    lastRunStatus: TaskOutcome
    lastRunDurationMs: int
    nextRun: int


class TaskOutput(TypedDict, total=False):
    provider: Literal["baserow"]
    credentialId: str
    tableId: str
    onError: Literal["ignore", "fail"]


class Action(TypedDict, total=False):
    id: str
    type: str
    disabled: bool
    selector: str
    value: str
    typeMode: Literal["append", "replace"]
    key: str
    varName: str
    method: HttpMethod
    headers: str
    body: str
    conditionVar: str
    conditionVarType: VariableType
    conditionOp: str
    conditionValue: str
    captchaType: CaptchaType
    timeout: int
    cabinetId: str
    markAsUploaded: bool


class Task(TypedDict, total=False):
    id: str
    name: str
    description: str
    url: str
    mode: TaskMode
    wait: int
    selector: str
    rotateUserAgents: bool
    rotateProxies: bool
    rotateViewport: bool
    humanTyping: bool
    stealth: StealthConfig
    autoSolveCaptcha: bool
    actions: List[Action]
    variables: Dict[str, TaskVariable]
    schedule: Schedule
    output: TaskOutput
    extractionScript: str
    extractionFormat: ExtractionFormat
    includeHtml: bool
    includeShadowDom: bool
    disableRecording: bool
    statelessExecution: bool
    cabinetId: str
    versions: List["TaskVersion"]
    last_opened: int


class TaskSummary(TypedDict, total=False):
    id: str
    name: str
    description: str


class TaskVersion(TypedDict, total=False):
    id: str
    timestamp: int
    name: str
    mode: str


class ExecuteTaskOptions(TypedDict, total=False):
    variables: Dict[str, Any]
    taskVariables: Dict[str, Any]
    webhookUrl: str
    runId: str


class ExecutionResult(TypedDict, total=False):
    data: Any
    outcome: TaskOutcome
    success: bool
    error: str
    runId: str


class Execution(TypedDict, total=False):
    id: str
    timestamp: int
    method: str
    path: str
    status: str
    outcome: TaskOutcome
    durationMs: int
    source: str
    mode: str
    taskId: str
    taskName: str
    url: str
    result: Any


class Cabinet(TypedDict, total=False):
    id: str
    name: str
    isDefault: bool
    itemCount: int
    createdAt: int


class CabinetItem(TypedDict, total=False):
    id: str
    name: str
    kind: Literal["file", "zip", "folder"]
    status: CabinetItemStatus
    size: int
    createdAt: int


class Capture(TypedDict, total=False):
    name: str
    url: str
    size: int
    modified: int
    type: Literal["recording", "screenshot"]


class CredentialInput(TypedDict, total=False):
    name: str
    provider: Literal["baserow"]
    config: Dict[str, str]


class Credential(CredentialInput, total=False):
    id: str


class ProxyInput(TypedDict, total=False):
    server: str
    username: str
    password: str
    label: str
    isRotatingPool: bool
    estimatedPoolSize: int


class Proxy(ProxyInput, total=False):
    id: str
    isDefault: bool


class BrowserSession(TypedDict, total=False):
    sessionId: str
    status: str
    wsEndpoint: str


class SelectorCandidate(TypedDict, total=False):
    css: str
    xpath: str
    confidence: float


class HealthStatus(TypedDict, total=False):
    status: str
    version: str


class User(TypedDict, total=False):
    id: str
    name: str
    email: str


class RequestOptions(TypedDict, total=False):
    headers: Mapping[str, str]
    timeout: Optional[float]


class StreamEvent(TypedDict, total=False):
    data: Any
    raw: str
    event: str
    id: str
    retry: int


AiModels = Dict[AiProvider, str]
RuntimeVariables = Dict[str, Any]
Headers = Mapping[str, str]
MutableJsonObject = MutableMapping[str, Any]
StringSequence = Sequence[str]
