"""
Модуль для включения эффекта размытия (blur) в Windows через DWM.

Использует DwmEnableBlurBehindWindow для создания эффекта Aero/Glass.
Работает только на Windows Vista и выше.
"""

import sys
import ctypes
from ctypes import wintypes


# Проверка, что мы на Windows
IS_WINDOWS = sys.platform == "win32"

# Определение версии Windows
WINDOWS_VERSION = None
WINDOWS_BUILD = 0
if IS_WINDOWS:
    try:
        version = sys.getwindowsversion()
        WINDOWS_VERSION = (version.major, version.minor)
        WINDOWS_BUILD = version.build
    except Exception:
        WINDOWS_VERSION = (10, 0)
        WINDOWS_BUILD = 0

# Windows 11 начинается с build 22000 (версия 21H2)
IS_WINDOWS_11 = WINDOWS_BUILD >= 22000

if IS_WINDOWS:
    # Загружаем DWM API
    dwmapi = ctypes.windll.dwmapi

    # Константы для DWM
    DWM_BB_ENABLE = 1
    DWM_BB_BLURREGION = 2
    DWM_BB_TRANSITIONONMAXIMIZED = 4
    DWMWA_USE_HOSTBACKDROPBRUSH = 17  # Windows 10 1809+
    DWMWA_SYSTEMBACKDROP_TYPE = 38  # Windows 11 22H2+

    # Константы для DWMWA_SYSTEMBACKDROP_TYPE (Windows 11)
    DWM_SYSTEMBACKDROP_TYPE_AUTO = 0  # Системный
    DWM_SYSTEMBACKDROP_TYPE_NONE = 1  # Без эффекта
    DWM_SYSTEMBACKDROP_TYPE_ACRYLIC = 2  # Сильное размытие
    DWM_SYSTEMBACKDROP_TYPE_MICA = 3  # Слабый эффект
    DWM_SYSTEMBACKDROP_TYPE_MICA_ALT = 4  # Mica Alt

    # Структура DWM_BLURBEHIND
    class DWM_BLURBEHIND(ctypes.Structure):
        _fields_ = [
            ("dwFlags", wintypes.DWORD),
            ("fEnable", wintypes.BOOL),
            ("hRgnBlur", wintypes.HRGN),
            ("fTransitionOnMaximized", wintypes.BOOL),
        ]

    def _set_blur(hwnd: int, enable: bool) -> bool:
        try:
            blur_behind = DWM_BLURBEHIND()
            blur_behind.dwFlags = DWM_BB_ENABLE
            blur_behind.fEnable = bool(enable)
            blur_behind.hRgnBlur = 0  # Blur на всё окно
            blur_behind.fTransitionOnMaximized = False

            result = dwmapi.DwmEnableBlurBehindWindow(
                hwnd, ctypes.byref(blur_behind)
            )

            return result == 0
        except Exception as e:
            action = "enabling" if enable else "disabling"
            print(f"Error {action} blur: {e}")
            return False

    # Функция для включения blur на всё окно
    def enable_blur(hwnd: int) -> bool:
        """
        Включает размытие фона для окна.

        Args:
            hwnd: Handle окна

        Returns:
            True если успешно, False иначе
        """
        return _set_blur(hwnd, True)

    def disable_blur(hwnd: int) -> bool:
        """
        Отключает размытие фона для окна.

        Args:
            hwnd: Handle окна

        Returns:
            True если успешно, False иначе
        """
        return _set_blur(hwnd, False)

    def _set_system_backdrop_type(hwnd: int, backdrop_type: int) -> bool:
        """
        Устанавливает тип системного фона (Windows 11 22H2+).

        Args:
            hwnd: Handle окна
            backdrop_type: Тип фона (0=Auto, 1=None, 2=Acrylic, 3=Mica, 4=Mica Alt)

        Returns:
            True если успешно, False иначе
        """
        try:
            result = dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_SYSTEMBACKDROP_TYPE,
                ctypes.byref(ctypes.c_int(backdrop_type)),
                ctypes.sizeof(ctypes.c_int)
            )
            return result == 0
        except Exception as e:
            print(f"Error setting system backdrop type: {e}")
            return False
else:
    # Заглушки для не-Windows платформ
    def enable_blur(hwnd: int) -> bool:
        return False

    def disable_blur(hwnd: int) -> bool:
        return False

    def _set_system_backdrop_type(hwnd: int, backdrop_type: int) -> bool:
        return False


def apply_glass_effect(widget) -> bool:
    """
    Применяет эффект стекла к виджету PySide6.

    Args:
        widget: QWidget к которому применить эффект

    Returns:
        True если успешно, False иначе
    """
    if not IS_WINDOWS:
        return False

    try:
        # Получаем HWND от виджета
        hwnd = int(widget.winId())

        # Включаем blur
        success = enable_blur(hwnd)

        return success
    except Exception as e:
        print(f"Error applying glass effect: {e}")
        return False


def apply_acrylic_effect(widget, intensity: int = 100) -> bool:
    """
    Применяет эффект Acrylic (Windows 10/11) - более сильное размытие.
    Требует Windows 10 версии 1809 или выше.

    Args:
        widget: QWidget к которому применить эффект
        intensity: Интенсивность размытия (0-100)
                   0 = выключено, 50 = среднее, 100 = максимальное

    Returns:
        True если успешно, False иначе
    """
    if not IS_WINDOWS:
        return False

    try:
        hwnd = int(widget.winId())

        # Для Windows 11 используем DWMWA_SYSTEMBACKDROP_TYPE
        if IS_WINDOWS_11:
            # Маппинг интенсивности на типы фона
            if intensity <= 0:
                backdrop_type = DWM_SYSTEMBACKDROP_TYPE_NONE
            elif intensity <= 33:
                backdrop_type = DWM_SYSTEMBACKDROP_TYPE_MICA  # Слабое
            elif intensity <= 66:
                backdrop_type = DWM_SYSTEMBACKDROP_TYPE_MICA_ALT  # Среднее
            else:
                backdrop_type = DWM_SYSTEMBACKDROP_TYPE_ACRYLIC  # Сильное

            result = _set_system_backdrop_type(hwnd, backdrop_type)
            if result:
                # Дополнительно включаем blur для лучшего эффекта
                if intensity > 0:
                    enable_blur(hwnd)
                return True
            # Fallback на Windows 10 метод если не сработало
        else:
            # Windows 10 - используем host backdrop brush
            # Интенсивность регулируется через включение/выключение
            if intensity > 50:
                # Включаем Acrylic для высокой интенсивности
                result = dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_USE_HOSTBACKDROPBRUSH,
                    ctypes.byref(ctypes.c_int(1)),
                    ctypes.sizeof(ctypes.c_int)
                )
                if result == 0:
                    enable_blur(hwnd)
                    return True
            elif intensity > 0:
                # Для низкой интенсивности только blur
                enable_blur(hwnd)
                return True
            else:
                # Intensity = 0, отключаем всё
                disable_blur(hwnd)
                dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_USE_HOSTBACKDROPBRUSH,
                    ctypes.byref(ctypes.c_int(0)),
                    ctypes.sizeof(ctypes.c_int)
                )
                return True

        return False
    except Exception as e:
        print(f"Error applying acrylic effect: {e}")
        return False


def set_blur_intensity(widget, intensity: int) -> bool:
    """
    Устанавливает интенсивность размытия фона.

    Args:
        widget: QWidget к которому применить
        intensity: Интенсивность от 0 до 100
                   0 = без размытия
                   1-33 = Слабое размытие
                   34-66 = Среднее размытие
                   67-100 = Сильное размытие

    Returns:
        True если успешно, False иначе
    """
    if not IS_WINDOWS:
        return False

    # Ограничиваем диапазон
    intensity = max(0, min(100, intensity))

    try:
        hwnd = int(widget.winId())

        # Для Windows 11 используем DWMWA_SYSTEMBACKDROP_TYPE
        if IS_WINDOWS_11:
            # Маппинг интенсивности на типы фона
            if intensity <= 0:
                backdrop_type = DWM_SYSTEMBACKDROP_TYPE_NONE
            elif intensity <= 33:
                backdrop_type = DWM_SYSTEMBACKDROP_TYPE_MICA  # Слабое
            elif intensity <= 66:
                backdrop_type = DWM_SYSTEMBACKDROP_TYPE_MICA_ALT  # Среднее
            else:
                backdrop_type = DWM_SYSTEMBACKDROP_TYPE_ACRYLIC  # Сильное

            result = _set_system_backdrop_type(hwnd, backdrop_type)
            
            if result and intensity > 0:
                enable_blur(hwnd)
            return result
        else:
            # Windows 10 - используем комбинацию атрибутов
            if intensity <= 0:
                # Отключаем всё
                disable_blur(hwnd)
                dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_USE_HOSTBACKDROPBRUSH,
                    ctypes.byref(ctypes.c_int(0)),
                    ctypes.sizeof(ctypes.c_int)
                )
                return True
            elif intensity <= 50:
                # Только blur для низкой интенсивности
                disable_blur(hwnd)  # Сначала отключаем
                enable_blur(hwnd)  # Затем включаем для применения
                dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_USE_HOSTBACKDROPBRUSH,
                    ctypes.byref(ctypes.c_int(0)),
                    ctypes.sizeof(ctypes.c_int)
                )
                return True
            else:
                # Acrylic для высокой интенсивности
                result = dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_USE_HOSTBACKDROPBRUSH,
                    ctypes.byref(ctypes.c_int(1)),
                    ctypes.sizeof(ctypes.c_int)
                )
                if result == 0:
                    enable_blur(hwnd)
                    return True
                return False

    except Exception as e:
        print(f"Error setting blur intensity: {e}")
        return False


def remove_acrylic_effect(widget) -> bool:
    """
    Отключает эффект Acrylic.

    Args:
        widget: QWidget к которому применить

    Returns:
        True если успешно, False иначе
    """
    if not IS_WINDOWS:
        return False

    try:
        hwnd = int(widget.winId())

        # Для Windows 11 устанавливаем None
        if IS_WINDOWS_11:
            _set_system_backdrop_type(hwnd, DWM_SYSTEMBACKDROP_TYPE_NONE)

        # Отключаем host backdrop brush
        result = dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_HOSTBACKDROPBRUSH,
            ctypes.byref(ctypes.c_int(0)),
            ctypes.sizeof(ctypes.c_int)
        )

        # Отключаем blur
        disable_blur(hwnd)

        return result == 0
    except Exception as e:
        print(f"Error removing acrylic effect: {e}")
        return False


def get_blur_intensity_label(intensity: int) -> str:
    """
    Возвращает текстовое описание интенсивности размытия.

    Args:
        intensity: Интенсивность от 0 до 100

    Returns:
        Строка с описанием уровня размытия
    """
    if intensity <= 0:
        return "Выключено"
    elif intensity <= 33:
        return "Слабое"
    elif intensity <= 66:
        return "Среднее"
    else:
        return "Сильное"


def remove_glass_effect(widget) -> bool:
    """
    Отключает эффект стекла.

    Args:
        widget: QWidget к которому применить

    Returns:
        True если успешно, False иначе
    """
    if not IS_WINDOWS:
        return False

    try:
        hwnd = int(widget.winId())
        return disable_blur(hwnd)
    except Exception as e:
        print(f"Error removing glass effect: {e}")
        return False
