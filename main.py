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
        self.layout.setSpacing(3)  # Slightly increased spacing
        self.setLayout(self.layout)
        
        # Default values
        self.string_count = 6
        self.fret_count = 12
        self.tuning = ["E", "B", "G", "D", "A", "E"]  # Standard guitar tuning
        
        self.note_calculator = NoteCalculator()
        self.note_labels = []
        self.highlighted_notes = set()  # Store which notes should be highlighted
        self.string_tuning_combos = []  # Store references to tuning combo boxes
        
        self.initialize_grid()
        
    def initialize_grid(self):
        # Clear existing grid items
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        self.note_labels = []
        self.string_tuning_combos = []  # Reset tuning combos list
        
        # Header styling - softer colors
        header_style = "background-color: #3498db; color: #ecf0f1; font-weight: bold; border-radius: 3px; padding: 2px;"
        button_style = "background-color: #3498db; color: white; font-weight: bold; border-radius: 3px; padding: 2px; min-width: 25px; min-height: 25px;"
        
        # Create header row for fret numbers
        fret_header = QLabel("String/Fret")
        fret_header.setStyleSheet(header_style)
        fret_header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(fret_header, 0, 0)
        
        for fret in range(self.fret_count + 1):
            fret_label = QLabel(str(fret))
            fret_label.setStyleSheet(header_style)
            fret_label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(fret_label, 0, fret + 1)
        
        # Add +/- buttons for frets (columns)
        fret_control_widget = QWidget()
        fret_control_layout = QHBoxLayout(fret_control_widget)
        fret_control_layout.setContentsMargins(2, 2, 2, 2)
        fret_control_layout.setSpacing(2)
        
        add_fret_btn = QPushButton("+")
        add_fret_btn.setStyleSheet(button_style)
        add_fret_btn.setToolTip("Add fret")
        add_fret_btn.clicked.connect(self.add_fret)
        fret_control_layout.addWidget(add_fret_btn)
        
        remove_fret_btn = QPushButton("-")
        remove_fret_btn.setStyleSheet(button_style)
        remove_fret_btn.setToolTip("Remove fret")
        remove_fret_btn.clicked.connect(self.remove_fret)
        fret_control_layout.addWidget(remove_fret_btn)
        
        self.layout.addWidget(fret_control_widget, 0, self.fret_count + 2)
        
        # Create rows for each string
        for string_idx in range(self.string_count):
            string_num = string_idx + 1
            
            # Create a container for string number and tuning combo
            string_container = QWidget()
            string_layout = QHBoxLayout(string_container)
            string_layout.setContentsMargins(2, 2, 2, 2)
            string_layout.setSpacing(3)
            
            # String number label
            string_label = QLabel(f"String {string_num}")
            string_label.setStyleSheet(header_style)
            string_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            string_layout.addWidget(string_label)
            
            # Tuning combo box - fix contrast issue with better styling
            tuning_combo = QComboBox()
            tuning_combo.addItems(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])
            tuning = self.tuning[string_idx] if string_idx < len(self.tuning) else "E"
            tuning_combo.setCurrentText(tuning)
            tuning_combo.setStyleSheet("background-color: #f0f0f0; color: #333333; border: 1px solid #999999;")
            tuning_combo.currentTextChanged.connect(lambda note, idx=string_idx: self.update_tuning(idx, note))
            string_layout.addWidget(tuning_combo)
            
            self.string_tuning_combos.append(tuning_combo)
            self.layout.addWidget(string_container, string_idx + 1, 0)
            
            # Add note for each fret on this string
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
                
                # Better color scheme with less contrast
                if fret % 2 == 0:
                    base_style = "background-color: #f0f0f0; color: #333333;"
                else:
                    base_style = "background-color: #e0e0e0; color: #333333;"
                
                # Special style for open strings (fret 0) - softer blue
                if fret == 0:
                    base_style = "background-color: #b3d9ff; color: #333333;"
                
                # Highlight with a more readable color
                if note in self.highlighted_notes:
                    base_style = "background-color: #2ecc71; color: #ffffff; font-weight: bold;"
                
                note_label.setStyleSheet(base_style)
                note_layout.addWidget(note_label)
                
                self.layout.addWidget(note_frame, string_idx + 1, fret + 1)
                string_notes.append(note_label)
            self.note_labels.append(string_notes)
    
    def update_tuning(self, string_idx, note):
        if string_idx < self.string_count and string_idx < len(self.tuning):
            self.tuning[string_idx] = note
            
            # Update the combo box if needed (to avoid infinite recursion)
            if string_idx < len(self.string_tuning_combos):
                combo = self.string_tuning_combos[string_idx]
                if combo.currentText() != note:
                    combo.setCurrentText(note)
            
            # Update all notes on this string
            for fret in range(self.fret_count + 1):
                note_at_fret = self.note_calculator.get_note_at_fret(note, fret)
                self.note_labels[string_idx][fret].setText(note_at_fret)
                
                # Update highlighting
                if fret % 2 == 0:
                    base_style = "background-color: #f0f0f0; color: #333333;"
                else:
                    base_style = "background-color: #e0e0e0; color: #333333;"
                
                if fret == 0:
                    base_style = "background-color: #b3d9ff; color: #333333;"
                
                if note_at_fret in self.highlighted_notes:
                    base_style = "background-color: #2ecc71; color: #ffffff; font-weight: bold;"
                    
                self.note_labels[string_idx][fret].setStyleSheet(base_style)
    
    def update_highlighted_notes(self, note, is_selected):
        if is_selected:
            self.highlighted_notes.add(note)
        elif note in self.highlighted_notes:
            self.highlighted_notes.remove(note)
        
        # Update all labels
        for string_idx in range(self.string_count):
            for fret in range(self.fret_count + 1):
                note_at_fret = self.note_labels[string_idx][fret].text()
                
                # Set base style based on fret position
                if fret % 2 == 0:
                    base_style = "background-color: #f0f0f0; color: #333333;"
                else:
                    base_style = "background-color: #e0e0e0; color: #333333;"
                
                if fret == 0:
                    base_style = "background-color: #b3d9ff; color: #333333;"
                
                # Apply highlight with better color
                if note_at_fret in self.highlighted_notes:
                    base_style = "background-color: #2ecc71; color: #ffffff; font-weight: bold;"
                
                self.note_labels[string_idx][fret].setStyleSheet(base_style)
    
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
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                font-size: 10pt;
            }
            QCheckBox {
                spacing: 5px;
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
            }
            QComboBox {
                min-height: 25px;
                min-width: 70px;
                padding: 5px;
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
        
        # Preset dropdown
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Scale Presets:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Select a scale...", "C Major", "A Minor", "G Major", "E Minor", "F Major", "D Minor"])
        self.preset_combo.currentTextChanged.connect(self.handle_preset_change)
        preset_layout.addWidget(self.preset_combo)
        
        # Add clear button
        clear_button = QPushButton("Clear Highlighting")
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
        }
        
        if preset_name in scale_notes:
            self.add_predefined_key(preset_name, scale_notes[preset_name])
            
        # Reset the dropdown after applying
        QApplication.processEvents()  # Allow UI to update
        self.preset_combo.setCurrentIndex(0)
    
    @Slot(int)
    def update_string_count(self, count):
        # First, update the fretboard
        self.fretboard.update_string_count(count)
        
        # No need to update tuning combos in the top area anymore since they're removed
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())