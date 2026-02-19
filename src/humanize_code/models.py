from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class Issue:
    code: str
    severity: str
    message: str
    line: int | None = None
    suggestion: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class FileReport:
    path: str
    score: int
    issues: list[Issue] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "score": self.score,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass
class RewriteResult:
    path: str
    changed: bool
    original: str
    rewritten: str
    change_count: int

