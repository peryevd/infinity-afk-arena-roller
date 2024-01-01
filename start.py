import time
import pytesseract
import pyautogui
import os
import platform
import numpy as np
import subprocess
import matplotlib.pyplot as plt

from datetime import datetime
from config import TELEGRAM_TOKEN, CHAT_ID

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pyautogui.MINIMUM_DURATION = 0  # Минимальное время между операциями
# Минимальное время ожидания между командными операциями
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0


pixel_coords = [(1432, 551), (1432, 1004),
                (1432, 1408), (1886, 88), (1760, 751), (1760, 1203), (1760, 1737), (2250, 326), (2094, 1085), (2092, 1419)]
colors = [((56, 48, 34), (63, 180, 253)), ((83, 74, 69),
                                           (90, 206, 255)), ((48, 40, 40), (55, 172, 255)), ((16, 15, 31), (30, 174, 255)), ((70, 57, 39), (76, 183, 252)), ((66, 56, 69), (70, 181, 255)), ((51, 38, 24), (55, 163, 237)), ((92, 89, 82), (107, 253, 255)), ((44, 31, 36), (64, 115, 181)), ((39, 41, 41), (43, 167, 252))]

common_count = 0
rare_count = 0
epic_count = 0

common_card_counts = [0] * 11
rare_card_counts = [0] * 11
epic_card_counts = [0] * 11


plt.ion()
fig, axs = plt.subplots(3, 1, figsize=(10, 8))
fig.patch.set_facecolor('#24d468')

header_text_obj = None


def update_graph(common, rare, epic):
    global axs
    # Очищаем оси для нового содержимого
    for ax in axs:
        ax.cla()

    # Для каждого подграфика создаем столбчатую диаграмму
    bars_common = axs[0].bar(
        np.arange(len(common)), common, color='grey', edgecolor='black', linewidth=1)
    axs[0].set_title('Обычные карты', fontsize=18, color='#033e19')
    axs[0].set_xticks(np.arange(len(common)))
    axs[0].set_facecolor('lightgray')
    axs[0].grid(True, color="gray", linestyle='--',
                linewidth=0.5, axis='y', alpha=0.7)
    axs[0].tick_params(axis='both', which='both',
                       labelsize=12, colors='#320611')

    bars_rare = axs[1].bar(np.arange(len(rare)), rare,
                           color='blue', edgecolor='black', linewidth=1)
    axs[1].set_title('Редкие карты', fontsize=18, color='#095170')
    axs[1].set_xticks(np.arange(len(rare)))
    axs[1].set_facecolor('lightblue')
    axs[1].grid(True, color="gray", linestyle='--',
                linewidth=0.5, axis='y', alpha=0.7)
    axs[1].tick_params(axis='both', which='both',
                       labelsize=12, colors='#320611')

    bars_epic = axs[2].bar(np.arange(len(epic)), epic,
                           color='gold', edgecolor='black', linewidth=1)
    axs[2].set_title('Другие карты', fontsize=18, color='#44520a')
    axs[2].set_xticks(np.arange(len(epic)))
    axs[2].set_facecolor('lightyellow')
    axs[2].grid(True, color="gray", linestyle='--',
                linewidth=0.5, axis='y', alpha=0.7)
    axs[2].tick_params(axis='both', which='both',
                       labelsize=12, colors='#320611')

    # Добавляем подписи количества на столбцы для каждого подграфика
    for idx, bars in enumerate([bars_common, bars_rare, bars_epic]):
        for bar in bars:
            height = bar.get_height()
            axs[idx].text(bar.get_x() + bar.get_width() / 2, height, f'{height}',
                          ha='center', va='bottom')

        ymax = max([bar.get_height() for bar in bars])
        axs[idx].set_ylim(0, ymax + ymax * 0.2)

    # Отображаем фигуру и оси
    fig.canvas.manager.window.setWindowTitle('Информация')
    fig.canvas.draw()
    plt.tight_layout()


def send_photo(screenshot_name, screenshot_folder, win_box):
    screenshot_path = os.path.join(
        screenshot_folder, screenshot_name)

    pyautogui.screenshot(screenshot_path, region=win_box)

    curl_command = [
        'curl', '-X', 'POST',

        f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto',
        '-F', f'chat_id={CHAT_ID}',
        '-F', f'photo=@{screenshot_path}'
    ]
    subprocess.run(curl_command)


def clear_console():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')


def countdown(seconds):
    for i in range(seconds, 0, -1):
        clear_console()
        print("Старт программы через ", i)
        time.sleep(1)


def is_color_within_range(target_color, actual_color, tolerance):
    return all(abs(tc - ac) <= tolerance for tc, ac in zip(target_color, actual_color))


def count_colored_points(points, colors, tolerance):
    gray_count, blue_count, other_count = 0, 0, 0

    for point, color_pair in zip(points, colors):
        point_color = pyautogui.pixel(*point)
        # Серый цвет
        if is_color_within_range(color_pair[0], point_color, tolerance):
            gray_count += 1
        # Синий цвет
        elif is_color_within_range(color_pair[1], point_color, tolerance):
            blue_count += 1
        else:
            other_count += 1

    return gray_count, blue_count, other_count


def stat_output(epic, attempt_count, count_dict, png_files, common_card_counts, rare_card_counts, epic_card_counts, time_delta):
    global header_text_obj
    clear_console()

    update_graph(common_card_counts, rare_card_counts, epic_card_counts)

    hours, remainder = divmod(time_delta .total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    header_text = f"Всего попыток - {attempt_count}\n"
    header_text += "\n".join(
        [f"{file.split('.')[0]} количество - {count_dict[file]} (шанс {count_dict[file] / attempt_count:.2%})"
         for file in png_files])
    header_text += f"\n\nОбщее количество карточек: {attempt_count * 10}\n"
    header_text += f"Эпические: {epic} (шанс {epic / (attempt_count * 10):.2%})\n"
    header_text += f"Прошло времени: {int(hours)} часов {int(minutes)} минут {int(seconds)} секунд"

    # Удаление предыдущего текста, если он существует
    if header_text_obj:
        header_text_obj.remove()

    # Добавление нового текста в "figure space"
    header_text_obj = plt.figtext(x=0.5, y=0.99, s=header_text,
                                  ha='center', fontsize=10, va='top')

    # Увеличить верхнее пространство
    plt.subplots_adjust(top=0.82)

    plt.pause(0.1)


def main():
    start_time = datetime.now()
    global common_count, rare_count, epic_count
    global common_card_counts, rare_card_counts, epic_card_counts
    update_graph(common_card_counts, rare_card_counts, epic_card_counts)
    plt.pause(0.1)

    countdown(5)
    start_coords = pyautogui.position()

    count_dict = {}
    attempt_count = 0
    screenshot_folder = "./images"
    images_directory = "./"

    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)

    win = pyautogui.getActiveWindow()
    crop_percentage = 30

    central_box = (
        int(max(0, win.left) + win.width * (crop_percentage / 100)),
        int(max(0, win.top)),
        int(win.width - 2 * (win.width * (crop_percentage / 100))),
        int(win.height)
    )

    print(win.title)
    offset = 350
    # offset = win.width*0.35

    # Получаем список всех .png файлов в директории
    png_files = [f for f in os.listdir(images_directory) if f.endswith('.png')]

    # Инициализируем счетчики для каждого файла
    for file in png_files:
        count_dict[file] = 0

    while True:
        current_coords = pyautogui.position()
        if current_coords != start_coords:
            input("Движение мышью, программа остановлена...")

        pyautogui.screenshot(
            "./images/current_screenshot.png", region=central_box)

        common, rare, epic = count_colored_points(pixel_coords, colors, 60)

        common_count += common
        rare_count += rare
        epic_count += epic

        common_card_counts[common] += 1
        rare_card_counts[rare] += 1
        epic_card_counts[epic] += 1

        attempt_count += 1
        files_found = 0

        # Перебираем все файлы и проверяем их наличие на экране
        for file in png_files:
            file_path = os.path.join(images_directory, file)
            location = pyautogui.locateOnScreen(
                file_path, confidence=0.7,  region=central_box)
            if location:
                count_dict[file] += 1
                files_found += 1

        # Выводим информацию о количестве совпадений на экране каждого файла
        stat_output(epic_count, attempt_count, count_dict, png_files,
                    common_card_counts, rare_card_counts, epic_card_counts, datetime.now() - start_time)

        if files_found == len(png_files):
            send_photo("winning_screenshot.png", "./", central_box)
            input("Все герои найдены!")
            return

        pyautogui.click()
        time.sleep(1)
        pyautogui.click((start_coords[0] + offset, start_coords[1]))
        time.sleep(0.5)
        for _ in range(5):
            pyautogui.click((start_coords[0] + offset, start_coords[1]))
            time.sleep(0.1)
        pyautogui.moveTo(start_coords)
        time.sleep(0.5)


main()
