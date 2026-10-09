
"""
Q10: Tkinter Assignment Tracker
Python 3.10+

Features:
- Add assignments
- Display assignments in a table
- Mark assignments as completed
- Delete assignments
- Save data in JSON format
- Export assignments to CSV
"""

import csv
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path


# Store data beside this Python file.
DATA_FILE = Path(__file__).resolve().parent / "assignments.json"

FIELDS = ["id", "title", "subject", "due_date", "status"]


class AssignmentTracker:
    """GUI application for managing assignments."""

    def __init__(self, root):
        self.root = root
        self.root.title("Assignment Tracker")
        self.root.geometry("900x550")
        self.root.minsize(700, 450)

        self.assignments = []
        self.next_id = 1

        self.title_var = tk.StringVar()
        self.subject_var = tk.StringVar()
        self.date_var = tk.StringVar()

        self.load_data()
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        """Create the application interface."""

        heading = ttk.Label(
            self.root,
            text="Assignment Tracker",
            font=("Arial", 20, "bold"),
        )
        heading.pack(pady=12)

        form = ttk.LabelFrame(
            self.root, text="Add New Assignment", padding=12
        )
        form.pack(fill="x", padx=15, pady=5)

        ttk.Label(form, text="Title:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            form, textvariable=self.title_var, width=24
        ).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Subject:").grid(
            row=0, column=2, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            form, textvariable=self.subject_var, width=20
        ).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Due Date (YYYY-MM-DD):").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            form, textvariable=self.date_var, width=24
        ).grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(
            form, text="Add Assignment", command=self.add_assignment
        ).grid(row=1, column=2, columnspan=2, padx=5, pady=5)

        table_frame = ttk.Frame(self.root, padding=10)
        table_frame.pack(fill="both", expand=True, padx=5)

        columns = ("ID", "Title", "Subject", "Due Date", "Status")

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        widths = {
            "ID": 55,
            "Title": 230,
            "Subject": 160,
            "Due Date": 130,
            "Status": 120,
        }

        for column in columns:
            self.table.heading(column, text=column)
            self.table.column(
                column,
                width=widths[column],
                anchor="center",
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview,
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        actions = ttk.Frame(self.root, padding=10)
        actions.pack(fill="x", padx=10, pady=5)

        ttk.Button(
            actions,
            text="Mark Completed",
            command=self.mark_completed,
        ).pack(side="left", padx=5)

        ttk.Button(
            actions,
            text="Delete Selected",
            command=self.delete_assignment,
        ).pack(side="left", padx=5)

        ttk.Button(
            actions,
            text="Export CSV",
            command=self.export_csv,
        ).pack(side="left", padx=5)

        ttk.Button(
            actions,
            text="Refresh",
            command=self.refresh_table,
        ).pack(side="left", padx=5)

        self.status_label = ttk.Label(
            self.root, text="Ready", anchor="w"
        )
        self.status_label.pack(fill="x", padx=15, pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.close_application)

    def load_data(self):
        """Load assignments from JSON if the file exists."""

        if not DATA_FILE.exists():
            return

        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("Invalid assignment data format.")

            loaded = []

            for item in data:
                if not isinstance(item, dict):
                    raise ValueError("Invalid assignment record.")

                if any(field not in item for field in FIELDS):
                    raise ValueError("Missing assignment fields.")

                if not isinstance(item["id"], int) or item["id"] < 1:
                    raise ValueError("Invalid assignment ID.")

                if not all(
                    isinstance(item[field], str)
                    for field in FIELDS
                    if field != "id"
                ):
                    raise ValueError("Invalid assignment field types.")

                datetime.strptime(item["due_date"], "%Y-%m-%d")

                if item["status"] not in ("Pending", "Completed"):
                    raise ValueError("Invalid assignment status.")

                loaded.append({
                    field: item[field] for field in FIELDS
                })

            ids = [item["id"] for item in loaded]

            if len(ids) != len(set(ids)):
                raise ValueError("Duplicate assignment IDs.")

            self.assignments = loaded
            self.next_id = max(ids, default=0) + 1

        except (OSError, json.JSONDecodeError, ValueError) as error:
            messagebox.showwarning(
                "Load Warning",
                f"Could not load saved assignments:\n{error}",
            )

    def save_data(self):
        """Save assignment records to JSON safely."""

        temporary_file = DATA_FILE.with_suffix(".tmp")

        try:
            with temporary_file.open(
                "w", encoding="utf-8"
            ) as file:
                json.dump(
                    self.assignments,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

            temporary_file.replace(DATA_FILE)
            return True

        except OSError as error:
            messagebox.showerror(
                "Save Error",
                f"Could not save assignments:\n{error}",
            )
            return False

    def add_assignment(self):
        """Validate and add a new assignment."""

        title = self.title_var.get().strip()
        subject = self.subject_var.get().strip()
        due_date = self.date_var.get().strip()

        if not title or not subject or not due_date:
            messagebox.showwarning(
                "Missing Information",
                "Please fill in all three fields.",
            )
            return

        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning(
                "Invalid Date",
                "Enter the date in YYYY-MM-DD format.",
            )
            return

        assignment = {
            "id": self.next_id,
            "title": title,
            "subject": subject,
            "due_date": due_date,
            "status": "Pending",
        }

        self.assignments.append(assignment)

        if not self.save_data():
            self.assignments.pop()
            return

        self.next_id += 1

        self.title_var.set("")
        self.subject_var.set("")
        self.date_var.set("")

        self.refresh_table()
        self.status_label.config(text="Assignment added successfully.")

    def selected_assignment(self):
        """Return the selected assignment or None."""

        selection = self.table.selection()

        if not selection:
            messagebox.showinfo(
                "Select Assignment",
                "Please select an assignment from the table.",
            )
            return None

        selected_id = int(selection[0])

        for assignment in self.assignments:
            if assignment["id"] == selected_id:
                return assignment

        return None

    def mark_completed(self):
        """Mark the selected assignment as completed."""

        assignment = self.selected_assignment()

        if assignment is None:
            return

        if assignment["status"] == "Completed":
            messagebox.showinfo(
                "Already Completed",
                "This assignment is already completed.",
            )
            return

        assignment["status"] = "Completed"

        if not self.save_data():
            assignment["status"] = "Pending"
            return

        self.refresh_table()
        self.status_label.config(text="Assignment marked completed.")

    def delete_assignment(self):
        """Delete the selected assignment."""

        assignment = self.selected_assignment()

        if assignment is None:
            return

        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Delete '{assignment['title']}'?",
        )

        if not confirmed:
            return

        self.assignments.remove(assignment)

        if not self.save_data():
            self.assignments.append(assignment)
            return

        self.refresh_table()
        self.status_label.config(text="Assignment deleted.")

    def refresh_table(self):
        """Refresh the table with saved records."""

        for item in self.table.get_children():
            self.table.delete(item)

        for assignment in sorted(
            self.assignments,
            key=lambda item: (item["due_date"], item["id"]),
        ):
            self.table.insert(
                "",
                "end",
                iid=str(assignment["id"]),
                values=(
                    assignment["id"],
                    assignment["title"],
                    assignment["subject"],
                    assignment["due_date"],
                    assignment["status"],
                ),
            )

        pending = sum(
            item["status"] == "Pending"
            for item in self.assignments
        )
        completed = len(self.assignments) - pending

        self.status_label.config(
            text=(
                f"Total: {len(self.assignments)} | "
                f"Pending: {pending} | Completed: {completed}"
            )
        )

    def export_csv(self):
        """Export assignment records to a CSV file."""

        if not self.assignments:
            messagebox.showinfo(
                "No Data", "Add an assignment before exporting."
            )
            return

        output_path = filedialog.asksaveasfilename(
            title="Export Assignments",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="assignments.csv",
        )

        if not output_path:
            return

        try:
            with open(
                output_path, "w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.DictWriter(file, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(self.assignments)

            messagebox.showinfo(
                "Export Successful",
                f"Assignments exported to:\n{output_path}",
            )

        except OSError as error:
            messagebox.showerror(
                "Export Error", str(error)
            )

    def close_application(self):
        """Save changes before closing the application."""

        if self.save_data():
            self.root.destroy()


def main():
    root = tk.Tk()
    AssignmentTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
