"""
Генератор диаграмм для аналитики Битрикс24.

Использует matplotlib для создания диаграмм.
"""

import matplotlib

matplotlib.use("Agg")  # Неинтерактивный режим для сохранения без GUI

import matplotlib.pyplot as plt
import io
import pandas as pd
from pathlib import Path


def _theme_colors(dark_theme: bool) -> tuple[str, str]:
    text_color = "white" if dark_theme else "black"
    fig_color = "#2d2d30" if dark_theme else "white"
    return text_color, fig_color


def _normalize_labels(labels: list[str]) -> list[str]:
    return [label if label else "Без названия" for label in labels]


def _save_figure(fig: plt.Figure, dpi: int) -> bytes:
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def create_pie_chart(
    data: dict[str, int],
    title: str = "",
    figsize: tuple[int, int] = (14, 12),  # Ещё больше
    max_slices: int = 8,  # Меньше секторов
    dark_theme: bool = False,
) -> bytes:
    """
    Создаёт круговую диаграмму с умным объединением мелких секторов.

    Args:
        data: Словарь {метка: значение}
        title: Заголовок диаграммы
        figsize: Размер фигуры (ширина, высота)
        max_slices: Максимальное количество секторов
        dark_theme: Тёмная тема

    Returns:
        BytesIO с PNG изображением
    """
    text_color, fig_color = _theme_colors(dark_theme)
    fig, ax = plt.subplots(
        figsize=figsize, facecolor=fig_color
    )
    ax.set_facecolor(fig_color)

    # Сортируем данные по убыванию
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)

    total = sum(v for _, v in sorted_data)

    # Объединяем мелкие сектора (< 3%) в "Другое"
    filtered_data = []
    other_sum = 0

    for label, value in sorted_data:
        percentage = (value / total) * 100
        if percentage >= 3:
            filtered_data.append((label, value))
        else:
            other_sum += value

    # Добавляем "Другое" если есть
    if other_sum > 0 and len(filtered_data) < max_slices:
        filtered_data.append(("Другое", other_sum))

    # Если всё ещё много секторов, режем до max_slices
    if len(filtered_data) > max_slices:
        top_data = filtered_data[: max_slices - 1]
        other_sum = sum(v for _, v in filtered_data[max_slices - 1 :])
        if other_sum > 0:
            filtered_data = top_data + [("Другое", other_sum)]

    labels = _normalize_labels([x[0] for x in filtered_data])
    values = [x[1] for x in filtered_data]

    # Цветовая палитра (пастельные тона)
    colors = plt.cm.Set3(range(len(labels)))

    # Создаём диаграмму с выносками для маленьких секторов
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        pctdistance=0.75,  # Ближе к центру
        labeldistance=1.15,  # Подписи снаружи
        wedgeprops={"edgecolor": "#2d2d30", "linewidth": 2},  # Границы секторов
    )

    # Поворачиваем проценты для читаемости
    for i, autotext in enumerate(autotexts):
        percentage = (values[i] / sum(values)) * 100
        fontsize = 9 if percentage < 10 else 11
        autotext.set_color(text_color)
        autotext.set_fontsize(fontsize)
        autotext.set_fontweight("bold")

    # Подписи категорий - делаем жирными и крупнее
    for text in texts:
        text.set_color(text_color)
        text.set_fontsize(11)
        text.set_fontweight("bold")

    ax.set_title(title, fontsize=18, fontweight="bold", pad=30, color=text_color)

    return _save_figure(fig, dpi=150)


def create_bar_chart(
    data: dict[str, int],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "Количество",
    figsize: tuple[int, int] = (12, 7),
    horizontal: bool = False,
    max_bars: int = 15,
    color: str = "#1a73e8",
    dark_theme: bool = False,
) -> bytes:
    """
    Создаёт столбчатую диаграмму.

    Args:
        data: Словарь {метка: значение}
        title: Заголовок диаграммы
        xlabel: Подпись оси X
        ylabel: Подпись оси Y
        figsize: Размер фигуры
        horizontal: Горизонтальная ориентация
        max_bars: Максимальное количество столбцов
        color: Цвет столбцов

    Returns:
        BytesIO с PNG изображением
    """
    text_color, fig_color = _theme_colors(dark_theme)

    fig, ax = plt.subplots(figsize=figsize, facecolor=fig_color)
    ax.set_facecolor(fig_color)

    # Сортируем и берём топ N
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)[:max_bars]

    labels = _normalize_labels([x[0] for x in sorted_data])
    values = [x[1] for x in sorted_data]

    # Поворачиваем подписи если вертикальная
    rotation = 45 if not horizontal else 0

    if horizontal:
        # Горизонтальная диаграмма
        y_pos = range(len(labels))
        ax.barh(y_pos, values, color=color)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=10, color=text_color)
        ax.set_xlabel(xlabel, color=text_color)
        ax.set_ylabel(ylabel, color=text_color)
    else:
        # Вертикальная диаграмма
        ax.bar(range(len(labels)), values, color=color)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(
            labels, rotation=rotation, ha="right", fontsize=9, color=text_color
        )
        ax.set_xlabel(xlabel, color=text_color)
        ax.set_ylabel(ylabel, color=text_color)

    ax.set_title(title, fontsize=14, fontweight="bold", color=text_color)

    # Цвет осей
    ax.tick_params(colors=text_color)
    for spine in ax.spines.values():
        spine.set_color(text_color)

    # Сетка
    ax.grid(axis="y", alpha=0.3, color=text_color)

    return _save_figure(fig, dpi=100)


def create_funnel_chart(
    stages: list[str],
    values: list[int],
    title: str = "Воронка продаж",
    dark_theme: bool = False,
    figsize: tuple[int, int] = (14, 12),  # Увеличенный размер
) -> bytes:
    """
    Создаёт воронку продаж.

    Args:
        stages: Список названий стадий
        values: Список значений для каждой стадии
        title: Заголовок

    Returns:
        BytesIO с PNG изображением
    """
    text_color, fig_color = _theme_colors(dark_theme)

    fig, ax = plt.subplots(figsize=(10, 10), facecolor=fig_color)
    ax.set_facecolor(fig_color)

    # Нормализуем значения
    max_value = max(values) if values else 1

    # Цвета для стадий
    colors = plt.cm.Blues_r([0.3 + 0.7 * i / len(stages) for i in range(len(stages))])

    # Рисуем воронку
    y_positions = range(len(stages))
    widths = [v / max_value for v in values]

    for i, (y, width, color) in enumerate(zip(y_positions, widths, colors)):
        # Центрируем каждый уровень
        x_start = (1 - width) / 2
        ax.barh(y, width, left=x_start, height=0.8, color=color, edgecolor="white")

        # Подписи
        ax.text(
            0.5,
            y,
            f"{stages[i]}\n{values[i]}",
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="white" if width > 0.5 else "black",
        )

    ax.set_ylim(-0.5, len(stages) - 0.5)
    ax.set_xlim(0, 1.5)  # Увеличил с 1.2 до 1.5 для лучшей видимости
    ax.axis("off")
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20, color=text_color)

    return _save_figure(fig, dpi=100)


def create_conversion_chart(
    conversion_data: dict[str, dict],
    title: str = "Конверсия по категориям",
    max_categories: int = 10,
    dark_theme: bool = False,
) -> bytes:
    """
    Создаёт диаграмму конверсии по категориям.

    Args:
        conversion_data: {категория: {'leads': N, 'deals': N, 'conversion': N}}
        title: Заголовок
        max_categories: Максимальное количество категорий

    Returns:
        BytesIO с PNG изображением
    """
    text_color, fig_color = _theme_colors(dark_theme)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), facecolor=fig_color)
    fig.suptitle(title, fontsize=16, fontweight="bold", color=text_color)

    # Сортируем по конверсии
    sorted_cats = sorted(
        conversion_data.items(), key=lambda x: x[1].get("conversion", 0), reverse=True
    )[:max_categories]

    categories = _normalize_labels([x[0] for x in sorted_cats])
    leads = [x[1]["leads"] for x in sorted_cats]
    deals = [x[1]["deals"] for x in sorted_cats]
    conversions = [x[1]["conversion"] for x in sorted_cats]

    # Левая диаграмма: лиды vs сделки
    x = range(len(categories))
    width = 0.35

    ax1.bar([i - width / 2 for i in x], leads, width, label="Лиды", color="#1a73e8")
    ax1.bar([i + width / 2 for i in x], deals, width, label="Сделки", color="#34a853")

    ax1.set_xlabel("Категория", color=text_color)
    ax1.set_ylabel("Количество", color=text_color)
    ax1.set_title("Лиды и сделки по категориям", color=text_color)
    ax1.set_xticks(x)
    ax1.set_xticklabels(
        categories, rotation=45, ha="right", fontsize=9, color=text_color
    )
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    # Правая диаграмма: процент конверсии
    colors = [
        "#34a853" if c >= 20 else "#fbbc04" if c >= 10 else "#ea4335"
        for c in conversions
    ]
    ax2.bar(categories, conversions, color=colors)
    ax2.set_xlabel("Категория", color=text_color)
    ax2.set_ylabel("Конверсия, %", color=text_color)
    ax2.set_title("Конверсия по категориям", color=text_color)
    ax2.set_xticks(x)
    ax2.set_xticklabels(
        categories, rotation=45, ha="right", fontsize=9, color=text_color
    )
    ax2.grid(axis="y", alpha=0.3)

    # Добавляем значения на столбцы
    for i, (v, c) in enumerate(zip(conversions, categories)):
        ax2.text(
            i,
            v + 1,
            f"{v:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            color=text_color,
        )

    return _save_figure(fig, dpi=100)


def create_manager_performance_chart(
    leads_by_manager: dict[str, int],
    deals_by_manager: dict[str, int],
    title: str = "Эффективность менеджеров",
    dark_theme: bool = False,
) -> bytes:
    """
    Создаёт диаграмму эффективности менеджеров.

    Args:
        leads_by_manager: {менеджер: количество лидов}
        deals_by_manager: {менеджер: количество сделок}
        title: Заголовок

    Returns:
        BytesIO с PNG изображением
    """
    text_color, fig_color = _theme_colors(dark_theme)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), facecolor=fig_color)
    fig.suptitle(title, fontsize=16, fontweight="bold", color=text_color)

    # Объединяем всех менеджеров
    all_managers = set(leads_by_manager.keys()) | set(deals_by_manager.keys())
    all_managers = [m for m in all_managers if m]  # Убираем пустые

    # Сортируем по количеству сделок
    manager_deals = [(m, deals_by_manager.get(m, 0)) for m in all_managers]
    manager_deals.sort(key=lambda x: x[1], reverse=True)
    managers = [m[0] for m in manager_deals[:15]]

    leads = [leads_by_manager.get(m, 0) for m in managers]
    deals = [deals_by_manager.get(m, 0) for m in managers]
    conversions = [d / l * 100 if l > 0 else 0 for l, d in zip(leads, deals)]

    x = range(len(managers))
    width = 0.35

    # Левая диаграмма: лиды и сделки
    ax1.bar([i - width / 2 for i in x], leads, width, label="Лиды", color="#1a73e8")
    ax1.bar([i + width / 2 for i in x], deals, width, label="Сделки", color="#34a853")

    ax1.set_xlabel("Менеджер", color=text_color)
    ax1.set_ylabel("Количество", color=text_color)
    ax1.set_title("Лиды и сделки по менеджерам", color=text_color)
    ax1.set_xticks(x)
    ax1.set_xticklabels(managers, rotation=45, ha="right", fontsize=9, color=text_color)
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    # Правая диаграмма: конверсия
    colors = [
        "#34a853" if c >= 20 else "#fbbc04" if c >= 10 else "#ea4335"
        for c in conversions
    ]
    ax2.bar(managers, conversions, color=colors)
    ax2.set_xlabel("Менеджер", color=text_color)
    ax2.set_ylabel("Конверсия, %", color=text_color)
    ax2.set_title("Конверсия по менеджерам", color=text_color)
    ax2.set_xticks(x)
    ax2.set_xticklabels(managers, rotation=45, ha="right", fontsize=9, color=text_color)
    ax2.grid(axis="y", alpha=0.3)

    return _save_figure(fig, dpi=100)


# =============================================================================
# Функции-обёртки для работы с DataFrame
# =============================================================================


def build_leads_funnel(
    leads_data: pd.DataFrame,
    output_path: str,
    dark_theme: bool = False,
) -> bool:
    """
    Строит воронку лидов из DataFrame.

    Args:
        leads_data: DataFrame с колонками 'Категория' и 'Количество'
        output_path: Путь для сохранения изображения
        dark_theme: Тёмная тема

    Returns:
        True если успешно, False если данные пустые
    """
    if leads_data.empty or "Категория" not in leads_data.columns or "Количество" not in leads_data.columns:
        return False

    stages = leads_data["Категория"].tolist()
    values = leads_data["Количество"].tolist()

    if not stages or not values:
        return False

    image_bytes = create_funnel_chart(
        stages=stages,
        values=values,
        title="Воронка лидов",
        dark_theme=dark_theme,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return True


def build_category_chart(
    leads_data: pd.DataFrame,
    output_path: str,
    dark_theme: bool = False,
) -> bool:
    """
    Строит диаграмму категорий из DataFrame.

    Args:
        leads_data: DataFrame с колонками 'Категория' и 'Количество'
        output_path: Путь для сохранения изображения
        dark_theme: Тёмная тема

    Returns:
        True если успешно, False если данные пустые
    """
    if leads_data.empty or "Категория" not in leads_data.columns or "Количество" not in leads_data.columns:
        return False

    data = dict(zip(leads_data["Категория"], leads_data["Количество"]))

    if not data:
        return False

    image_bytes = create_bar_chart(
        data=data,
        title="Категории лидов",
        xlabel="Категория",
        ylabel="Количество",
        horizontal=True,
        dark_theme=dark_theme,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return True


def build_manager_chart(
    leads_data: pd.DataFrame,
    output_path: str,
    dark_theme: bool = False,
) -> bool:
    """
    Строит диаграмму менеджеров из DataFrame.

    Args:
        leads_data: DataFrame с колонками 'Менеджер' и 'Количество'
        output_path: Путь для сохранения изображения
        dark_theme: Тёмная тема

    Returns:
        True если успешно, False если данные пустые
    """
    if leads_data.empty or "Менеджер" not in leads_data.columns or "Количество" not in leads_data.columns:
        return False

    data = dict(zip(leads_data["Менеджер"], leads_data["Количество"]))

    if not data:
        return False

    image_bytes = create_bar_chart(
        data=data,
        title="Лиды по менеджерам",
        xlabel="Менеджер",
        ylabel="Количество",
        horizontal=True,
        dark_theme=dark_theme,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return True


def build_refusals_chart(
    leads_data: pd.DataFrame,
    output_path: str,
    dark_theme: bool = False,
) -> bool:
    """
    Строит диаграмму причин отказов из DataFrame.

    Args:
        leads_data: DataFrame с колонками 'Причина отказа' и 'Количество'
        output_path: Путь для сохранения изображения
        dark_theme: Тёмная тема

    Returns:
        True если успешно, False если данные пустые
    """
    if leads_data.empty or "Причина отказа" not in leads_data.columns or "Количество" not in leads_data.columns:
        return False

    data = dict(zip(leads_data["Причина отказа"], leads_data["Количество"]))

    if not data:
        return False

    image_bytes = create_pie_chart(
        data=data,
        title="Причины отказов",
        dark_theme=dark_theme,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return True


def build_leads_source_chart(
    leads_data: pd.DataFrame,
    output_path: str,
    dark_theme: bool = False,
) -> bool:
    """
    Строит диаграмму источников лидов из DataFrame.

    Args:
        leads_data: DataFrame с колонками 'Источник' и 'Количество'
        output_path: Путь для сохранения изображения
        dark_theme: Тёмная тема

    Returns:
        True если успешно, False если данные пустые
    """
    if leads_data.empty or "Источник" not in leads_data.columns or "Количество" not in leads_data.columns:
        return False

    data = dict(zip(leads_data["Источник"], leads_data["Количество"]))

    if not data:
        return False

    image_bytes = create_pie_chart(
        data=data,
        title="Источники лидов",
        dark_theme=dark_theme,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return True
