import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QLabel,
                              QSpinBox, QComboBox, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QCheckBox, QGroupBox, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QColor

class NoteCalculator:
    def __init__(self):
        # Notes in the chromatic scale (using sharps)
        self.notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        
    def get_note_at_fret(self, open_note, fret):
        """Calculate the note at a specific fret given the open string note"""
        start_idx = self.notes.index(open_note)
        note_idx = (start_idx + fret) % len(self.notes)
        return self.notes[note_idx]

class FretboardGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout()
        self.layout.setSpacing(3)
        self.setLayout(self.layout)
        
        # Default values
        self.string_count = 6
        self.fret_count = 12
        self.tuning = ["E", "B", "G", "D", "A", "E"]  # Standard guitar tuning
        
        self.note_calculator = NoteCalculator()
        self.note_labels = []
        self.highlighted_notes = set()  # Store which notes should be highlighted
        self.string_tuning_combos = []  # Store references to tuning combo boxes
        self.note_clicked_callback = None  # Callback for note clicks
        
        self.initialize_grid()
    
    def get_note_style(self, fret, note):
        # Professional color scheme logic for dynamic updates
        note_even = "background-color: #b8c1ec; color: #232946; border-radius: 4px;"
        note_odd = "background-color: #fffffe; color: #232946; border-radius: 4px;"
        note_open = "background-color: #eebbc3; color: #232946; font-weight: bold; border-radius: 4px;"
        note_highlight = "background-color: #f9bc60; color: #232946; font-weight: bold; border-radius: 4px; border: 2px solid #232946;"
        if fret == 0:
            return note_open
        elif note in self.highlighted_notes:
            return note_highlight
        elif fret % 2 == 0:
            return note_even
        else:
            return note_odd

    def initialize_grid(self):
        # Clear existing grid items
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        self.note_labels = []
        self.string_tuning_combos = []

        # --- Professional, modern color palette ---
        header_style = (
            "background-color: #232946;"
            "color: #fffffe;"
            "font-weight: bold;"
            "border-radius: 6px;"
            "padding: 6px;"
            "font-size: 12pt;"
            "letter-spacing: 1px;"
        )
        button_style = (
            "background-color: #eebbc3;"
            "color: #232946;"
            "font-weight: bold;"
            "border-radius: 6px;"
            "padding: 4px 10px;"
            "font-size: 12pt;"
            "min-width: 32px;"
            "min-height: 32px;"
            "border: none;"
        )
        button_style_hover = (
            "QPushButton:hover {"
            "background-color: #d4939d;"
            "color: #fffffe;"
            "}"
        )
        combo_style = (
            "background-color: #fffffe;"
            "color: #232946;"
            "border: 1px solid #b8c1ec;"
            "border-radius: 4px;"
            "font-size: 11pt;"
            "padding: 2px 8px;"
        )

        # --- Header row for fret numbers ---
        fret_header = QLabel("String/Fret")
        fret_header.setStyleSheet(header_style)
        fret_header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(fret_header, 0, 0)

        for fret in range(self.fret_count + 1):
            fret_label = QLabel(str(fret))
            fret_label.setStyleSheet(header_style)
            fret_label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(fret_label, 0, fret + 1)

        # --- Fret +/- controls (columns) ---
        fret_control_widget = QWidget()
        fret_control_layout = QHBoxLayout(fret_control_widget)
        fret_control_layout.setContentsMargins(2, 2, 2, 2)
        fret_control_layout.setSpacing(6)

        add_fret_btn = QPushButton("+")
        add_fret_btn.setStyleSheet(button_style + button_style_hover)
        add_fret_btn.setToolTip("Add fret")
        add_fret_btn.clicked.connect(self.add_fret)
        fret_control_layout.addWidget(add_fret_btn)

        remove_fret_btn = QPushButton("-")
        remove_fret_btn.setStyleSheet(button_style + button_style_hover)
        remove_fret_btn.setToolTip("Remove fret")
        remove_fret_btn.clicked.connect(self.remove_fret)
        fret_control_layout.addWidget(remove_fret_btn)

        self.layout.addWidget(fret_control_widget, 0, self.fret_count + 2)

        # --- String rows ---
        for string_idx in range(self.string_count):
            string_num = string_idx + 1

            string_container = QWidget()
            string_layout = QHBoxLayout(string_container)
            string_layout.setContentsMargins(2, 2, 2, 2)
            string_layout.setSpacing(6)

            string_label = QLabel(f"String {string_num}")
            string_label.setStyleSheet(header_style)
            string_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            string_layout.addWidget(string_label)

            tuning_combo = QComboBox()
            tuning_combo.addItems(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])
            tuning = self.tuning[string_idx] if string_idx < len(self.tuning) else "E"
            tuning_combo.setCurrentText(tuning)
            tuning_combo.setStyleSheet(combo_style)
            tuning_combo.currentTextChanged.connect(lambda note, idx=string_idx: self.update_tuning(idx, note))
            string_layout.addWidget(tuning_combo)

            self.string_tuning_combos.append(tuning_combo)
            self.layout.addWidget(string_container, string_idx + 1, 0)

            string_notes = []
            for fret in range(self.fret_count + 1):
                if string_idx < len(self.tuning):
                    note = self.note_calculator.get_note_at_fret(self.tuning[string_idx], fret)
                else:
                    note = self.note_calculator.get_note_at_fret("E", fret)

                note_frame = QFrame()
                note_frame.setFrameStyle(QFrame.Box | QFrame.Plain)
                note_frame.setLineWidth(1)
                note_layout = QVBoxLayout(note_frame)
                note_layout.setContentsMargins(3, 3, 3, 3)
                note_layout.setSpacing(0)

                note_label = QLabel(note)
                note_label.setAlignment(Qt.AlignCenter)
                note_label.setMinimumWidth(35)
                note_label.setMinimumHeight(25)
                note_label.setStyleSheet(self.get_note_style(fret, note))
                note_layout.addWidget(note_label)
                self.layout.addWidget(note_frame, string_idx + 1, fret + 1)
                string_notes.append(note_label)
                # --- Make note clickable ---
                note_label.setCursor(Qt.PointingHandCursor)
                note_label.mousePressEvent = self._make_note_click_handler(note)
            self.note_labels.append(string_notes)

        # --- String +/- controls under last string ---
        string_control_widget = QWidget()
        string_control_layout = QHBoxLayout(string_control_widget)
        string_control_layout.setContentsMargins(2, 2, 2, 2)
        string_control_layout.setSpacing(6)

        add_string_btn = QPushButton("+")
        add_string_btn.setStyleSheet(button_style + button_style_hover)
        add_string_btn.setToolTip("Add string")
        add_string_btn.clicked.connect(self.add_string)
        string_control_layout.addWidget(add_string_btn)

        remove_string_btn = QPushButton("-")
        remove_string_btn.setStyleSheet(button_style + button_style_hover)
        remove_string_btn.setToolTip("Remove string")
        remove_string_btn.clicked.connect(self.remove_string)
        string_control_layout.addWidget(remove_string_btn)

        self.layout.addWidget(string_control_widget, self.string_count + 1, 0)
    
    def set_note_clicked_callback(self, callback):
        self.note_clicked_callback = callback

    def update_tuning(self, string_idx, note):
        if string_idx < self.string_count and string_idx < len(self.tuning):
            self.tuning[string_idx] = note
            if string_idx < len(self.string_tuning_combos):
                combo = self.string_tuning_combos[string_idx]
                if combo.currentText() != note:
                    combo.setCurrentText(note)
            for fret in range(self.fret_count + 1):
                note_at_fret = self.note_calculator.get_note_at_fret(note, fret)
                self.note_labels[string_idx][fret].setText(note_at_fret)
                # Use dynamic color scheme
                self.note_labels[string_idx][fret].setStyleSheet(self.get_note_style(fret, note_at_fret))

    def update_highlighted_notes(self, note, is_selected):
        if is_selected:
            self.highlighted_notes.add(note)
        elif note in self.highlighted_notes:
            self.highlighted_notes.remove(note)
        for string_idx in range(self.string_count):
            for fret in range(self.fret_count + 1):
                note_at_fret = self.note_labels[string_idx][fret].text()
                self.note_labels[string_idx][fret].setStyleSheet(self.get_note_style(fret, note_at_fret))

    def add_string(self):
        """Add a new string to the fretboard"""
        if self.string_count < 12:  # Maximum limit
            self.string_count += 1
            self.tuning.append("E")  # Default tuning for new string
            self.initialize_grid()
    
    def remove_string(self):
        """Remove the last string from the fretboard"""
        if self.string_count > 1:  # Minimum limit
            self.string_count -= 1
            self.initialize_grid()
    
    def add_fret(self):
        """Add a new fret to the fretboard"""
        if self.fret_count < 24:  # Maximum limit
            self.fret_count += 1
            self.initialize_grid()
    
    def remove_fret(self):
        """Remove the last fret from the fretboard"""
        if self.fret_count > 5:  # Minimum limit
            self.fret_count -= 1
            self.initialize_grid()

    def _make_note_click_handler(self, note):
        def handler(event):
            if self.note_clicked_callback:
                self.note_clicked_callback(note)
        return handler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Notez - String Instrument Visualizer")
        self.setMinimumSize(900, 600)
        
        # Set main window style with improved colors
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                border: 1px solid #ced4da;
                border-radius: 5px;
                margin-top: 12px;
                font-weight: bold;
                background-color: #2c3e50;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #ffffff;
            }
            QLabel {
                font-size: 10pt;
                color: #ffffff;
            }
            QCheckBox {
                spacing: 5px;
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QSpinBox {
                min-height: 25px;
                min-width: 70px;
                padding-right: 10px;
                background-color: #e0e0e0;
                color: #333333;
            }
            QComboBox {
                min-height: 25px;
                min-width: 70px;
                padding: 5px;
                background-color: #e0e0e0;
                color: #333333;
            }
        """)
        
        # Create scrollable area for the entire content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)
        
        # Create main widget to hold everything
        self.central_widget = QWidget()
        scroll_area.setWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Create title
        title_label = QLabel("Notez - String Instrument Visualizer")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #2c3e50; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)
        
        # ===== CONFIGURATION SECTION AT TOP =====
        config_section = QHBoxLayout()
        
        # Note highlighting section - now taking full width
        highlight_group = QGroupBox("Highlighting")
        highlight_layout = QVBoxLayout(highlight_group)
        
        # Preset dropdown with improved coloring (NO +/- here)
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Scale Presets:")
        preset_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        preset_layout.addWidget(preset_label)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Select a scale...", "C Major", "A Minor", "G Major", "E Minor", "F Major", "D Minor"
        ])
        self.preset_combo.currentTextChanged.connect(self.handle_preset_change)
        self.preset_combo.setStyleSheet("""
            QComboBox {
                background-color: #2980b9;
                color: #ffffff;
                min-height: 25px;
                min-width: 120px;
                padding: 5px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView {
                background-color: #2c3e50;
                color: #ffffff;
                selection-background-color: #3498db;
                selection-color: #ffffff;
            }
        """)
        preset_layout.addWidget(self.preset_combo)
        # Remove add_string_btn and remove_string_btn from here!
        clear_button = QPushButton("Clear Highlighting")
        clear_button.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; border-radius: 3px; min-width: 80px;")
        clear_button.clicked.connect(self.clear_highlighted_notes)
        preset_layout.addWidget(clear_button)
        preset_layout.addStretch()
        highlight_layout.addLayout(preset_layout)
        
        # Note checkboxes
        notes_layout = QGridLayout()
        notes_layout.setSpacing(5)
        self.note_checkboxes = {}
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        
        # Arrange checkboxes in a 2x6 grid
        for i, note in enumerate(notes):
            row, col = divmod(i, 6)
            checkbox = QCheckBox(note)
            checkbox.toggled.connect(lambda checked, n=note: self.toggle_note_highlight(n, checked))
            notes_layout.addWidget(checkbox, row, col)
            self.note_checkboxes[note] = checkbox
        
        highlight_layout.addLayout(notes_layout)
        
        config_section.addWidget(highlight_group, 1)
        self.layout.addLayout(config_section)
        
        # Create the fretboard visualization
        self.fretboard = FretboardGrid()
        self.fretboard.set_note_clicked_callback(self.handle_note_clicked)
        fretboard_wrapper = QVBoxLayout()
        fretboard_wrapper.addWidget(self.fretboard)
        self.layout.addLayout(fretboard_wrapper)
        self.layout.addStretch(1)
    
    def handle_preset_change(self, preset_name):
        """Handle selection of a preset from dropdown"""
        if preset_name == "Select a scale...":
            return
            
        scale_notes = {
            "C Major": ["C", "D", "E", "F", "G", "A", "B"],
            "A Minor": ["A", "B", "C", "D", "E", "F", "G"],
            "G Major": ["G", "A", "B", "C", "D", "E", "F#"],
            "E Minor": ["E", "F#", "G", "A", "B", "C", "D"],
            "F Major": ["F", "G", "A", "A#", "C", "D", "E"],
            "D Minor": ["D", "E", "F", "G", "A", "A#", "C"]
        };
        
        if preset_name in scale_notes:
            self.add_predefined_key(preset_name, scale_notes[preset_name])
            
        # Reset the dropdown after applying
        QApplication.processEvents()  # Allow UI to update
        self.preset_combo.setCurrentIndex(0)
    
    @Slot(int)
    def update_string_count(self, count):
        # First, update the fretboard
        self.fretboard.update_string_count(count)
        
        # No need to update tuning combos in the top area anymore since they'reremoved
    @Slot(int)
    def update_fret_count(self, count):
        self.fretboard.update_fret_count(count)
    
    @Slot(str)
    def update_tuning(self, string_idx, note):
        self.fretboard.update_tuning(string_idx, note)
        
    @Slot(bool)
    def toggle_note_highlight(self, note, checked):
        self.fretboard.update_highlighted_notes(note, checked)
        
    def add_predefined_key(self, key_name, notes):
        """Helper method to add a predefined music key"""
        # Clear current selection
        for checkbox in self.note_checkboxes.values():
            checkbox.setChecked(False)
            
        # Enable checkboxes for notes in the key
        for note in notes:
            if note in self.note_checkboxes:
                self.note_checkboxes[note].setChecked(True)
    
    def clear_highlighted_notes(self):
        """Clear all highlighted notes"""
        for checkbox in self.note_checkboxes.values():
            checkbox.setChecked(False)

    def handle_note_clicked(self, note):
        # Check the corresponding checkbox if not already checked
        checkbox = self.note_checkboxes.get(note)
        if checkbox and not checkbox.isChecked():
            checkbox.setChecked(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())