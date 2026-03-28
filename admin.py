import tkinter as tk
from tkinter import ttk
import API
from tkcalendar import DateEntry

from Calc import DiagnosticCalculator

# Constants
COLORS = {
    'bg': '#F5F5F5',
    'accent': '#3498DB',
    'entry_bg': '#FFFFFF',
    'text': '#2C3E50',
    'highlight': 'black'
}

FRAME_DEFINITIONS = {
    'personal_data': {
        'description': 'Ваши личные данные',
        'api_url': 'personal_data',
        'tab_name': 'Личные данные'
    },
    'user_info': {
        'description': 'Данные пользователей (основная информация о пациентах)',
        'api_url': 'users',
        'tab_name': 'Данные пользователей'
    },
    # 'medicine': {
    #     'description': 'Лекарства и препараты (список медикаментов)',
    #     'api_url': 'medications',
    #     'tab_name': 'Лекарства'
    # },
    'diseases': {
        'description': 'Заболевания (диагнозы и медицинские состояния)',
        'api_url': 'diseases',
        'tab_name': 'Заболевания'
    },
    'metrics': {
        'description': 'Метрики окуломоторной активности',
        'api_url': 'eye-metrics',
        'tab_name': 'Метрики окуломоторной активности'
    },
    'medical_norms_groups':{
        'description': 'Группы медицинских норм',
        'api_url': 'reference-groups',
        'tab_name': 'Группы медицинских норм'
    },
    'medical_norms': {
        'description': 'Референсные значения показателей ОМА',
        'api_url': 'reference-values',
        'tab_name': 'Референсные значения'
    },
    'thresholds': {
        'description': 'Пороговые значения заболеваний (критические показатели для диагностики)',
        'api_url': 'diagnostic-thresholds',
        'tab_name': 'Пороговые значения заболеваний'
    },
    'weights' :{
        'description': 'Весовые коэффициенты показателей ОМА',
        'api_url': 'weights',
        'tab_name': 'Весовые коэффициенты'
    },
    'results': {
        'description': 'Обследования и результаты тестирования',
        'api_url': 'test-results',
        'tab_name': 'Обследования'
    }
}

class ComboBoxWithHiddenValues(ttk.Combobox):
    def __init__(self, parent, data, display_key, value_key="id", initial_value=None, **kwargs):
        self.data = data
        self.display_key = display_key
        self.value_key = value_key
        print(display_key, value_key)
        # Create display values
        display_values = [item[display_key] for item in data]

        # Initialize the combobox
        super().__init__(parent, values=display_values, state="readonly", **kwargs)

        # Set initial value if provided
        if initial_value is not None:
            self.set_by_value(initial_value)

    def set_by_value(self, value):
        """Set selection by hidden value (e.g., id)"""
        for item in self.data:
            if item[self.value_key] == value:
                self.set(item[self.display_key])
                return True
        # If value not found, clear selection
        self.set('')
        return False

    def set_by_display(self, display_text):
        """Set selection by display text"""
        if display_text in self['values']:
            self.set(display_text)
            return True
        return False

    def get_selected_value(self):
        """Returns the hidden value for the selected item"""
        selected_display = self.get()
        for item in self.data:
            if item[self.display_key] == selected_display:
                return item[self.value_key]
        return None

    def get_selected_data(self):
        """Returns the entire data dict for the selected item"""
        selected_display = self.get()
        for item in self.data:
            if item[self.display_key] == selected_display:
                return item
        return None

class AdminWindow:
    def __init__(self, user_id, role):
        self.diagnostic_calculator = DiagnosticCalculator()
        self.root = tk.Tk()
        self.frame_data_dict = FRAME_DEFINITIONS.copy()
        selected_keys = []
        match role:
            case 'Инженер по знаниям':
                selected_keys = ['personal_data', 'weights', 'thresholds', 'medical_norms', 'medical_norms_groups']
            case 'Пациент':
                selected_keys = ['personal_data', 'results']
            case 'Врач':
                selected_keys = ['personal_data', 'weights', 'results']
        if(role != 'Администратор'):
            self.frame_data_dict = {key: FRAME_DEFINITIONS[key] for key in selected_keys}
        self._setup_window()
        self._create_widgets()
        self._bind_events()
        self.user_id = user_id
        self.role = role
        self.validation_rules = self._setup_validation_rules()

    def _setup_validation_rules(self):
        """Define validation rules for each field type"""
        return {
            'personal_data': {
                'username': {'required': True, 'numeric': False},
                'password': {'required': True, 'numeric': False},
                'name': {'required': True, 'numeric': False},
                'birth_date': {'required': False, 'numeric': False},
                'gender': {'required': False, 'numeric': False}
            },
            'users': {
                'username': {'required': True, 'numeric': False},
                'password': {'required': True, 'numeric': False},
                'name': {'required': True, 'numeric': False},
                'role_id': {'required': True, 'numeric': True},
                'birth_date': {'required': False, 'numeric': False},
                'gender': {'required': False, 'numeric': False}
            },
            'diseases': {
                'name': {'required': True, 'numeric': False}
            },
            'eye-metrics': {
                'name': {'required': True, 'numeric': False},
                'unit': {'required': True, 'numeric': False}
            },
            'reference-groups': {
                'name': {'required': True, 'numeric': False},
                'age_min': {'required': True, 'numeric': True},
                'age_max': {'required': True, 'numeric': True},
                'sample_size': {'required': True, 'numeric': True}
            },
            'reference-values': {
                'metric_id': {'required': True, 'numeric': True},
                'reference_group_id': {'required': True, 'numeric': True},
                'p5': {'required': True, 'numeric': True},
                'p50': {'required': True, 'numeric': True},
                'p95': {'required': True, 'numeric': True},
                'std_dev': {'required': True, 'numeric': True}
            },
            'weights': {
                'disease_id': {'required': True, 'numeric': True},
                'metric_id': {'required': True, 'numeric': True},
                'weight': {'required': True, 'numeric': True}
            },
            'diagnostic-thresholds': {
                'disease_id': {'required': True, 'numeric': True},
                'Tmax': {'required': False, 'numeric': True},
                'Tmin': {'required': False, 'numeric': True},
                'C': {'required': True, 'numeric': True}
            },
            'test-results': {
                'metric_values': {'required': False, 'numeric': True},
                'doctor_id': {'required': True, 'numeric': True},
                'patient_id': {'required': True, 'numeric': True}
            }
        }

    def validate_entry(self, value, field_name, api_url):
        """
        Validate a single entry based on its rules

        Args:
            value: The value to validate
            field_name: Name of the field (e.g., 'username', 'age_min')
            api_url: API endpoint name (e.g., 'users', 'reference-values')

        Returns:
            tuple: (is_valid, error_message)
        """
        # Get validation rules for this field
        if api_url not in self.validation_rules:
            return True, ""  # No validation rules defined

        if field_name not in self.validation_rules[api_url]:
            return True, ""  # No specific rules for this field

        rules = self.validation_rules[api_url][field_name]

        # Check if required
        if rules['required'] and (value is None or str(value).strip() == ''):
            return False, f"Поле '{field_name}' обязательно для заполнения"

        # Check if value is empty (allowed for non-required fields)
        if value is None or str(value).strip() == '':
            return True, ""  # Empty is OK for non-required fields

        # Check if numeric when required
        if rules['numeric']:
            try:
                # Try to convert to float (supports integers and decimals)
                float(str(value).strip())
            except ValueError:
                return False, f"Поле '{field_name}' должно содержать числовое значение"

        return True, ""

    def validate_form_entries(self, entries_dict, api_url):
        """
        Validate multiple entries at once

        Args:
            entries_dict: Dictionary of field_name: value pairs
            api_url: API endpoint name

        Returns:
            tuple: (all_valid, errors_dict)
        """
        errors = {}
        all_valid = True

        for field_name, value in entries_dict.items():
            is_valid, error_msg = self.validate_entry(value, field_name, api_url)
            if not is_valid:
                errors[field_name] = error_msg
                all_valid = False

        return all_valid, errors

    def show_validation_errors(self, errors_dict):
        """Display validation errors to the user"""
        if not errors_dict:
            return

        # Create error message
        error_text = "Обнаружены ошибки:\n\n"
        for field, error in errors_dict.items():
            error_text += f"• {field}: {error}\n"

        # Show error message
        error_window = tk.Toplevel(self.root)
        error_window.title("Ошибка валидации")
        error_window.geometry("400x200")
        error_window.configure(bg=COLORS['bg'])

        # Center the window
        error_window.transient(self.root)
        error_window.grab_set()

        # Error label
        error_label = tk.Label(
            error_window,
            text=error_text,
            bg=COLORS['bg'],
            fg='red',
            font=('Arial', 10),
            justify='left',
            wraplength=380
        )
        error_label.pack(pady=20, padx=20, fill='both', expand=True)

        # OK button
        ok_button = tk.Button(
            error_window,
            text="OK",
            command=error_window.destroy,
            width=10
        )
        ok_button.pack(pady=10)

    def validate_and_save(self, api_url, data_dict, save_function):
        """
        Validate entries and save if valid

        Args:
            api_url: API endpoint name
            data_dict: Dictionary of field data
            save_function: Function to call if validation passes
        """
        # Validate all fields
        is_valid, errors = self.validate_form_entries(data_dict, api_url)

        if not is_valid:
            self.show_validation_errors(errors)
            return False

        # If validation passed, call the save function
        return save_function()
    def _setup_window(self):
        """Configure window properties and position"""
        print('opened admin window!!!')

        self.root.state('zoomed')
        self.root.title("Панель администратора")
        self.root.configure(bg=COLORS['bg'])

        # Calculate centered position (though zoomed will fill screen)
        window_width = 1920
        window_height = 1080
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')

    def _create_widgets(self):
        """Create all UI widgets"""
        self._create_main_frame()
        self._create_notebook_and_tabs()
        self._create_info_frame()
        self._create_controls()

    def _create_main_frame(self):
        self.main_frame = tk.Frame(self.root, bg=COLORS['bg'], padx=40, pady=40)
        self.main_frame.pack(expand=True, fill='both')

        self.notebook_frame = tk.Frame(self.main_frame, bg=COLORS['bg'], padx=10, pady=10)
        self.notebook_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 20))

        self.info_frame = tk.Frame(self.main_frame,
                                   highlightbackground=COLORS['highlight'],
                                   highlightthickness=1,
                                   padx=10, pady=10)
        self.info_frame.grid(row=0, column=1, sticky='nsew')

        self.info_frame.pack_propagate(False)  # Prevent frame from resizing to fit content
        self.info_frame.config(width=400)  # Set fixed width in pixels

        self.main_frame.grid_columnconfigure(0, weight=3)  # 3/4 width for notebook
        self.main_frame.grid_columnconfigure(1, weight=0)  # 1/4 width for info
        self.main_frame.grid_rowconfigure(0, weight=1)

    def _create_notebook_and_tabs(self):
        """Create notebook widget and all tabs"""
        self.notebook = ttk.Notebook(self.notebook_frame)
        self.notebook.pack(expand=True, fill='both')

        # Create frame for each tab definition
        for key, frame_info in self.frame_data_dict.items():
            frame = tk.Frame(self.notebook, bg=COLORS['bg'], padx=10, pady=10)
            self.notebook.add(frame, text=frame_info['tab_name'])
            frame_info['frame'] = frame
            frame_info['tree'] = None

    def _create_info_frame(self):
        """Initialize info frame with default content"""
        self.update_info_frame("Выберите вкладку для просмотра данных")

    def _create_controls(self):
        """Create control buttons at the bottom"""
        controls_frame = tk.Frame(self.notebook_frame, bg=COLORS['bg'], padx=10, pady=10)
        controls_frame.pack(side='bottom', fill='x', pady=(10, 0))

        # Control buttons
        add_button = tk.Button(
            controls_frame,
            text="Добавить",
            command=lambda: self._add_new_row()
        )
        delete_button = tk.Button(
            controls_frame,
            text="Удалить",
            command=lambda: self._delete_selected_row()
        )

        add_button.pack(side='left', padx=5)
        delete_button.pack(side='left', padx=5)

    def _get_current_tab_frame_info(self):
        """Get the frame info for the currently selected tab"""
        selected_tab = self.notebook.index(self.notebook.select())
        tab_text = self.notebook.tab(selected_tab, "text")

        # Find the corresponding frame info
        for key, frame_info in self.frame_data_dict.items():
            if frame_info['tab_name'] == tab_text:
                return key, frame_info

        return None, None

    def _add_new_row(self):
        print('adding new row')
        tab_key, frame_info = self._get_current_tab_frame_info()
        print(f'Adding new row to: {frame_info["tab_name"]}')
        print(f'API URL: {frame_info["api_url"]}')

        # Очищаем инфо-фрейм и вызываем метод создания/редактирования с пустыми данными
        self.clear_frame(self.info_frame)
        self._create_edit_form(frame_info['api_url'], None)  # None означает новую запись

    def fill_info_frame(self, table_row, api_url):
        """Fill info frame with existing data"""
        print(f"API URL: {api_url} \nrow: {table_row} id: {table_row[0]}")
        self.clear_frame(self.info_frame)

        # Получаем данные записи (если не weights)
        row_data = {}
        if api_url != "weights":
            row_data = API.get_row_data(api_url, table_row[0])["info"]
            if api_url == "diagnostic-thresholds" or api_url == "test-results":
                row_data = row_data[0]

            print(row_data)

        # Вызываем общий метод создания/редактирования формы с данными записи
        self._create_edit_form(api_url, row_data, table_row)

    def _create_edit_form(self, api_url, row_data=None, table_row=None):
        """Общий метод для создания формы редактирования/добавления записи"""
        # Определяем, редактируем ли существующую запись или создаём новую
        is_edit = row_data is not None
        record_id = row_data.get('id') if row_data else None
        print("create edit form")
        match (api_url):
            case "personal_data":
                # View-only personal data
                row_data = API.get_row_data("users", table_row[0])["info"]
                main_info_label = tk.Label(self.info_frame,
                                           text=f"Ваши данные (ID: {row_data["id"]})",
                                           bg=COLORS['bg'],
                                           font=('Arial', 12),
                                           wraplength=300,
                                           justify='left')
                main_info_label.pack(anchor='w', pady=(10, 20))

                username_frame, username_entry = self.create_labeled_entry(
                    self.info_frame, "Логин: ", row_data["username"]
                )
                password_frame, password_entry = self.create_labeled_entry(
                    self.info_frame, "Пароль: ", row_data["password"]
                )
                full_name_frame, full_name_entry = self.create_labeled_entry(
                    self.info_frame, "ФИО: ", row_data["name"]
                )
                if(self.role == "Пациент"):
                    date_of_birth_frame, date_of_birth_entry = self.create_labeled_calendar(
                        self.info_frame, "Дата рождения: ", row_data["birth_date"]
                    )
                    gender_frame, gender_entry = self.create_labeled_combobox(
                        self.info_frame, "Пол: ", 1 if row_data["gender"] == "М" else 2,
                        [{"id": 1, "gender": "М"}, {"id": 2, "gender": "Ж"}], "gender"
                    )
                save_button = tk.Button(
                    self.info_frame,
                    text="Сохранить" if is_edit else "Добавить",
                    command=lambda: self.validate_and_save(
                        "personal_data",
                        {
                            'username': username_entry.get(),
                            'password': password_entry.get(),
                            'name': full_name_entry.get(),
                            'birth_date': date_of_birth_entry.get() if 'date_of_birth_entry' in locals() else None,
                            'gender': gender_entry.get_selected_data().get(
                                'gender') if 'gender_entry' in locals() and gender_entry.get_selected_data() else None
                        },
                        lambda: API.post(
                            "edit_user", {
                                "id": self.user_id,
                                "username": username_entry.get(),
                                "password": password_entry.get(),
                                "name": full_name_entry.get(),
                                "role": self.role,
                                "birth_date": date_of_birth_entry.get() if 'date_of_birth_entry' in locals() else None,
                                "gender": gender_entry.get_selected_data().get(
                                    'gender') if 'gender_entry' in locals() and gender_entry.get_selected_data() else None
                            }
                        ) and self._refresh_tab()
                    )
                )
                save_button.pack(pady=20)
            case "users":
                # Заголовок в зависимости от режима
                if is_edit:
                    title_text = f"Данные для пользователя с id: {record_id}"
                else:
                    title_text = "Добавление нового пользователя"

                main_info_label = tk.Label(self.info_frame,
                                           text=title_text,
                                           bg=COLORS['bg'],
                                           font=('Arial', 12),
                                           wraplength=300,
                                           justify='left')
                main_info_label.pack(anchor='w', pady=(10, 20))

                # Получаем значения из данных или пустые строки
                username_val = row_data.get("username", "") if row_data else ""
                password_val = row_data.get("password", "") if row_data else ""
                name_val = row_data.get("name", "") if row_data else ""
                role_id_val = row_data.get("role_id", "") if row_data else ""

                # Создаем поля ввода
                username_frame, username_entry = self.create_labeled_entry(
                    self.info_frame, "Логин: ", username_val
                )
                password_frame, password_entry = self.create_labeled_entry(
                    self.info_frame, "Пароль: ", password_val
                )
                full_name_frame, full_name_entry = self.create_labeled_entry(
                    self.info_frame, "ФИО: ", name_val
                )

                # Получаем список ролей
                all_roles = API.get_table_data("roles", None)["info"]
                role_frame, role_combobox = self.create_labeled_combobox(
                    self.info_frame, "Роль: ", role_id_val, all_roles, "name"
                )
                # Create containers for patient-specific fields
                patient_fields_container = tk.Frame(self.info_frame, bg=COLORS['bg'])
                patient_fields_container.pack(fill='x', pady=(10, 0))
                print(row_data)
                # print(row_data["birth_date"])
                # Create date_of_birth_frame and gender_frame but pack them in the container
                birth_date_val = row_data.get("birth_date") if row_data and row_data.get(
                    "birth_date") is not None else "2000-01-01"
                # birth_date_val = row_data.get("birth_date", "2000-01-01") if (row_data and "birth_date" in row_data) else "2000-01-01"
                gender_val = row_data.get("gender", "М") if row_data else "М"

                date_of_birth_frame, date_of_birth_entry = self.create_labeled_calendar(
                    patient_fields_container, "Дата рождения: ", birth_date_val
                )
                gender_frame, gender_entry = self.create_labeled_combobox(
                    patient_fields_container, "Пол: ",
                    1 if gender_val == "М" else 2,
                    [{"id": 1, "gender": "М"}, {"id": 2, "gender": "Ж"}],
                    "gender"
                )

                # Store references to patient fields for easy access
                self.date_of_birth_frame = date_of_birth_frame
                self.gender_frame = gender_frame
                self.patient_fields_container = patient_fields_container
                self.date_of_birth_entry = date_of_birth_entry
                self.gender_entry = gender_entry

                # Initially show/hide based on current role
                self._update_patient_fields_visibility(role_combobox.get_selected_value())

                # Function to handle role changes
                def on_role_changed(event):
                    selected_role_id = role_combobox.get_selected_value()
                    self._update_patient_fields_visibility(selected_role_id)

                # Bind the combobox change event
                role_combobox.bind("<<ComboboxSelected>>", on_role_changed)

                # Кнопка сохранения
                save_button = tk.Button(
                    self.info_frame,
                    text="Сохранить" if is_edit else "Добавить",
                    command=lambda: self.validate_and_save(
                        "users",
                        {
                            'username': username_entry.get(),
                            'password': password_entry.get(),
                            'name': full_name_entry.get(),
                            'role_id': role_combobox.get_selected_value(),
                            'birth_date': date_of_birth_entry.get() if hasattr(self, 'date_of_birth_entry') else None,
                            'gender': gender_entry.get_selected_data().get('gender') if hasattr(self, 'gender_entry') and gender_entry.get_selected_data() else None
                        },
                        lambda: API.post(
                            "add_user" if not record_id else "edit_user", {
                                "id": record_id,
                                "username": username_entry.get(),
                                "password": password_entry.get(),
                                "name": full_name_entry.get(),
                                "role_id": role_combobox.get_selected_value(),
                                "birth_date": date_of_birth_entry.get() if hasattr(self, 'date_of_birth_entry') else None,
                                "gender": gender_entry.get_selected_data().get('gender') if hasattr(self, 'gender_entry') and gender_entry.get_selected_data() else None
                            }
                        ) and self._refresh_tab()
                    )
                )
                save_button.pack(pady=20)

            case "diseases":
                # Заголовок в зависимости от режима
                if is_edit:
                    title_text = f"Данные для заболевания с id: {record_id}"
                else:
                    title_text = "Добавление нового заболевания"

                main_info_label = tk.Label(self.info_frame,
                                           text=title_text,
                                           bg=COLORS['bg'],
                                           font=('Arial', 12),
                                           wraplength=300,
                                           justify='left')
                main_info_label.pack(anchor='w', pady=(10, 20))

                # Значение названия
                name_val = row_data.get("name", "") if row_data else ""

                name_frame, name_entry = self.create_labeled_entry(
                    self.info_frame, "Название: ", name_val
                )

                # Кнопка сохранения
                save_button = tk.Button(
                    self.info_frame,
                    text="Сохранить" if is_edit else "Добавить",
                    command=lambda: self.validate_and_save(
                        "diseases",
                        {"name": name_entry.get()},
                        lambda: API.post(
                            "add_disease", {
                                "id": record_id,
                                "name": name_entry.get(),
                            }
                        ) and self._refresh_tab()
                    )
                )
                save_button.pack(pady=20)

            case "eye-metrics":
                # row_data = row_data[0]

                if is_edit:
                    title_text = f"Данные для метрики с id: {record_id}"
                else:
                    title_text = "Добавление новой метрики"
                    row_data = {'id': "", 'name': ""}

                main_info_label = tk.Label(self.info_frame,
                                           text=title_text,
                                           bg=COLORS['bg'],
                                           font=('Arial', 12),
                                           wraplength=300,
                                           justify='left')
                main_info_label.pack(anchor='w', pady=(10, 20))

                name_frame, name_entry = self.create_labeled_entry(
                    self.info_frame, "Название: ", row_data.get("name", "")
                )
                unit_frame, unit_entry = self.create_labeled_entry(
                    self.info_frame, "Единица измерения: ", row_data.get("unit", "")
                )

                # Кнопка сохранения
                save_button = tk.Button(
                    self.info_frame,
                    text="Сохранить" if is_edit else "Добавить",
                    command=lambda: self.validate_and_save(
                        "eye-metrics",
                        {
                            'name': name_entry.get(),
                            'unit': unit_entry.get()
                        },
                        lambda: API.post(
                            "add_metric", {
                                "id": record_id,
                                "name": name_entry.get(),
                                "unit": unit_entry.get()
                            }
                        ) and self._refresh_tab()
                    )
                )
                save_button.pack(pady=20)
            case "reference-groups":
                # row_data = row_data[0]
                if is_edit:
                    title_text = f"Данные для группы с id: {record_id}"
                else:
                    title_text = "Добавление новой группы"
                    row_data = {'id': "", 'name': "", 'age_min': "", 'age_max': "", 'sample_size': ""}

                main_info_label = tk.Label(self.info_frame,
                                           text=title_text,
                                           bg=COLORS['bg'],
                                           font=('Arial', 12),
                                           wraplength=300,
                                           justify='left')
                main_info_label.pack(anchor='w', pady=(10, 20))

                name_frame, name_entry = self.create_labeled_entry(
                    self.info_frame, "Название: ", row_data.get("name", "")
                )
                age_min_frame, age_min_entry = self.create_labeled_entry(
                    self.info_frame, "Минимальный возраст: ", row_data.get("age_min", "")
                )
                age_max_frame, age_max_entry = self.create_labeled_entry(
                    self.info_frame, "Максимальный возраст: ", row_data.get("age_max", "")
                )
                sample_size_frame, sample_size_entry = self.create_labeled_entry(
                    self.info_frame, "Размер группы: ", row_data.get("sample_size", "")
                )

                # Кнопка сохранения
                save_button = tk.Button(
                    self.info_frame,
                    text="Сохранить" if is_edit else "Добавить",
                    command=lambda: self.validate_and_save(
                        "reference-groups",
                        {
                            'name': name_entry.get(),
                            'age_min': age_min_entry.get(),
                            'age_max': age_max_entry.get(),
                            'sample_size': sample_size_entry.get()
                        },
                        lambda: API.post(
                            "add-ref-group", {
                                "id": record_id,
                                "name": name_entry.get(),
                                "age_min": age_min_entry.get(),
                                "age_max": age_max_entry.get(),
                                "sample_size": sample_size_entry.get(),
                            }
                        ) and self._refresh_tab()
                    )
                )
                save_button.pack(pady=20)
            case "reference-values":
                if is_edit:
                    title_text = f"Редактирование референсного значения #:{table_row[0]}\n"
                    # row_data = row_data
                else:
                    title_text = "Добавление нового референсного значения"
                    row_data = {"Tmax": "", "Tmin": "", "C": ""}
                main_info_label = tk.Label(self.info_frame,
                                           text=title_text,
                                           bg=COLORS['bg'],
                                           font=('Arial', 12),
                                           justify='left')
                main_info_label.pack(anchor='w', pady=(10, 20))
                all_metrics = API.get_table_data("eye-metrics", None)["info"]
                all_ref_groups = API.get_table_data("reference-groups", None)["info"]
                metric_frame, metric_combo = self.create_labeled_combobox(
                    self.info_frame, "Метрика: ",
                    row_data.get("metric_id", ""),
                    all_metrics, "Название"
                )
                all_ref_groups_frame, all_ref_groups_combo = self.create_labeled_combobox(
                    self.info_frame, "Референсная группа: ",
                    row_data.get("ref_id", ""),
                    all_ref_groups, "Название"
                )
                p5_frame, p5_entry = self.create_labeled_entry(
                    self.info_frame, "5 процентиль: ", row_data.get("p5", "")
                )
                p50_frame, p50_entry = self.create_labeled_entry(
                    self.info_frame, "Медиана: ", row_data.get("p50", "")
                )
                p95_frame, p95_entry = self.create_labeled_entry(
                    self.info_frame, "95 процентиль: ", row_data.get("p95", "")
                )
                s_frame, s_entry = self.create_labeled_entry(
                    self.info_frame, "Стандартное отклонение: ", row_data.get("s", "")
                )

                save_button = tk.Button(
                    self.info_frame,
                    text="Сохранить" if is_edit else "Добавить",
                    command=lambda: self.validate_and_save(
                        "reference-values",
                        {
                            'metric_id': metric_combo.get_selected_value(),
                            'reference_group_id': all_ref_groups_combo.get_selected_value(),
                            'p5': p5_entry.get(),
                            'p50': p50_entry.get(),
                            'p95': p95_entry.get(),
                            'std_dev': s_entry.get()
                        },
                        lambda: API.post(
                            "add-ref-metric", {
                                "id": record_id,
                                "metric_id": metric_combo.get_selected_value(),
                                "reference_group_id": all_ref_groups_combo.get_selected_value(),
                                "p5": p5_entry.get(),
                                "p50": p50_entry.get(),
                                "p95": p95_entry.get(),
                                "std_dev": s_entry.get(),
                            }
                        ) and self._refresh_tab()
                    )
                )
                save_button.pack(pady=20)

            case "weights":
                # Для weights данные могут приходить по-разному
                if is_edit:
                    row_data = API.get_row_data("weights_by_ids", [table_row[0], table_row[1]])["info"]
                    row_data = row_data[0]
                    title_text = f"Редактирование весового коэффициента"
                else:
                    row_data = {"disease_id": "", "metric_id": "", "w": ""}
                    title_text = "Добавление нового весового коэффициента"

                main_info_label = tk.Label(self.info_frame,
                                           text=title_text,
                                           bg=COLORS['bg'],
                                           font=('Arial', 12),
                                           justify='left')
                main_info_label.pack(anchor='w', pady=(10, 20))

                # Получаем списки для комбобоксов
                all_diseases = API.get_table_data("diseases", None)["info"]
                all_metrics = API.get_table_data("eye-metrics", None)["info"]
                print(all_diseases)
                print(all_metrics)

                # Комбобоксы для выбора заболевания и метрики
                disease_frame, disease_combo = self.create_labeled_combobox(
                    self.info_frame, "Заболевание: ",
                    row_data.get("disease_id", ""),
                    all_diseases, "Название"
                )
                metric_frame, metric_combo = self.create_labeled_combobox(
                    self.info_frame, "Метрика: ",
                    row_data.get("metric_id", ""),
                    all_metrics, "Название"
                )

                # Поле для веса
                weight_frame, weight_entry = self.create_labeled_entry(
                    self.info_frame, "Весовой коэффициент: ", row_data.get("w", "")
                )
                save_button = tk.Button(
                    self.info_frame,
                    text="Сохранить" if is_edit else "Добавить",
                    command=lambda: self.validate_and_save(
                        "weights",
                        {
                            'disease_id': disease_combo.get_selected_value(),
                            'metric_id': metric_combo.get_selected_value(),
                            'weight': weight_entry.get()
                        },
                        lambda: API.post(
                            "update_weight_row", {
                                "old_disease_id": row_data.get("disease_id", None),
                                "old_metric_id": row_data.get("metric_id", None),
                                "disease_id": disease_combo.get_selected_value(),
                                "metric_id": metric_combo.get_selected_value(),
                                "weight": weight_entry.get(),
                            }
                        ) and self._refresh_tab()
                    )
                )
                # # Кнопка сохранения
                # save_button = tk.Button(
                #     self.info_frame,
                #     text="Сохранить" if is_edit else "Добавить",
                #     command=lambda: self._save_weight_data(
                #         is_edit,
                #         {
                #             "disease_id": disease_combo.get_selected_value(),
                #             "metric_id": metric_combo.get_selected_value(),
                #             "weight": weight_entry.get(),
                #         },
                #         row_data.get("disease_id") if is_edit else None,
                #         row_data.get("metric_id") if is_edit else None
                #     )
                # )
                save_button.pack(pady=20)

            case "diagnostic-thresholds":
                print("===============")
                print(row_data)
                record_id = row_data.get('severity_id') if row_data else None
                if is_edit:
                    title_text = (f"Редактирование порогового значения #:{table_row[0]}"
                                  f"\n(предельные значения оставьте пустыми)")
                    row_data = row_data
                else:
                    title_text = "Добавление нового порогового значения"
                    row_data = {"id": '', "Tmax": "", "Tmin": "", "C": "", "disease_id": ""}
                print(row_data)
                main_info_label = tk.Label(self.info_frame,
                                           text=title_text,
                                           bg=COLORS['bg'],
                                           font=('Arial', 12),
                                           justify='left')
                main_info_label.pack(anchor='w', pady=(10, 20))
                all_diseases = API.get_table_data("diseases", None)["info"]

                disease_frame, disease_combo = self.create_labeled_combobox(
                    self.info_frame, "Заболевание: ",
                    row_data.get("disease_id", ""),
                    all_diseases, "Название"
                )
                max_frame, max_entry = self.create_labeled_entry(self.info_frame, "Максимальный интегральный индекс: ", row_data["Tmax"])
                min_frame, min_entry = self.create_labeled_entry(self.info_frame, "Минимальный интегральный индекс: ", row_data["Tmin"])
                sev_frame, sev_entry = self.create_labeled_entry(self.info_frame, "Степень заболевания: ", row_data["C"])
                save_button = tk.Button(
                    self.info_frame,
                    text="Сохранить" if is_edit else "Добавить",
                    command=lambda: self.validate_and_save(
                        "diagnostic-thresholds",
                        {
                            'disease_id': disease_combo.get_selected_value(),
                            'Tmax': max_entry.get(),
                            'Tmin': min_entry.get(),
                            'C': sev_entry.get()
                        },
                        lambda: API.post(
                            "update_sev_row", {
                                "id": record_id,
                                "disease_id": disease_combo.get_selected_value(),
                                "Tmax": max_entry.get(),
                                "Tmin": min_entry.get(),
                                "C": sev_entry.get(),
                            }
                        ) and self._refresh_tab()
                    )
                )
                save_button.pack(pady=20)
                # save_button = tk.Button(
                #     self.info_frame,
                #     text="Сохранить",
                #     command=lambda: self._update_sev_row(data)
                # )
                # save_button.pack(pady=20)

            case "test-results":
                if not is_edit:
                    metrics = API.get_table_data("eye-metrics", None)["info"]

                    print(metrics)

                    main_info_label = tk.Label(self.info_frame,
                                               text=f"Добавление нового тестирования.",
                                               bg=COLORS['bg'],
                                               font=('Arial', 12),
                                               wraplength=300,
                                               justify='left')
                    main_info_label.pack(anchor='w', pady=(10, 20))
                    tk.Label(self.info_frame,
                             text="Показатели ОМА\n (оставьте поле пустым, если показатель не замерялся):",
                             bg=COLORS['bg'],
                             font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 10))
                    metric_entries = []
                    for metric in metrics:
                        frame, entry = self.create_labeled_entry(
                            self.info_frame,
                            f"{metric['Название']}, {metric['Единица измерения']}: ",
                            ""
                        )
                        metric_entries.append({
                            "entry": entry,
                            "metric_id": metric["id"],
                        })
                    patient_id = ''
                    doctor_id = ''
                    if self.role != 'Врач':
                        doctors = API.get_table_data("doctors", None)["info"]
                        doctor_frame, doctor_entry = self.create_labeled_combobox(
                            self.info_frame,
                            "Врач",
                            doctors[0]["id"],
                            doctors,
                            "name"
                        )
                    if self.role != 'Пациент':
                        patients = API.get_table_data("patients", None)["info"]
                        patient_frame, patient_entry = self.create_labeled_combobox(
                            self.info_frame,
                            "Пациент",
                            patients[0]["id"],
                            patients,
                            "name"
                        )
                    save_button = tk.Button(
                        self.info_frame,
                        text="Сохранить",
                        command=lambda: self._validate_and_add_new_results_row(
                            metric_entries,
                            doctor_entry.get_selected_value() if self.role != "Врач" else self.user_id,
                            patient_entry.get_selected_value() if self.role != "Пациент" else self.user_id,
                        )
                    )
                    save_button.pack(pady=20)
                else:
                    metrics = API.get_row_data(api_url, [table_row[0]])["info"]
                    print(metrics)
                    main_info_label = tk.Label(self.info_frame,
                                               text=f"Результаты теста (ID: {table_row[0]})",
                                               bg=COLORS['bg'],
                                               font=('Arial', 12),
                                               wraplength=300,
                                               justify='left')
                    main_info_label.pack(anchor='w', pady=(10, 20))

                    metric_entries = []
                    for metric in metrics:
                        frame, entry = self.create_labeled_entry(
                            self.info_frame,
                            f"{metric['Название метрики']}, {metric['Ед. измерения']}: ",
                            metric["Числовое значение"]
                        )
                        metric_entries.append({
                            "entry": entry,
                            "metric_id": metric["id метрики"],
                            "name": metric["Название метрики"]
                        })
                    previous_diagnostics_percentile = \
                    API.get_table_data("metric_analysis_percentile_results", [table_row[0]])["info"]
                    previous_diagnostics_conclusion = \
                    API.get_table_data("metric_analysis_diagnostic_result", [table_row[0]])["info"]
                    if previous_diagnostics_percentile is not None and previous_diagnostics_conclusion is not None:

                        previous_diagnostics_label = tk.Label(self.info_frame,
                                                              text=f"Предыдущие результаты диагностики:",
                                                              bg=COLORS['bg'],
                                                              font=('Arial', 12),
                                                              wraplength=300,
                                                              justify='left')
                        previous_diagnostics_label.pack(anchor='w', pady=(10, 20))
                        tk.Label(self.info_frame,
                                 text="Анализ возможных заболеваний:",
                                 bg=COLORS['bg'],
                                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 10))

                        for conclusion in previous_diagnostics_conclusion:
                            text = f"• {conclusion['name']}, уровень: {conclusion['severity']} "
                            text += f"(интегральный индекс = {conclusion['idx']})"
                            tk.Label(self.info_frame,
                                     text=text,
                                     bg=COLORS['bg'],
                                     wraplength=300).pack(anchor='w', padx=10)
                        tk.Label(self.info_frame,
                                 text="Процентили по метрикам:",
                                 bg=COLORS['bg'],
                                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
                        for previous_diagnostic in previous_diagnostics_percentile:
                            text = f"• {previous_diagnostic["metric_name"]}: {previous_diagnostic['percentile_rank']}%"
                            tk.Label(self.info_frame,
                                     text=text,
                                     bg=COLORS['bg']).pack(anchor='w', padx=10)
                    calculate_button = tk.Button(
                        self.info_frame,
                        text="Анализ результатов",
                        command=lambda: self._calculate_diagnostics(metric_entries, table_row[0])
                    )
                    calculate_button.pack(pady=20)


            case _:
                print(f"Форма для {api_url} ещё не реализована")

    def _validate_and_add_new_results_row(self, metrics_entries, doctor_id, patient_id):
        """Validate and add new results row"""
        # Prepare data for validation
        validation_data = {
            'doctor_id': doctor_id,
            'patient_id': patient_id
        }

        # Add metric values if they exist
        for entry in metrics_entries:
            metric_value = entry["entry"].get()
            if metric_value:  # Only validate non-empty metric values
                validation_data[f'metric_{entry["metric_id"]}'] = metric_value

        # Define the save function
        def save_function():
            metric_values = []
            for entry in metrics_entries:
                metric = entry["entry"].get()
                if metric:  # This checks if metric is truthy (not empty string, not None)
                    metric_values.append({
                        "metric": metric,
                        "metric_id": entry["metric_id"]
                    })

            result = API.post("add_new_examination_session", {
                "doctor_id": doctor_id,
                "patient_id": patient_id,
                "session_metrics": metric_values
            })

            if result:  # If save was successful
                # Just trigger the tab changed event to reload everything
                self._refresh_tab()
            return result

        # Validate and save (use 'test-results' for validation rules)
        return self.validate_and_save("test-results", validation_data, save_function)

    def _add_new_results_row(self, metrics_entries, doctor_id, patient_id):
        metric_values = []
        for entry in metrics_entries:
            metric = entry["entry"].get()
            if metric:  # This checks if metric is truthy (not empty string, not None)
                metric_values.append({
                    "metric": metric,
                    "metric_id": entry["metric_id"]
                })
        result = API.post("add_new_examination_session", {
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "session_metrics": metric_values
        })

        if result:  # If save was successful
            # Just trigger the tab changed event to reload everything
            self._refresh_tab()
    def _update_patient_fields_visibility(self, role_id):
        """Show or hide patient-specific fields based on role ID"""
        if role_id == 4:  # Patient role
            self.date_of_birth_frame.pack(fill='x', pady=(10, 20), in_=self.patient_fields_container)
            self.gender_frame.pack(fill='x', pady=(10, 20), in_=self.patient_fields_container)
        else:
            # Hide the frames by removing them from display
            self.date_of_birth_frame.pack_forget()
            self.gender_frame.pack_forget()
    def _calculate_diagnostics(self, metrics_entries, examination_id):
        """Расчет диагностики с использованием отдельного класса"""
        # Удаляем предыдущий фрейм с результатами
        for widget in self.info_frame.winfo_children():
            if hasattr(widget, '_is_results_frame') and widget._is_results_frame:
                widget.destroy()

        # Подготавливаем данные метрик
        metric_values = []
        for entry in metrics_entries:
            metric_values.append({
                "metric": entry["entry"].get(),
                "metric_id": entry["metric_id"],
                "name": entry["name"]
            })

        # Используем DiagnosticCalculator для расчета

        percentile_results, conclusions = self.diagnostic_calculator.calculate_all(metric_values, 4)

        # Отображаем результаты
        self._display_diagnostic_results(percentile_results, conclusions, metric_values, examination_id)
    def _display_diagnostic_results(self, percentile_results, conclusions, metric_values, examination_id):
        """Отображение результатов диагностики в интерфейсе"""
        results_frame = tk.Frame(self.info_frame, bg=COLORS['bg'])
        results_frame._is_results_frame = True
        results_frame.pack(fill='x', pady=10)

        # Отображение возможных заболеваний
        if conclusions:
            tk.Label(results_frame,
                     text="Анализ возможных заболеваний:",
                     bg=COLORS['bg'],
                     font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 10))

            for conclusion in conclusions:
                text = f"• {conclusion['name']}, уровень: {conclusion['C']} "
                text += f"(интегральный индекс = {conclusion['idx']:.2f})"
                tk.Label(results_frame,
                         text=text,
                         bg=COLORS['bg'],
                         wraplength=300).pack(anchor='w', padx=10)
        else:
            tk.Label(results_frame,
                     text="По результатам анализа заболеваний не выявлено.",
                     bg=COLORS['bg']).pack(anchor='w')

        # Отображение процентилей
        if percentile_results:
            tk.Label(results_frame,
                     text="\nПроцентили по метрикам:",
                     bg=COLORS['bg'],
                     font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))

            for percentile in percentile_results:
                text = f"• {percentile['name']}: {percentile['P']:.2f}%"
                tk.Label(results_frame,
                         text=text,
                         bg=COLORS['bg']).pack(anchor='w', padx=10)

        save_button = tk.Button(
            results_frame,
            text="Сохранить",
            command=lambda: self._validate_and_save_diagnostic_results(
                metric_values, percentile_results, conclusions, examination_id
            )
        )
        save_button.pack(pady=20)

    def _validate_and_save_diagnostic_results(self, metric_values, percentile_results, conclusions, examination_id):
        """Validate and save diagnostic results"""
        # Prepare data for validation
        validation_data = {}

        # Add metric values for validation (they should be numeric if provided)
        for metric in metric_values:
            if metric['metric']:  # Only validate non-empty values
                validation_data[f'metric_{metric["metric_id"]}'] = metric['metric']

        # Define save function
        def save_function():
            result = API.post("update_examination_session", {
                "examination_session_id": examination_id,
                "session_metrics": metric_values,
                "metric_analysis_results": percentile_results,
                "examination_session": conclusions
            })

            if result:  # If save was successful
                # Just trigger the tab changed event to reload everything
                self._refresh_tab()
            return result

        # Validate and save
        return self.validate_and_save("test-results", validation_data, save_function)
    def _save_data_to_db(self, metric_values, percentile_results, conclusions, examination_id):
        print("++++")
        print(metric_values)
        print(percentile_results)
        print(conclusions)
        print("++++")

        result = API.post("update_examination_session", {
            "examination_session_id": examination_id,
            "session_metrics": metric_values,
            "metric_analysis_results": percentile_results,
            "examination_session": conclusions
        })

        if result:  # If save was successful
            # Just trigger the tab changed event to reload everything
            self._refresh_tab()
    def _delete_selected_row(self):
        """Handle deleting selected row from the current tab"""
        tab_key, frame_info = self._get_current_tab_frame_info()

        if frame_info and frame_info.get('tree'):
            tree = frame_info['tree']
            selected_items = tree.selection()

            if selected_items:
                # Get the IDs or values from selected items
                for item in selected_items:
                    values = tree.item(item)["values"]
                    print(f"Deleting row from {frame_info['tab_name']}: {values}")
                    API.delete(frame_info['api_url'], values)
                    self._refresh_tab()
                    # Here you would implement deletion logic
                    # 1. Extract ID from values (usually first column)
                    # 2. Send DELETE request to API
                    # 3. Remove item from treeview
                    # 4. Refresh the data if needed

                    # Example: delete from treeview
                    # tree.delete(item)

                    # Example: send API delete request
                    # API.delete(frame_info['api_url'], values[0])
            else:
                print("No row selected for deletion")
        else:
            print("No tab selected or no treeview available")


    def _bind_events(self):
        """Bind event handlers"""
        self.notebook.bind("<<NotebookTabChanged>>", self._refresh_tab)

    def _refresh_tab(self, event=None):
        """Handle notebook tab selection change"""
        print("refreshing")
        selected_tab = self.notebook.index(self.notebook.select())
        tab_text = self.notebook.tab(selected_tab, "text")

        # Find the corresponding frame info
        for frame_info in self.frame_data_dict.values():
            if frame_info['tab_name'] == tab_text:
                print(f"Selected tab: {tab_text}")
                print(f"API URL: {frame_info['api_url']}")

                # Update info frame description
                self.update_info_frame(frame_info['description'])

                # Load and display data
                self._load_tab_data(frame_info)
                break

    def _load_tab_data(self, frame_info):
        """Load data from API and display in treeview"""
        if(frame_info['api_url'] == 'personal_data'):
            data = API.get_row_data(frame_info['api_url'], self.user_id)
            if(self.role != "Пациент"):
                data["info"].pop("Дата рождения")
                data["info"].pop("Пол")
            data = {'info': [data["info"]]}
            print(data)
        else:
            data = API.get_table_data(frame_info['api_url'], None)
        print(data)
        if data and 'info' in data and len(data['info']) > 0:
            self._create_and_populate_treeview(frame_info, data)
        else:
            print(f"No data available for {frame_info['api_url']}")
            # Clear existing treeview if any
            if frame_info.get('tree'):
                frame_info['tree'].destroy()
                frame_info['tree'] = None

    def _on_treeview_select(self, event):
        """Generic treeview selection handler"""
        tree = event.widget  # Get the tree that triggered the event

        # Store API URL as tree attribute when creating it
        api_url = getattr(tree, 'api_url', 'unknown')

        for selected_item in tree.selection():
            # print(tree.item(selected_item)["values"], api_url)
            self.fill_info_frame(tree.item(selected_item)["values"], api_url)

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def create_labeled_entry(self, parent, label_text, textvariable):
        """Create a frame with label and entry widget"""
        frame = tk.Frame(parent, bg=COLORS['bg'])
        frame.pack(fill='x', pady=(10, 20))
        label = tk.Label(frame, text=label_text, bg=COLORS['bg'])
        entry = tk.Entry(frame, width=20, textvariable=tk.StringVar(value=textvariable))
        label.pack(side='left')
        entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        return frame, entry

    def create_labeled_combobox(self, parent, label_text, initial_variable, all_variables, display_key):
        """Create a frame with label and combobox widget"""
        frame = tk.Frame(parent, bg=COLORS['bg'])
        frame.pack(fill='x', pady=(10, 20))
        label = tk.Label(frame, text=label_text, bg=COLORS['bg'])
        # combobox = ttk.Combobox(frame, width=20, values=allvariables)
        combo = ComboBoxWithHiddenValues(
            frame,
            data=all_variables,
            display_key=display_key,
            value_key="id",
            initial_value=initial_variable
        )
        label.pack(side='left')
        combo.pack(side='left', fill='x', expand=True, padx=(5, 0))
        return frame, combo
    def create_labeled_calendar(self, parent, label_text, initial_date):
        """Create a frame with label and calendar widget"""
        frame = tk.Frame(parent, bg=COLORS['bg'])
        frame.pack(fill='x', pady=(10, 20))
        label = tk.Label(frame, text=label_text, bg=COLORS['bg'])
        # Split on 'T' to separate date from time
        date_part = initial_date.split('T')[0]

        # Split the date part
        year, month, day = map(int, date_part.split('-'))

        cal = DateEntry(frame,
                        date_pattern="yyyy-mm-dd",
                        year=year,
                        month=month,
                        day=day
                        )

        label.pack(side='left')
        cal.pack(side='left', fill='x', expand=True, padx=(5, 0))
        return frame, cal
    # def fill_info_frame(self, table_row, api_url):
    #     """Fill info frame"""
    #
    #     print(f"API URL: {api_url} \nrow: {table_row} id: {table_row[0]}")
    #     self.clear_frame(self.info_frame)
    #     row_data = {}
    #     if api_url != "weights":
    #         row_data = API.get_row_data(api_url, table_row[0])["info"]
    #         print(row_data)
    #
    #     match (api_url):
    #         case "users":
    #             main_info_label = tk.Label(self.info_frame,
    #                                        text=f"Данные для пользователя с id: {row_data["id"]}",
    #                                        bg = COLORS['bg'],
    #                                        font = ('Arial', 12),
    #                                        wraplength = 300,
    #                                        justify = 'left')
    #             main_info_label.pack(anchor='w', pady=(10, 20))
    #
    #             # Create all entries using the function
    #             username_frame, username_entry = self.create_labeled_entry(
    #                 self.info_frame, "Логин: ", row_data["username"]
    #             )
    #             password_frame, password_entry = self.create_labeled_entry(
    #                 self.info_frame, "Пароль: ", row_data["password"]
    #             )
    #             full_name_frame, full_name_entry = self.create_labeled_entry(
    #                 self.info_frame, "ФИО: ", row_data["name"]
    #             )
    #             all_roles = API.get_table_data("roles", None)["info"]
    #             role_frame, role_combobox = self.create_labeled_combobox(
    #                 self.info_frame, "Роль: ", int(row_data["role_id"]), all_roles, "name"
    #             )
    #             if row_data["role_id"] == 4:
    #                 date_of_birth_frame, date_of_birth_entry = self.create_labeled_calendar(
    #                     self.info_frame, "Дата рождения: ", row_data["birth_date"]
    #                 )
    #                 gender_frame, gender_entry = self.create_labeled_combobox(
    #                     self.info_frame, "Пол: ", 1 if row_data["gender"] == "М" else 2, [{"id": 1, "gender": "М"}, {"id":2, "gender":"Ж"}], "gender"
    #                 )
    #         case "medications":
    #             main_info_label = tk.Label(self.info_frame,
    #                                        text=f"Данные для лекарства с id: {row_data["id"]}",
    #                                        bg=COLORS['bg'],
    #                                        font=('Arial', 12),
    #                                        wraplength=300,
    #                                        justify='left')
    #             main_info_label.pack(anchor='w', pady=(10, 20))
    #
    #             # Medicine name entry
    #             name_frame, name_entry = self.create_labeled_entry(
    #                 self.info_frame, "Название: ", row_data["name"]
    #             )
    #
    #             # Get all diseases
    #             all_diseases = API.get_table_data("diseases", None)["info"]
    #
    #             # Create disease relationship management sections
    #             # 1. Diseases treated by this medicine
    #             self._create_relationship_section(
    #                 self.info_frame,
    #                 section_title="Лечение заболеваний:",
    #                 api_url=api_url,
    #                 item_id=row_data["id"],
    #                 relationship_table="medicine_treats_disease",
    #                 item_key="medicine_id",
    #                 related_key="disease_id",
    #                 related_items=all_diseases,
    #                 display_key="Название"
    #             )
    #
    #             # 2. Diseases contraindicated for this medicine
    #             self._create_relationship_section(
    #                 self.info_frame,
    #                 section_title="Противопоказания при заболеваниях:",
    #                 api_url=api_url,
    #                 item_id=row_data["id"],
    #                 relationship_table="medicine_contraindicated_for",
    #                 item_key="medicine_id",
    #                 related_key="disease_id",
    #                 related_items=all_diseases,
    #                 display_key="Название"
    #             )
    #
    #             # Save button for medication data
    #             save_button = tk.Button(
    #                 self.info_frame,
    #                 text="Сохранить изменения",
    #                 command=lambda: self._save_medication_changes(
    #                     row_data["id"], name_entry.get()
    #                 )
    #             )
    #             save_button.pack(pady=20)
    #         case "diseases":
    #             main_info_label = tk.Label(self.info_frame,
    #                                        text=f"Данные для заболевания с id: {row_data["id"]}",
    #                                        bg=COLORS['bg'],
    #                                        font=('Arial', 12),
    #                                        wraplength=300,
    #                                        justify='left')
    #             main_info_label.pack(anchor='w', pady=(10, 20))
    #             name_frame, name_entry = self.create_labeled_entry(
    #                 self.info_frame, "Название: ", row_data["name"]
    #             )
    #         case "weights":
    #             row_data = API.get_row_data("weights_by_ids", [table_row[0], table_row[1]])["info"]
    #             row_data= row_data[0]
    #             print(row_data)
    #             main_info_label = tk.Label(self.info_frame,
    #                                        text=f"Редактирование весового коэффициента",
    #                                        bg=COLORS['bg'],
    #                                        font=('Arial', 12),
    #
    #                                        justify='left')
    #             main_info_label.pack(anchor='w', pady=(10, 20))
    #             weight_frame, weight_entry = self.create_labeled_entry(self.info_frame, "Весовой коэффициент: ", row_data["w"])
    #             weight_entry = {
    #                 "disease_id": row_data["disease_id"],
    #                 "metric_id": row_data["metric_id"],
    #                 "weight": weight_entry,
    #             }
    #             save_button = tk.Button(
    #                 self.info_frame,
    #                 text="Сохранить",
    #                 command=lambda: self._update_weight_row(weight_entry)
    #             )
    #             save_button.pack(pady=20)
    #         case "diagnostic-thresholds":
    #             row_data = row_data[0]
    #             main_info_label = tk.Label(self.info_frame,
    #                                        text=f"Редактирование порогового значения #:{table_row[0]}\n для заболевания {table_row[1]}"
    #                                             f"\n(предельные значения оставьте пустыми)",
    #                                        bg=COLORS['bg'],
    #                                        font=('Arial', 12),
    #                                        justify='left')
    #             main_info_label.pack(anchor='w', pady=(10, 20))
    #             max_frame, max_entry = self.create_labeled_entry(self.info_frame, "Максимальный интегральный индекс: ", row_data["Tmax"])
    #             min_frame, min_entry = self.create_labeled_entry(self.info_frame, "Минимальный интегральный индекс: ", row_data["Tmin"])
    #             sev_frame, sev_entry = self.create_labeled_entry(self.info_frame, "Степень заболвения: ", row_data["C"])
    #             data = {
    #                 "id": table_row[0],
    #                 "Tmax": max_entry,
    #                 "Tmin": min_entry,
    #                 "C": sev_entry,
    #             }
    #
    #             save_button = tk.Button(
    #                 self.info_frame,
    #                 text="Сохранить",
    #                 command=lambda: self._update_sev_row(data)
    #             )
    #             save_button.pack(pady=20)
    #         # case "reference-values":
    #         #
    #         # case "test-results":
    #         #
    #         case _:
    #             print(f"lol lmao you fricked up")
    def _update_weight_row(self, weight_entry):
        weight_value = {
            "disease_id": weight_entry["disease_id"],
            "metric_id": weight_entry["metric_id"],
            "weight": weight_entry["weight"].get(),
        }
        result = API.post("update_weight_row", {
            "user_id": self.user_id,
            "weights": weight_value
        })
        if result:  # If save was successful
            # Just trigger the tab changed event to reload everything
            self._refresh_tab()
    def _create_relationship_section(self, parent, section_title, api_url, item_id,
                                     relationship_table, item_key, related_key,
                                     related_items, display_key):
        """Create a reusable section for managing many-to-many relationships"""

        # Create section frame
        section_frame = tk.Frame(parent, bg=COLORS['bg'], pady=10)
        section_frame.pack(fill='x', padx=5)

        # Section title
        title_label = tk.Label(
            section_frame,
            text=section_title,
            bg=COLORS['bg'],
            font=('Arial', 11, 'bold'),
            anchor='w'
        )
        title_label.pack(anchor='w', pady=(0, 5))

        # Get current related items
        current_related = self._get_related_items(
            relationship_table, item_key, item_id, related_key
        )
        current_related = [str(related_item["disease_id"]) for related_item in current_related]

        # Create listbox for current items
        listbox_frame = tk.Frame(section_frame, bg=COLORS['bg'])
        listbox_frame.pack(fill='x', pady=5)

        listbox_label = tk.Label(
            listbox_frame,
            text="Текущие:",
            bg=COLORS['bg'],
            font=('Arial', 10),
            width=10
        )
        listbox_label.pack(side='left', padx=(0, 5))

        current_listbox = tk.Listbox(
            listbox_frame,
            height=4,
            selectmode=tk.SINGLE,
            bg=COLORS['entry_bg']
        )
        current_listbox.pack(side='left', fill='x', expand=True)
        print("===")
        print(current_related)
        print("+++")
        print(related_items)
        print("===")
        # Populate listbox with current items
        for item_id in current_related:
            for related_item in related_items:
                if str(related_item["id"]) == str(item_id):
                    print("OKE")
                    current_listbox.insert(tk.END, related_item[display_key])
                    break
                else:
                    print("NOT OKE", str(related_item["id"]), str(item_id))

        # Create combobox and buttons frame
        controls_frame = tk.Frame(section_frame, bg=COLORS['bg'])
        controls_frame.pack(fill='x', pady=5)

        # Combobox for available items (excluding already added ones)
        available_items = []
        for item in related_items:
            if str(item["id"]) not in current_related:
                available_items.append(item)

        combo = ComboBoxWithHiddenValues(
            controls_frame,
            data=available_items,
            display_key=display_key,
            value_key="id"
        )
        combo.pack(side='left', fill='x', expand=True, padx=(0, 10))

        # Add button
        add_button = tk.Button(
            controls_frame,
            text="+ Добавить",
            width=10,
            command=lambda: self._add_relationship_item(
                relationship_table, item_key, item_id,
                related_key, combo.get_selected_value(),
                current_listbox, combo, available_items, display_key
            )
        )
        add_button.pack(side='left', padx=(0, 5))

        # Remove button
        remove_button = tk.Button(
            controls_frame,
            text="- Удалить",
            width=10,
            command=lambda: self._remove_relationship_item(
                relationship_table, item_key, item_id,
                related_key, current_listbox, combo,
                related_items, display_key
            )
        )
        remove_button.pack(side='left')

    def _get_related_items(self, relationship_table, item_key, item_id, related_key):
        """Get current related items from the relationship table"""
        # This would need API support to query relationship tables
        # For now, return empty list - you'll need to implement this
        print(f"Getting related items from {relationship_table} where {item_key}={item_id}")
        return API.get_row_data(relationship_table, item_id)["info"]  # Implement API call here

    def _add_relationship_item(self, relationship_table, item_key, item_id,
                               related_key, related_id, current_listbox,
                               combo, available_items, display_key):
        """Add a new relationship item"""
        if not related_id:
            return

        # Find the item to add
        item_to_add = None
        for item in available_items:
            if item["id"] == related_id:
                item_to_add = item
                break

        if not item_to_add:
            return

        # Add to listbox
        current_listbox.insert(tk.END, item_to_add[display_key])

        # Remove from combobox
        combo['values'] = [item[display_key] for item in available_items if item["id"] != related_id]
        combo.set('')

        # Here you would call API to add to database
        print(f"Adding to {relationship_table}: {item_key}={item_id}, {related_key}={related_id}")
        # Implement API call here

    def _remove_relationship_item(self, relationship_table, item_key, item_id,
                                  related_key, current_listbox, combo,
                                  all_items, display_key):
        """Remove a relationship item"""
        selection = current_listbox.curselection()
        if not selection:
            return

        # Get the display text of selected item
        selected_text = current_listbox.get(selection[0])

        # Find the corresponding item ID
        related_id = None
        for item in all_items:
            if item[display_key] == selected_text:
                related_id = item["id"]
                break

        if not related_id:
            return

        # Remove from listbox
        current_listbox.delete(selection[0])

        # Add back to combobox
        current_values = list(combo['values'])
        current_values.append(selected_text)
        combo['values'] = current_values

        # Here you would call API to remove from database
        print(f"Removing from {relationship_table}: {item_key}={item_id}, {related_key}={related_id}")
        # Implement API call here

    def _save_medication_changes(self, medication_id, new_name):
        """Save changes to medication data"""
        print(f"Saving medication {medication_id}: name={new_name}")
        # Implement API call to update medication
    def _create_and_populate_treeview(self, frame_info, data):
        """Create treeview widget and populate with data"""
        # Clear existing TreeView if any
        if frame_info.get('tree'):
            frame_info['tree'].destroy()

        # Get column names from first item
        first_item = data['info'][0]
        columns = list(first_item.keys())

        # Create new TreeView
        tree = ttk.Treeview(
            frame_info['frame'],
            columns=columns,
            show='headings',
            height=20
        )

        # def handle_treeview_element_selection(event):
        #     """Handle treeview item selection"""
        #     for selected_item in tree.selection():
        #         print(tree.item(selected_item)["values"], frame_info['api_url'])
        tree.api_url = frame_info['api_url']
        tree.bind('<<TreeviewSelect>>', self._on_treeview_select)

        # Configure headings and columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor='center')

        # Insert data
        for item in data['info']:
            values = tuple(str(item[col]) for col in columns)
            tree.insert('', 'end', values=values)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame_info['frame'], orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack everything
        tree.pack(side='left', expand=True, fill='both')
        # scrollbar.pack(side='right', fill='y')

        # Fit columns to content
        self._fit_columns_to_content(tree)

        # Store reference to tree
        frame_info['tree'] = tree

    def _fit_columns_to_content(self, tree):
        """Adjust column widths to fit content"""
        tree.update_idletasks()

        # For each column
        for col in tree['columns']:
            # Get the header text width
            header = tree.heading(col)['text']
            max_width = len(header) * 10

            # Check all items in this column
            for child in tree.get_children():
                value = tree.set(child, col)
                if value:
                    cell_width = len(str(value)) * 8
                    max_width = max(max_width, cell_width)

            # Set the column width
            tree.column(col, width=min(max_width + 20, 300))  # Cap at 300 pixels

    def update_info_frame(self, description):
        """Update the info frame with description"""
        # Clear info frame
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        # Add description label
        desc_label = tk.Label(
            self.info_frame,
            text=description,
            bg=COLORS['bg'],
            font=('Arial', 12),
            wraplength=300,
            justify='left'
        )
        desc_label.pack(anchor='w', pady=(10, 20))

    def run(self):
        """Start the main loop"""
        self.root.mainloop()


def open_admin_window(user_id, role):
    """Public function to open admin window"""
    admin_window = AdminWindow(user_id, role)
    admin_window.run()