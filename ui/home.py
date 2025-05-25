from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget,
    QLineEdit, QListWidgetItem, QStackedLayout, QFrame, QMessageBox, QComboBox, QDialog, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QEvent, QTime
from ui.master_password import MasterPasswordWindow

class HomeWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        from core.db import get_expiring_passwords, log_notification
        expiring = get_expiring_passwords(username)
        for name, status in expiring:
            if status == "expired":
                log_notification(username, f"Password for '{name}' has expired.")
            elif status == "soon":
                log_notification(username, f"Password for '{name}' is expiring soon.")
        self.current_view = "All Items"
        self.setWindowTitle("Password Vault")
        self.setGeometry(400, 150, 1000, 600)
        self.init_ui()
        self.lock_timer = QTimer()
        self.lock_timer.timeout.connect(self.auto_lock)
        self.inactivity_timeout = 2 * 60 * 1000 
        self.lock_timer.start(self.inactivity_timeout)
        self.installEventFilter(self)  # Listen to mouse/keyboard events


    def open_entry_view(self, item):
        index = self.vault_list.row(item)
        from core.db import fetch_all_passwords
        entry_list = fetch_all_passwords()
        entry_id = entry_list[index][0]

        from ui.view_password import ViewPasswordWindow
        self.detail_window = ViewPasswordWindow(entry_id, refresh_callback=self.reload_all)
        self.detail_window.show()

    def init_ui(self):
        from PyQt5.QtWidgets import QFrame

        # Layouts
        main_layout = QHBoxLayout()
        sidebar_layout = QVBoxLayout()
        content_wrapper = QVBoxLayout()
        self.stack = QStackedLayout()

        # --- Styled Sidebar ---
        sidebar_frame = QFrame()
        sidebar_frame.setStyleSheet("""
            QFrame {
                background-color: #222052;
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
                padding: 10px;
            }

            QPushButton {
                background-color: transparent;
                color: #EFE9E1;
                border: none;
                text-align: left;
                padding: 6px 10px;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #000000;
                border-radius: 6px;
            }
        """)
        sidebar_frame.setLayout(sidebar_layout)

        all_items_btn = QPushButton("All Items")
        all_items_btn.clicked.connect(lambda: self.switch_view("All Items"))
        sidebar_layout.addWidget(all_items_btn)

        fav_btn = QPushButton("Favorites")
        fav_btn.clicked.connect(lambda: self.switch_view("Favorites"))
        sidebar_layout.addWidget(fav_btn)

        notif_btn = QPushButton("Notifications")
        notif_btn.clicked.connect(lambda: self.switch_view("Notifications"))
        sidebar_layout.addWidget(notif_btn)

        self.vault_toggle = QPushButton("▸ Vault")
        self.vault_toggle.setCheckable(True)
        self.vault_toggle.setChecked(False)
        self.vault_toggle.clicked.connect(self.toggle_vault_menu)
        sidebar_layout.addWidget(self.vault_toggle)

        self.vault_menu = QVBoxLayout()
        self.vault_menu_widget = QFrame()
        self.vault_menu_widget.setLayout(self.vault_menu)
        self.vault_menu_widget.setVisible(False)

        list_btn = QPushButton("   • List of Passwords")
        list_btn.clicked.connect(lambda: self.switch_view("Vault"))
        self.vault_menu.addWidget(list_btn)

        folder_btn = QPushButton("   • Folders")
        folder_btn.clicked.connect(lambda: self.switch_view("Folders"))
        self.vault_menu.addWidget(folder_btn)

        sidebar_layout.addWidget(self.vault_menu_widget)

        tools_btn = QPushButton("Password Generator")
        tools_btn.clicked.connect(lambda: self.switch_view("Password Generator"))
        sidebar_layout.addWidget(tools_btn)

        sidebar_layout.addStretch()

        # --- Styled Topbar ---
        topbar_frame = QFrame()
        topbar_frame.setStyleSheet("""
            QFrame {
                background-color: #EFE9E1;
                padding: 10px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }

            QLineEdit {
                background-color: white;
                border: 1px solid #C3B4A6;
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
            }

            QPushButton {
                background-color: #222052;
                color: #EFE9E1;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
            }

            QPushButton:hover {
                background-color: #000000;
            }
        """)
        topbar_layout = QHBoxLayout(topbar_frame)
        topbar_layout.setContentsMargins(10, 5, 10, 5)
        topbar_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search")
        self.search_input.setFixedWidth(200)
        self.search_input.setClearButtonEnabled(True)

        self.add_btn = QPushButton("+")
        self.add_btn.setFixedWidth(30)
        self.add_btn.clicked.connect(self.handle_add_click)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setFixedWidth(100)
        self.logout_btn.clicked.connect(self.logout)

        topbar_layout.addWidget(self.search_input)
        topbar_layout.addWidget(self.add_btn)
        topbar_layout.addStretch()
        topbar_layout.addWidget(self.logout_btn)

        # --- Views ---
        self.views = {
            "All Items": self.build_recent_view(),
            "Vault": self.build_vault_view(),
            "Folders": self.build_folder_view(),
            "Favorites": self.build_favourites_view(),
            "Notifications": self.build_notifications_view(),
            "Password Generator": self.build_generator_view()
        }

        for v in self.views.values():
            self.stack.addWidget(v)

        content_wrapper.addWidget(topbar_frame)
        content_wrapper.addLayout(self.stack)

        main_layout.addWidget(sidebar_frame)
        main_layout.addLayout(content_wrapper)

        self.setLayout(main_layout)

        # --- Global Style ---
        self.setStyleSheet("""
            QWidget {
                background-color: #DDD7CE;
                font-family: 'Segoe UI', sans-serif;
                color: #222052;
            }

            QLabel {
                font-weight: bold;
            }
        """)

        self.switch_view("All Items")

    def toggle_vault_menu(self):
        is_open = self.vault_toggle.isChecked()
        self.vault_toggle.setText("▾ Vault" if is_open else "▸ Vault")
        self.vault_menu_widget.setVisible(is_open)

    def switch_view(self, name):
        self.current_view = name
        index = list(self.views.keys()).index(name)
        self.stack.setCurrentIndex(index)

        if name == "Vault" and hasattr(self, "current_folder_id"):
            # If we were in a folder view, reset the vault entries
            self.current_folder_id = None
            self.reload_vault()


    def build_recent_view(self):
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QHBoxLayout
        from PyQt5.QtCore import Qt, QSize
        from PyQt5.QtGui import QFont

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 20)

        # Title
        title = QLabel("Recent")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #222052;
            margin-bottom: 14px;
        """)
        layout.addWidget(title)

        # List
        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                margin: 10px 0;
                border: none;
            }
            QListWidget::item:selected {
                background: transparent;
            }
        """)

        from core.db import fetch_recent_passwords
        self.recent_entries = fetch_recent_passwords()

        for entry in self.recent_entries:
            if len(entry) < 4:
                continue

            entry_id, name, modified, used = entry

            # Row widget
            row_widget = QWidget()
            row_widget.setFixedHeight(45)  # Or whatever height you prefer
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(20, 12, 20, 12)
            row_layout.setSpacing(10)
            row_widget.setStyleSheet("""
                QWidget {
                    background-color: #EEE5D3;
                    border-radius: 12px;
                }
            """)

            # Text label
            name_label = QLabel(name if name else "(Unnamed)")
            name_label.setFont(QFont("Segoe UI", 8, QFont.Bold))
            name_label.setStyleSheet("color: #222052;")

            # Icon label
            icon_label = QLabel("➡️")  # Emoji or Unicode arrow → 🡺
            icon_label.setFont(QFont("Segoe UI Emoji", 10))
            icon_label.setStyleSheet("color: #222052;")
            icon_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

            row_layout.addWidget(name_label)
            row_layout.addStretch()
            row_layout.addWidget(icon_label)

            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 54))  # Bigger row
            self.recent_list.addItem(item)
            self.recent_list.setItemWidget(item, row_widget)

        self.recent_list.itemClicked.connect(self.open_recent_entry)

        layout.addWidget(self.recent_list)
        widget.setLayout(layout)
        return widget


    def build_vault_view(self):

        widget = QWidget()
        layout = QVBoxLayout()

        # Header row
        header_layout = QHBoxLayout()
        title = QLabel("List of Passwords")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #222052;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        arrange_label = QLabel("Arrange By")
        arrange_label.setStyleSheet("font-size: 12px;")
        sort_dropdown = QComboBox()
        sort_dropdown.addItems(["Name", "Last Modified", "Last Used"])
        sort_dropdown.currentTextChanged.connect(self.sort_vault_entries)
        self.sort_dropdown = sort_dropdown  
        sort_dropdown.setStyleSheet("QComboBox { border: none; background: transparent; }")
        header_layout.addWidget(arrange_label)
        header_layout.addWidget(sort_dropdown)

        layout.addLayout(header_layout)

        # Column Headers
        column_header = QLabel("Name     Last Modified     Last Used")
        column_header.setStyleSheet("color: #666666; padding-left: 10px;")
        layout.addWidget(column_header)

        # Password List
        self.vault_list = QListWidget()
        self.vault_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                padding: 10px;
            }
            QListWidget::item {
                background-color: #EEE5D3;
                border-radius: 12px;
                margin: 6px 0;
                padding: 12px;
            }
            QListWidget::item:selected {
                background-color: #C3B4A6;
            }
        """)

        self.vault_list.itemClicked.connect(self.open_entry_view)

        from core.db import fetch_all_passwords
        self.vault_entries = fetch_all_passwords()

        for entry in self.vault_entries:
            if len(entry) < 4:
                continue

            entry_id, name, modified, used = entry

            # Format date strings
            modified_str = "-"
            used_str = "-"
            
            if modified:
                try:
                    modified_dt = datetime.strptime(modified, "%Y-%m-%d %H:%M:%S")
                    modified_str = modified_dt.strftime("%d %b %Y")
                except:
                    pass

            if used:
                try:
                    used_dt = datetime.strptime(used, "%Y-%m-%d %H:%M:%S")
                    used_str = used_dt.strftime("%d %b %Y")
                except:
                    pass

            item_text = f"{name:<20}   {modified_str:<15}   {used_str:<15}"
            item = QListWidgetItem(item_text)
            self.vault_list.addItem(item)

        layout.addWidget(self.vault_list)
        widget.setLayout(layout)
        return widget


    def build_folder_view(self):
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidgetItem, QListWidget

        widget = QWidget()
        layout = QVBoxLayout()

        header_layout = QHBoxLayout()
        title = QLabel("Folders")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #222052;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        back_btn = QPushButton("← Back to All Passwords")
        back_btn.setStyleSheet("font-size: 12px; background: transparent; color: #222052;")
        back_btn.clicked.connect(lambda: self.switch_view("Vault"))
        header_layout.addWidget(back_btn)

        arrange_label = QLabel("Arrange By")
        arrange_label.setStyleSheet("font-size: 12px;")
        sort_dropdown = QComboBox()
        sort_dropdown.addItems(["Name"])
        sort_dropdown.setStyleSheet("QComboBox { border: none; background: transparent; }")
        header_layout.addWidget(arrange_label)
        header_layout.addWidget(sort_dropdown)

        layout.addLayout(header_layout)

        column_header = QLabel("Name")
        column_header.setStyleSheet("color: #666666; padding-left: 10px;")
        layout.addWidget(column_header)

        self.folder_list = QListWidget()
        self.folder_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                padding: 10px;
            }
            QListWidget::item {
                background-color: #EEE5D3;
                border-radius: 12px;
                margin: 6px 0;
                padding: 12px;
            }
            QListWidget::item:selected {
                background-color: #C3B4A6;
            }
        """)

        from core.db import fetch_folders
        folders = fetch_folders()
        for _, name in folders:
            QListWidgetItem(name + "     ➜", self.folder_list)

        self.folder_list.itemClicked.connect(self.open_folder_passwords)

        layout.addWidget(self.folder_list)
        widget.setLayout(layout)
        return widget

    
    def open_folder_passwords(self, item):
        from core.db import fetch_folders, fetch_passwords_by_folder

        index = self.folder_list.row(item)
        folder_id = fetch_folders()[index][0]  # Get folder ID from DB

        self.current_folder_id = folder_id
        self.current_view = f"Folder:{folder_id}"

        passwords = fetch_passwords_by_folder(folder_id)
        self.vault_entries = passwords  # Store only these

        self.vault_list.clear()
        for entry_id, name in passwords:
            item = QListWidgetItem(name)
            self.vault_list.addItem(item)

        self.stack.setCurrentIndex(list(self.views.keys()).index("Vault"))



    def build_label(self, text):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(text))
        widget.setLayout(layout)
        return widget

    def handle_add_click(self):
        if self.current_view == "Vault":
            from ui.add_password import AddPasswordWindow
            self.add_window = AddPasswordWindow()
            self.add_window.setAttribute(Qt.WA_DeleteOnClose)
            self.add_window.destroyed.connect(self.reload_all)
            self.add_window.show()

        elif self.current_view == "Folders":
            self.add_new_folder()

        else:
            print(f"No action for + in view: {self.current_view}")

    def logout(self):
        self.close()  # Close HomeWindow

        # Close any other subwindows (e.g. view/edit)
        if hasattr(self, "detail_window"):
            self.detail_window.close()

        from ui.master_password import MasterPasswordWindow
        self.master_pw_window = MasterPasswordWindow(self.username)  # Or just blank if username isn’t needed
        self.master_pw_window.show()

        
    def reload_vault(self):
        from core.db import fetch_all_passwords
        self.current_folder_id = None
        self.vault_list.clear()
        entries = fetch_all_passwords()
        self.vault_entries = entries

        for entry in entries:
            entry_id, name = entry[0], entry[1]
            QListWidgetItem(name, self.vault_list)

    def open_entry_view(self, item):
        index = self.vault_list.row(item)
        entry_id = self.vault_entries[index][0]

        from ui.view_password import ViewPasswordWindow
        self.detail_window = ViewPasswordWindow(entry_id, self.username, refresh_callback=self.reload_vault)
        self.detail_window.show()
        

    def add_new_folder(self):
        from ui.folder_dialog import FolderDialog  
        dialog = FolderDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.folder_name
            from core.db import insert_folder
            try:
                insert_folder(name)
                QMessageBox.information(self, "Folder Created", f"Folder '{name}' added.")
                self.reload_folders()
            except Exception as e:
                import traceback
                traceback.print_exc()
                QMessageBox.warning(self, "Error", f"Could not add folder:\n{str(e)}")



    def reload_folders(self):
        from core.db import fetch_folders

        # Clear the folder list widget first
        self.folder_list.clear()

        folders = fetch_folders()
        for _, name in folders:
            QListWidgetItem(name, self.folder_list)

    def reload_recent_view(self):
        from core.db import fetch_recent_passwords

        self.recent_list.clear()
        recent_entries = fetch_recent_passwords()
        self.recent_entries = recent_entries

        for entry_id, name in recent_entries:
            QListWidgetItem(name, self.recent_list)

    def reload_all(self):
        self.reload_vault()
        self.reload_recent_view()
        self.reload_favourites()

    def open_recent_entry(self, item):
        index = self.recent_list.row(item)
        entry_id = self.recent_entries[index][0]

        from ui.view_password import ViewPasswordWindow
        self.detail_window = ViewPasswordWindow(entry_id, self.username, refresh_callback=self.reload_all)
        self.detail_window.show()

    def build_generator_view(self):
        from core.utils import generate_password
        from PyQt5.QtWidgets import QCheckBox, QSpinBox, QTextEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Generator")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #222052;")
        layout.addWidget(title)

        # Output Box (top)
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setFixedHeight(50)
        self.output_box.setStyleSheet("""
            QTextEdit {
                background-color: #EFE9E1;
                border: 2px solid #C3B4A6;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.output_box)

        # Quality Meter (optional mock)
        quality_label = QLabel("Password Quality Meter")
        quality_label.setStyleSheet("font-size: 12px; margin-top: -10px; margin-bottom: 2px; color: #444;")
        layout.addWidget(quality_label)

        from PyQt5.QtWidgets import QProgressBar

        self.quality_bar = QProgressBar()
        self.quality_bar.setFixedHeight(12)
        self.quality_bar.setRange(0, 100)
        self.quality_bar.setValue(0)
        self.quality_bar.setTextVisible(False)
        self.quality_bar.setStyleSheet("""
            QProgressBar {
                background-color: #DDD7CE;
                border-radius: 6px;
            }
            QProgressBar::chunk {
                background-color: #4C4A96;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.quality_bar)


        # Length
        options_label = QLabel("Options")
        options_label.setStyleSheet("font-size: 14px; margin-top: 20px;")
        layout.addWidget(options_label)

        length_row = QHBoxLayout()
        length_label = QLabel("Length")
        length_label.setStyleSheet("font-size: 13px;")
        self.length_input = QSpinBox()
        self.length_input.setRange(5, 128)
        self.length_input.setValue(12)
        self.length_input.setFixedWidth(100)
        self.length_input.setStyleSheet("""
            QSpinBox {
                background-color: #EFE9E1;
                border: 2px solid #C3B4A6;
                border-radius: 12px;
                padding: 6px;
            }
        """)
        length_row.addWidget(length_label)
        length_row.addWidget(self.length_input)
        length_row.addStretch()
        layout.addLayout(length_row)

        # Character checkboxes
        checkbox_row = QHBoxLayout()
        checkbox_row.setSpacing(20)

        # Replace QCheckBox with QPushButton
        self.upper_btn = QPushButton("A–Z")
        self.lower_btn = QPushButton("a–z")
        self.digits_btn = QPushButton("0–9")
        self.symbols_btn = QPushButton("!@#$")

        for btn in [self.upper_btn, self.lower_btn, self.digits_btn, self.symbols_btn]:
            btn.setCheckable(True)
            btn.setChecked(True)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 13px;
                    background-color: #EFE9E1;
                    padding: 6px 12px;
                    border: 2px solid #C3B4A6;
                    border-radius: 12px;
                }
                QPushButton:checked {
                    background-color: #222052;
                    color: #EFE9E1;
                    border: 2px solid #222052;
                }
            """)
            checkbox_row.addWidget(btn)

        layout.addLayout(checkbox_row)

        # Generate Button
        generate_btn = QPushButton("Generate")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #222052;
                color: #EFE9E1;
                font-weight: bold;
                border-radius: 16px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #000000;
            }
        """)
        generate_btn.clicked.connect(lambda: self.generate_password_ui(generate_password))
        layout.addWidget(generate_btn, alignment=Qt.AlignCenter)

        # Copy Button
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #222052;
                border: none;
                font-size: 12px;
                text-decoration: underline;
                margin-top: 10px;
            }
        """)
        copy_btn.clicked.connect(self.copy_password_to_clipboard)
        layout.addWidget(copy_btn, alignment=Qt.AlignCenter)

        widget.setLayout(layout)
        return widget

    
    def generate_password_ui(self, generator_func):
        length = self.length_input.value()
        password = generator_func(
            length=length,
            use_upper=self.upper_btn.isChecked(),
            use_lower=self.lower_btn.isChecked(),
            use_digits=self.digits_btn.isChecked(),
            use_symbols=self.symbols_btn.isChecked()
        )
        self.output_box.setText(password)

        # Update quality bar
        score = self.evaluate_password_strength(password)
        self.quality_bar.setValue(score)


    def copy_password_to_clipboard(self):
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_box.toPlainText())

        QMessageBox.information(self, "Copied", "Password copied to clipboard!")
    
    def build_favourites_view(self):
        from core.db import fetch_favourites

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Favourites"))

        self.fav_list = QListWidget()
        self.fav_entries = fetch_favourites()
        for entry_id, name in self.fav_entries:
            QListWidgetItem(name, self.fav_list)

        self.fav_list.itemClicked.connect(self.open_favourite_entry)
        layout.addWidget(self.fav_list)
        widget.setLayout(layout)
        return widget
    
    def open_favourite_entry(self, item):
        index = self.fav_list.row(item)
        entry_id = self.fav_entries[index][0]

        from ui.view_password import ViewPasswordWindow
        self.detail_window = ViewPasswordWindow(entry_id, self.username, refresh_callback=self.reload_all)
        self.detail_window.show()

    def reload_favourites(self):
        from core.db import fetch_favourites
        self.fav_list.clear()
        self.fav_entries = fetch_favourites()
        for entry_id, name in self.fav_entries:
            QListWidgetItem(name, self.fav_list)

    from PyQt5.QtCore import QTime

    def eventFilter(self, obj, event):
        # Avoid resetting timer on every minor mouse movement
        if not hasattr(self, 'last_event_time'):
            self.last_event_time = QTime.currentTime()

        now = QTime.currentTime()
        ms_since_last = self.last_event_time.msecsTo(now)

        if event.type() in [QEvent.MouseMove, QEvent.KeyPress]:
            if ms_since_last > 1000:  # Only reset timer every 1 second max
                print("Resetting inactivity timer")  # For testing
                self.lock_timer.start(self.inactivity_timeout)  
                self.last_event_time = now

        return super().eventFilter(obj, event)

    
    def auto_lock(self):
        print("Auto-lock triggered")
        self.lock_timer.stop()

        # Close all open windows that might still be alive
        for widget in QApplication.topLevelWidgets():
            if widget is not self:
                widget.close()

        self.close()

        # Show master password screen
        self.master_pw_window = MasterPasswordWindow(self.get_current_username())
        self.master_pw_window.show()

    
    def get_current_username(self):
        return self.username if hasattr(self, 'username') else ""
    
    def build_notifications_view(self):
        from core.db import fetch_notifications

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Notifications"))

        self.notif_list = QListWidget()
        notifications = fetch_notifications(self.username)

        for msg, ts in notifications:
            display_text = f"{msg} ({ts})"
            item = QListWidgetItem(display_text)
            self.notif_list.addItem(item)

        layout.addWidget(self.notif_list)
        widget.setLayout(layout)
        return widget
    
    def evaluate_password_strength(self, password: str) -> int:
        import re
        length = len(password)
        score = 0

        if length < 8:
            return 10  # Very weak, immediate return
        if length < 12:
            score -= 20  # Penalise short passwords

        if length >= 14:
            score += 25
        elif length >= 12:
            score += 15

        if re.search(r"[A-Z]", password):
            score += 20
        if re.search(r"[a-z]", password):
            score += 20
        if re.search(r"[0-9]", password):
            score += 20
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 15

        return min(max(score, 0), 100)


    def sort_vault_entries(self, sort_type):
        from datetime import datetime
        from core.db import fetch_all_passwords, fetch_all_passwords_sorted
        from core.db import fetch_passwords_by_folder, fetch_passwords_by_folder_sorted

        # Fetch based on current view (folder or all)
        if hasattr(self, "current_folder_id") and self.current_folder_id:
            passwords = fetch_passwords_by_folder_sorted(self.current_folder_id, sort_type)
        else:
            passwords = fetch_all_passwords_sorted(sort_type)

        self.vault_entries = passwords
        self.vault_list.clear()

        for entry in passwords:
            if len(entry) < 4:
                continue

            entry_id, name, modified, used = entry
            modified_str = used_str = "-"

            if modified:
                try:
                    modified_dt = datetime.strptime(modified, "%Y-%m-%d %H:%M:%S")
                    modified_str = modified_dt.strftime("%d %b %Y")
                except:
                    pass

            if used:
                try:
                    used_dt = datetime.strptime(used, "%Y-%m-%d %H:%M:%S")
                    used_str = used_dt.strftime("%d %b %Y")
                except:
                    pass

            item_text = f"{name:<20}   {modified_str:<15}   {used_str:<15}"
            self.vault_list.addItem(QListWidgetItem(item_text))





        









