import sys
import json
import csv
import os
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QTextEdit, QGroupBox, QFormLayout, QFileDialog,
    QMessageBox, QProgressBar, QTabWidget, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal
from idealista_api import Idealista, Search
from idealista_api.consts import URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# Translations
TRANSLATIONS = {
    'pt': {
        'window_title': 'Cliente API Idealista',
        'auth_tab': 'Autenticação',
        'search_tab': 'Filtros de Pesquisa',
        'results_tab': 'Resultados',
        'not_connected': 'Não conectado',
        'auth_group': 'Autenticação API',
        'api_key': 'Chave API:',
        'api_secret': 'Segredo API:',
        'api_key_placeholder': 'Digite sua chave API',
        'api_secret_placeholder': 'Digite seu segredo API',
        'connect': 'Conectar',
        'required_fields': 'Campos Obrigatórios',
        'country': 'País:',
        'operation': 'Operação:',
        'property_type': 'Tipo de Propriedade:',
        'sale': 'Venda',
        'rent': 'Arrendamento',
        'homes': 'Casas',
        'offices': 'Escritórios',
        'premises': 'Estabelecimentos',
        'garages': 'Garagens',
        'bedrooms': 'Quartos',
        'location': 'Localização',
        'location_id': 'ID de Localização:',
        'location_type': 'Tipo de Localização:',
        'all_types': 'Todos os Tipos',
        'select_location': 'Selecione uma localização...',
        'center': 'Centro (lat,lon):',
        'center_placeholder': 'ex: 40.4165,-3.70256',
        'distance': 'Distância:',
        'price_range': 'Faixa de Preço',
        'min_price': 'Preço Mínimo:',
        'max_price': 'Preço Máximo:',
        'pagination': 'Paginação',
        'max_items': 'Máximo de Itens:',
        'page_number': 'Número da Página:',
        'other_filters': 'Outros Filtros',
        'locale': 'Idioma:',
        'since_date': 'Desde Data:',
        'since_date_placeholder': 'AAAA-MM-DD',
        'order': 'Ordem:',
        'sort_by': 'Ordenar Por:',
        'has_multimedia': 'Tem Multimédia:',
        'bank_offer': 'Oferta Bancária:',
        'ad_ids': 'IDs de Anúncios:',
        'ad_ids_placeholder': 'IDs separados por vírgula',
        'search': 'Pesquisar',
        'no_results': 'Sem resultados ainda',
        'export_json': 'Exportar para JSON',
        'export_csv': 'Exportar para CSV',
        'missing_credentials': 'Credenciais em Falta',
        'missing_credentials_msg': 'Por favor, insira a chave e o segredo da API.',
        'connected_success': 'Conectado com sucesso!',
        'success': 'Sucesso',
        'connected_msg': 'Conectado à API Idealista!',
        'connection_error': 'Erro de Conexão',
        'connection_failed': 'Conexão falhou',
        'connection_failed_msg': 'Falha ao conectar',
        'not_connected_msg': 'Por favor, conecte-se à API primeiro.',
        'searching': 'A pesquisar...',
        'search_error': 'Erro de Pesquisa',
        'search_failed': 'Pesquisa falhou',
        'found_properties': 'Encontradas {} propriedades',
        'page_info': 'Página {}/{}',
        'showing_items': 'A mostrar {} itens',
        'search_completed': 'Pesquisa concluída: {} resultados encontrados',
        'search_results': 'Resultados da Pesquisa:',
        'property': 'Propriedade',
        'code': 'Código',
        'type': 'Tipo',
        'address': 'Endereço',
        'price': 'Preço',
        'no_results_export': 'Sem Resultados',
        'no_results_export_msg': 'Sem resultados para exportar.',
        'export_json_title': 'Exportar para JSON',
        'export_csv_title': 'Exportar para CSV',
        'json_files': 'Ficheiros JSON (*.json)',
        'csv_files': 'Ficheiros CSV (*.csv)',
        'export_success': 'Resultados exportados para:\n{}',
        'exported_json': 'Exportado para JSON: {}',
        'exported_csv': 'Exportado para CSV: {}',
        'export_error': 'Erro de Exportação',
        'export_failed': 'Falha ao exportar: {}',
        'language': 'Idioma:',
        'not_set': 'Não definido',
        'asc': 'Ascendente',
        'desc': 'Descendente',
        'auto_connect_success': 'Conectado automaticamente à API!',
        'auto_connect_failed': 'Falha na conexão automática. Por favor, insira as credenciais manualmente.',
        'env_not_found': 'Arquivo .env não encontrado. Por favor, configure as credenciais manualmente.',
        'fetch_all_pages': 'Buscar Todas as Páginas',
        'fetching_page': 'A buscar página {} de {}...',
        'all_pages_fetched': 'Todas as páginas buscadas! Total: {} propriedades',
        'delay_seconds': 'Atraso entre páginas (segundos):',
        'auto_pagination': 'Paginação Automática',
        'enable_auto_fetch': 'Ativar busca automática de todas as páginas',
        'collected_properties': 'Propriedades coletadas: {}',
        'fetch_cancelled': 'Busca cancelada pelo utilizador',
        'cancel_fetch': 'Cancelar Busca',
    },
    'en': {
        'window_title': 'Idealista API Client',
        'auth_tab': 'Authentication',
        'search_tab': 'Search Filters',
        'results_tab': 'Results',
        'not_connected': 'Not connected',
        'auth_group': 'API Authentication',
        'api_key': 'API Key:',
        'api_secret': 'API Secret:',
        'api_key_placeholder': 'Enter your API key',
        'api_secret_placeholder': 'Enter your API secret',
        'connect': 'Connect',
        'required_fields': 'Required Fields',
        'country': 'Country:',
        'operation': 'Operation:',
        'property_type': 'Property Type:',
        'sale': 'Sale',
        'rent': 'Rent',
        'homes': 'Homes',
        'offices': 'Offices',
        'premises': 'Premises',
        'garages': 'Garages',
        'bedrooms': 'Bedrooms',
        'location': 'Location',
        'location_id': 'Location ID:',
        'location_type': 'Location Type:',
        'all_types': 'All Types',
        'select_location': 'Select a location...',
        'center': 'Center (lat,lon):',
        'center_placeholder': 'e.g., 40.4165,-3.70256',
        'distance': 'Distance:',
        'price_range': 'Price Range',
        'min_price': 'Min Price:',
        'max_price': 'Max Price:',
        'pagination': 'Pagination',
        'max_items': 'Max Items:',
        'page_number': 'Page Number:',
        'other_filters': 'Other Filters',
        'locale': 'Locale:',
        'since_date': 'Since Date:',
        'since_date_placeholder': 'YYYY-MM-DD',
        'order': 'Order:',
        'sort_by': 'Sort By:',
        'has_multimedia': 'Has Multimedia:',
        'bank_offer': 'Bank Offer:',
        'ad_ids': 'Ad IDs:',
        'ad_ids_placeholder': 'Comma-separated IDs',
        'search': 'Search',
        'no_results': 'No results yet',
        'export_json': 'Export to JSON',
        'export_csv': 'Export to CSV',
        'missing_credentials': 'Missing Credentials',
        'missing_credentials_msg': 'Please enter both API key and secret.',
        'connected_success': 'Connected successfully!',
        'success': 'Success',
        'connected_msg': 'Connected to Idealista API!',
        'connection_error': 'Connection Error',
        'connection_failed': 'Connection failed',
        'connection_failed_msg': 'Failed to connect',
        'not_connected_msg': 'Please connect to the API first.',
        'searching': 'Searching...',
        'search_error': 'Search Error',
        'search_failed': 'Search failed',
        'found_properties': 'Found {} properties',
        'page_info': 'Page {}/{}',
        'showing_items': 'Showing {} items',
        'search_completed': 'Search completed: {} results found',
        'search_results': 'Search Results:',
        'property': 'Property',
        'code': 'Code',
        'type': 'Type',
        'address': 'Address',
        'price': 'Price',
        'no_results_export': 'No Results',
        'no_results_export_msg': 'No results to export.',
        'export_json_title': 'Export to JSON',
        'export_csv_title': 'Export to CSV',
        'json_files': 'JSON Files (*.json)',
        'csv_files': 'CSV Files (*.csv)',
        'export_success': 'Results exported to:\n{}',
        'exported_json': 'Exported to JSON: {}',
        'exported_csv': 'Exported to CSV: {}',
        'export_error': 'Export Error',
        'export_failed': 'Failed to export: {}',
        'language': 'Language:',
        'not_set': 'Not set',
        'asc': 'Ascending',
        'desc': 'Descending',
        'auto_connect_success': 'Automatically connected to API!',
        'auto_connect_failed': 'Auto-connection failed. Please enter credentials manually.',
        'env_not_found': '.env file not found. Please configure credentials manually.',
        'fetch_all_pages': 'Fetch All Pages',
        'fetching_page': 'Fetching page {} of {}...',
        'all_pages_fetched': 'All pages fetched! Total: {} properties',
        'delay_seconds': 'Delay between pages (seconds):',
        'auto_pagination': 'Auto Pagination',
        'enable_auto_fetch': 'Enable automatic fetch of all pages',
        'collected_properties': 'Properties collected: {}',
        'fetch_cancelled': 'Fetch cancelled by user',
        'cancel_fetch': 'Cancel Fetch',
    }
}


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


class MultiPageWorker(QThread):
    """Worker thread to handle multi-page API calls with delay"""
    progress = Signal(int, int, int)  # current_page, total_pages, properties_count
    finished = Signal(list)  # Emits list of all Response objects
    error = Signal(str)  # Emits error message
    
    def __init__(self, idealista_client, search_params, delay_seconds=2):
        super().__init__()
        self.idealista_client = idealista_client
        self.search_params = search_params
        self.delay_seconds = delay_seconds
        self.should_cancel = False
        
    def cancel(self):
        """Cancel the multi-page fetch"""
        self.should_cancel = True
    
    def run(self):
        import time
        from idealista_api import Search
        
        all_responses = []
        total_properties = 0
        
        try:
            # First request to get total pages
            first_search = Search(**self.search_params)
            first_response = self.idealista_client.query(first_search)
            all_responses.append(first_response)
            total_properties += len(first_response.element_list)
            
            total_pages = first_response.total_pages
            logger.info(f"Total pages to fetch: {total_pages}")
            
            self.progress.emit(1, total_pages, total_properties)
            
            # Fetch remaining pages
            for page in range(2, total_pages + 1):
                if self.should_cancel:
                    logger.info("Multi-page fetch cancelled by user")
                    break
                    
                # Delay before next request
                time.sleep(self.delay_seconds)
                
                # Update page number
                page_params = self.search_params.copy()
                page_params['num_page'] = page
                
                search = Search(**page_params)
                response = self.idealista_client.query(search)
                all_responses.append(response)
                total_properties += len(response.element_list)
                
                logger.info(f"Fetched page {page}/{total_pages} - {len(response.element_list)} properties")
                self.progress.emit(page, total_pages, total_properties)
            
            self.finished.emit(all_responses)
            
        except Exception as e:
            logger.error(f"Error in multi-page fetch: {e}")
            self.error.emit(str(e))


class IdealistaGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.idealista_client = None
        self.last_response = None
        self.all_responses = []  # Store all responses from multi-page fetch
        self.current_language = 'pt'  # Default to Portuguese
        self.locations_data = self.load_locations()
        self.multi_page_worker = None  # Track multi-page worker
        self.init_ui()
        # Automatically connect to API after UI is initialized
        self.auto_connect_api()

    def tr(self, key):
        """Translate a key to the current language"""
        return TRANSLATIONS[self.current_language].get(key, key)

    def load_locations(self):
        """Load location data from JSON file"""
        try:
            json_path = Path(__file__).parent / "locationId_list.json"
            
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Warning: locationId_list.json not found at {json_path}")
                return []
        except Exception as e:
            print(f"Error loading locations: {e}")
            return []

    def get_location_types(self):
        """Get unique location types from loaded data"""
        types = set()
        for loc in self.locations_data:
            types.add(loc.get('type', ''))
        return sorted(types)

    def filter_locations_by_type(self, location_type):
        """Filter locations by type"""
        if not location_type or location_type == self.tr('all_types'):
            return self.locations_data
        return [loc for loc in self.locations_data if loc.get('type') == location_type]

    def load_env_credentials(self):
        """Load API credentials from .env file"""
        # Get project root directory (parent of idealista_api_ui)
        project_root = Path(__file__).parent.parent
        env_path = project_root / '.env'
        
        if env_path.exists():
            load_dotenv(env_path)
            api_key = os.getenv('API_KEY')
            api_secret = os.getenv('API_SECRET')
            return api_key, api_secret
        return None, None

    def auto_connect_api(self):
        """Automatically connect to API using credentials from .env file"""
        api_key, api_secret = self.load_env_credentials()
        
        if api_key and api_secret:
            # Populate the input fields
            self.api_key_input.setText(api_key)
            self.api_secret_input.setText(api_secret)
            
            try:
                self.idealista_client = Idealista(api_key=api_key, api_secret=api_secret)
                self.statusBar().showMessage(self.tr('auto_connect_success'))
                self.search_btn.setEnabled(True)
            except Exception as e:
                self.statusBar().showMessage(self.tr('auto_connect_failed'))
                print(f"Auto-connection error: {e}")
        else:
            self.statusBar().showMessage(self.tr('env_not_found'))

    def init_ui(self):
        self.setWindowTitle(self.tr('window_title'))
        self.setMinimumSize(900, 700)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Language selector at top
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(self.tr('language')))
        self.language_combo = QComboBox()
        self.language_combo.addItems(['Português', 'English'])
        self.language_combo.setCurrentIndex(0)  # Portuguese as default
        self.language_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch()
        main_layout.addLayout(lang_layout)

        # Create tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Authentication tab
        self.auth_tab = self.create_auth_tab()
        self.tabs.addTab(self.auth_tab, self.tr('auth_tab'))

        # Search filters tab
        self.search_tab = self.create_search_tab()
        self.tabs.addTab(self.search_tab, self.tr('search_tab'))

        # Results tab
        self.results_tab = self.create_results_tab()
        self.tabs.addTab(self.results_tab, self.tr('results_tab'))

        # Status bar
        self.statusBar().showMessage(self.tr('not_connected'))

    def change_language(self, index):
        """Change the application language"""
        self.current_language = 'pt' if index == 0 else 'en'
        self.refresh_ui()

    def refresh_ui(self):
        """Refresh all UI text with current language"""
        self.setWindowTitle(self.tr('window_title'))
        self.statusBar().showMessage(self.tr('not_connected') if not self.idealista_client else self.tr('connected_success'))
        
        # Update tab titles
        self.tabs.setTabText(0, self.tr('auth_tab'))
        self.tabs.setTabText(1, self.tr('search_tab'))
        self.tabs.setTabText(2, self.tr('results_tab'))
        
        # Recreate tabs with new language
        current_tab = self.tabs.currentIndex()
        
        # Store current values before refresh
        api_key = getattr(self, 'api_key_input', None)
        api_secret = getattr(self, 'api_secret_input', None)
        old_key = api_key.text() if api_key else ""
        old_secret = api_secret.text() if api_secret else ""
        
        # Remove old tabs
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)
        
        # Create new tabs
        self.auth_tab = self.create_auth_tab()
        self.tabs.addTab(self.auth_tab, self.tr('auth_tab'))
        
        # Restore auth values
        if old_key:
            self.api_key_input.setText(old_key)
        if old_secret:
            self.api_secret_input.setText(old_secret)
        
        self.search_tab = self.create_search_tab()
        self.tabs.addTab(self.search_tab, self.tr('search_tab'))
        
        self.results_tab = self.create_results_tab()
        self.tabs.addTab(self.results_tab, self.tr('results_tab'))
        
        # Restore tab selection
        self.tabs.setCurrentIndex(current_tab)

    def create_auth_tab(self):
        """Create authentication tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Auth group
        auth_group = QGroupBox(self.tr('auth_group'))
        auth_layout = QFormLayout()

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText(self.tr('api_key_placeholder'))
        auth_layout.addRow(self.tr('api_key'), self.api_key_input)

        self.api_secret_input = QLineEdit()
        self.api_secret_input.setPlaceholderText(self.tr('api_secret_placeholder'))
        self.api_secret_input.setEchoMode(QLineEdit.Password)
        auth_layout.addRow(self.tr('api_secret'), self.api_secret_input)

        # Connect button
        self.connect_btn = QPushButton(self.tr('connect'))
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
        required_group = QGroupBox(self.tr('required_fields'))
        required_layout = QFormLayout()

        self.country_combo = QComboBox()
        self.country_combo.addItems(["es", "pt", "it"])
        self.country_combo.setCurrentText("pt")  # Default to Portugal
        required_layout.addRow(self.tr('country'), self.country_combo)

        self.operation_combo = QComboBox()
        operation_items = {
            'sale': self.tr('sale'),
            'rent': self.tr('rent')
        }
        for key, value in operation_items.items():
            self.operation_combo.addItem(value, key)
        required_layout.addRow(self.tr('operation'), self.operation_combo)

        self.property_type_combo = QComboBox()
        property_types = {
            'homes': self.tr('homes'),
            'offices': self.tr('offices'),
            'premises': self.tr('premises'),
            'garages': self.tr('garages'),
            'bedrooms': self.tr('bedrooms')
        }
        for key, value in property_types.items():
            self.property_type_combo.addItem(value, key)
        required_layout.addRow(self.tr('property_type'), self.property_type_combo)

        required_group.setLayout(required_layout)
        layout.addWidget(required_group)

        # Location fields
        location_group = QGroupBox(self.tr('location'))
        location_layout = QFormLayout()

        # Location type filter
        self.location_type_combo = QComboBox()
        self.location_type_combo.addItem(self.tr('all_types'))
        if self.locations_data:
            self.location_type_combo.addItems(self.get_location_types())
        self.location_type_combo.currentTextChanged.connect(self.on_location_type_changed)
        location_layout.addRow(self.tr('location_type'), self.location_type_combo)

        # Location ID dropdown
        self.location_id_combo = QComboBox()
        self.location_id_combo.setEditable(True)
        self.location_id_combo.lineEdit().setPlaceholderText(self.tr('select_location'))
        self.populate_location_combo()
        location_layout.addRow(self.tr('location_id'), self.location_id_combo)

        self.center_input = QLineEdit()
        self.center_input.setPlaceholderText(self.tr('center_placeholder'))
        location_layout.addRow(self.tr('center'), self.center_input)

        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setRange(0, 100000)
        self.distance_spin.setSuffix(" m")
        self.distance_spin.setSpecialValueText("")
        location_layout.addRow(self.tr('distance'), self.distance_spin)

        location_group.setLayout(location_layout)
        layout.addWidget(location_group)

        # Price fields
        price_group = QGroupBox(self.tr('price_range'))
        price_layout = QFormLayout()

        self.min_price_spin = QSpinBox()
        self.min_price_spin.setRange(0, 100000000)
        self.min_price_spin.setSuffix(" €")
        self.min_price_spin.setSpecialValueText("")
        price_layout.addRow(self.tr('min_price'), self.min_price_spin)

        self.max_price_spin = QSpinBox()
        self.max_price_spin.setRange(0, 100000000)
        self.max_price_spin.setSuffix(" €")
        self.max_price_spin.setSpecialValueText("")
        price_layout.addRow(self.tr('max_price'), self.max_price_spin)

        price_group.setLayout(price_layout)
        layout.addWidget(price_group)

        # Pagination fields
        pagination_group = QGroupBox(self.tr('pagination'))
        pagination_layout = QFormLayout()

        self.max_items_spin = QSpinBox()
        self.max_items_spin.setRange(1, 50)
        self.max_items_spin.setValue(20)
        pagination_layout.addRow(self.tr('max_items'), self.max_items_spin)

        self.num_page_spin = QSpinBox()
        self.num_page_spin.setRange(1, 1000)
        self.num_page_spin.setValue(1)
        pagination_layout.addRow(self.tr('page_number'), self.num_page_spin)

        # Auto-pagination controls
        self.auto_fetch_check = QCheckBox(self.tr('enable_auto_fetch'))
        pagination_layout.addRow("", self.auto_fetch_check)

        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 10)
        self.delay_spin.setValue(2)
        self.delay_spin.setSuffix(" s")
        pagination_layout.addRow(self.tr('delay_seconds'), self.delay_spin)

        pagination_group.setLayout(pagination_layout)
        layout.addWidget(pagination_group)

        # Other fields
        other_group = QGroupBox(self.tr('other_filters'))
        other_layout = QFormLayout()

        self.locale_combo = QComboBox()
        self.locale_combo.addItems(["", "es_ES", "ca_ES", "en_GB", "pt_PT", "it_IT"])
        other_layout.addRow(self.tr('locale'), self.locale_combo)

        self.since_date_input = QLineEdit()
        self.since_date_input.setPlaceholderText(self.tr('since_date_placeholder'))
        other_layout.addRow(self.tr('since_date'), self.since_date_input)

        self.order_combo = QComboBox()
        order_items = ["", self.tr('asc'), self.tr('desc')]
        self.order_combo.addItems(order_items)
        other_layout.addRow(self.tr('order'), self.order_combo)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["", "price", "publicationDate", "size", "floor"])
        other_layout.addRow(self.tr('sort_by'), self.sort_combo)

        self.has_multimedia_check = QCheckBox()
        other_layout.addRow(self.tr('has_multimedia'), self.has_multimedia_check)

        self.bank_offer_check = QCheckBox()
        other_layout.addRow(self.tr('bank_offer'), self.bank_offer_check)

        self.ad_ids_input = QLineEdit()
        self.ad_ids_input.setPlaceholderText(self.tr('ad_ids_placeholder'))
        other_layout.addRow(self.tr('ad_ids'), self.ad_ids_input)

        other_group.setLayout(other_layout)
        layout.addWidget(other_group)

        # Search button
        self.search_btn = QPushButton(self.tr('search'))
        self.search_btn.clicked.connect(self.perform_search)
        self.search_btn.setEnabled(False)
        layout.addWidget(self.search_btn)

        layout.addStretch()

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(scroll)
        return container

    def populate_location_combo(self, location_type=None):
        """Populate location combo with filtered locations"""
        self.location_id_combo.clear()
        
        filtered_locations = self.filter_locations_by_type(location_type)
        
        for loc in filtered_locations:
            display_text = f"{loc['name']} ({loc['type']})"
            self.location_id_combo.addItem(display_text, loc['id'])

    def on_location_type_changed(self, location_type):
        """Handle location type filter change"""
        if location_type == self.tr('all_types'):
            self.populate_location_combo(None)
        else:
            self.populate_location_combo(location_type)

    def create_results_tab(self):
        """Create results display tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Info label
        self.results_info = QLabel(self.tr('no_results'))
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
        
        self.export_json_btn = QPushButton(self.tr('export_json'))
        self.export_json_btn.clicked.connect(self.export_json)
        self.export_json_btn.setEnabled(False)
        export_layout.addWidget(self.export_json_btn)

        self.export_csv_btn = QPushButton(self.tr('export_csv'))
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.export_csv_btn.setEnabled(False)
        export_layout.addWidget(self.export_csv_btn)

        layout.addLayout(export_layout)

        return widget

    def connect_api(self):
        """Connect to Idealista API (manual connection)"""
        api_key = self.api_key_input.text().strip()
        api_secret = self.api_secret_input.text().strip()

        if not api_key or not api_secret:
            QMessageBox.warning(self, self.tr('missing_credentials'), 
                              self.tr('missing_credentials_msg'))
            return

        try:
            self.idealista_client = Idealista(api_key=api_key, api_secret=api_secret)
            self.statusBar().showMessage(self.tr('connected_success'))
            self.search_btn.setEnabled(True)
            QMessageBox.information(self, self.tr('success'), self.tr('connected_msg'))
        except Exception as e:
            QMessageBox.critical(self, self.tr('connection_error'), f"{self.tr('connection_failed_msg')}: {str(e)}")
            self.statusBar().showMessage(self.tr('connection_failed'))

    def perform_search(self):
        """Perform search with current filters"""
        if not self.idealista_client:
            QMessageBox.warning(self, self.tr('not_connected'), 
                              self.tr('not_connected_msg'))
            return

        try:
            # Build search parameters
            search_params = {
                "country": self.country_combo.currentText(),
                "operation": self.operation_combo.currentData(),
                "property_type": self.property_type_combo.currentData(),
            }

            # Location ID from combo
            if self.location_id_combo.currentData():
                search_params["location_id"] = self.location_id_combo.currentData()
            elif self.location_id_combo.currentText().strip():
                # If user typed something manually
                search_params["location_id"] = self.location_id_combo.currentText().strip()
            
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

            # Sorting - map translated values back to API values
            order_text = self.order_combo.currentText()
            if order_text == self.tr('asc'):
                search_params["order"] = "asc"
            elif order_text == self.tr('desc'):
                search_params["order"] = "desc"
            
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

            # Log API request details
            api_url = URL.format(country=search_params['country'])
            logger.info("=" * 80)
            logger.info("API Request")
            logger.info("=" * 80)
            logger.info(f"URL: {api_url}")
            logger.info("Filters:")
            for key, value in search_params.items():
                logger.info(f"  {key}: {value}")
            logger.info("=" * 80)

            # Show progress
            self.progress_bar.setVisible(True)
            self.search_btn.setEnabled(False)
            
            # Check if auto-fetch all pages is enabled
            if self.auto_fetch_check.isChecked():
                # Multi-page fetch
                self.progress_bar.setRange(0, 100)  # Determinate
                self.results_info.setText(self.tr('searching'))
                self.all_responses = []
                
                # Update button to cancel
                self.search_btn.setText(self.tr('cancel_fetch'))
                self.search_btn.setEnabled(True)
                self.search_btn.clicked.disconnect()
                self.search_btn.clicked.connect(self.cancel_multi_page_fetch)
                
                delay_seconds = self.delay_spin.value()
                self.multi_page_worker = MultiPageWorker(self.idealista_client, search_params, delay_seconds)
                self.multi_page_worker.progress.connect(self.on_multi_page_progress)
                self.multi_page_worker.finished.connect(self.on_multi_page_finished)
                self.multi_page_worker.error.connect(self.on_search_error)
                self.multi_page_worker.start()
            else:
                # Single page fetch
                self.progress_bar.setRange(0, 0)  # Indeterminate
                self.results_info.setText(self.tr('searching'))
                
                self.worker = ApiWorker(self.idealista_client, search)
                self.worker.finished.connect(self.on_search_finished)
                self.worker.error.connect(self.on_search_error)
                self.worker.start()

        except Exception as e:
            QMessageBox.critical(self, self.tr('search_error'), f"{self.tr('search_failed')}: {str(e)}")
            self.progress_bar.setVisible(False)
            self.search_btn.setEnabled(True)
            self.reset_search_button()

    def on_search_finished(self, response):
        """Handle successful search"""
        self.progress_bar.setVisible(False)
        self.search_btn.setEnabled(True)
        self.last_response = response

        # Update info label
        info_parts = [
            self.tr('found_properties').format(response.total),
            self.tr('page_info').format(response.actual_page, response.total_pages),
            self.tr('showing_items').format(len(response.element_list))
        ]
        info_text = " | ".join(info_parts)
        self.results_info.setText(info_text)

        # Display results
        results_text = f"{self.tr('search_results')}\n"
        results_text += f"{'=' * 80}\n\n"
        
        for i, prop in enumerate(response.element_list, 1):
            results_text += f"{self.tr('property')} {i}:\n"
            results_text += f"  {self.tr('code')}: {prop.property_code}\n"
            results_text += f"  {self.tr('type')}: {prop.property_type}\n"
            results_text += f"  {self.tr('address')}: {prop.address}\n"
            results_text += f"  {self.tr('price')}: {prop.price}\n"
            results_text += f"  {self.tr('operation')}: {prop.operation}\n"
            results_text += f"{'-' * 80}\n"

        self.results_text.setPlainText(results_text)

        # Enable export buttons
        self.export_json_btn.setEnabled(True)
        self.export_csv_btn.setEnabled(True)

        self.statusBar().showMessage(self.tr('search_completed').format(response.total))

    def on_search_error(self, error_msg):
        """Handle search error"""
        self.progress_bar.setVisible(False)
        self.reset_search_button()
        self.results_info.setText(self.tr('search_failed'))
        QMessageBox.critical(self, self.tr('search_error'), f"{self.tr('search_failed')}: {error_msg}")
        self.statusBar().showMessage(self.tr('search_failed'))

    def reset_search_button(self):
        """Reset search button to original state"""
        self.search_btn.setText(self.tr('search'))
        self.search_btn.setEnabled(True)
        try:
            self.search_btn.clicked.disconnect()
        except:
            pass
        self.search_btn.clicked.connect(self.perform_search)

    def cancel_multi_page_fetch(self):
        """Cancel the multi-page fetch"""
        if self.multi_page_worker:
            self.multi_page_worker.cancel()
        self.progress_bar.setVisible(False)
        self.reset_search_button()
        self.statusBar().showMessage(self.tr('fetch_cancelled'))

    def on_multi_page_progress(self, current_page, total_pages, properties_count):
        """Handle multi-page fetch progress"""
        progress_percent = int((current_page / total_pages) * 100)
        self.progress_bar.setValue(progress_percent)
        
        status_text = self.tr('fetching_page').format(current_page, total_pages)
        self.results_info.setText(f"{status_text} | {self.tr('collected_properties').format(properties_count)}")
        logger.info(f"Progress: Page {current_page}/{total_pages} - Total properties: {properties_count}")

    def on_multi_page_finished(self, all_responses):
        """Handle multi-page fetch completion"""
        self.progress_bar.setVisible(False)
        self.reset_search_button()
        self.all_responses = all_responses
        
        # Combine all responses
        total_properties = sum(len(resp.element_list) for resp in all_responses)
        
        # Use the first response metadata
        first_response = all_responses[0]
        
        # Update info label
        info_text = self.tr('all_pages_fetched').format(total_properties)
        self.results_info.setText(info_text)

        # Display results from all pages
        results_text = f"{self.tr('search_results')}\n"
        results_text += f"{'=' * 80}\n"
        results_text += f"Total pages fetched: {len(all_responses)}\n"
        results_text += f"Total properties: {total_properties}\n"
        results_text += f"{'=' * 80}\n\n"
        
        property_num = 1
        for response in all_responses:
            for prop in response.element_list:
                results_text += f"{self.tr('property')} {property_num}:\n"
                results_text += f"  {self.tr('code')}: {prop.property_code}\n"
                results_text += f"  {self.tr('type')}: {prop.property_type}\n"
                results_text += f"  {self.tr('address')}: {prop.address}\n"
                results_text += f"  {self.tr('price')}: {prop.price}\n"
                results_text += f"  {self.tr('operation')}: {prop.operation}\n"
                results_text += f"{'-' * 80}\n"
                property_num += 1

        self.results_text.setPlainText(results_text)

        # Enable export buttons
        self.export_json_btn.setEnabled(True)
        self.export_csv_btn.setEnabled(True)

        self.statusBar().showMessage(self.tr('search_completed').format(total_properties))
        logger.info(f"Multi-page fetch completed: {total_properties} properties from {len(all_responses)} pages")

    def export_json(self):
        """Export results to JSON"""
        # Check if we have multi-page or single-page results
        if self.all_responses:
            responses = self.all_responses
            is_multi_page = True
        elif self.last_response:
            responses = [self.last_response]
            is_multi_page = False
        else:
            QMessageBox.warning(self, self.tr('no_results_export'), self.tr('no_results_export_msg'))
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, self.tr('export_json_title'), 
            f"idealista_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            self.tr('json_files')
        )

        if file_path:
            try:
                # Collect all properties from all responses
                all_properties = []
                for response in responses:
                    all_properties.extend([prop.to_dict() for prop in response.element_list])
                
                # Use first response for metadata
                first_response = responses[0]
                
                data = {
                    "metadata": {
                        "total": sum(resp.total for resp in responses) if is_multi_page else first_response.total,
                        "pages_fetched": len(responses),
                        "total_pages": first_response.total_pages,
                        "items_per_page": first_response.items_per_page,
                        "properties_count": len(all_properties),
                        "export_date": datetime.now().isoformat(),
                        "multi_page_fetch": is_multi_page
                    },
                    "properties": all_properties
                }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                QMessageBox.information(self, self.tr('success'), 
                                      self.tr('export_success').format(file_path))
                self.statusBar().showMessage(self.tr('exported_json').format(file_path))
            except Exception as e:
                QMessageBox.critical(self, self.tr('export_error'), 
                                   self.tr('export_failed').format(str(e)))

    def export_csv(self):
        """Export results to CSV"""
        # Check if we have multi-page or single-page results
        if self.all_responses:
            responses = self.all_responses
        elif self.last_response:
            responses = [self.last_response]
        else:
            QMessageBox.warning(self, self.tr('no_results_export'), self.tr('no_results_export_msg'))
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, self.tr('export_csv_title'),
            f"idealista_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            self.tr('csv_files')
        )

        if file_path:
            try:
                # Collect all properties from all responses
                all_properties = []
                for response in responses:
                    all_properties.extend(response.element_list)
                
                # Collect all unique keys from all properties
                all_keys = set()
                for prop in all_properties:
                    all_keys.update(prop.to_dict().keys())
                
                # Sort keys for consistent column order
                fieldnames = sorted(all_keys)

                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for prop in all_properties:
                        writer.writerow(prop.to_dict())

                QMessageBox.information(self, self.tr('success'),
                                      self.tr('export_success').format(file_path))
                self.statusBar().showMessage(self.tr('exported_csv').format(file_path))
            except Exception as e:
                QMessageBox.critical(self, self.tr('export_error'),
                                   self.tr('export_failed').format(str(e)))


def main():
    app = QApplication(sys.argv)
    window = IdealistaGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
