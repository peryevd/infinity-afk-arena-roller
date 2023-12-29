import time
import pytesseract
import pyautogui
import os
import platform

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


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


def main():
    countdown(5)
    start_coords = pyautogui.position()

    # Словарь для подсчета количества каждого файла
    count_dict = {}
    attempt_count = 0
    # Относительный путь к папке где лежит скрипт
    images_directory = "./"

    # Получаем список всех .png файлов в директории
    png_files = [f for f in os.listdir(images_directory) if f.endswith('.png')]

    # Инициализируем счетчики для каждого файла
    for file in png_files:
        count_dict[file] = 0

    while True:
        current_coords = pyautogui.position()
        if current_coords != start_coords:
            input("Движение мышью, программа остановлена...")
            break

        attempt_count += 1
        files_found = 0

        # Перебираем все файлы и проверяем их наличие на экране
        for file in png_files:
            file_path = os.path.join(images_directory, file)
            location = pyautogui.locateOnScreen(file_path, confidence=0.7)
            if location:
                count_dict[file] += 1
                files_found += 1

        clear_console()

        # Выводим информацию о количестве совпадений на экране каждого файла
        print("всего попыток - ", attempt_count, "\n")
        print("\n".join(
            [f"{file.split('.')[0]} количество - {count_dict[file]} (шанс {count_dict[file] / attempt_count:.2%})" for file in png_files]))

        if files_found == len(png_files):
            input("Все герои найдены!")
            return

        pyautogui.click()
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(1)
        pyautogui.click()
        time.sleep(1)


main()
