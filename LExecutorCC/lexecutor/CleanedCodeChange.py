from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CleanedCodeChange:
    repo: str
    old_sha: str
    new_sha: str
    old_code: str
    new_code: str
    old_changed_lines: List[int]
    new_changed_lines: List[int]
