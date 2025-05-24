from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget,
    QLineEdit, QListWidgetItem, QStackedLayout, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt

class HomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_view = "All Items"
        self.setWindowTitle("Password Vault")
        self.setGeometry(400, 150, 1000, 600)
        self.init_ui()

    def open_entry_view(self, item):
        index = self.vault_list.row(item)
        from core.db import fetch_all_passwords
        entry_list = fetch_all_passwords()
        entry_id = entry_list[index][0]

        from ui.view_password import ViewPasswordWindow
        self.detail_window = ViewPasswordWindow(entry_id, refresh_callback=self.reload_all)
        self.detail_window.show()

    def init_ui(self):
        # Layouts
        main_layout = QHBoxLayout()
        sidebar_layout = QVBoxLayout()
        content_wrapper = QVBoxLayout()
        topbar_layout = QHBoxLayout()
        self.stack = QStackedLayout()

        # --- Sidebar with collapsible Vault section ---
        all_items_btn = QPushButton("All Items")
        all_items_btn.clicked.connect(lambda: self.switch_view("All Items"))
        sidebar_layout.addWidget(all_items_btn)

        fav_btn = QPushButton("Favorites")
        fav_btn.clicked.connect(lambda: self.switch_view("Favorites"))
        sidebar_layout.addWidget(fav_btn)

        notif_btn = QPushButton("Notifications")
        notif_btn.clicked.connect(lambda: self.switch_view("Notifications"))
        sidebar_layout.addWidget(notif_btn)

        # Vault (collapsible)
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

        tools_btn = QPushButton("Tools")
        tools_btn.clicked.connect(lambda: self.switch_view("Tools"))
        sidebar_layout.addWidget(tools_btn)

        sidebar_layout.addStretch()

        # Topbar
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

        # Views
        self.views = {
            "All Items": self.build_recent_view(),
            "Vault": self.build_vault_view(),
            "Folders": self.build_folder_view(),
            "Favorites": self.build_favourites_view(),
            "Notifications": self.build_label("Notifications view coming soon"),
            "Tools": self.build_generator_view()
        }

        for v in self.views.values():
            self.stack.addWidget(v)

        content_wrapper.addLayout(topbar_layout)
        content_wrapper.addLayout(self.stack)

        main_layout.addLayout(sidebar_layout)
        main_layout.addLayout(content_wrapper)
        self.setLayout(main_layout)

        self.switch_view("All Items")

    def toggle_vault_menu(self):
        is_open = self.vault_toggle.isChecked()
        self.vault_toggle.setText("▾ Vault" if is_open else "▸ Vault")
        self.vault_menu_widget.setVisible(is_open)

    def switch_view(self, name):
        self.current_view = name  # Store the view for button logic
        index = list(self.views.keys()).index(name)
        self.stack.setCurrentIndex(index)

    def build_recent_view(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Recent"))

        self.recent_list = QListWidget()

        from core.db import fetch_recent_passwords
        recent_entries = fetch_recent_passwords()
        self.recent_entries = recent_entries  # store IDs to track clicks

        for entry_id, name in recent_entries:
            QListWidgetItem(name, self.recent_list)

        self.recent_list.itemClicked.connect(self.open_recent_entry)

        layout.addWidget(self.recent_list)
        widget.setLayout(layout)
        return widget


    def build_vault_view(self):
        from core.db import fetch_all_passwords  # Make sure this exists
        from PyQt5.QtWidgets import QListWidgetItem, QWidget, QVBoxLayout, QLabel, QListWidget

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("List of Passwords"))
        
        self.vault_list = QListWidget()
        self.vault_list.itemClicked.connect(self.open_entry_view)

        # Load saved passwords from DB
        self.vault_entries = fetch_all_passwords()  # [(id, name), ...]
        for entry_id, name in self.vault_entries:
            item = QListWidgetItem(name)
            self.vault_list.addItem(item)

        layout.addWidget(self.vault_list)
        widget.setLayout(layout)
        return widget


    def build_folder_view(self):
        from core.db import fetch_folders
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Folders"))
        
        self.folder_list = QListWidget()
        folders = fetch_folders()
        for _, name in folders:
            QListWidgetItem(name, self.folder_list)

        self.folder_list.itemClicked.connect(self.open_folder_passwords)

        layout.addWidget(self.folder_list)
        widget.setLayout(layout)
        return widget
    
    def open_folder_passwords(self, item):
        from core.db import fetch_folders, fetch_passwords_by_folder

        index = self.folder_list.row(item)
        folder_id = fetch_folders()[index][0]  # Get folder ID from DB

        self.current_folder_id = folder_id  # For tracking
        self.current_view = f"Folder:{folder_id}"  # Update context

        self.vault_list.clear()
        passwords = fetch_passwords_by_folder(folder_id)
        self.vault_entries = passwords  # Store for click/view access

        for entry_id, name in passwords:
            QListWidgetItem(name, self.vault_list)

        self.switch_view("Vault")  # Show vault layout, but filtered


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
        from ui.start import StartPage  # Move to local import to fix circular import
        self.start_page = StartPage()
        self.start_page.show()
        self.close()
        
    def reload_vault(self):
        from core.db import fetch_all_passwords
        self.vault_list.clear()
        entries = fetch_all_passwords()
        for entry_id, name in entries:
            QListWidgetItem(name, self.vault_list)

    def open_entry_view(self, item):
        index = self.vault_list.row(item)
        from core.db import fetch_all_passwords
        entry_list = fetch_all_passwords()
        entry_id = entry_list[index][0]

        from ui.view_password import ViewPasswordWindow
        self.detail_window = ViewPasswordWindow(entry_id, refresh_callback=self.reload_vault)
        self.detail_window.show()

    def add_new_folder(self):
        from PyQt5.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")

        if ok and name:
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
        self.detail_window = ViewPasswordWindow(entry_id, refresh_callback=self.reload_all)
        self.detail_window.show()

    def build_generator_view(self):
        from core.utils import generate_password
        from PyQt5.QtWidgets import QCheckBox, QSpinBox, QTextEdit

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Password Generator"))

        # Options
        self.length_input = QSpinBox()
        self.length_input.setRange(4, 64)
        self.length_input.setValue(12)

        self.upper_cb = QCheckBox("Include Uppercase Letters")
        self.upper_cb.setChecked(True)

        self.lower_cb = QCheckBox("Include Lowercase Letters")
        self.lower_cb.setChecked(True)

        self.digits_cb = QCheckBox("Include Numbers")
        self.digits_cb.setChecked(True)

        self.symbols_cb = QCheckBox("Include Symbols")
        self.symbols_cb.setChecked(True)

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)

        generate_btn = QPushButton("Generate Password")
        generate_btn.clicked.connect(lambda: self.generate_password_ui(generate_password))

        # Layout
        layout.addWidget(QLabel("Length"))
        layout.addWidget(self.length_input)
        layout.addWidget(self.upper_cb)
        layout.addWidget(self.lower_cb)
        layout.addWidget(self.digits_cb)
        layout.addWidget(self.symbols_cb)
        layout.addWidget(generate_btn)
        layout.addWidget(self.output_box)
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_password_to_clipboard)
        layout.addWidget(copy_btn)


        widget.setLayout(layout)
        return widget
    
    def generate_password_ui(self, generator_func):
        length = self.length_input.value()
        password = generator_func(
            length=length,
            use_upper=self.upper_cb.isChecked(),
            use_lower=self.lower_cb.isChecked(),
            use_digits=self.digits_cb.isChecked(),
            use_symbols=self.symbols_cb.isChecked()
        )
        self.output_box.setText(password)

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
        self.detail_window = ViewPasswordWindow(entry_id, refresh_callback=self.reload_all)
        self.detail_window.show()

    def reload_favourites(self):
        from core.db import fetch_favourites
        self.fav_list.clear()
        self.fav_entries = fetch_favourites()
        for entry_id, name in self.fav_entries:
            QListWidgetItem(name, self.fav_list)

    









