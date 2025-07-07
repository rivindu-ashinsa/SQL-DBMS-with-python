import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mariadb

class SimpleSQLGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SQL-DBMS with Python (GUI)")
        self.geometry("900x650")
        self.configure(bg="#1e1e1e")  # Dark background

        self.conn = None
        self.cur = None

        self.set_dark_theme()
        self.create_widgets()

    def set_dark_theme(self):
        style = ttk.Style(self)
        self.option_add("*Font", ("Segoe UI", 12))  # FIXED line
        style.theme_use("default")

        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff")
        style.configure("TEntry", fieldbackground="#2e2e2e", foreground="#ffffff")
        style.configure("TButton", background="#444", foreground="#ffffff")
        style.configure("TLabelframe", background="#1e1e1e", foreground="#ffffff")
        style.configure("TLabelframe.Label", background="#1e1e1e", foreground="#ffffff")
        style.configure("Treeview", background="#2e2e2e", fieldbackground="#2e2e2e", foreground="#ffffff")
        style.map("TButton", background=[("active", "#666")])

    def create_widgets(self):
        # Database connection frame
        conn_frame = ttk.LabelFrame(self, text="Database Connection", padding=10)
        conn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, sticky="w")
        self.host_entry = ttk.Entry(conn_frame, width=15)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1)

        ttk.Label(conn_frame, text="User:").grid(row=0, column=2, sticky="w")
        self.user_entry = ttk.Entry(conn_frame, width=12)
        self.user_entry.insert(0, "root")
        self.user_entry.grid(row=0, column=3)

        ttk.Label(conn_frame, text="Password:").grid(row=0, column=4, sticky="w")
        self.pw_entry = ttk.Entry(conn_frame, width=12, show="*")
        self.pw_entry.grid(row=0, column=5)

        ttk.Label(conn_frame, text="Database:").grid(row=0, column=6, sticky="w")
        self.db_entry = ttk.Entry(conn_frame, width=15)
        self.db_entry.grid(row=0, column=7)

        self.conn_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_db)
        self.conn_btn.grid(row=0, column=8, padx=5)

        # Query frame
        query_frame = ttk.LabelFrame(self, text="SQL Query", padding=10)
        query_frame.pack(fill="x", padx=10, pady=5)

        self.query_text = scrolledtext.ScrolledText(query_frame, height=5, font=("Consolas", 12), bg="#2e2e2e", fg="#ffffff", insertbackground="white")
        self.query_text.pack(fill="x", padx=5, pady=5)
        self.query_text.insert(tk.END, "SELECT * FROM ")

        self.run_btn = ttk.Button(query_frame, text="Run Query", command=self.run_query, state=tk.DISABLED)
        self.run_btn.pack(anchor="e", padx=5, pady=5)

        # Results frame
        results_frame = ttk.LabelFrame(self, text="Results", padding=10)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.result_table = ttk.Treeview(results_frame, show="headings")
        self.result_table.pack(fill="both", expand=True)

        # Status bar
        self.status = tk.Label(self, text="Not connected.", anchor="w", fg="white", bg="#1e1e1e", font=("Segoe UI", 10))
        self.status.pack(fill="x", side="bottom")

    def connect_db(self):
        host = self.host_entry.get()
        user = self.user_entry.get()
        pw = self.pw_entry.get()
        db = self.db_entry.get()
        try:
            self.conn = mariadb.connect(
                host=host,
                user=user,
                password=pw,
                database=db if db else None
            )
            self.cur = self.conn.cursor()
            self.status.config(text=f"Connected to {db} as {user}@{host}.")
            self.conn_btn.config(state=tk.DISABLED)
            self.run_btn.config(state=tk.NORMAL)
        except mariadb.Error as e:
            messagebox.showerror("Connection Error", str(e))
            self.status.config(text="Connection failed.")

    def run_query(self):
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a SQL query.")
            return
        try:
            self.cur.execute(query)
            if self.cur.description:  # SELECT or similar
                columns = [desc[0] for desc in self.cur.description]
                rows = self.cur.fetchall()
                self.display_results(columns, rows)
                self.status.config(text=f"Query OK. {len(rows)} row(s) returned.")
            else:  # DDL/DML
                self.conn.commit()
                self.display_results([], [])
                self.status.config(text="Query OK. Statement executed.")
        except mariadb.Error as e:
            messagebox.showerror("SQL Error", str(e))
            self.status.config(text="SQL Error.")

    def display_results(self, columns, rows):
        self.result_table.delete(*self.result_table.get_children())
        self.result_table["columns"] = columns
        for col in columns:
            self.result_table.heading(col, text=col)
            self.result_table.column(col, width=120, anchor="center")
        for row in rows:
            self.result_table.insert("", "end", values=row)

if __name__ == "__main__":
    app = SimpleSQLGui()
    app.mainloop()
