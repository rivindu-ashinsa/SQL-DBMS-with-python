from __future__ import annotations

import os
import re
from typing import Iterable

import mariadb
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from dbms.connection import get_connection
from dbms.ddl import create_database, create_table, drop_table, list_databases, list_tables
from dbms.dml import delete_row, execute_sql, fetch_rows, insert_row, update_row


BG = (0.05, 0.06, 0.09, 1)
PANEL = (0.09, 0.11, 0.16, 1)
PANEL_ALT = (0.12, 0.14, 0.2, 1)
PANEL_DEEP = (0.07, 0.08, 0.12, 1)
ACCENT = (0.17, 0.75, 0.58, 1)
ACCENT_SOFT = (0.17, 0.75, 0.58, 0.14)
TEXT = (0.96, 0.98, 1, 1)
MUTED = (0.67, 0.72, 0.8, 1)
ERROR = (0.95, 0.35, 0.35, 1)

TYPE_OPTIONS = (
    "INT",
    "BIGINT",
    "SMALLINT",
    "VARCHAR",
    "TEXT",
    "DATE",
    "DATETIME",
    "TIMESTAMP",
    "DECIMAL",
    "FLOAT",
    "DOUBLE",
    "BOOLEAN",
)

SIZE_RECOMMENDED_TYPES = {"VARCHAR", "DECIMAL", "CHAR"}
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def parse_key_value_lines(raw_text: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if "=" not in stripped:
            raise ValueError("Each line must use the format column=value.")
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError("Column names cannot be empty.")
        entries[key] = value
    if not entries:
        raise ValueError("Enter at least one column=value pair.")
    return entries


class Card(BoxLayout):
    def __init__(self, **kwargs):
        background_color = kwargs.pop("background_color", PANEL)
        super().__init__(**kwargs)
        self.padding = dp(16)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        with self.canvas.before:
            from kivy.graphics import Color, Line, RoundedRectangle

            self._bg_color = Color(rgba=background_color)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
            self._line_color = Color(rgba=(1, 1, 1, 0.05))
            self._border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(18)), width=1)
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *_args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(18))


class CellLabel(BoxLayout):
    def __init__(self, text: str, header: bool = False, **kwargs):
        background_color = kwargs.pop("background_color", PANEL_ALT if header else PANEL_DEEP)
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(38)
        self.padding = (dp(10), dp(6))
        with self.canvas.before:
            from kivy.graphics import Color, Line, RoundedRectangle

            self._bg_color = Color(rgba=background_color)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            self._line_color = Color(rgba=(1, 1, 1, 0.05))
            self._border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)), width=1)
        self.bind(pos=self._update_canvas, size=self._update_canvas)

        label = Label(
            text=text,
            color=TEXT,
            bold=header,
            halign="left",
            valign="middle",
        )
        label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        self.add_widget(label)

    def _update_canvas(self, *_args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(10))


def create_field(label_text: str, hint_text: str = "", *, multiline: bool = False, password: bool = False, height: int = 42):
    container = BoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None)
    container.bind(minimum_height=container.setter("height"))
    container.add_widget(
        Label(
            text=label_text,
            color=TEXT,
            size_hint_y=None,
            height=dp(18),
            halign="left",
            valign="middle",
        )
    )
    field = TextInput(
        hint_text=hint_text,
        multiline=multiline,
        password=password,
        background_color=PANEL_DEEP,
        foreground_color=TEXT,
        cursor_color=ACCENT,
        padding=(dp(10), dp(10)),
        size_hint_y=None,
        height=dp(height),
    )
    container.add_widget(field)
    return container, field


def create_spacer(height: int = 8):
    spacer = BoxLayout(size_hint_y=None, height=dp(height))
    return spacer


class ResultPanel(Card):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", background_color=PANEL)
        self.title = Label(
            text="Results",
            color=TEXT,
            bold=True,
            size_hint_y=None,
            height=dp(24),
            halign="left",
            valign="middle",
        )
        self.title.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        self.summary = Label(
            text="No query has been run yet.",
            color=MUTED,
            size_hint_y=None,
            height=dp(22),
            halign="left",
            valign="middle",
        )
        self.summary.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        self.scroll = ScrollView(do_scroll_x=True, do_scroll_y=True)
        self.scroll.size_hint_y = None
        self.scroll.height = dp(200)
        self.grid = GridLayout(cols=1, spacing=dp(1), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)

        self.add_widget(self.title)
        self.add_widget(self.summary)
        self.add_widget(self.scroll)
        self.show_message("Connect to a local MariaDB server to begin.")

    def show_message(self, message: str):
        self.summary.text = message
        self.grid.cols = 1
        self.grid.height = dp(38)
        self.grid.clear_widgets()
        self.grid.add_widget(CellLabel("No tabular output to display."))

    def show_rows(self, columns: Iterable[str], rows: Iterable[Iterable[object]], summary: str):
        columns = list(columns)
        rows = list(rows)
        self.summary.text = summary
        self.grid.clear_widgets()

        if not columns:
            self.grid.cols = 1
            self.grid.height = dp(38)
            self.grid.add_widget(CellLabel("Statement completed successfully."))
            return

        self.grid.cols = len(columns)
        total_rows = len(rows) + 1
        self.grid.height = dp(38) * total_rows
        for column_name in columns:
            self.grid.add_widget(CellLabel(str(column_name), header=True))
        for row in rows:
            for value in row:
                self.grid.add_widget(CellLabel("NULL" if value is None else str(value)))


class BaseScreen(Screen):
    def __init__(self, root_widget, **kwargs):
        super().__init__(**kwargs)
        self.root_widget = root_widget
        outer = ScrollView(do_scroll_x=False, do_scroll_y=True)
        self.content = BoxLayout(orientation="vertical", spacing=dp(14), padding=(0, 0, 0, dp(12)), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))
        outer.add_widget(self.content)
        self.add_widget(outer)

    def section_card(self, title_text: str, subtitle_text: str | None = None):
        card = Card(orientation="vertical", background_color=PANEL)
        header = Label(
            text=title_text,
            color=TEXT,
            bold=True,
            size_hint_y=None,
            height=dp(24),
            halign="left",
            valign="middle",
        )
        header.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        card.add_widget(header)
        if subtitle_text:
            subtitle = Label(
                text=subtitle_text,
                color=MUTED,
                size_hint_y=None,
                height=dp(20),
                halign="left",
                valign="middle",
            )
            subtitle.bind(size=lambda instance, value: setattr(instance, "text_size", value))
            card.add_widget(subtitle)
        return card

    def action_button(self, text: str, on_press):
        button = Button(
            text=text,
            size_hint_y=None,
            height=dp(42),
            background_normal="",
            background_color=ACCENT,
            color=(0.03, 0.07, 0.05, 1),
            bold=True,
        )
        button.bind(on_release=on_press)
        return button


class DashboardScreen(BaseScreen):
    def __init__(self, root_widget, **kwargs):
        super().__init__(root_widget, name="dashboard", **kwargs)

        card = self.section_card("Local Connection", "Connect to the MariaDB instance running on your machine.")
        host_section, self.host_field = create_field("Host", "localhost")
        user_section, self.user_field = create_field("User", "root")
        password_section, self.password_field = create_field("Password", "Optional", password=True)
        database_section, self.database_field = create_field("Database", "Leave blank to connect to the server")

        self.host_field.text = os.getenv("DB_HOST", "localhost")
        self.user_field.text = os.getenv("DB_USER", "root")
        self.password_field.text = os.getenv("DB_PASS", "")
        self.database_field.text = os.getenv("DB_NAME", "")

        card.add_widget(host_section)
        card.add_widget(user_section)
        card.add_widget(password_section)
        card.add_widget(database_section)
        card.add_widget(self.action_button("Connect", self.connect))
        self.content.add_widget(card)

        overview = self.section_card("Database Overview", "All databases visible from this local server.")
        self.active_database_label = Label(
            text="Active database: (none)",
            color=TEXT,
            bold=True,
            size_hint_y=None,
            height=dp(22),
            halign="left",
            valign="middle",
        )
        self.active_database_label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        overview.add_widget(self.active_database_label)

        self.database_scroll = ScrollView(do_scroll_x=False, do_scroll_y=True, size_hint_y=None, height=dp(190))
        self.database_grid = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)
        self.database_grid.bind(minimum_height=self.database_grid.setter("height"))
        self.database_scroll.add_widget(self.database_grid)
        overview.add_widget(self.database_scroll)

        button_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(10))
        button_row.add_widget(self.action_button("Refresh Databases", self.root_widget.refresh_database_lists))
        button_row.add_widget(self.action_button("Refresh Tables", self.root_widget.refresh_table_lists))
        overview.add_widget(button_row)
        self.content.add_widget(overview)

        guide = self.section_card("Quick Guide")
        guide.add_widget(
            Label(
                text=(
                    "Use the DDL tab to create databases and tables, the DML tab to insert/update/delete rows, "
                    "and the SQL tab for custom queries. The table builder in DDL lets you create columns using "
                    "drop-down selections for data type, nullability, and key behavior."
                ),
                color=MUTED,
                halign="left",
                valign="top",
                text_size=(dp(720), None),
                size_hint_y=None,
                height=dp(90),
            )
        )
        self.content.add_widget(guide)

    def refresh_databases(self, database_names: list[str], active_database: str | None):
        active_text = active_database if active_database else "(server-level connection)"
        self.active_database_label.text = f"Active database: {active_text}"
        self.database_grid.clear_widgets()
        if not database_names:
            self.database_grid.add_widget(CellLabel("No databases found."))
            return

        for name in database_names:
            marker = " [active]" if active_database and name == active_database else ""
            self.database_grid.add_widget(CellLabel(f"{name}{marker}"))

    def connect(self, *_args):
        self.root_widget.connect_to_database(
            host=self.host_field.text,
            user=self.user_field.text,
            password=self.password_field.text,
            database=self.database_field.text,
        )


class ColumnFormRow(Card):
    def __init__(self, on_remove, **kwargs):
        super().__init__(orientation="vertical", background_color=PANEL_DEEP, **kwargs)
        self.on_remove = on_remove

        top = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        self.column_name = TextInput(
            hint_text="Column name",
            multiline=False,
            background_color=PANEL_ALT,
            foreground_color=TEXT,
            cursor_color=ACCENT,
        )
        self.data_type = Spinner(text="VARCHAR", values=TYPE_OPTIONS, size_hint_x=0.42)
        self.size_value = TextInput(
            hint_text="Size (optional)",
            multiline=False,
            background_color=PANEL_ALT,
            foreground_color=TEXT,
            cursor_color=ACCENT,
            size_hint_x=0.36,
        )
        remove_button = Button(
            text="Remove",
            size_hint_x=0.22,
            background_normal="",
            background_color=(0.78, 0.25, 0.31, 1),
            color=TEXT,
            bold=True,
        )
        remove_button.bind(on_release=self._remove)

        top.add_widget(self.column_name)
        top.add_widget(self.data_type)
        top.add_widget(self.size_value)
        top.add_widget(remove_button)

        bottom = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        self.null_mode = Spinner(text="NOT NULL", values=("NOT NULL", "NULL"), size_hint_x=0.30)
        self.key_mode = Spinner(text="NONE", values=("NONE", "PRIMARY KEY", "UNIQUE"), size_hint_x=0.30)
        self.extra_mode = Spinner(text="NONE", values=("NONE", "AUTO_INCREMENT"), size_hint_x=0.30)
        self.default_value = TextInput(
            hint_text="Default (optional)",
            multiline=False,
            background_color=PANEL_ALT,
            foreground_color=TEXT,
            cursor_color=ACCENT,
            size_hint_x=0.42,
        )

        bottom.add_widget(self.null_mode)
        bottom.add_widget(self.key_mode)
        bottom.add_widget(self.extra_mode)
        bottom.add_widget(self.default_value)

        self.add_widget(top)
        self.add_widget(bottom)

    def _remove(self, *_args):
        self.on_remove(self)

    def to_sql_fragment(self):
        name = self.column_name.text.strip()
        data_type = self.data_type.text.strip().upper()
        size = self.size_value.text.strip()
        null_mode = self.null_mode.text.strip().upper()
        key_mode = self.key_mode.text.strip().upper()
        extra_mode = self.extra_mode.text.strip().upper()
        default_value = self.default_value.text.strip()

        if not name:
            raise ValueError("Each column needs a name.")
        if not IDENTIFIER_RE.match(name):
            raise ValueError(f"Invalid column name: {name}")

        parts = [f"`{name}`", data_type]
        if size:
            parts[-1] = f"{data_type}({size})"
        elif data_type in SIZE_RECOMMENDED_TYPES:
            raise ValueError(f"Column '{name}' should include a size for {data_type}.")

        parts.append(null_mode)
        if key_mode != "NONE":
            parts.append(key_mode)
        if extra_mode != "NONE":
            parts.append(extra_mode)

        if default_value:
            if default_value.upper().startswith("CURRENT_") or default_value.isdigit():
                parts.append(f"DEFAULT {default_value}")
            else:
                escaped = default_value.replace("'", "''")
                parts.append(f"DEFAULT '{escaped}'")

        return " ".join(parts)


class DDLScreen(BaseScreen):
    def __init__(self, root_widget, **kwargs):
        super().__init__(root_widget, name="ddl", **kwargs)

        create_db = self.section_card("Create Database", "Create a local database on the connected server.")
        db_section, self.database_name_field = create_field("Database name", "analytics")
        create_db.add_widget(db_section)
        create_db.add_widget(self.action_button("Create Database", self.create_database))
        self.content.add_widget(create_db)

        create_table_card = self.section_card("Create Table", "Build table columns using dropdowns and structured inputs.")
        table_section, self.table_name_field = create_field("Table name", "customers")
        self.column_rows: list[ColumnFormRow] = []
        self.columns_host = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.columns_host.bind(minimum_height=self.columns_host.setter("height"))
        self.columns_scroll = ScrollView(do_scroll_x=False, do_scroll_y=True, size_hint_y=None, height=dp(280))
        self.columns_scroll.add_widget(self.columns_host)

        button_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(10))
        button_row.add_widget(self.action_button("Add Column", self.add_column_row))
        button_row.add_widget(self.action_button("Reset Columns", self.reset_columns))

        create_table_card.add_widget(table_section)
        create_table_card.add_widget(button_row)
        create_table_card.add_widget(self.columns_scroll)
        create_table_card.add_widget(self.action_button("Create Table", self.create_table))
        self.content.add_widget(create_table_card)

        self.add_column_row()
        self.add_column_row()

        drop_card = self.section_card("Drop Table", "Remove a table from the current database.")
        self.drop_spinner = Spinner(text="Select table", values=(), size_hint_y=None, height=dp(42))
        drop_card.add_widget(self.drop_spinner)
        drop_card.add_widget(self.action_button("Drop Table", self.drop_selected_table))
        self.content.add_widget(drop_card)

    def refresh_tables(self, table_names: list[str]):
        values = tuple(table_names)
        self.drop_spinner.values = values
        if values:
            self.drop_spinner.text = values[0]
        else:
            self.drop_spinner.text = "Select table"

    def create_database(self, *_args):
        self.root_widget.create_database_action(self.database_name_field.text)

    def add_column_row(self, *_args):
        row = ColumnFormRow(self.remove_column_row)
        self.column_rows.append(row)
        self.columns_host.add_widget(row)

    def remove_column_row(self, row: ColumnFormRow):
        if len(self.column_rows) <= 1:
            self.root_widget.report_error("Table form", "At least one column is required.")
            return
        self.column_rows.remove(row)
        self.columns_host.remove_widget(row)

    def reset_columns(self, *_args):
        self.columns_host.clear_widgets()
        self.column_rows = []
        self.add_column_row()
        self.add_column_row()

    def create_table(self, *_args):
        self.root_widget.create_table_from_form_action(self.table_name_field.text, self.column_rows)

    def drop_selected_table(self, *_args):
        self.root_widget.drop_table_action(self.drop_spinner.text)


class DMLScreen(BaseScreen):
    def __init__(self, root_widget, **kwargs):
        super().__init__(root_widget, name="dml", **kwargs)

        browse_card = self.section_card("Browse Table", "Pick a table and preview the current rows.")
        self.browse_spinner = Spinner(text="Select table", values=(), size_hint_y=None, height=dp(42))
        browse_card.add_widget(self.browse_spinner)
        browse_buttons = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(10))
        browse_buttons.add_widget(self.action_button("Refresh Tables", self.root_widget.refresh_table_lists))
        browse_buttons.add_widget(self.action_button("Browse", self.browse_selected_table))
        browse_card.add_widget(browse_buttons)
        self.content.add_widget(browse_card)

        insert_card = self.section_card("Insert Row", "Provide one column=value pair per line.")
        self.insert_spinner = Spinner(text="Select table", values=(), size_hint_y=None, height=dp(42))
        self.insert_values_field = TextInput(
            hint_text="name=Grace\nage=29",
            multiline=True,
            background_color=PANEL_DEEP,
            foreground_color=TEXT,
            cursor_color=ACCENT,
            padding=(dp(10), dp(10)),
            size_hint_y=None,
            height=dp(120),
        )
        insert_card.add_widget(self.insert_spinner)
        insert_card.add_widget(self.insert_values_field)
        insert_card.add_widget(self.action_button("Insert Row", self.insert_row))
        self.content.add_widget(insert_card)

        update_card = self.section_card("Update Row", "Select the matching key column and provide new values.")
        self.update_spinner = Spinner(text="Select table", values=(), size_hint_y=None, height=dp(42))
        key_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(10))
        self.key_column_field = TextInput(hint_text="Key column", background_color=PANEL_DEEP, foreground_color=TEXT, cursor_color=ACCENT, size_hint_y=None, height=dp(42))
        self.key_value_field = TextInput(hint_text="Key value", background_color=PANEL_DEEP, foreground_color=TEXT, cursor_color=ACCENT, size_hint_y=None, height=dp(42))
        key_row.add_widget(self.key_column_field)
        key_row.add_widget(self.key_value_field)
        self.update_values_field = TextInput(
            hint_text="status=active\nscore=95",
            multiline=True,
            background_color=PANEL_DEEP,
            foreground_color=TEXT,
            cursor_color=ACCENT,
            padding=(dp(10), dp(10)),
            size_hint_y=None,
            height=dp(120),
        )
        update_card.add_widget(self.update_spinner)
        update_card.add_widget(key_row)
        update_card.add_widget(self.update_values_field)
        update_card.add_widget(self.action_button("Update Row", self.update_row))
        self.content.add_widget(update_card)

        delete_card = self.section_card("Delete Row", "Delete a record by matching a single column value.")
        self.delete_spinner = Spinner(text="Select table", values=(), size_hint_y=None, height=dp(42))
        delete_row_fields = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(10))
        self.delete_key_column_field = TextInput(hint_text="Key column", background_color=PANEL_DEEP, foreground_color=TEXT, cursor_color=ACCENT, size_hint_y=None, height=dp(42))
        self.delete_key_value_field = TextInput(hint_text="Key value", background_color=PANEL_DEEP, foreground_color=TEXT, cursor_color=ACCENT, size_hint_y=None, height=dp(42))
        delete_row_fields.add_widget(self.delete_key_column_field)
        delete_row_fields.add_widget(self.delete_key_value_field)
        delete_card.add_widget(self.delete_spinner)
        delete_card.add_widget(delete_row_fields)
        delete_card.add_widget(self.action_button("Delete Row", self.delete_row))
        self.content.add_widget(delete_card)

    def refresh_tables(self, table_names: list[str]):
        values = tuple(table_names)
        for spinner in (self.browse_spinner, self.insert_spinner, self.update_spinner, self.delete_spinner):
            spinner.values = values
            spinner.text = values[0] if values else "Select table"

    def browse_selected_table(self, *_args):
        self.root_widget.browse_table_action(self.browse_spinner.text)

    def insert_row(self, *_args):
        self.root_widget.insert_row_action(self.insert_spinner.text, self.insert_values_field.text)

    def update_row(self, *_args):
        self.root_widget.update_row_action(
            self.update_spinner.text,
            self.key_column_field.text,
            self.key_value_field.text,
            self.update_values_field.text,
        )

    def delete_row(self, *_args):
        self.root_widget.delete_row_action(
            self.delete_spinner.text,
            self.delete_key_column_field.text,
            self.delete_key_value_field.text,
        )


class SQLScreen(BaseScreen):
    def __init__(self, root_widget, **kwargs):
        super().__init__(root_widget, name="sql", **kwargs)

        sql_card = self.section_card("SQL Console", "Run custom SQL against the active connection.")
        self.query_input = TextInput(
            hint_text="SELECT * FROM your_table;",
            multiline=True,
            background_color=PANEL_DEEP,
            foreground_color=TEXT,
            cursor_color=ACCENT,
            padding=(dp(10), dp(10)),
            size_hint_y=None,
            height=dp(180),
        )
        sql_card.add_widget(self.query_input)
        button_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(10))
        button_row.add_widget(self.action_button("Run Query", self.run_query))
        button_row.add_widget(self.action_button("Clear", self.clear_query))
        sql_card.add_widget(button_row)
        self.content.add_widget(sql_card)

    def run_query(self, *_args):
        self.root_widget.run_custom_sql_action(self.query_input.text)

    def clear_query(self, *_args):
        self.query_input.text = ""


class SidebarButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(48)
        self.background_normal = ""
        self.background_color = PANEL_DEEP
        self.color = TEXT
        self.bold = True
        self.font_size = "15sp"


class SQLWorkbenchRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(14), padding=dp(16), **kwargs)
        Window.clearcolor = BG
        self.connection = None
        self.database_names: list[str] = []
        self.active_database = None
        self.table_names: list[str] = []
        self.status_text = "Ready. Connect to a local MariaDB server."

        self.header = Card(orientation="horizontal", background_color=PANEL)
        self.header.height = dp(96)
        self.header.size_hint_y = None
        self.header.padding = dp(18)
        self.header.spacing = dp(12)

        title_block = BoxLayout(orientation="vertical", spacing=dp(2))
        title = Label(
            text="SQL Workbench",
            color=TEXT,
            bold=True,
            font_size="24sp",
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(28),
        )
        title.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        subtitle = Label(
            text="Professional local database management for MariaDB and MySQL-style servers.",
            color=MUTED,
            font_size="14sp",
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(24),
        )
        subtitle.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        title_block.add_widget(title)
        title_block.add_widget(subtitle)

        self.connection_chip = Label(
            text="Disconnected",
            color=ACCENT,
            bold=True,
            size_hint_x=None,
            width=dp(180),
            halign="right",
            valign="middle",
        )
        self.connection_chip.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        self.header.add_widget(title_block)
        self.header.add_widget(self.connection_chip)
        self.add_widget(self.header)

        main = BoxLayout(orientation="horizontal", spacing=dp(14))

        sidebar = Card(orientation="vertical", background_color=PANEL)
        sidebar.width = dp(230)
        sidebar.size_hint_x = None
        navigation_label = Label(
            text="Navigation",
            color=TEXT,
            bold=True,
            size_hint_y=None,
            height=dp(24),
            halign="left",
            valign="middle",
        )
        navigation_label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        sidebar.add_widget(navigation_label)
        sidebar.children[0].bind(size=lambda instance, value: setattr(instance, "text_size", value))
        sidebar.add_widget(self._sidebar_button("Dashboard", lambda *_args: self.switch_screen("dashboard")))
        sidebar.add_widget(self._sidebar_button("DDL Tools", lambda *_args: self.switch_screen("ddl")))
        sidebar.add_widget(self._sidebar_button("DML Tools", lambda *_args: self.switch_screen("dml")))
        sidebar.add_widget(self._sidebar_button("SQL Console", lambda *_args: self.switch_screen("sql")))
        sidebar.add_widget(create_spacer(6))
        sidebar.add_widget(
            Label(
                text=(
                    "Local-first workflow\n"
                    "- create databases\n"
                    "- create tables\n"
                    "- insert and update rows\n"
                    "- inspect live results"
                ),
                color=MUTED,
                halign="left",
                valign="top",
                text_size=(dp(180), None),
                size_hint_y=None,
                height=dp(120),
            )
        )

        self.manager = ScreenManager(transition=SlideTransition(duration=0.15))
        self.dashboard_screen = DashboardScreen(self)
        self.ddl_screen = DDLScreen(self)
        self.dml_screen = DMLScreen(self)
        self.sql_screen = SQLScreen(self)
        self.manager.add_widget(self.dashboard_screen)
        self.manager.add_widget(self.ddl_screen)
        self.manager.add_widget(self.dml_screen)
        self.manager.add_widget(self.sql_screen)

        main.add_widget(sidebar)
        main.add_widget(self.manager)
        self.add_widget(main)

        self.result_panel = ResultPanel()
        self.add_widget(self.result_panel)

        self.status_bar = Label(
            text=self.status_text,
            color=MUTED,
            size_hint_y=None,
            height=dp(24),
            halign="left",
            valign="middle",
        )
        self.status_bar.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        self.add_widget(self.status_bar)

        Clock.schedule_once(lambda *_args: self.refresh_table_lists(), 0)
        Clock.schedule_once(lambda *_args: self.refresh_database_lists(), 0)

    def _sidebar_button(self, text: str, callback):
        button = SidebarButton(text=text)
        button.bind(on_release=callback)
        return button

    def switch_screen(self, screen_name: str):
        self.manager.current = screen_name

    def set_status(self, message: str):
        self.status_text = message
        self.status_bar.text = message

    def set_connection_chip(self, text: str, color=ACCENT):
        self.connection_chip.text = text
        self.connection_chip.color = color

    def popup_message(self, title: str, message: str):
        content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
        label = Label(text=message, color=TEXT, halign="left", valign="top")
        label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        button = Button(text="Close", size_hint_y=None, height=dp(42), background_normal="", background_color=ACCENT, color=(0.03, 0.07, 0.05, 1), bold=True)
        popup = Popup(title=title, content=content, size_hint=(0.55, 0.35), auto_dismiss=False)
        button.bind(on_release=popup.dismiss)
        content.add_widget(label)
        content.add_widget(button)
        popup.open()

    def report_error(self, title: str, error: Exception | str):
        message = str(error)
        self.set_status(f"{title}: {message}")
        self.result_panel.show_message(message)
        self.popup_message(title, message)

    def ensure_connection(self):
        if self.connection is None:
            raise RuntimeError("Connect to a local database first.")

    def connect_to_database(self, host: str, user: str, password: str, database: str):
        try:
            if self.connection is not None:
                self.connection.close()
        except Exception:
            pass

        host = host.strip() or None
        user = user.strip() or None
        password = password or None
        database = database.strip() or None

        try:
            self.connection = get_connection(host=host, user=user, password=password, database=database)
            self.active_database = self._get_active_database()
            self.set_connection_chip(f"Connected: {database or 'server'}")
            self.set_status(f"Connected to {host or 'localhost'} as {user or 'root'}.")
            self.refresh_database_lists()
            self.refresh_table_lists()
            self.result_panel.show_message("Connection established successfully.")
        except mariadb.Error as exc:
            self.connection = None
            self.active_database = None
            self.set_connection_chip("Disconnected", color=ERROR)
            self.report_error("Connection failed", exc)

    def _get_active_database(self):
        if self.connection is None:
            return None
        cursor = self.connection.cursor()
        cursor.execute("SELECT DATABASE()")
        row = cursor.fetchone()
        return row[0] if row else None

    def refresh_database_lists(self, *_args):
        if self.connection is None:
            self.database_names = []
            self.active_database = None
            self.dashboard_screen.refresh_databases([], None)
            return

        try:
            self.database_names = list_databases(connection=self.connection)
            self.active_database = self._get_active_database()
            self.dashboard_screen.refresh_databases(self.database_names, self.active_database)
        except mariadb.Error as exc:
            self.report_error("Could not load databases", exc)

    def refresh_table_lists(self, *_args):
        if self.connection is None:
            self.table_names = []
            self.ddl_screen.refresh_tables([])
            self.dml_screen.refresh_tables([])
            self.set_status("Ready. Connect to a local MariaDB server.")
            return

        try:
            self.table_names = list_tables(connection=self.connection)
            self.ddl_screen.refresh_tables(self.table_names)
            self.dml_screen.refresh_tables(self.table_names)
            if self.table_names:
                self.set_status(f"Loaded {len(self.table_names)} table(s) from the current database.")
            else:
                self.set_status("Connection ready. No tables found in the current database.")
        except mariadb.Error as exc:
            self.report_error("Could not load tables", exc)

    def create_database_action(self, database_name: str):
        try:
            self.ensure_connection()
            database_name = database_name.strip()
            if not database_name:
                raise ValueError("Database name is required.")
            create_database(database_name, connection=self.connection)
            self.refresh_database_lists()
            self.set_status(f"Database '{database_name}' is ready.")
            self.result_panel.show_message(f"Database '{database_name}' was created or already existed.")
        except (RuntimeError, ValueError, mariadb.Error) as exc:
            self.report_error("Create database failed", exc)

    def create_table_from_form_action(self, table_name: str, column_rows: list[ColumnFormRow]):
        column_sql_parts = []
        for row in column_rows:
            column_sql_parts.append(row.to_sql_fragment())
        self.create_table_action(table_name, ", ".join(column_sql_parts))

    def create_table_action(self, table_name: str, columns_definition: str):
        try:
            self.ensure_connection()
            table_name = table_name.strip()
            if not table_name:
                raise ValueError("Table name is required.")
            create_table(table_name, columns_definition, connection=self.connection)
            self.set_status(f"Table '{table_name}' is ready.")
            self.result_panel.show_message(f"Table '{table_name}' was created or already existed.")
            self.refresh_table_lists()
        except (RuntimeError, ValueError, mariadb.Error) as exc:
            self.report_error("Create table failed", exc)

    def drop_table_action(self, table_name: str):
        try:
            self.ensure_connection()
            table_name = table_name.strip()
            if not table_name or table_name == "Select table":
                raise ValueError("Choose a table to drop.")
            drop_table(table_name, connection=self.connection)
            self.set_status(f"Table '{table_name}' was removed.")
            self.result_panel.show_message(f"Table '{table_name}' dropped successfully.")
            self.refresh_table_lists()
        except (RuntimeError, ValueError, mariadb.Error) as exc:
            self.report_error("Drop table failed", exc)

    def browse_table_action(self, table_name: str):
        try:
            self.ensure_connection()
            table_name = table_name.strip()
            if not table_name or table_name == "Select table":
                raise ValueError("Choose a table to browse.")
            columns, rows = fetch_rows(table_name, connection=self.connection)
            self.result_panel.show_rows(columns, rows, f"{len(rows)} row(s) loaded from {table_name}.")
            self.set_status(f"Loaded {len(rows)} row(s) from '{table_name}'.")
        except (RuntimeError, ValueError, mariadb.Error) as exc:
            self.report_error("Browse table failed", exc)

    def insert_row_action(self, table_name: str, raw_data: str):
        try:
            self.ensure_connection()
            table_name = table_name.strip()
            if not table_name or table_name == "Select table":
                raise ValueError("Choose a table to insert into.")
            data = parse_key_value_lines(raw_data)
            insert_row(table_name, data, connection=self.connection)
            self.set_status(f"Inserted 1 row into '{table_name}'.")
            self.result_panel.show_message(f"Inserted 1 row into '{table_name}'.")
        except (RuntimeError, ValueError, mariadb.Error) as exc:
            self.report_error("Insert failed", exc)

    def update_row_action(self, table_name: str, key_column: str, key_value: str, raw_data: str):
        try:
            self.ensure_connection()
            table_name = table_name.strip()
            key_column = key_column.strip()
            if not table_name or table_name == "Select table":
                raise ValueError("Choose a table to update.")
            if not key_column:
                raise ValueError("Key column is required.")
            if not key_value:
                raise ValueError("Key value is required.")
            data = parse_key_value_lines(raw_data)
            update_row(table_name, key_column, key_value, data, connection=self.connection)
            self.set_status(f"Updated rows in '{table_name}'.")
            self.result_panel.show_message(f"Updated rows in '{table_name}'.")
        except (RuntimeError, ValueError, mariadb.Error) as exc:
            self.report_error("Update failed", exc)

    def delete_row_action(self, table_name: str, key_column: str, key_value: str):
        try:
            self.ensure_connection()
            table_name = table_name.strip()
            key_column = key_column.strip()
            if not table_name or table_name == "Select table":
                raise ValueError("Choose a table to delete from.")
            if not key_column:
                raise ValueError("Key column is required.")
            if not key_value:
                raise ValueError("Key value is required.")
            delete_row(table_name, key_column, key_value, connection=self.connection)
            self.set_status(f"Deleted matching rows from '{table_name}'.")
            self.result_panel.show_message(f"Deleted matching rows from '{table_name}'.")
        except (RuntimeError, ValueError, mariadb.Error) as exc:
            self.report_error("Delete failed", exc)

    def run_custom_sql_action(self, query: str):
        try:
            self.ensure_connection()
            query = query.strip()
            if not query:
                raise ValueError("SQL query is required.")
            columns, rows, rowcount = execute_sql(query, connection=self.connection)
            if columns:
                self.result_panel.show_rows(columns, rows, f"Query returned {len(rows)} row(s).")
                self.set_status(f"Query returned {len(rows)} row(s).")
            else:
                self.result_panel.show_message(f"Statement executed successfully. {rowcount} row(s) affected.")
                self.set_status(f"Statement executed successfully. {rowcount} row(s) affected.")
                lower_query = query.lower()
                if lower_query.startswith(("create ", "drop ", "alter ")):
                    self.refresh_table_lists()
        except (RuntimeError, ValueError, mariadb.Error) as exc:
            self.report_error("SQL execution failed", exc)


class SQLWorkbenchApp(App):
    title = "SQL Workbench"

    def build(self):
        return SQLWorkbenchRoot()


if __name__ == "__main__":
    SQLWorkbenchApp().run()
