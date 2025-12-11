import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QTextEdit, QGroupBox, QFormLayout, QFileDialog,
    QMessageBox, QProgressBar, QTabWidget, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal
from idealista_api import Idealista, Search


class ApiWorker(QThread):
    """Worker thread to handle API calls without blocking the UI"""
    finished = Signal(object)  # Emits the Response object
    error = Signal(str)  # Emits error message

    def __init__(self, idealista_client, search_params):
        super().__init__()
        self.idealista_client = idealista_client
        self.search_params = search_params

    def run(self):
        try:
            response = self.idealista_client.query(self.search_params)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


class IdealistaGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.idealista_client = None
        self.last_response = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Idealista API Client")
        self.setMinimumSize(900, 700)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Authentication tab
        auth_tab = self.create_auth_tab()
        tabs.addTab(auth_tab, "Authentication")

        # Search filters tab
        search_tab = self.create_search_tab()
        tabs.addTab(search_tab, "Search Filters")

        # Results tab
        results_tab = self.create_results_tab()
        tabs.addTab(results_tab, "Results")

        # Status bar
        self.statusBar().showMessage("Not connected")

    def create_auth_tab(self):
        """Create authentication tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Auth group
        auth_group = QGroupBox("API Authentication")
        auth_layout = QFormLayout()

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key")
        auth_layout.addRow("API Key:", self.api_key_input)

        self.api_secret_input = QLineEdit()
        self.api_secret_input.setPlaceholderText("Enter your API secret")
        self.api_secret_input.setEchoMode(QLineEdit.Password)
        auth_layout.addRow("API Secret:", self.api_secret_input)

        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_api)
        auth_layout.addRow("", self.connect_btn)

        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)
        layout.addStretch()

        return widget

    def create_search_tab(self):
        """Create search filters tab"""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        layout = QVBoxLayout(widget)

        # Required fields
        required_group = QGroupBox("Required Fields")
        required_layout = QFormLayout()

        self.country_combo = QComboBox()
        self.country_combo.addItems(["es", "pt", "it"])
        required_layout.addRow("Country:", self.country_combo)

        self.operation_combo = QComboBox()
        self.operation_combo.addItems(["sale", "rent"])
        required_layout.addRow("Operation:", self.operation_combo)

        self.property_type_combo = QComboBox()
        self.property_type_combo.addItems(["homes", "offices", "premises", "garages", "bedrooms"])
        required_layout.addRow("Property Type:", self.property_type_combo)

        required_group.setLayout(required_layout)
        layout.addWidget(required_group)

        # Location fields
        location_group = QGroupBox("Location")
        location_layout = QFormLayout()

        self.location_id_input = QLineEdit()
        self.location_id_input.setPlaceholderText("e.g., 0-EU-ES-01")
        location_layout.addRow("Location ID:", self.location_id_input)

        self.center_input = QLineEdit()
        self.center_input.setPlaceholderText("e.g., 40.4165,-3.70256")
        location_layout.addRow("Center (lat,lon):", self.center_input)

        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setRange(0, 100000)
        self.distance_spin.setSuffix(" m")
        self.distance_spin.setSpecialValueText("Not set")
        location_layout.addRow("Distance:", self.distance_spin)

        location_group.setLayout(location_layout)
        layout.addWidget(location_group)

        # Price fields
        price_group = QGroupBox("Price Range")
        price_layout = QFormLayout()

        self.min_price_spin = QSpinBox()
        self.min_price_spin.setRange(0, 100000000)
        self.min_price_spin.setSuffix(" €")
        self.min_price_spin.setSpecialValueText("Not set")
        price_layout.addRow("Min Price:", self.min_price_spin)

        self.max_price_spin = QSpinBox()
        self.max_price_spin.setRange(0, 100000000)
        self.max_price_spin.setSuffix(" €")
        self.max_price_spin.setSpecialValueText("Not set")
        price_layout.addRow("Max Price:", self.max_price_spin)

        price_group.setLayout(price_layout)
        layout.addWidget(price_group)

        # Pagination fields
        pagination_group = QGroupBox("Pagination")
        pagination_layout = QFormLayout()

        self.max_items_spin = QSpinBox()
        self.max_items_spin.setRange(1, 50)
        self.max_items_spin.setValue(20)
        pagination_layout.addRow("Max Items:", self.max_items_spin)

        self.num_page_spin = QSpinBox()
        self.num_page_spin.setRange(1, 1000)
        self.num_page_spin.setValue(1)
        pagination_layout.addRow("Page Number:", self.num_page_spin)

        pagination_group.setLayout(pagination_layout)
        layout.addWidget(pagination_group)

        # Other fields
        other_group = QGroupBox("Other Filters")
        other_layout = QFormLayout()

        self.locale_combo = QComboBox()
        self.locale_combo.addItems(["", "es_ES", "ca_ES", "en_GB", "pt_PT", "it_IT"])
        other_layout.addRow("Locale:", self.locale_combo)

        self.since_date_input = QLineEdit()
        self.since_date_input.setPlaceholderText("YYYY-MM-DD")
        other_layout.addRow("Since Date:", self.since_date_input)

        self.order_combo = QComboBox()
        self.order_combo.addItems(["", "asc", "desc"])
        other_layout.addRow("Order:", self.order_combo)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["", "price", "publicationDate", "size", "floor"])
        other_layout.addRow("Sort By:", self.sort_combo)

        self.has_multimedia_check = QCheckBox()
        other_layout.addRow("Has Multimedia:", self.has_multimedia_check)

        self.bank_offer_check = QCheckBox()
        other_layout.addRow("Bank Offer:", self.bank_offer_check)

        self.ad_ids_input = QLineEdit()
        self.ad_ids_input.setPlaceholderText("Comma-separated IDs")
        other_layout.addRow("Ad IDs:", self.ad_ids_input)

        other_group.setLayout(other_layout)
        layout.addWidget(other_group)

        # Search button
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        self.search_btn.setEnabled(False)
        layout.addWidget(self.search_btn)

        layout.addStretch()

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(scroll)
        return container

    def create_results_tab(self):
        """Create results display tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Info label
        self.results_info = QLabel("No results yet")
        self.results_info.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(self.results_info)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        # Export buttons
        export_layout = QHBoxLayout()
        
        self.export_json_btn = QPushButton("Export to JSON")
        self.export_json_btn.clicked.connect(self.export_json)
        self.export_json_btn.setEnabled(False)
        export_layout.addWidget(self.export_json_btn)

        self.export_csv_btn = QPushButton("Export to CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.export_csv_btn.setEnabled(False)
        export_layout.addWidget(self.export_csv_btn)

        layout.addLayout(export_layout)

        return widget

    def connect_api(self):
        """Connect to Idealista API"""
        api_key = self.api_key_input.text().strip()
        api_secret = self.api_secret_input.text().strip()

        if not api_key or not api_secret:
            QMessageBox.warning(self, "Missing Credentials", 
                              "Please enter both API key and secret.")
            return

        try:
            self.idealista_client = Idealista(api_key=api_key, api_secret=api_secret)
            self.statusBar().showMessage("Connected successfully!")
            self.search_btn.setEnabled(True)
            QMessageBox.information(self, "Success", "Connected to Idealista API!")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect: {str(e)}")
            self.statusBar().showMessage("Connection failed")

    def perform_search(self):
        """Perform search with current filters"""
        if not self.idealista_client:
            QMessageBox.warning(self, "Not Connected", 
                              "Please connect to the API first.")
            return

        try:
            # Build search parameters
            search_params = {
                "country": self.country_combo.currentText(),
                "operation": self.operation_combo.currentText(),
                "property_type": self.property_type_combo.currentText(),
            }

            # Optional location parameters
            if self.location_id_input.text().strip():
                search_params["location_id"] = self.location_id_input.text().strip()
            
            if self.center_input.text().strip():
                search_params["center"] = self.center_input.text().strip()
            
            if self.distance_spin.value() > 0:
                search_params["distance"] = self.distance_spin.value()

            # Optional locale
            if self.locale_combo.currentText():
                search_params["locale"] = self.locale_combo.currentText()

            # Pagination
            search_params["max_items"] = self.max_items_spin.value()
            search_params["num_page"] = self.num_page_spin.value()

            # Price range
            if self.min_price_spin.value() > 0:
                search_params["min_price"] = self.min_price_spin.value()
            
            if self.max_price_spin.value() > 0:
                search_params["max_price"] = self.max_price_spin.value()

            # Date filter
            if self.since_date_input.text().strip():
                search_params["since_date"] = self.since_date_input.text().strip()

            # Sorting
            if self.order_combo.currentText():
                search_params["order"] = self.order_combo.currentText()
            
            if self.sort_combo.currentText():
                search_params["sort"] = self.sort_combo.currentText()

            # Boolean filters
            if self.has_multimedia_check.isChecked():
                search_params["has_multimedia"] = True
            
            if self.bank_offer_check.isChecked():
                search_params["bank_offer"] = True

            # Ad IDs
            if self.ad_ids_input.text().strip():
                ad_ids = [id.strip() for id in self.ad_ids_input.text().split(",")]
                search_params["ad_ids"] = ad_ids

            search = Search(**search_params)

            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            self.search_btn.setEnabled(False)
            self.results_info.setText("Searching...")

            # Create worker thread
            self.worker = ApiWorker(self.idealista_client, search)
            self.worker.finished.connect(self.on_search_finished)
            self.worker.error.connect(self.on_search_error)
            self.worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Search Error", f"Failed to create search: {str(e)}")
            self.progress_bar.setVisible(False)
            self.search_btn.setEnabled(True)

    def on_search_finished(self, response):
        """Handle successful search"""
        self.progress_bar.setVisible(False)
        self.search_btn.setEnabled(True)
        self.last_response = response

        # Update info label
        info_text = (f"Found {response.total} properties | "
                    f"Page {response.actual_page}/{response.total_pages} | "
                    f"Showing {len(response.element_list)} items")
        self.results_info.setText(info_text)

        # Display results
        results_text = f"Search Results:\n"
        results_text += f"{'=' * 80}\n\n"
        
        for i, prop in enumerate(response.element_list, 1):
            results_text += f"Property {i}:\n"
            results_text += f"  Code: {prop.property_code}\n"
            results_text += f"  Type: {prop.property_type}\n"
            results_text += f"  Address: {prop.address}\n"
            results_text += f"  Price: {prop.price}\n"
            results_text += f"  Operation: {prop.operation}\n"
            results_text += f"{'-' * 80}\n"

        self.results_text.setPlainText(results_text)

        # Enable export buttons
        self.export_json_btn.setEnabled(True)
        self.export_csv_btn.setEnabled(True)

        self.statusBar().showMessage(f"Search completed: {response.total} results found")

    def on_search_error(self, error_msg):
        """Handle search error"""
        self.progress_bar.setVisible(False)
        self.search_btn.setEnabled(True)
        self.results_info.setText("Search failed")
        QMessageBox.critical(self, "Search Error", f"Search failed: {error_msg}")
        self.statusBar().showMessage("Search failed")

    def export_json(self):
        """Export results to JSON"""
        if not self.last_response:
            QMessageBox.warning(self, "No Results", "No results to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to JSON", 
            f"idealista_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                data = {
                    "metadata": {
                        "total": self.last_response.total,
                        "actual_page": self.last_response.actual_page,
                        "total_pages": self.last_response.total_pages,
                        "items_per_page": self.last_response.items_per_page,
                        "export_date": datetime.now().isoformat()
                    },
                    "properties": [prop.to_dict() for prop in self.last_response.element_list]
                }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                QMessageBox.information(self, "Success", 
                                      f"Results exported to:\n{file_path}")
                self.statusBar().showMessage(f"Exported to JSON: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", 
                                   f"Failed to export: {str(e)}")

    def export_csv(self):
        """Export results to CSV"""
        if not self.last_response:
            QMessageBox.warning(self, "No Results", "No results to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV",
            f"idealista_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )

        if file_path:
            try:
                # Collect all unique keys from all properties
                all_keys = set()
                for prop in self.last_response.element_list:
                    all_keys.update(prop.to_dict().keys())
                
                # Sort keys for consistent column order
                fieldnames = sorted(all_keys)

                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for prop in self.last_response.element_list:
                        writer.writerow(prop.to_dict())

                QMessageBox.information(self, "Success",
                                      f"Results exported to:\n{file_path}")
                self.statusBar().showMessage(f"Exported to CSV: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error",
                                   f"Failed to export: {str(e)}")


def main():
    app = QApplication(sys.argv)
    window = IdealistaGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
