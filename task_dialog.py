"""
task_dialog.py
タスク追加・編集用のモーダルダイアログ
"""

import tkinter as tk
from tkinter import ttk, messagebox

PRIORITIES = ["高", "中", "低"]


class TaskDialog(tk.Toplevel):
    """タスクの追加・編集を行うダイアログウィンドウ"""

    def __init__(self, parent, title: str = "タスク追加", task: dict | None = None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()  # モーダル化

        self.result: dict | None = None  # OK 時に結果を格納

        self._build_ui(task)
        self._center(parent)

    def _build_ui(self, task: dict | None) -> None:
        pad = {"padx": 10, "pady": 6}

        # タイトル
        tk.Label(self, text="タイトル *", anchor="w").grid(
            row=0, column=0, sticky="w", **pad
        )
        self.title_var = tk.StringVar(value=task["title"] if task else "")
        self.title_entry = tk.Entry(self, textvariable=self.title_var, width=40)
        self.title_entry.grid(row=0, column=1, **pad)

        # 詳細説明
        tk.Label(self, text="詳細説明", anchor="w").grid(
            row=1, column=0, sticky="nw", **pad
        )
        self.desc_text = tk.Text(self, width=40, height=5)
        self.desc_text.grid(row=1, column=1, **pad)
        if task:
            self.desc_text.insert("1.0", task.get("description", ""))

        # 優先度
        tk.Label(self, text="優先度", anchor="w").grid(
            row=2, column=0, sticky="w", **pad
        )
        self.priority_var = tk.StringVar(
            value=task["priority"] if task else "中"
        )
        priority_cb = ttk.Combobox(
            self,
            textvariable=self.priority_var,
            values=PRIORITIES,
            state="readonly",
            width=10,
        )
        priority_cb.grid(row=2, column=1, sticky="w", **pad)

        # ボタン
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="OK", width=10, command=self._on_ok).pack(
            side="left", padx=8
        )
        tk.Button(btn_frame, text="キャンセル", width=10, command=self.destroy).pack(
            side="left", padx=8
        )

        self.title_entry.focus_set()

    def _on_ok(self) -> None:
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("入力エラー", "タイトルは必須です。", parent=self)
            self.title_entry.focus_set()
            return

        self.result = {
            "title": title,
            "description": self.desc_text.get("1.0", "end-1c").strip(),
            "priority": self.priority_var.get(),
        }
        self.destroy()

    def _center(self, parent) -> None:
        """親ウィンドウの中央に配置する"""
        self.update_idletasks()
        pw = parent.winfo_rootx() + parent.winfo_width() // 2
        ph = parent.winfo_rooty() + parent.winfo_height() // 2
        w = self.winfo_width()
        h = self.winfo_height()
        self.geometry(f"+{pw - w // 2}+{ph - h // 2}")
