"""
Страница настроек приложения LeadGen v5.

Модуль предоставляет виджет SettingsPage для управления настройками:
- Настройки Битрикс24 (вебхук, статус, лимиты)
- Настройки интерфейса (шрифт, размер, прозрачность)
- Экспорт/Импорт конфигурации

Classes:
    SettingsPage: QWidget для настроек приложения.

Example:
    >>> page = SettingsPage()
    >>> page.show()
"""

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

# Импортируем специализированные исключения для обработки ошибок Битрикс24
from modules.exceptions import (
    BitrixWebhookNotFoundError,
    BitrixWebhookForbiddenError,
    BitrixWebhookInvalidURLError,
    BitrixWebhookConnectionError,
    BitrixWebhookError,
)


def validate_bitrix_webhook_url(url: str) -> tuple[bool, str]:
    """
    Валидирует URL вебхука Битрикс24.
    
    Args:
        url: URL для проверки
        
    Returns:
        Кортеж (успех, сообщение)
    """
    if not url:
        return False, "URL не указан"
    
    url = url.strip()
    
    # Проверка формата через regex
    pattern = r'^https://[a-zA-Z0-9.-]+\.bitrix24\.[a-z]+/rest/\d+/[a-zA-Z0-9]+/?$'
    if not re.match(pattern, url):
        return False, (
            "Неверный формат вебхука Битрикс24.\n"
            "Пример: https://your-company.bitrix24.ru/rest/1/xxxxx/"
        )
    
    # Проверка схемы
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return False, "Требуется HTTPS соединение"
    
    # Проверка домена
    if not parsed.netloc.endswith('.bitrix24.ru'):
        return False, "URL должен заканчиваться на .bitrix24.ru (или другой домен Битрикс)"
    
    return True, "URL корректен"

from gui.styles.theme import (
    ACCENT_CYAN,
    ACCENT_CYAN_HOVER,
    BACKGROUND_PRIMARY,
    BACKGROUND_SECONDARY,
    BACKGROUND_TERTIARY,
    BORDER_COLOR,
    FONT_FAMILY,
    FONT_SIZE_BODY,
    FONT_SIZE_SMALL,
    FONT_SIZE_TITLE,
    STATUS_SUCCESS,
    STATUS_ERROR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    GLASS_CARD_BG,
    GLASS_BORDER,
    GLASS_BUTTON_BG,
    GLASS_HOVER,
)
from utils.config_loader import load_config, save_config

JSON_FILE_FILTER = "JSON файлы (*.json)"


class SettingsPage(QWidget):
    """
    Страница настроек приложения.

    Example:
        >>> page = SettingsPage()
        >>> page.show()
    """

    settings_saved = Signal(dict)
    transparency_changed = Signal(bool)
    blur_intensity_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SettingsPage")

        # Загрузка конфигурации
        self._config = load_config()

        self._init_ui()
        self._apply_styles()
        self._connect_signals()
        self._load_settings()

    def _init_ui(self):
        """Инициализация UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Заголовок
        self._page_title = QLabel("Настройки")
        self._page_title.setObjectName("pageTitle")
        layout.addWidget(self._page_title)

        # Скролл для настроек
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(24)

        # 1. Настройки Битрикс24
        bitrix_group = self._create_bitrix_group()
        settings_layout.addWidget(bitrix_group)

        # 2. Настройки интерфейса
        interface_group = self._create_interface_group()
        settings_layout.addWidget(interface_group)

        # 3. Экспорт/Импорт
        export_group = self._create_export_group()
        settings_layout.addWidget(export_group)

        settings_layout.addStretch()
        scroll.setWidget(settings_widget)
        layout.addWidget(scroll, stretch=1)

    def _create_bitrix_group(self) -> QFrame:
        """Группа настроек Битрикс24."""
        card = QFrame()
        card.setObjectName("settingsCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Заголовок
        title = QLabel("Настройки Битрикс24")
        title.setObjectName("settingsCardTitle")
        layout.addWidget(title)

        # URL вебхука
        layout.addWidget(QLabel("URL вебхука:"))
        self._webhook_input = QLineEdit()
        self._webhook_input.setPlaceholderText(
            "https://your-company.bitrix24.ru/rest/1/xxxxx/"
        )
        layout.addWidget(self._webhook_input)

        # Статус для поиска лидов
        layout.addWidget(QLabel("Статус для поиска лидов:"))
        self._status_combo = QComboBox()
        self._status_combo.addItems(
            [
                "Новая заявка",
                "В работе",
                "Выставлен счёт",
                "Успешно реализовано",
                "Нереализовано",
            ]
        )
        layout.addWidget(self._status_combo)

        # Макс. лидов на менеджера
        max_leads_layout = QHBoxLayout()
        max_leads_layout.addWidget(QLabel("Макс. лидов на менеджера:"))
        self._max_leads_spin = QSpinBox()
        self._max_leads_spin.setRange(5, 500)
        self._max_leads_spin.setSingleStep(5)
        max_leads_layout.addWidget(self._max_leads_spin)
        max_leads_layout.addStretch()
        layout.addLayout(max_leads_layout)

        # Стадия лида
        layout.addWidget(QLabel("Стадия лида по умолчанию:"))
        self._stage_input = QLineEdit()
        layout.addWidget(self._stage_input)

        # Источник
        layout.addWidget(QLabel("Источник лида:"))
        self._source_input = QLineEdit()
        layout.addWidget(self._source_input)

        # Тип услуги
        layout.addWidget(QLabel("Тип услуги:"))
        self._service_input = QLineEdit()
        layout.addWidget(self._service_input)

        return card

    def _create_interface_group(self) -> QFrame:
        """Группа настроек интерфейса."""
        card = QFrame()
        card.setObjectName("settingsCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Заголовок
        title = QLabel("Настройки интерфейса")
        title.setObjectName("settingsCardTitle")
        layout.addWidget(title)

        # Чекбокс прозрачности
        self._transparency_checkbox = QCheckBox("Включить прозрачность фона")
        self._transparency_checkbox.setObjectName("transparencyCheckbox")
        layout.addWidget(self._transparency_checkbox)

        # Степень размытия
        blur_layout = QVBoxLayout()
        blur_layout.setSpacing(8)
        
        # Заголовок и значение
        blur_header_layout = QHBoxLayout()
        blur_header_layout.addWidget(QLabel("Степень размытия:"))
        self._blur_value_label = QLabel("Сильное")
        self._blur_value_label.setObjectName("blurValueLabel")
        blur_header_layout.addWidget(self._blur_value_label)
        blur_header_layout.addStretch()
        blur_layout.addLayout(blur_header_layout)
        
        # Слайдер
        self._blur_slider = QSlider(Qt.Orientation.Horizontal)
        self._blur_slider.setRange(0, 100)
        self._blur_slider.setSingleStep(1)
        self._blur_slider.setPageStep(10)
        self._blur_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._blur_slider.setTickInterval(25)
        self._blur_slider.setObjectName("blurSlider")
        blur_layout.addWidget(self._blur_slider)
        
        # Подписи к слайдеру
        slider_labels_layout = QHBoxLayout()
        slider_labels_layout.addWidget(QLabel("Выкл"))
        slider_labels_layout.addStretch()
        slider_labels_layout.addWidget(QLabel("Слабое"))
        slider_labels_layout.addStretch()
        slider_labels_layout.addWidget(QLabel("Среднее"))
        slider_labels_layout.addStretch()
        slider_labels_layout.addWidget(QLabel("Сильное"))
        blur_layout.addLayout(slider_labels_layout)
        
        layout.addLayout(blur_layout)

        return card

    def _create_export_group(self) -> QFrame:
        """Группа экспорта/импорта настроек."""
        card = QFrame()
        card.setObjectName("settingsCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Заголовок
        title = QLabel("Экспорт/Импорт настроек")
        title.setObjectName("settingsCardTitle")
        layout.addWidget(title)

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(16)

        self._save_btn = QPushButton("Сохранить настройки")
        self._save_btn.setObjectName("accentButton")
        buttons_layout.addWidget(self._save_btn)

        self._export_btn = QPushButton("Экспорт в файл")
        self._export_btn.setObjectName("minimalButton")
        buttons_layout.addWidget(self._export_btn)

        self._import_btn = QPushButton("Импорт из файла")
        self._import_btn.setObjectName("minimalButton")
        buttons_layout.addWidget(self._import_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Статус
        self._status_label = QLabel("")
        self._status_label.setObjectName("settingsStatus")
        layout.addWidget(self._status_label)

        return card

    def _connect_signals(self):
        """Подключение сигналов."""
        self._save_btn.clicked.connect(self._save_settings)
        self._export_btn.clicked.connect(self._export_settings)
        self._import_btn.clicked.connect(self._import_settings)

        # Прозрачность фона
        self._transparency_checkbox.stateChanged.connect(self._on_transparency_changed)

        # Интенсивность размытия
        self._blur_slider.valueChanged.connect(self._on_blur_intensity_changed)

        # Валидация вебхука в реальном времени
        self._webhook_input.textChanged.connect(self._on_webhook_changed)

    def _on_webhook_changed(self, text: str) -> None:
        """Обработка изменения поля вебхука."""
        if text.strip():
            is_valid, _ = validate_bitrix_webhook_url(text)
            if not is_valid:
                self._webhook_input.setStyleSheet(
                    f"QLineEdit {{ border: 1px solid {STATUS_ERROR}; }}"
                )
            else:
                self._webhook_input.setStyleSheet(
                    f"QLineEdit {{ border: 1px solid {STATUS_SUCCESS}; }}"
                )
        else:
            self._webhook_input.setStyleSheet("")

    def _on_transparency_changed(self, state: int) -> None:
        """Обработчик изменения состояния чекбокса прозрачности."""
        # state=0 => unchecked, state=2 => checked
        enabled = state != 0
        self.transparency_changed.emit(enabled)

    def _on_blur_intensity_changed(self, value: int) -> None:
        """Обработчик изменения интенсивности размытия."""
        # Обновляем текстовую метку
        from utils.windows_blur import get_blur_intensity_label
        self._blur_value_label.setText(get_blur_intensity_label(value))
        # Испускаем сигнал
        self.blur_intensity_changed.emit(value)

    def _apply_styles(self):
        """Применение стилей."""
        self.setStyleSheet(f"""
            QWidget#SettingsPage {{
                background-color: {BACKGROUND_PRIMARY};
            }}
        """)

        # Заголовок
        self._page_title.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 24px;
                font-weight: bold;
                font-family: {FONT_FAMILY};
            }}
        """)

        # Карточки с glassmorphism (более прозрачные)
        for card in self.findChildren(QFrame, "settingsCard"):
            card.setStyleSheet(f"""
                QFrame#settingsCard {{
                    background-color: rgba(30, 30, 30, 60);
                    border: 1px solid rgba(255, 255, 255, 30);
                    border-radius: 10px;
                }}
            """)

        # Заголовки карточек
        for label in self.findChildren(QLabel, "settingsCardTitle"):
            label.setStyleSheet(f"""
                QLabel {{
                    color: {ACCENT_CYAN};
                    font-size: 18px;
                    font-weight: bold;
                    font-family: {FONT_FAMILY};
                }}
            """)

        # Поля ввода
        for input_widget in self.findChildren(QLineEdit):
            input_widget.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {BACKGROUND_TERTIARY};
                    color: {TEXT_PRIMARY};
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-family: {FONT_FAMILY};
                    font-size: {FONT_SIZE_BODY}px;
                }}
                QLineEdit:focus {{
                    border: 1px solid {ACCENT_CYAN};
                }}
            """)

        # Слайдер размытия
        if hasattr(self, '_blur_slider'):
            self._blur_slider.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    border: 1px solid {BORDER_COLOR};
                    height: 8px;
                    background: {BACKGROUND_TERTIARY};
                    border-radius: 4px;
                }}
                QSlider::handle:horizontal {{
                    background: {ACCENT_CYAN};
                    border: 1px solid {ACCENT_CYAN};
                    width: 18px;
                    margin: -5px 0;
                    border-radius: 9px;
                }}
                QSlider::handle:horizontal:hover {{
                    background: {ACCENT_CYAN_HOVER};
                }}
                QSlider::sub-page:horizontal {{
                    background: {ACCENT_CYAN};
                    border-radius: 4px;
                }}
                QSlider::add-page:horizontal {{
                    background: {BACKGROUND_TERTIARY};
                    border-radius: 4px;
                }}
            """)
        
        # Метка значения размытия
        if hasattr(self, '_blur_value_label'):
            self._blur_value_label.setStyleSheet(f"""
                QLabel {{
                    color: {ACCENT_CYAN};
                    font-size: {FONT_SIZE_BODY}px;
                    font-weight: bold;
                    font-family: {FONT_FAMILY};
                }}
            """)

        # ComboBox
        for combo in self.findChildren(QComboBox):
            combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {BACKGROUND_TERTIARY};
                    color: {TEXT_PRIMARY};
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-family: {FONT_FAMILY};
                    font-size: {FONT_SIZE_BODY}px;
                }}
                QComboBox:focus {{
                    border: 1px solid {ACCENT_CYAN};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 24px;
                }}
            """)

        # SpinBox
        for spin in self.findChildren(QSpinBox):
            spin.setStyleSheet(f"""
                QSpinBox {{
                    background-color: {BACKGROUND_TERTIARY};
                    color: {TEXT_PRIMARY};
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-family: {FONT_FAMILY};
                    font-size: {FONT_SIZE_BODY}px;
                }}
                QSpinBox:focus {{
                    border: 1px solid {ACCENT_CYAN};
                }}
            """)

        # Кнопки с glassmorphism
        for btn in self.findChildren(QPushButton):
            if btn.objectName() == "accentButton":
                btn.setStyleSheet(f"""
                    QPushButton#accentButton {{
                        background-color: {GLASS_BUTTON_BG};
                        color: {BACKGROUND_PRIMARY};
                        border: 1px solid rgba(6, 182, 212, 100);
                        border-radius: 8px;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-family: {FONT_FAMILY};
                        font-size: {FONT_SIZE_BODY}px;
                    }}
                    QPushButton#accentButton:hover {{
                        background-color: rgba(6, 182, 212, 220);
                    }}
                """)
            elif btn.objectName() == "minimalButton":
                btn.setStyleSheet(f"""
                    QPushButton#minimalButton {{
                        background-color: rgba(255, 255, 255, 10);
                        color: {TEXT_PRIMARY};
                        border: 1px solid {GLASS_BORDER};
                        border-radius: 8px;
                        padding: 10px 20px;
                        font-family: {FONT_FAMILY};
                        font-size: {FONT_SIZE_BODY}px;
                    }}
                    QPushButton#minimalButton:hover {{
                        background-color: {GLASS_HOVER};
                        border: 1px solid rgba(255, 255, 255, 40);
                        color: {ACCENT_CYAN};
                    }}
                """)

        # Статус
        self._status_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: {FONT_SIZE_SMALL}px;
                font-family: {FONT_FAMILY};
                padding: 8px;
            }}
        """)

    def _load_settings(self):
        """Загрузка настроек из конфигурации."""
        # Битрикс24
        bitrix_webhook = self._config.get("bitrix_webhook", {})
        self._webhook_input.setText(bitrix_webhook.get("webhook_url", ""))
        self._status_combo.setCurrentText(
            bitrix_webhook.get("status_id", "Новая заявка")
        )
        self._max_leads_spin.setValue(bitrix_webhook.get("max_leads_per_manager", 100))

        bitrix = self._config.get("bitrix", {})
        self._stage_input.setText(bitrix.get("stage", "Новая заявка"))
        self._source_input.setText(bitrix.get("source", "Холодный звонок"))
        self._service_input.setText(bitrix.get("service_type", "ГЦК"))

        # Интерфейс - прозрачность
        ui = self._config.get("ui", {})
        transparency_enabled = ui.get("transparency_enabled", True)
        self._transparency_checkbox.setChecked(
            transparency_enabled
        )
        
        # Интерфейс - интенсивность размытия
        blur_intensity = ui.get("blur_intensity", 100)
        self._blur_slider.setValue(blur_intensity)
        # Обновляем текстовую метку
        from utils.windows_blur import get_blur_intensity_label
        self._blur_value_label.setText(get_blur_intensity_label(blur_intensity))

    def _save_settings(self):
        """Сохранение настроек."""
        # Проверка вебхука
        webhook_url = self._webhook_input.text().strip()
        is_valid, message = validate_bitrix_webhook_url(webhook_url)
        if not is_valid:
            self._status_label.setText(f"❌ {message}")
            self._status_label.setStyleSheet(f"color: {STATUS_ERROR};")
            print(f"Пользователь ввёл некорректный вебхук: {webhook_url[:20] if webhook_url else 'пустой'}...")
            return
        
        # Сохранение валидного вебхука
        # Битрикс24
        if "bitrix_webhook" not in self._config:
            self._config["bitrix_webhook"] = {}

        self._config["bitrix_webhook"]["webhook_url"] = webhook_url
        self._config["bitrix_webhook"]["status_id"] = self._status_combo.currentText()
        self._config["bitrix_webhook"][
            "max_leads_per_manager"
        ] = self._max_leads_spin.value()

        # Сохраняем webhook_url также в .env
        try:
            env_path = Path(__file__).parent.parent.parent / ".env"
            if env_path.exists():
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # Обновляем BITRIX_WEBHOOK_URL
                env_updated = False
                for i, line in enumerate(lines):
                    if line.startswith("BITRIX_WEBHOOK_URL="):
                        lines[i] = f"BITRIX_WEBHOOK_URL={webhook_url}\n"
                        env_updated = True
                        break

                if not env_updated:
                    lines.append(f"\nBITRIX_WEBHOOK_URL={webhook_url}\n")

                with open(env_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
        except Exception as e:
            print(f"Ошибка сохранения .env: {e}")

        if "bitrix" not in self._config:
            self._config["bitrix"] = {}

        self._config["bitrix"]["stage"] = self._stage_input.text().strip()
        self._config["bitrix"]["source"] = self._source_input.text().strip()
        self._config["bitrix"]["service_type"] = self._service_input.text().strip()

        # Интерфейс - прозражность
        if "ui" not in self._config:
            self._config["ui"] = {}
        self._config["ui"]["transparency_enabled"] = self._transparency_checkbox.isChecked()
        self._config["ui"]["blur_intensity"] = self._blur_slider.value()

        # Города и районы
        self._config["regions"] = self._cities
        self._config["city_districts"] = self._city_districts

        # Сохранение
        if save_config(self._config):
            self._status_label.setText("✅ Настройки сохранены")
            self._status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
            self.settings_saved.emit(self._config)
        else:
            self._status_label.setText("❌ Ошибка сохранения")
            self._status_label.setStyleSheet(f"color: {STATUS_ERROR};")

    def _export_settings(self):
        """Экспорт настроек в файл."""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Экспорт настроек", "leadgen_settings.json", JSON_FILE_FILTER
        )

        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(self._config, f, indent=4, ensure_ascii=False)
                self._status_label.setText(f"✅ Настройки экспортированы: {filepath}")
                self._status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
            except Exception as e:
                self._status_label.setText(f"❌ Ошибка экспорта: {e}")
                self._status_label.setStyleSheet(f"color: {STATUS_ERROR};")

    def _import_settings(self):
        """Импорт настроек из файла."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Импорт настроек", "", JSON_FILE_FILTER
        )

        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    imported_config = json.load(f)

                self._config.update(imported_config)
                self._load_settings()
                self._status_label.setText("✅ Настройки импортированы")
                self._status_label.setStyleSheet(f"color: {STATUS_SUCCESS};")
            except Exception as e:
                self._status_label.setText(f"❌ Ошибка импорта: {e}")
                self._status_label.setStyleSheet(f"color: {STATUS_ERROR};")
