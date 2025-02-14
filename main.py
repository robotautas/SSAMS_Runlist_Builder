from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QTextEdit,
    QPushButton,
    QLabel,
    QFileDialog,
    QFormLayout,
    QLineEdit,
    QGroupBox,
    QCheckBox,
    QHBoxLayout,
    QComboBox,
    QMessageBox,
)
from PySide6.QtCore import Qt, QEvent, QSettings
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
import os
import sys
import json
import pandas as pd

from builder import RunlistBuilder


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.runlist_for_saving = ''
        settings = QSettings("SSAMS", "runlist_builder").value("inputs", "{}")
        previous_inputs = json.loads(settings)
        print(previous_inputs)

        self.setWindowTitle("SSAMS Runlist Builder")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        main_layout = QVBoxLayout()

        # Top layout (Table and Text Area)
        top_layout = QHBoxLayout()

        # Table (Top Left)
        self.table_view = QTableView()
        self.table_view.setFixedWidth(407)
        self.table_model = QStandardItemModel()
        self.table_view.setModel(self.table_model)
        # self.table_view.verticalHeader().setDefaultSectionSize(8)
        # self.table_view.verticalHeader().setFont(QFont("Arial", 8))
        # self.table_view  # Set smaller row height
        top_layout.addWidget(self.table_view, 1)

        # Text Area (Top Right)
        self.preview_area = QTextEdit()
        self.preview_area.setMinimumWidth(600)
        self.preview_area.setReadOnly(True)
        top_layout.addWidget(self.preview_area, 2)

        main_layout.addLayout(top_layout)

        # Bottom Layout (Split into Four Sections)
        bottom_layout = QHBoxLayout()

        self.file_path = None

        # Batch Controls Section
        batch_controls_group = QGroupBox("Batch Controls")
        batch_controls_group.setFixedWidth(200)
        self.batch_controls_layout = QFormLayout(batch_controls_group)

        self.batch_controls_inputs = {
            "mode": QComboBox(),
            "parkmode": QCheckBox(),
            "judge": QCheckBox(),
        }

        previous_bc_inputs = previous_inputs.get("batch_controls", {})

        self.batch_controls_inputs["mode"].addItems(["nrm", "rpt"])
        previous_mode_input = previous_bc_inputs.get("mode", "nrm")
        self.batch_controls_inputs["mode"].setCurrentText(previous_mode_input)

        previous_parkmode_value = previous_bc_inputs.get("parkmode", "off")
        previous_parkmode_input = True if previous_parkmode_value == "on" else False
        self.batch_controls_inputs["parkmode"].setChecked(previous_parkmode_input)

        previous_judge_value = previous_bc_inputs.get("judge", "off")
        previous_judge_input = True if previous_judge_value == "on" else False
        self.batch_controls_inputs["judge"].setChecked(previous_judge_input)

        for label_text, widget in self.batch_controls_inputs.items():
            label = QLabel(label_text)  # Create a QLabel for the setting name
            label.setFixedWidth(75)
            widget.setFixedWidth(75)
            self.batch_controls_layout.addRow(label, widget)

        bottom_layout.addWidget(batch_controls_group)

        # Settings Section
        settings_group = QGroupBox("Settings")
        settings_group.setFixedWidth(200)
        self.settings_layout = QFormLayout(settings_group)

        previous_settings_inputs = previous_inputs.get("settings", {})
        self.settings_inputs = {
            "runs": QLineEdit(previous_settings_inputs.get("runs", "20")),
            "tlimit": QLineEdit(previous_settings_inputs.get("tlimit", "1800")),
            "jn": QLineEdit(previous_settings_inputs.get("jn", "6")),
            "warm": QLineEdit(previous_settings_inputs.get("warm", "100")),
        }
        # for label, widget in self.settings_inputs.items():
        #     label.setFixedWidth(70)
        #     self.settings_layout.addRow(label, widget)

        for label_text, widget in self.settings_inputs.items():
            label = QLabel(label_text)  # Create a QLabel for the setting name
            label.setFixedWidth(50)
            widget.setFixedWidth(75)  # Set the width of the label
            self.settings_layout.addRow(label, widget)  # Add QLabel and QLineEdit

        bottom_layout.addWidget(settings_group)

        # JLimits Section
        jlimits_group = QGroupBox("JLimits")
        jlimits_group.setFixedWidth(200)
        self.jlimits_layout = QVBoxLayout(jlimits_group)

        previous_jlimits_inputs = previous_inputs.get("jlimits", {})
        grafitas_value, grafitas_checked = previous_jlimits_inputs.get(
            "grafitas", ["9", "off"]
        )
        ft_value, ft_checked = previous_jlimits_inputs.get("ft", ["3", "off"])
        c1_value, c1_checked = previous_jlimits_inputs.get("c1", ["0.24", "off"])
        c2_value, c2_checked = previous_jlimits_inputs.get("c2", ["0.24", "off"])
        c3_value, c3_checked = previous_jlimits_inputs.get("c3", ["0.23", "off"])
        c5_value, c5_checked = previous_jlimits_inputs.get("c5", ["0.24", "off"])
        c7_value, c7_checked = previous_jlimits_inputs.get("c7", ["0.24", "off"])
        c8_value, c8_checked = previous_jlimits_inputs.get("c8", ["3", "off"])
        c9_value, c9_checked = previous_jlimits_inputs.get("c9", ["3", "off"])
        oxii_value, oxii_checked = previous_jlimits_inputs.get("oxii", ["0.5", "off"])

        self.jlimits_inputs = {
            "default": QLineEdit(previous_jlimits_inputs.get("default", "0.24")),
            "grafitas": (
                QCheckBox(checked=True if grafitas_checked == "on" else False),
                QLineEdit(grafitas_value),
            ),
            "ft": (
                QCheckBox(checked=True if ft_checked == "on" else False),
                QLineEdit(ft_value),
            ),
            "c1": (
                QCheckBox(checked=True if c1_checked == "on" else False),
                QLineEdit(c1_value),
            ),
            "c2": (
                QCheckBox(checked=True if c2_checked == "on" else False),
                QLineEdit(c2_value),
            ),
            "c3": (
                QCheckBox(checked=True if c3_checked == "on" else False),
                QLineEdit(c3_value),
            ),
            "c5": (
                QCheckBox(checked=True if c5_checked == "on" else False),
                QLineEdit(c5_value),
            ),
            "c7": (
                QCheckBox(checked=True if c7_checked == "on" else False),
                QLineEdit(c7_value),
            ),
            "c8": (
                QCheckBox(checked=True if c8_checked == "on" else False),
                QLineEdit(c8_value),
            ),
            "c9": (
                QCheckBox(checked=True if c9_checked == "on" else False),
                QLineEdit(c9_value),
            ),
            "oxii": (
                QCheckBox(checked=True if oxii_checked == "on" else False),
                QLineEdit(oxii_value),
            ),
        }

        for label_text, value in self.jlimits_inputs.items():
            row_layout = QHBoxLayout()
            row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label = QLabel(label_text)
            label.setFixedWidth(50)
            if isinstance(value, tuple):
                checkbox, line_edit = value
                line_edit.setFixedWidth(75)
                checkbox.setFixedWidth(13)
                row_layout.addWidget(checkbox)
                row_layout.addWidget(label)
                row_layout.addWidget(line_edit)
            else:
                empty_label = QLabel()
                empty_label.setFixedWidth(13)
                row_layout.addWidget(empty_label)
                row_layout.addWidget(label)
                row_layout.addWidget(value)
                value.setFixedWidth(75)
            self.jlimits_layout.addLayout(row_layout)

        bottom_layout.addWidget(jlimits_group)

        # Output Folder and Load Button Section
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)


        self.load_button = QPushButton("Load File")
        self.load_button.setFixedWidth(200)
        self.load_button.setFixedHeight(50)
        self.load_button.clicked.connect(self.load_file)
        output_layout.addWidget(self.load_button)

        self.generate_button = QPushButton("Generate Runlist")
        self.generate_button.setFixedWidth(200)
        self.generate_button.setFixedHeight(50)
        self.generate_button.clicked.connect(self.generate_runlist)
        output_layout.addWidget(self.generate_button)

        self.save_runlist_button = QPushButton("Save Runlist")
        self.save_runlist_button.clicked.connect(self.save_runlist)
        self.save_runlist_button.setFixedWidth(200)
        self.save_runlist_button.setFixedHeight(50)
        output_layout.addWidget(self.save_runlist_button)

        output_layout.addStretch()

        previous_output_folder_root = previous_inputs.get("output_folder", "C:\\runlists")
        todays_date = pd.Timestamp.now().strftime("%Y%m%d")
        output_folder = f"{previous_output_folder_root}\\{todays_date}"
        self.output_folder_input = QLineEdit(output_folder)
        output_layout.addWidget(QLabel("Output Folder"))
        output_layout.addWidget(self.output_folder_input)

        # output_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        bottom_layout.addWidget(output_group)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def event(self, event):
        """Intercept all child widget events in the main window"""
        if event.type() in {QEvent.KeyRelease, QEvent.FocusOut}:
            widget = self.focusWidget()
            print(f"value changed: {widget.objectName()} = {widget.text()}")
            # self.generate_runlist()
        return super().event(event)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open XLSX File", "", "Excel Files (*.xlsx)"
        )
        if file_path:
            df = pd.read_excel(file_path)
            self.file_path = file_path
            print(f"{self.file_path} is loaded")
            # make generate button clickable
            self.populate_table(df)

    def populate_table(self, df):
        df.columns = df.iloc[2]
        df = df[3:]
        df = df.dropna(subset=["Lab Code", "Client Code/Comment"], how="all")
        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(df.columns.tolist())
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setColumnWidth(0, 30)
        font = QFont("Arial", 8)  # Smaller font size
        self.table_view.setFont(font)
        self.table_view.verticalHeader().setDefaultSectionSize(15)
        self.table_view.setEditTriggers(QTableView.NoEditTriggers)
        
        for row in df.itertuples(index=False):
            items = [QStandardItem(str(item)) for item in row]
            self.table_model.appendRow(items)

    def generate_runlist(self):
        if not self.file_path:
            self.show_error_popup("Please load a file first")
            return

        jlimits, settings, batch_controls = self.get_all_settings()
        bldr = RunlistBuilder(
            self.file_path,
            batch_controls,
            settings,
            jlimits,
            self.output_folder_input.text(),
        )
        runlist = bldr.runlist_str()
        self.preview_area.setText(f"<pre>{runlist}</pre>")
        self.runlist_for_saving = runlist

    def get_all_settings(self) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
        jlimits_hboxes = self.jlimits_layout.children()
        jlimit_rows = []
        for hbox in jlimits_hboxes:
            items = []
            for i in range(hbox.count()):
                items.append(hbox.itemAt(i))
            jlimit_rows.append(items)
        jlimits = {}
        for row in jlimit_rows:
            if isinstance(row[0].widget(), QLabel):
                print("TYPE: 1", type(row[0]), row[0].widget())
                jlimits[row[1].widget().text()] = row[2].widget().text()
            else:
                print("TYPE: 2", type(row[0]), row[0].widget())

                jlimits[row[1].widget().text()] = [
                    row[2].widget().text(),
                    "on" if row[0].widget().isChecked() else "off",
                ]
        print(jlimits)

        settings_widgets = self.settings_layout
        settings_widgets_list = []
        for i in range(settings_widgets.count()):  # no way to get actual pairs????? :(
            settings_widgets_list.append(settings_widgets.itemAt(i).widget().text())
        settings_pairs = []
        for i in range(0, len(settings_widgets_list), 2):
            settings_pairs.append(
                (settings_widgets_list[i], settings_widgets_list[i + 1])
            )

        settings = dict(settings_pairs)

        bc_widgets = self.batch_controls_layout
        bc_widgets_list = []
        for i in range(bc_widgets.count()):
            widget = bc_widgets.itemAt(i).widget()
            if isinstance(widget, QLabel):
                bc_widgets_list.append(widget.text())
            elif isinstance(widget, QComboBox):
                text = widget.itemText(widget.currentIndex())
                bc_widgets_list.append(text)
            elif isinstance(widget, QCheckBox):
                bc_widgets_list.append("on" if widget.isChecked() else "off")
        bc_pairs = []
        for i in range(0, len(bc_widgets_list), 2):
            bc_pairs.append((bc_widgets_list[i], bc_widgets_list[i + 1]))
        batch_controls = dict(bc_pairs)

        return jlimits, settings, batch_controls

    def save_inputs(self) -> None:
        global_settings = QSettings("SSAMS", "runlist_builder")
        jlimits, settings, batch_controls = self.get_all_settings()
        splitted_runlists_folder = self.output_folder_input.text().split("\\")
        output_folder = ""
        if splitted_runlists_folder[-1].startswith('20'):
            output_folder = "\\".join(splitted_runlists_folder[:-1])
        else:
            output_folder = "\\".join(splitted_runlists_folder)

        all_settings = {
            "jlimits": jlimits,
            "settings": settings,
            "batch_controls": batch_controls,
            "output_folder": output_folder,
        }
        global_settings.setValue("inputs", json.dumps(all_settings))
        print("saving inputs..")

    
    def show_success_popup(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("Success")
        msg_box.setText("Runlist saved successfully")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def show_error_popup(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()


    def save_runlist(self):
        if not self.runlist_for_saving:
            self.show_error_popup("Please generate a runlist first")
            return
        output_folder = self.output_folder_input.text()

        if output_folder:
            folder_path = self.output_folder_input.text()
            os.makedirs(folder_path, exist_ok=True)  # Ensure the folder exists

            path = os.path.join(folder_path, 'runlist')  # Use os.path.join for cross-platform compatibility
            with open(path, "w") as f:
                f.write(self.runlist_for_saving)
            self.show_success_popup()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.aboutToQuit.connect(window.save_inputs)
    sys.exit(app.exec())
