import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import os

# Инициализация last_month текущим месяцем
last_month = datetime.now().strftime("%m")

# URL страницы
url = "https://www.gismeteo.ru/weather-sankt-peterburg-4079/statistics/"

# Словарь для преобразования названий месяцев в числа
month_map = {
    "янв": "01", "фев": "02", "мар": "03", "апр": "04",
    "май": "05", "июн": "06", "июл": "07", "авг": "08",
    "сен": "09", "окт": "10", "ноя": "11", "дек": "12"
}

# Тестовые данные для проверки перехода через год
test_weather_data = [
    ("29 дек", "-5"),  # Декабрь текущего года
    ("30 дек", "-10"),
    ("31 дек", "-11"),
    ("1 янв", "0"),   # Январь следующего года
    ("2 янв", "1"),
    ("3 янв", "2"),
]

# Определяем текущий год
current_year = datetime.now().year

# Функция для форматирования даты
def format_date(date_str, current_year):
    global last_month  # Объявляем переменную как глобальную
    parts = date_str.split()
    day = parts[0].zfill(2)  # День с ведущим нулём
    # Если месяц отсутствует, используем текущий месяц
    if len(parts) >= 2 and parts[1][:3] in month_map:
        month = month_map[parts[1][:3]]  # Месяц из словаря
        # Проверяем, не перешли ли мы в новый год
        if "last_month" in globals() and last_month is not None and int(month) < int(last_month):
            current_year += 1  # Увеличиваем год, если месяц стал меньше предыдущего
    else:
        # Если месяц отсутствует, используем месяц из предыдущей даты
        month = last_month if "last_month" in globals() and last_month is not None else "??"  # Используем ??, если месяц неизвестен
    # Запоминаем последний использованный месяц
    last_month = month
    return f"{day}.{month}.{str(current_year)[-2:]}", current_year  # Год в формате ГГ

# Тест смены года
def test_year_transition():
    global last_month  # Используем только last_month как глобальную переменную
    last_month = datetime.now().strftime("%m")  # Устанавливаем текущий месяц
    test_current_year = 2025  # Локальная переменная для теста (переименована)
    last_month = None  # Сбрасываем последний месяц
    formatted_test_dates = []
    for date, _ in test_weather_data:
        formatted_date, test_current_year = format_date(date, test_current_year)  # Передаем год
        formatted_test_dates.append(formatted_date)
    # Выводим результаты теста
    print("\nТестовые даты с проверкой изменения года:")
    for i, (original_date, _) in enumerate(test_weather_data):
        print(f"Оригинальная дата: {original_date} -> Отформатированная дата: {formatted_test_dates[i]}")
    # Отладочная информация для проверки индексов
    print(f"Индекс последней даты декабря: {test_weather_data.index(('31 дек', '-11'))}")
    print(f"Индекс первой даты января: {test_weather_data.index(('1 янв', '0'))}")
    # Проверка, что год изменился после декабря
    december_last_date = formatted_test_dates[-len(test_weather_data) + test_weather_data.index(("31 дек", "-11"))]
    january_first_date = formatted_test_dates[-len(test_weather_data) + test_weather_data.index(("1 янв", "0"))]
    print(f"Последняя дата декабря: {december_last_date}")
    print(f"Первая дата января: {january_first_date}")
    if december_last_date.endswith(str(test_current_year - 1)[-2:]) and january_first_date.endswith(str(test_current_year)[-2:]):
        print("Год успешно изменился после декабря!")
    else:
        print("Ошибка: Год не изменился корректно!")

# Тест смены месяца
def test_month_transition():
    global last_month  # Используем глобальную переменную для последнего месяца
    test_current_year = 2025  # Локальная переменная для теста
    last_month = None  # Сбрасываем последний месяц
    formatted_test_dates = []
    previous_month = None  # Для отслеживания предыдущего месяца
    errors_found = False  # Флаг для отслеживания ошибок

    for date, _ in test_weather_data:
        formatted_date, test_current_year = format_date(date, test_current_year)  # Передаем год
        month = formatted_date[3:5]  # Извлекаем месяц из форматированной даты
        if previous_month is not None:
            # Проверяем, что месяц увеличивается корректно или остается таким же
            if (
                int(month) != int(previous_month) + 1
                and not (previous_month == "12" and month == "01")
                and int(month) != int(previous_month)
            ):
                print(f"Ошибка: Некорректная смена месяца! Предыдущий месяц: {previous_month}, Текущий месяц: {month}")
                errors_found = True  # Устанавливаем флаг ошибки
        previous_month = month  # Обновляем предыдущий месяц
        formatted_test_dates.append(formatted_date)

    # Выводим результаты теста
    print("\nТестовые даты с проверкой изменения месяца:")
    for i, (original_date, _) in enumerate(test_weather_data):
        print(f"Оригинальная дата: {original_date} -> Отформатированная дата: {formatted_test_dates[i]}")

    # Выводим итоговое сообщение
    if not errors_found:
        print("Смена месяцев прошла успешно. Ошибок не обнаружено.")
    else:
        print("Тест завершен с ошибками. Проверьте сообщения выше.")

# === ОСНОВНОЙ КОД ===
if __name__ == "__main__":
    # Инициализация браузера
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Отключаем флаг автоматизации
    driver = webdriver.Chrome(options=options)
    try:
        # Открываем страницу
        driver.get(url)
        print("Страница успешно открыта.")
        # Ждем загрузки страницы
        time.sleep(3)
        # Поиск поля для ввода местоположения
        try:
            location_search = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "input"))
            )
            location_search.click()
            print("Поле поиска местоположения найдено и кликнуто.")
            # Ввод названия города
            location_search.send_keys("Санкт-Петербург")
            print("Введено название города: Санкт-Петербург.")
            time.sleep(3)
            # Выбор города: Санкт-Петербург
            saint_petersburg = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.group-city:nth-child(1)'))
            )
            saint_petersburg.click()
            print("Выбран город: Санкт-Петербург.")
            time.sleep(6)
        except Exception as e:
            print(f"Ошибка при поиске или выборе города: {e}")
        # Погода на месяц вперед
        try:
            weather_month = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-stat-value="month"]'))
            )
            print("Кнопка 'Месяц' найдена.")
            weather_month.click()
            print("Открылась страница с информацией о погоде на месяц вперед.")
            time.sleep(3)
        except Exception as e:
            print(f"Ошибка: кнопка 'Месяц' не найдена или не кликабельна: {e}")
            driver.quit()
            exit()
        time.sleep(5)
        # Ждем загрузки контейнера с прогнозом
        widget_body = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "widget-body"))
        )
        print("Контейнер с прогнозом найден.")
        # Получаем HTML-код контейнера
        widget_html = widget_body.get_attribute("outerHTML")
        soup = BeautifulSoup(widget_html, 'html.parser')
        # Извлекаем данные
        weather_data = []
        forecast_items = soup.find_all("a", class_="row-item row-item-month-date")
        print(f"Найдено {len(forecast_items)} элементов с прогнозами.")
        for item in forecast_items:
            date_element = item.find("div", class_="date")
            if not date_element:
                print("Пропущен элемент: дата не найдена.")
                continue
            date = date_element.text.strip()
            maxt_element = item.find("div", class_="maxt")
            if not maxt_element:
                print("Пропущен элемент: максимальная температура не найдена.")
                continue
            temperature_value = maxt_element.find("temperature-value")
            if not temperature_value:
                print("Пропущен элемент: значение температуры не найдено.")
                continue
            temperature = temperature_value.text.strip()
            weather_data.append((date, temperature))
            print(f"Извлечены данные: Дата={date}, Температура={temperature}")
        # Проверка данных
        if not weather_data:
            print("Данные о погоде не найдены.")
        else:
            print("Данные о погоде успешно извлечены.")
        # Находим первый месяц, чтобы задать начальное значение для last_month
        for date, _ in weather_data:
            parts = date.split()
            if len(parts) >= 2 and parts[1][:3] in month_map:
                last_month = month_map[parts[1][:3]]
                break
        else:
            last_month = datetime.now().strftime("%m")
        # Преобразуем все даты в формат ДД.ММ.ГГ
        formatted_dates = []
        for date, _ in weather_data:
            if last_month is None:  # Проверяем, что last_month не равен None
                last_month = datetime.now().strftime("%m")  # Устанавливаем текущий месяц
            formatted_date, current_year = format_date(date, current_year)
            formatted_dates.append(formatted_date)
        # Создаем новый список с отформатированными данными
        formatted_weather_data = list(zip(formatted_dates, [temp for _, temp in weather_data]))
        # Извлекаем начальную и конечную даты
        full_start_date = formatted_dates[0]
        full_end_date = formatted_dates[-1]
        # Анализ самых теплых и холодных дней
        max_temp = max(weather_data, key=lambda x: int(x[1].replace("−", "-")))[1]
        min_temp = min(weather_data, key=lambda x: int(x[1].replace("−", "-")))[1]
        max_temp_dates = [formatted_date for formatted_date, temp in formatted_weather_data if temp == max_temp]
        min_temp_dates = [formatted_date for formatted_date, temp in formatted_weather_data if temp == min_temp]
        def format_date_list(dates):
            return dates[0] if len(dates) == 1 else ", ".join(dates)
        warmest_days_message = (
            f"Самый теплый день в ближайшем месяце, предположительно, "
            f"{format_date_list(max_temp_dates)} (температура {max_temp}°C). "
            f"Можно планировать встречу на этот день."
        ) if len(max_temp_dates) == 1 else (
            f"Самые теплые дни в ближайшем месяце, предположительно, "
            f"{format_date_list(max_temp_dates)} (температура {max_temp}°C). "
            f"Можно планировать встречу в один из этих дней."
        )
        coldest_days_message = (
            f"Самый холодный день в ближайшем месяце, предположительно, "
            f"{format_date_list(min_temp_dates)} (температура {min_temp}°C). "
            f"Лучше в этот день ничего не планировать."
        ) if len(min_temp_dates) == 1 else (
            f"Самые холодные дни в ближайшем месяце, предположительно, "
            f"{format_date_list(min_temp_dates)} (температура {min_temp}°C). "
            f"Лучше в эти дни ничего не планировать."
        )
        # Сохраняем данные в файл
        file_path = os.path.join(os.getcwd(), "inform.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            # Заголовок таблицы
            file.write(f"Температура за месяц с {full_start_date} по {full_end_date}\n")
            file.write("╔════════╦══════╗\n")  # Верхняя граница таблицы
            file.write("║ {:^8}  {:^7} ║\n".format("Дата", "Темпе-"))  # Заголовок: Дата
            file.write("║ {:^8}  {:^7} ║\n".format("", "ратура"))      # Заголовок: Температура
            file.write("╠════════╬══════╣\n")  # Разделитель заголовка

            # Тело таблицы
            for i, (date, temperature) in enumerate(weather_data):
                formatted_date = formatted_dates[i]
                file.write("║ {:^8}  {:>7} ║\n".format(formatted_date, temperature))  # Строка данных
                if i < len(weather_data) - 1:
                    file.write("╟───────────────╢\n")  # Разделитель между строками

            # Нижняя граница таблицы
            file.write("╚════════╩══════╝\n")
            file.write("\n")

            # Дополнительная информация о самых теплых и холодных днях
            file.write(warmest_days_message + "\n")
            file.write(coldest_days_message + "\n")

        print(f"Данные успешно сохранены в файл: {file_path}")
    finally:
        driver.quit()
        print("Браузер закрыт.")

    # === ТЕСТОВЫЙ БЛОК ===
    RUN_TEST = True  # Установите False, если не хотите запускать тесты
    if RUN_TEST:
        print("\n=== ЗАПУСК ТЕСТОВ ===")
        test_year_transition()
        test_month_transition()
