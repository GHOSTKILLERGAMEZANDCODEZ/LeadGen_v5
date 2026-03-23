"""
Модуль с QSS стилями для PySide6 компонентов.

Модуль предоставляет функцию для генерации полной таблицы стилей
в формате QSS (Qt Style Sheets) для всех GUI компонентов приложения.
Использует цветовую палитру из theme.py для обеспечения единого стиля.

Functions:
    get_main_stylesheet: Возвращает полную QSS строку со всеми стилями.

Example:
    >>> from gui.styles.stylesheet import get_main_stylesheet
    >>> stylesheet = get_main_stylesheet()
    >>> app.setStyleSheet(stylesheet)
"""

from gui.styles.theme import (
    ACCENT_CYAN,
    ACCENT_CYAN_ACTIVE,
    ACCENT_CYAN_HOVER,
    BACKGROUND_PRIMARY,
    BACKGROUND_SECONDARY,
    BACKGROUND_TERTIARY,
    BORDER_COLOR,
    BORDER_LIGHT,
    FONT_FAMILY,
    FONT_SIZE_BODY,
    FONT_SIZE_SMALL,
    FONT_SIZE_TITLE,
    STATUS_ERROR,
    STATUS_INFO,
    STATUS_SUCCESS,
    STATUS_WARNING,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    GLASS_SIDEBAR_BG,
    GLASS_CARD_BG,
    GLASS_BUTTON_BG,
    GLASS_BORDER,
    GLASS_HOVER,
)


def get_main_stylesheet() -> str:
    """
    Возвращает полную QSS строку со стилями для всех компонентов.

    Функция собирает все стили в единую таблицу стилей, включая:
    - Общие стили для QWidget и QMainWindow
    - Стили для sidebar и навигации
    - Стили для кнопок различных типов
    - Стили для полей ввода
    - Стили для таблиц
    - Стили для progress bar и скроллбаров
    - Стили для ComboBox, CheckBox, GroupBox
    - Стили для label различных состояний
    - Стили для toast уведомлений
    - Стили для splitter и tab widget

    Returns:
        str: Полная QSS строка со всеми стилями.

    Example:
        >>> stylesheet = get_main_stylesheet()
        >>> app.setStyleSheet(stylesheet)
    """
    styles: list[str] = []

    # =========================================================================
    # Общие стили
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   ОБЩИЕ СТИЛИ
   ============================================================================= */

QWidget {
    background-color: transparent;
    color: %(TEXT_PRIMARY)s;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
}

QMainWindow {
    background-color: transparent;
}
"""
        % {
            "BACKGROUND_PRIMARY": BACKGROUND_PRIMARY,
            "TEXT_PRIMARY": TEXT_PRIMARY,
            "FONT_FAMILY": FONT_FAMILY,
            "FONT_SIZE_BODY": FONT_SIZE_BODY,
            "GLASS_BORDER": GLASS_BORDER,
            "GLASS_HOVER": GLASS_HOVER,
        }
    )

    # =========================================================================
    # Sidebar
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   SIDEBAR
   ============================================================================= */

QWidget#sidebar {
    background-color: %(BACKGROUND_SECONDARY)s;
    border-right: 1px solid %(BORDER_COLOR)s;
}
"""
        % {
            "BACKGROUND_SECONDARY": BACKGROUND_SECONDARY,
            "BORDER_COLOR": BORDER_COLOR,
        }
    )

    # =========================================================================
    # Кнопки с glassmorphism
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   КНОПКИ
   ============================================================================= */

QPushButton {
    background-color: rgba(30, 30, 30, 50);
    color: %(TEXT_PRIMARY)s;
    border: 1px solid %(GLASS_BORDER)s;
    border-radius: 8px;
    padding: 8px 16px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    font-weight: 500;
}

QPushButton:hover {
    background-color: %(GLASS_HOVER)s;
    border-color: rgba(255, 255, 255, 40);
}

QPushButton:pressed {
    background-color: rgba(35, 35, 35, 60);
}

QPushButton:disabled {
    background-color: rgba(255, 255, 255, 10);
    color: %(TEXT_MUTED)s;
    border-color: transparent;
}

/* Accent Button - Glassmorphism Cyan */
QPushButton#accentButton {
    background-color: rgba(6, 182, 212, 100);
    color: %(BACKGROUND_PRIMARY)s;
    border: 1px solid rgba(6, 182, 212, 60);
}

QPushButton#accentButton:hover {
    background-color: rgba(6, 182, 212, 150);
    border-color: rgba(6, 182, 212, 100);
}

QPushButton#accentButton:pressed {
    background-color: rgba(6, 182, 212, 80);
    border-color: rgba(6, 182, 212, 60);
}

QPushButton#accentButton:disabled {
    background-color: rgba(255, 255, 255, 10);
    color: %(TEXT_MUTED)s;
    border-color: transparent;
}

/* Minimal Button - Glassmorphism */
QPushButton#minimalButton {
    background-color: rgba(255, 255, 255, 5);
    border: 1px solid %(GLASS_BORDER)s;
}

QPushButton#minimalButton:hover {
    background-color: %(GLASS_HOVER)s;
    border-color: rgba(255, 255, 255, 40);
}

QPushButton#minimalButton:pressed {
    background-color: rgba(255, 255, 255, 10);
}

/* Danger Button - Glassmorphism Red */
QPushButton#dangerButton {
    background-color: rgba(239, 68, 68, 80);
    color: %(BACKGROUND_PRIMARY)s;
    border: 1px solid rgba(239, 68, 68, 60);
    border-radius: 6px;
    padding: 8px 16px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    font-weight: 500;
}

QPushButton#dangerButton:hover {
    background-color: rgba(239, 68, 68, 120);
    border-color: rgba(239, 68, 68, 100);
}

QPushButton#dangerButton:pressed {
    background-color: rgba(220, 38, 38, 120);
    border-color: rgba(220, 38, 38, 100);
}

QPushButton#dangerButton:disabled {
    background-color: rgba(255, 255, 255, 10);
    color: %(TEXT_MUTED)s;
    border-color: transparent;
}
"""
        % {
            "BACKGROUND_PRIMARY": BACKGROUND_PRIMARY,
            "BACKGROUND_SECONDARY": BACKGROUND_SECONDARY,
            "BACKGROUND_TERTIARY": BACKGROUND_TERTIARY,
            "BORDER_COLOR": BORDER_COLOR,
            "BORDER_LIGHT": BORDER_LIGHT,
            "TEXT_PRIMARY": TEXT_PRIMARY,
            "TEXT_MUTED": TEXT_MUTED,
            "FONT_FAMILY": FONT_FAMILY,
            "FONT_SIZE_BODY": FONT_SIZE_BODY,
            "ACCENT_CYAN": ACCENT_CYAN,
            "ACCENT_CYAN_HOVER": ACCENT_CYAN_HOVER,
            "ACCENT_CYAN_ACTIVE": ACCENT_CYAN_ACTIVE,
            "STATUS_ERROR": STATUS_ERROR,
            "STATUS_SUCCESS": STATUS_SUCCESS,
            "STATUS_WARNING": STATUS_WARNING,
            "STATUS_INFO": STATUS_INFO,
            "GLASS_SIDEBAR_BG": GLASS_SIDEBAR_BG,
            "GLASS_CARD_BG": GLASS_CARD_BG,
            "GLASS_BUTTON_BG": GLASS_BUTTON_BG,
            "GLASS_BORDER": GLASS_BORDER,
            "GLASS_HOVER": GLASS_HOVER,
        }
    )

    # =========================================================================
    # Поля ввода с glassmorphism
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   ПОЛЯ ВВОДА
   ============================================================================= */

QLineEdit {
    background-color: rgba(30, 30, 30, 60);
    color: %(TEXT_PRIMARY)s;
    border: 1px solid %(GLASS_BORDER)s;
    border-radius: 8px;
    padding: 8px 12px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    selection-background-color: rgba(6, 182, 212, 100);
    selection-color: %(BACKGROUND_PRIMARY)s;
}

QLineEdit:hover {
    border-color: rgba(255, 255, 255, 40);
}

QLineEdit:focus {
    border-color: %(ACCENT_CYAN)s;
}

QLineEdit:disabled {
    background-color: rgba(40, 40, 40, 40);
    color: %(TEXT_MUTED)s;
    border-color: transparent;
}

QLineEdit::placeholder {
    color: %(TEXT_MUTED)s;
}

QTextEdit {
    background-color: rgba(30, 30, 30, 60);
    color: %(TEXT_PRIMARY)s;
    border: 1px solid %(GLASS_BORDER)s;
    border-radius: 8px;
    padding: 8px 12px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    selection-background-color: rgba(6, 182, 212, 100);
    selection-color: %(BACKGROUND_PRIMARY)s;
}

QTextEdit:hover {
    border-color: rgba(255, 255, 255, 40);
}

QTextEdit:focus {
    border-color: %(ACCENT_CYAN)s;
}

QTextEdit:disabled {
    background-color: rgba(40, 40, 40, 40);
    color: %(TEXT_MUTED)s;
    border-color: transparent;
}

QPlainTextEdit {
    background-color: rgba(30, 30, 30, 60);
    color: %(TEXT_PRIMARY)s;
    border: 1px solid %(GLASS_BORDER)s;
    border-radius: 8px;
    padding: 8px 12px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    selection-background-color: rgba(6, 182, 212, 100);
    selection-color: %(BACKGROUND_PRIMARY)s;
}

QPlainTextEdit:hover {
    border-color: rgba(255, 255, 255, 40);
}

QPlainTextEdit:focus {
    border-color: %(ACCENT_CYAN)s;
}

QPlainTextEdit:disabled {
    background-color: rgba(40, 40, 40, 40);
    color: %(TEXT_MUTED)s;
    border-color: transparent;
}
"""
        % {
            "BACKGROUND_PRIMARY": BACKGROUND_PRIMARY,
            "BACKGROUND_SECONDARY": BACKGROUND_SECONDARY,
            "BACKGROUND_TERTIARY": BACKGROUND_TERTIARY,
            "BORDER_COLOR": BORDER_COLOR,
            "BORDER_LIGHT": BORDER_LIGHT,
            "TEXT_PRIMARY": TEXT_PRIMARY,
            "TEXT_MUTED": TEXT_MUTED,
            "FONT_FAMILY": FONT_FAMILY,
            "FONT_SIZE_BODY": FONT_SIZE_BODY,
            "ACCENT_CYAN": ACCENT_CYAN,
            "GLASS_BORDER": GLASS_BORDER,
            "GLASS_HOVER": GLASS_HOVER,
        }
    )

    # =========================================================================
    # Таблицы
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   ТАБЛИЦЫ
   ============================================================================= */

QTableView {
    background-color: %(BACKGROUND_PRIMARY)s;
    color: %(TEXT_PRIMARY)s;
    border: 1px solid %(BORDER_COLOR)s;
    border-radius: 6px;
    gridline-color: %(BORDER_COLOR)s;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    selection-background-color: %(ACCENT_CYAN)s;
    selection-color: %(BACKGROUND_PRIMARY)s;
}

QTableView::item {
    padding: 8px;
    border: none;
}

QTableView::item:hover {
    background-color: %(BACKGROUND_TERTIARY)s;
}

QTableView::item:selected {
    background-color: %(ACCENT_CYAN)s;
    color: %(BACKGROUND_PRIMARY)s;
}

QTableWidget {
    background-color: rgba(30, 30, 30, 80);
    color: %(TEXT_PRIMARY)s;
    border: 1px solid %(GLASS_BORDER)s;
    border-radius: 8px;
    gridline-color: %(GLASS_BORDER)s;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    selection-background-color: rgba(6, 182, 212, 100);
    selection-color: %(BACKGROUND_PRIMARY)s;
}

QTableWidget::item {
    padding: 8px;
    border: none;
}

QTableWidget::item:hover {
    background-color: rgba(45, 45, 45, 80);
}

QTableWidget::item:selected {
    background-color: rgba(6, 182, 212, 120);
    color: %(BACKGROUND_PRIMARY)s;
}

QHeaderView::section {
    background-color: rgba(35, 35, 35, 80);
    color: %(TEXT_PRIMARY)s;
    border: none;
    border-bottom: 1px solid %(GLASS_BORDER)s;
    border-right: 1px solid %(GLASS_BORDER)s;
    padding: 8px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    font-weight: 600;
}

QHeaderView::section:hover {
    background-color: %(BACKGROUND_TERTIARY)s;
}

QHeaderView::section:first {
    border-top-left-radius: 6px;
}

QHeaderView::section:last {
    border-top-right-radius: 6px;
    border-right: none;
}

QHeaderView::section:horizontal:first {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
}

QHeaderView::section:horizontal:last {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    border-right: 1px solid %(BORDER_COLOR)s;
}

QHeaderView::section:vertical:first {
    border-top-left-radius: 0;
    border-top-right-radius: 0;
}

QHeaderView::section:vertical:last {
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
    border-bottom: none;
}
"""
        % {
            "BACKGROUND_PRIMARY": BACKGROUND_PRIMARY,
            "BACKGROUND_SECONDARY": BACKGROUND_SECONDARY,
            "BACKGROUND_TERTIARY": BACKGROUND_TERTIARY,
            "BORDER_COLOR": BORDER_COLOR,
            "TEXT_PRIMARY": TEXT_PRIMARY,
            "FONT_FAMILY": FONT_FAMILY,
            "FONT_SIZE_BODY": FONT_SIZE_BODY,
            "ACCENT_CYAN": ACCENT_CYAN,
            "GLASS_BORDER": GLASS_BORDER,
            "GLASS_HOVER": GLASS_HOVER,
        }
    )

    # =========================================================================
    # Progress Bar
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   PROGRESS BAR
   ============================================================================= */

QProgressBar {
    background-color: %(BACKGROUND_TERTIARY)s;
    border: 1px solid %(BORDER_COLOR)s;
    border-radius: 6px;
    text-align: center;
    color: %(TEXT_PRIMARY)s;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_SMALL)dpx;
    height: 20px;
}

QProgressBar::chunk {
    background-color: %(ACCENT_CYAN)s;
    border-radius: 5px;
}
"""
        % {
            "BACKGROUND_TERTIARY": BACKGROUND_TERTIARY,
            "BORDER_COLOR": BORDER_COLOR,
            "TEXT_PRIMARY": TEXT_PRIMARY,
            "FONT_FAMILY": FONT_FAMILY,
            "FONT_SIZE_SMALL": FONT_SIZE_SMALL,
            "ACCENT_CYAN": ACCENT_CYAN,
        }
    )

    # =========================================================================
    # Скроллбары
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   СКРОЛЛБАРЫ
   ============================================================================= */

QScrollBar:vertical {
    background-color: %(BACKGROUND_SECONDARY)s;
    width: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: %(BORDER_LIGHT)s;
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: %(TEXT_MUTED)s;
}

QScrollBar::handle:vertical:pressed {
    background-color: %(ACCENT_CYAN)s;
}

QScrollBar::add-line:vertical {
    height: 0;
}

QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background-color: %(BACKGROUND_SECONDARY)s;
    height: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: %(BORDER_LIGHT)s;
    border-radius: 6px;
    min-width: 30px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: %(TEXT_MUTED)s;
}

QScrollBar::handle:horizontal:pressed {
    background-color: %(ACCENT_CYAN)s;
}

QScrollBar::add-line:horizontal {
    width: 0;
}

QScrollBar::sub-line:horizontal {
    width: 0;
}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: none;
}
"""
        % {
            "BACKGROUND_SECONDARY": BACKGROUND_SECONDARY,
            "BORDER_LIGHT": BORDER_LIGHT,
            "TEXT_MUTED": TEXT_MUTED,
            "ACCENT_CYAN": ACCENT_CYAN,
        }
    )

    # =========================================================================
    # ComboBox
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   COMBOBOX
   ============================================================================= */

QComboBox {
    background-color: rgba(30, 30, 30, 80);
    color: %(TEXT_PRIMARY)s;
    border: 1px solid %(GLASS_BORDER)s;
    border-radius: 8px;
    padding: 8px 12px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
}

QComboBox:hover {
    border-color: rgba(255, 255, 255, 40);
}

QComboBox:focus {
    border-color: %(ACCENT_CYAN)s;
}

QComboBox:disabled {
    background-color: rgba(40, 40, 40, 60);
    color: %(TEXT_MUTED)s;
    border-color: transparent;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
    padding-right: 8px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid %(TEXT_PRIMARY)s;
    margin-right: 4px;
}

QComboBox QAbstractItemView {
    background-color: %(BACKGROUND_TERTIARY)s;
    color: %(TEXT_PRIMARY)s;
    border: 1px solid %(BORDER_COLOR)s;
    border-radius: 6px;
    selection-background-color: %(ACCENT_CYAN)s;
    selection-color: %(BACKGROUND_PRIMARY)s;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
}

QComboBox QAbstractItemView::item {
    padding: 8px 12px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: %(BACKGROUND_SECONDARY)s;
}

QComboBox QAbstractItemView::item:selected {
    background-color: %(ACCENT_CYAN)s;
    color: %(BACKGROUND_PRIMARY)s;
}
"""
        % {
            "BACKGROUND_PRIMARY": BACKGROUND_PRIMARY,
            "BACKGROUND_SECONDARY": BACKGROUND_SECONDARY,
            "BACKGROUND_TERTIARY": BACKGROUND_TERTIARY,
            "BORDER_COLOR": BORDER_COLOR,
            "BORDER_LIGHT": BORDER_LIGHT,
            "TEXT_PRIMARY": TEXT_PRIMARY,
            "TEXT_MUTED": TEXT_MUTED,
            "FONT_FAMILY": FONT_FAMILY,
            "FONT_SIZE_BODY": FONT_SIZE_BODY,
            "ACCENT_CYAN": ACCENT_CYAN,
            "GLASS_BORDER": GLASS_BORDER,
            "GLASS_HOVER": GLASS_HOVER,
        }
    )

    # =========================================================================
    # CheckBox
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   CHECKBOX
   ============================================================================= */

QCheckBox {
    color: %(TEXT_PRIMARY)s;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid %(BORDER_COLOR)s;
    background-color: %(BACKGROUND_TERTIARY)s;
}

QCheckBox::indicator:hover {
    border-color: %(BORDER_LIGHT)s;
}

QCheckBox::indicator:checked {
    background-color: %(ACCENT_CYAN)s;
    border-color: %(ACCENT_CYAN)s;
}

QCheckBox::indicator:checked:hover {
    background-color: %(ACCENT_CYAN_HOVER)s;
    border-color: %(ACCENT_CYAN_HOVER)s;
}

QCheckBox::indicator:disabled {
    background-color: %(BACKGROUND_SECONDARY)s;
    border-color: %(BORDER_COLOR)s;
}
"""
        % {
            "BACKGROUND_SECONDARY": BACKGROUND_SECONDARY,
            "BACKGROUND_TERTIARY": BACKGROUND_TERTIARY,
            "BORDER_COLOR": BORDER_COLOR,
            "BORDER_LIGHT": BORDER_LIGHT,
            "TEXT_PRIMARY": TEXT_PRIMARY,
            "FONT_FAMILY": FONT_FAMILY,
            "FONT_SIZE_BODY": FONT_SIZE_BODY,
            "ACCENT_CYAN": ACCENT_CYAN,
            "ACCENT_CYAN_HOVER": ACCENT_CYAN_HOVER,
            "GLASS_BORDER": GLASS_BORDER,
            "GLASS_HOVER": GLASS_HOVER,
        }
    )

    # =========================================================================
    # GroupBox
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   GROUPBOX
   ============================================================================= */

QGroupBox {
    background-color: %(BACKGROUND_SECONDARY)s;
    border: 1px solid %(BORDER_COLOR)s;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_TITLE)dpx;
    font-weight: 600;
    color: %(TEXT_PRIMARY)s;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: 0;
    padding: 0 8px;
    color: %(TEXT_PRIMARY)s;
}
"""
        % {
            "BACKGROUND_SECONDARY": BACKGROUND_SECONDARY,
            "BORDER_COLOR": BORDER_COLOR,
            "TEXT_PRIMARY": TEXT_PRIMARY,
            "FONT_FAMILY": FONT_FAMILY,
            "FONT_SIZE_TITLE": FONT_SIZE_TITLE,
            "GLASS_BORDER": GLASS_BORDER,
        }
    )

    # =========================================================================
    # Labels
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   LABELS
   ============================================================================= */

QLabel#titleLabel {
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_TITLE)dpx;
    font-weight: 600;
    color: %(TEXT_PRIMARY)s;
}

QLabel#secondaryLabel {
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    color: %(TEXT_SECONDARY)s;
}

QLabel#successLabel {
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    color: %(STATUS_SUCCESS)s;
}

QLabel#errorLabel {
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    color: %(STATUS_ERROR)s;
}

QLabel#warningLabel {
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    color: %(STATUS_WARNING)s;
}
"""
        % {
            "TEXT_PRIMARY": TEXT_PRIMARY,
            "TEXT_SECONDARY": TEXT_SECONDARY,
            "FONT_FAMILY": FONT_FAMILY,
            "FONT_SIZE_TITLE": FONT_SIZE_TITLE,
            "FONT_SIZE_BODY": FONT_SIZE_BODY,
            "STATUS_SUCCESS": STATUS_SUCCESS,
            "STATUS_ERROR": STATUS_ERROR,
            "STATUS_WARNING": STATUS_WARNING,
            "GLASS_BORDER": GLASS_BORDER,
        }
    )

    # =========================================================================
    # Toast уведомления
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   TOAST УВЕДОМЛЕНИЯ
   ============================================================================= */

QWidget#toast {
    background-color: %(BACKGROUND_TERTIARY)s;
    border: 1px solid %(BORDER_COLOR)s;
    border-radius: 8px;
    padding: 12px 16px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    color: %(TEXT_PRIMARY)s;
}

QWidget#toastSuccess {
    background-color: %(STATUS_SUCCESS)s;
    border: 1px solid %(STATUS_SUCCESS)s;
    border-radius: 8px;
    padding: 12px 16px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    color: %(BACKGROUND_PRIMARY)s;
}

QWidget#toastError {
    background-color: %(STATUS_ERROR)s;
    border: 1px solid %(STATUS_ERROR)s;
    border-radius: 8px;
    padding: 12px 16px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    color: %(BACKGROUND_PRIMARY)s;
}

QWidget#toastWarning {
    background-color: %(STATUS_WARNING)s;
    border: 1px solid %(STATUS_WARNING)s;
    border-radius: 8px;
    padding: 12px 16px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    color: %(BACKGROUND_PRIMARY)s;
}

QWidget#toastInfo {
    background-color: %(STATUS_INFO)s;
    border: 1px solid %(STATUS_INFO)s;
    border-radius: 8px;
    padding: 12px 16px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    color: %(BACKGROUND_PRIMARY)s;
}
"""
        % {
            "BACKGROUND_PRIMARY": BACKGROUND_PRIMARY,
            "BACKGROUND_TERTIARY": BACKGROUND_TERTIARY,
            "BORDER_COLOR": BORDER_COLOR,
            "TEXT_PRIMARY": TEXT_PRIMARY,
            "FONT_FAMILY": FONT_FAMILY,
            "FONT_SIZE_BODY": FONT_SIZE_BODY,
            "STATUS_SUCCESS": STATUS_SUCCESS,
            "STATUS_ERROR": STATUS_ERROR,
            "STATUS_WARNING": STATUS_WARNING,
            "STATUS_INFO": STATUS_INFO,
            "GLASS_BORDER": GLASS_BORDER,
        }
    )

    # =========================================================================
    # Splitter
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   SPLITTER
   ============================================================================= */

QSplitter::handle {
    background-color: %(BORDER_COLOR)s;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QSplitter::handle:vertical {
    height: 1px;
}

QSplitter::handle:hover {
    background-color: %(ACCENT_CYAN)s;
}
"""
        % {
            "BORDER_COLOR": BORDER_COLOR,
            "ACCENT_CYAN": ACCENT_CYAN,
            "GLASS_BORDER": GLASS_BORDER,
        }
    )

    # =========================================================================
    # TabWidget
    # =========================================================================

    styles.append(
        """
/* =============================================================================
   TAB WIDGET
   ============================================================================= */

QTabWidget::pane {
    background-color: %(BACKGROUND_PRIMARY)s;
    border: 1px solid %(BORDER_COLOR)s;
    border-radius: 6px;
    top: -1px;
}

QTabBar::tab {
    background-color: %(BACKGROUND_SECONDARY)s;
    color: %(TEXT_SECONDARY)s;
    border: 1px solid %(BORDER_COLOR)s;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    font-family: %(FONT_FAMILY)s;
    font-size: %(FONT_SIZE_BODY)dpx;
    margin-right: 2px;
}

QTabBar::tab:hover {
    background-color: %(BACKGROUND_TERTIARY)s;
    color: %(TEXT_PRIMARY)s;
}

QTabBar::tab:selected {
    background-color: %(BACKGROUND_PRIMARY)s;
    color: %(TEXT_PRIMARY)s;
    border-color: %(BORDER_COLOR)s;
}

QTabBar::tab:first:selected {
    border-left: 1px solid %(BORDER_COLOR)s;
}

QTabBar::tab:last:selected {
    border-right: 1px solid %(BORDER_COLOR)s;
}
"""
        % {
            "BACKGROUND_PRIMARY": BACKGROUND_PRIMARY,
            "BACKGROUND_SECONDARY": BACKGROUND_SECONDARY,
            "BACKGROUND_TERTIARY": BACKGROUND_TERTIARY,
            "BORDER_COLOR": BORDER_COLOR,
            "TEXT_PRIMARY": TEXT_PRIMARY,
            "TEXT_SECONDARY": TEXT_SECONDARY,
            "FONT_FAMILY": FONT_FAMILY,
            "FONT_SIZE_BODY": FONT_SIZE_BODY,
            "GLASS_BORDER": GLASS_BORDER,
            "GLASS_HOVER": GLASS_HOVER,
        }
    )

    # =========================================================================
    # Сборка финальной строки
    # =========================================================================

    return "\n".join(styles)
