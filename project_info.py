"""Thông tin chính thức của nhóm thực hiện dự án ShorLab."""
from __future__ import annotations

PROJECT_NAME = "ShorLab"
COURSE_NAME = "Mật mã nâng cao"

TEAM = [
    {
        "name": "Dương Công Kiên",
        "student_id": "B25CHKH072",
        "role": "Nhóm trưởng",
    },
    {
        "name": "Nguyễn Cảnh Huỳnh",
        "student_id": "B25CHKH071",
        "role": "Thành viên",
    },
    {
        "name": "Phạm Anh Tuấn",
        "student_id": "B25CHKH086",
        "role": "Thành viên",
    },
]

TEAM_LEADER = TEAM[0]


def team_to_dict() -> list[dict[str, str]]:
    """Trả về bản sao thông tin nhóm để dùng trong API và tệp kết quả."""
    return [dict(member) for member in TEAM]


def member_label(member: dict[str, str]) -> str:
    """Định dạng họ tên và mã học viên trên một dòng."""
    return f"{member['name']} - {member['student_id']}"


def team_display(separator: str = " | ") -> str:
    """Chuỗi hiển thị đầy đủ danh sách thành viên."""
    return separator.join(member_label(member) for member in TEAM)
