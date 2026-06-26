"""
task_manager.py
タスクのデータ管理（CRUD・JSONファイル永続化）
"""

import json
import os
from datetime import datetime

DATA_FILE = "tasks.json"


def _now() -> str:
    """現在日時を ISO 8601 形式の文字列で返す"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_tasks() -> list[dict]:
    """JSONファイルからタスク一覧を読み込む"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_tasks(tasks: list[dict]) -> None:
    """タスク一覧をJSONファイルに保存する"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def _next_id(tasks: list[dict]) -> int:
    """次のタスクIDを返す"""
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def add_task(title: str, description: str = "", priority: str = "中") -> dict:
    """タスクを追加して保存し、追加したタスクを返す"""
    tasks = load_tasks()
    now = _now()
    task = {
        "id": _next_id(tasks),
        "title": title,
        "description": description,
        "priority": priority,
        "status": "未完了",
        "created_at": now,
        "updated_at": now,
    }
    tasks.append(task)
    save_tasks(tasks)
    return task


def update_task(task_id: int, title: str, description: str, priority: str) -> bool:
    """指定IDのタスクを更新する。成功時 True を返す"""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = title
            task["description"] = description
            task["priority"] = priority
            task["updated_at"] = _now()
            save_tasks(tasks)
            return True
    return False


def toggle_status(task_id: int) -> bool:
    """指定IDのタスクの完了状態を切り替える。成功時 True を返す"""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "完了" if task["status"] == "未完了" else "未完了"
            task["updated_at"] = _now()
            save_tasks(tasks)
            return True
    return False


def delete_task(task_id: int) -> bool:
    """指定IDのタスクを削除する。成功時 True を返す"""
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        return False
    save_tasks(new_tasks)
    return True
