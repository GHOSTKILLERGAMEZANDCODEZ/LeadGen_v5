"""
Круговой индикатор прогресса (Circular Progress Bar).

Компонент для отображения загрузки в виде кругового прогресс-бара
с поддержкой анимации и кастомизации размеров.

Пример использования:
    >>> progress = CircularProgress(size=60, line_width=6)
    >>> progress.set_value(75)
    >>> progress.start_animation()  # Для индетерминированного режима
"""

from PySide6.QtCore import Property, QRect, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from gui.styles.theme import ACCENT_CYAN, BACKGROUND_TERTIARY


class CircularProgress(QWidget):
    """
    Круговой индикатор прогресса.

    Отрисовывает круговой прогресс-бар с настраиваемыми размерами,
    толщиной линии и поддержкой анимации.

    Attributes:
        _size: Размер виджета в пикселях
        _line_width: Толщина линии прогресса
        _value: Текущее значение прогресса (0-100)
        _maximum: Максимальное значение прогресса
        _animation_angle: Угол вращения для анимации

    Example:
        >>> progress = CircularProgress(size=40, line_width=4)
        >>> progress.set_value(50)
        >>> progress.show()
    """

    def __init__(
        self,
        size: int = 40,
        line_width: int = 4,
        parent: QWidget | None = None,
    ) -> None:
        """
        Инициализирует круговой прогресс-бар.

        Args:
            size: Размер виджета в пикселях (ширина и высота). По умолчанию 40.
            line_width: Толщина линии прогресса в пикселях. По умолчанию 4.
            parent: Родительский виджет. По умолчанию None.

        Example:
            >>> progress = CircularProgress(size=60, line_width=6)
            >>> progress.set_value(75)
        """
        super().__init__(parent)

        self._size: int = size
        self._line_width: int = line_width
        self._value: int = 0
        self._maximum: int = 100
        self._animation_angle: int = 0

        # Настройка размеров виджета
        self.setFixedSize(size, size)

        # Таймер для анимации вращения
        self._animation_timer: QTimer | None = None


    @Property(int)
    def animation_angle(self) -> int:
        """
        Получает текущий угол вращения для анимации.

        Returns:
            Угол вращения в градусах (0-360).
        """
        return self._animation_angle

    @animation_angle.setter
    def animation_angle(self, angle: int) -> None:
        """
        Устанавливает угол вращения и обновляет виджет.

        Args:
            angle: Угол вращения в градусах.
        """
        self._animation_angle = angle % 360
        self.update()

    def set_value(self, value: int) -> None:
        """
        Устанавливает значение прогресса.

        Значение ограничивается диапазоном от 0 до maximum.

        Args:
            value: Новое значение прогресса. Должно быть в диапазоне 0-maximum.

        Example:
            >>> progress = CircularProgress()
            >>> progress.set_value(50)  # Установить 50%
            >>> progress.set_value(150)  # Будет ограничено до maximum (100)
        """
        clamped_value = max(0, min(value, self._maximum))
        if self._value != clamped_value:
            self._value = clamped_value
            self.update()

    def setMaximum(self, maximum: int) -> None:
        """
        Устанавливает максимальное значение прогресса.

        Args:
            maximum: Максимальное значение. Должно быть больше 0.

        Example:
            >>> progress = CircularProgress()
            >>> progress.setMaximum(200)  # Максимум 200 вместо 100
            >>> progress.set_value(150)  # Теперь это 75%
        """
        if maximum <= 0:
            raise ValueError("Maximum must be greater than 0")
        self._maximum = maximum
        # Пересчитываем текущее значение если оно выходит за новый максимум
        if self._value > maximum:
            self._value = maximum
        self.update()

    def value(self) -> int:
        """
        Получает текущее значение прогресса.

        Returns:
            Текущее значение прогресса (0-maximum).

        Example:
            >>> progress = CircularProgress()
            >>> progress.set_value(75)
            >>> progress.value()
            75
        """
        return self._value

    def start_animation(self) -> None:
        """
        Запускает анимацию непрерывного вращения.

        Используется для индетерминированного режима, когда неизвестно
        точное время выполнения операции.

        Example:
            >>> progress = CircularProgress()
            >>> progress.start_animation()  # Запустить вращение
            # ... выполнение операции ...
            >>> progress.stop_animation()  # Остановить
        """
        if self._animation_timer is None:
            self._animation_timer = QTimer(self)
            self._animation_timer.timeout.connect(self._on_animation_tick)

        if not self._animation_timer.isActive():
            self._animation_timer.start(50)  # 50ms интервал для плавности

    def stop_animation(self) -> None:
        """
        Останавливает анимацию вращения.

        Example:
            >>> progress = CircularProgress()
            >>> progress.start_animation()
            # ... выполнение операции ...
            >>> progress.stop_animation()
        """
        if self._animation_timer is not None:
            self._animation_timer.stop()
            self._animation_angle = 0
            self.update()

    def _on_animation_tick(self) -> None:
        """
        Обработчик тика таймера анимации.

        Увеличивает угол вращения на 30 градусов для создания
        эффекта плавного вращения.
        """
        self.animation_angle = self._animation_angle + 30

    def _create_pen(self, color: str) -> QPen:
        """
        Создаёт перо для отрисовки дуг.
        """
        pen = QPen(QColor(color))
        pen.setWidth(self._line_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        return pen

    def paintEvent(self, event) -> None:  # noqa: ARG002
        """
        Обработчик события отрисовки.

        Отрисовывает круговой прогресс-бар с использованием QPainter:
        1. Фоновый круг (серый, BACKGROUND_TERTIARY)
        2. Дуга прогресса (cyan, ACCENT_CYAN)

        Args:
            event: Событие отрисовки.

        Note:
            - Начало дуги: 12 часов (90 градусов против часовой стрелки)
            - Направление: по часовой стрелке
            - Сглаживание: включено (Antialiasing)
            - Концы линии: закруглённые (RoundCap)
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Вычисляем центр и радиус
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = (min(self.width(), self.height()) - self._line_width) // 2

        # Прямоугольник для отрисовки дуги
        rect = QRect(
            center_x - radius,
            center_y - radius,
            radius * 2,
            radius * 2,
        )

        # Отрисовка фонового круга (серый)
        painter.setPen(self._create_pen(BACKGROUND_TERTIARY))
        painter.drawArc(
            rect,
            0,
            360 * 16,  # Полный круг (в 16-х долях градуса)
        )

        # Отрисовка дуги прогресса (cyan)
        is_animating = self._animation_timer is not None and self._animation_timer.isActive()
        if self._value > 0 or is_animating:
            painter.setPen(self._create_pen(ACCENT_CYAN))

            if is_animating:
                # Режим анимации: вращающаяся дуга
                start_angle = (self._animation_angle - 45) * 16  # Начало с offset
                span_angle = 120 * 16  # Дуга 120 градусов
                painter.drawArc(rect, start_angle, span_angle)
            else:
                # Режим прогресса: дуга пропорциональна значению
                # Начало: 12 часов (-90 градусов = 270 градусов = -90 * 16)
                start_angle = -90 * 16
                # Вычисляем угол в 16-х долях градуса
                span_angle = int((self._value / self._maximum) * 360 * 16)
                painter.drawArc(rect, start_angle, span_angle)

        painter.end()

    def sizeHint(self) -> tuple[int, int]:
        """
        Возвращает рекомендуемый размер виджета.

        Returns:
            Кортеж (ширина, высота) рекомендуемого размера.
        """
        return (self._size, self._size)

    def minimumSizeHint(self) -> tuple[int, int]:
        """
        Возвращает минимальный размер виджета.

        Returns:
            Кортеж (ширина, высота) минимального размера.
        """
        return (self._line_width * 4, self._line_width * 4)
