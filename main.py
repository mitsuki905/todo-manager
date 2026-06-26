"""
main.py
ToDoアプリ メインウィンドウ
"""

import tkinter as tk
from tkinter import ttk, messagebox

import task_manager as tm
from task_dialog import TaskDialog

# 優先度ごとの文字色
PRIORITY_COLORS = {
    "高": "#cc0000",
    "中": "#e07000",
    "低": "#007700",
}

COLUMNS = ("title", "priority", "created_at", "status")
COL_HEADERS = {
    "title": "タイトル",
    "priority": "優先度",
    "created_at": "作成日",
    "status": "状態",
}
COL_WIDTHS = {
    "title": 280,
    "priority": 70,
    "created_at": 140,
    "status": 80,
}


class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ToDoマネージャー")
        self.geometry("700x480")
        self.minsize(600, 400)

        self._build_ui()
        self._refresh()

    # ------------------------------------------------------------------ #
    #  UI 構築
    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        # ---- ツールバー ----
        toolbar = tk.Frame(self, bd=1, relief="raised")
        toolbar.pack(side="top", fill="x")

        tk.Button(
            toolbar, text="＋ 追加", width=10, command=self._on_add
        ).pack(side="left", padx=4, pady=4)
        tk.Button(
            toolbar, text="✔ 完了切替", width=12, command=self._on_toggle
        ).pack(side="left", padx=4, pady=4)
        tk.Button(
            toolbar, text="🗑 削除", width=10, command=self._on_delete
        ).pack(side="left", padx=4, pady=4)

        # ---- Treeview ----
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.tree = ttk.Treeview(
            frame, columns=COLUMNS, show="headings", selectmode="browse"
        )

        for col in COLUMNS:
            self.tree.heading(col, text=COL_HEADERS[col])
            self.tree.column(col, width=COL_WIDTHS[col], anchor="w")

        # 優先度ごとのタグ設定
        for priority, color in PRIORITY_COLORS.items():
            self.tree.tag_configure(priority, foreground=color)
        # 完了タスクは薄いグレー
        self.tree.tag_configure("完了", foreground="#999999")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # ダブルクリックで編集
        self.tree.bind("<Double-1>", lambda e: self._on_edit())

    # ------------------------------------------------------------------ #
    #  データ表示
    # ------------------------------------------------------------------ #
    def _refresh(self) -> None:
        """Treeview を最新データで再描画する"""
        # 選択中の task_id を記憶
        selected_id = self._selected_task_id()

        for row in self.tree.get_children():
            self.tree.delete(row)

        tasks = tm.load_tasks()
        restore_iid = None

        for task in tasks:
            created = task["created_at"][:10]  # YYYY-MM-DD のみ表示
            tag = "完了" if task["status"] == "完了" else task["priority"]
            iid = str(task["id"])
            self.tree.insert(
                "",
                "end",
                iid=iid,
                values=(task["title"], task["priority"], created, task["status"]),
                tags=(tag,),
            )
            if task["id"] == selected_id:
                restore_iid = iid

        # 選択を復元
        if restore_iid and self.tree.exists(restore_iid):
            self.tree.selection_set(restore_iid)
            self.tree.focus(restore_iid)

    def _selected_task_id(self) -> int | None:
        """現在選択中のタスクIDを返す。未選択時は None"""
        sel = self.tree.selection()
        if not sel:
            return None
        try:
            return int(sel[0])
        except ValueError:
            return None

    def _get_task_by_id(self, task_id: int) -> dict | None:
        tasks = tm.load_tasks()
        for t in tasks:
            if t["id"] == task_id:
                return t
        return None

    # ------------------------------------------------------------------ #
    #  操作ハンドラ
    # ------------------------------------------------------------------ #
    def _on_add(self) -> None:
        dlg = TaskDialog(self, title="タスク追加")
        self.wait_window(dlg)
        if dlg.result:
            tm.add_task(
                title=dlg.result["title"],
                description=dlg.result["description"],
                priority=dlg.result["priority"],
            )
            self._refresh()

    def _on_edit(self) -> None:
        task_id = self._selected_task_id()
        if task_id is None:
            messagebox.showinfo("情報", "編集するタスクを選択してください。")
            return
        task = self._get_task_by_id(task_id)
        if task is None:
            return

        dlg = TaskDialog(self, title="タスク編集", task=task)
        self.wait_window(dlg)
        if dlg.result:
            tm.update_task(
                task_id=task_id,
                title=dlg.result["title"],
                description=dlg.result["description"],
                priority=dlg.result["priority"],
            )
            self._refresh()

    def _on_toggle(self) -> None:
        task_id = self._selected_task_id()
        if task_id is None:
            messagebox.showinfo("情報", "完了切替するタスクを選択してください。")
            return
        tm.toggle_status(task_id)
        self._refresh()

    def _on_delete(self) -> None:
        task_id = self._selected_task_id()
        if task_id is None:
            messagebox.showinfo("情報", "削除するタスクを選択してください。")
            return
        task = self._get_task_by_id(task_id)
        if task is None:
            return
        if messagebox.askyesno(
            "削除確認", f"「{task['title']}」を削除しますか？"
        ):
            tm.delete_task(task_id)
            self._refresh()


# ------------------------------------------------------------------ #
#  エントリポイント
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
