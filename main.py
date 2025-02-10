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
)
from PySide6.QtCore import QEvent
from PySide6.QtGui import QStandardItemModel, QStandardItem
import sys
import pandas as pd

from builder import RunlistBuilder


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 App Layout")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        main_layout = QVBoxLayout()

        # Top layout (Table and Text Area)
        top_layout = QHBoxLayout()

        # Table (Top Left)
        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.table_view.setModel(self.table_model)
        self.table_view.verticalHeader().setDefaultSectionSize(
            8
        )  # Set smaller row height
        top_layout.addWidget(self.table_view, 1)

        # Text Area (Top Right)
        self.preview_area = QTextEdit()
        top_layout.addWidget(self.preview_area, 2)

        main_layout.addLayout(top_layout)

        # Bottom Layout (Split into Four Sections)
        bottom_layout = QHBoxLayout()

        self.file_path = None

        # Batch Controls Section
        batch_controls_group = QGroupBox("Batch Controls")
        self.batch_controls_layout = QFormLayout(batch_controls_group)

        self.batch_controls_inputs = {
            "mode": QComboBox(),
            "parkmode": QCheckBox(),
            "judge": QCheckBox(),
        }

        self.batch_controls_inputs["mode"].addItems(["nrm", "rpt"])

        for label, widget in self.batch_controls_inputs.items():
            self.batch_controls_layout.addRow(label, widget)

        bottom_layout.addWidget(batch_controls_group)

        # Settings Section
        settings_group = QGroupBox("Settings")
        self.settings_layout = QFormLayout(settings_group)

        self.settings_inputs = {
            "runs": QLineEdit("20"),
            "tlimit": QLineEdit("1800"),
            "jn": QLineEdit("6"),
            "warm": QLineEdit("100"),
        }
        for label, widget in self.settings_inputs.items():
            self.settings_layout.addRow(label, widget)

        bottom_layout.addWidget(settings_group)

        # JLimits Section
        jlimits_group = QGroupBox("JLimits")
        self.jlimits_layout = QVBoxLayout(jlimits_group)

        self.jlimits_inputs = {
            "default": QLineEdit("0.24"),
            "grafitas": (QCheckBox(), QLineEdit("9")),
            "ft": (QCheckBox(), QLineEdit("3")),
            "c1": (QCheckBox(), QLineEdit("0.24")),
            "c2": (QCheckBox(), QLineEdit("0.24")),
            "c3": (QCheckBox(), QLineEdit("0.23")),
            "c5": (QCheckBox(), QLineEdit("0.24")),
            "c7": (QCheckBox(), QLineEdit("0.24")),
            "c8": (QCheckBox(), QLineEdit("3")),
            "c9": (QCheckBox(), QLineEdit("3")),
            "oxii": (QCheckBox(), QLineEdit("0.5")),
        }

        for label, value in self.jlimits_inputs.items():
            row_layout = QHBoxLayout()
            if isinstance(value, tuple):
                checkbox, line_edit = value
                row_layout.addWidget(checkbox)
                row_layout.addWidget(QLabel(label))
                row_layout.addWidget(line_edit)
            else:
                row_layout.addWidget(QLabel(label))
                row_layout.addWidget(value)
            self.jlimits_layout.addLayout(row_layout)

        bottom_layout.addWidget(jlimits_group)

        # Output Folder and Load Button Section
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)

        self.output_folder_input = QLineEdit("./runlists")
        output_layout.addWidget(QLabel("Output Folder"))
        output_layout.addWidget(self.output_folder_input)

        self.load_button = QPushButton("Load File")
        self.load_button.clicked.connect(self.load_file)
        output_layout.addWidget(self.load_button)

        self.generate_button = QPushButton("Generate Runlist")
        self.generate_button.clicked.connect(self.generate_runlist)
        output_layout.addWidget(self.generate_button)

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
        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(df.columns.tolist())
        for row in df.itertuples(index=False):
            items = [QStandardItem(str(item)) for item in row]
            self.table_model.appendRow(items)

    def generate_runlist(self):
        if not self.file_path:
            print("Please load a file first")
            return

        jlimits, settings, batch_controls = self.get_all_settings()
        bldr = RunlistBuilder(self.file_path, batch_controls, settings, jlimits, self.output_folder_input.text())
        runlist = bldr.runlist_str()
        self.preview_area.setText(f'<pre>{runlist}</pre>')
        

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
            if len(row) != 3:
                jlimits[row[0].widget().text()] = row[1].widget().text()
            else:
                jlimits[row[1].widget().text()] = [
                    row[2].widget().text(),
                    "on" if row[0].widget().isChecked() else "off",
                ]


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
