import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import os

# URL страницы
url = "https://www.gismeteo.ru/diary/4079/2023/4/"

# Словарь для преобразования названий месяцев в числа
month_map = {
    "янв": "01", "фев": "02", "мар": "03", "апр": "04",
    "май": "05", "июн": "06", "июл": "07", "авг": "08",
    "сен": "09", "окт": "10", "ноя": "11", "дек": "12"
}

# Определяем текущий год
current_year = datetime.now().year

# Функция для форматирования даты
def format_date(date_str):
    global last_month, current_year  # Объявляем переменную как глобальную
    parts = date_str.split()
    day = parts[0].zfill(2)  # День с ведущим нулём
            
    # Если месяц отсутствует, используем текущий месяц
    if len(parts) >= 2 and parts[1][:3] in month_map:
        month = month_map[parts[1][:3]]  # Месяц из словаря

        # Проверяем, не перешли ли мы в новый год
        if "last_month" in globals() and int(month) < int(last_month):
            current_year += 1 # Увеличиваем год, если месяц стал меньше предыдущего

    else:
        # Если месяц отсутствует, используем месяц из предыдущей даты
        month = last_month if "last_month" in globals() else "??"  # Используем ??, если месяц неизвестен

    # Запоминаем последний использованный месяц
    last_month = month
    return f"{day}.{month}.{str(current_year)[-2:]}"  # Год в формате ГГ

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
        # Поиск элемента, выбор города:
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
        # Явное ожидание появления кнопки "Месяц"
        weather_month = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-stat-value="month"]'))
        )
        print("Кнопка 'Месяц' найдена.")
        
        # Клик по кнопке
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
        # Ищем дату
        date_element = item.find("div", class_="date")
        if not date_element:
            print("Пропущен элемент: дата не найдена.")
            continue  # Пропускаем элемент, если дата не найдена
        date = date_element.text.strip()

        # Ищем максимальную температуру
        maxt_element = item.find("div", class_="maxt")
        if not maxt_element:
            print("Пропущен элемент: максимальная температура не найдена.")
            continue  # Пропускаем элемент, если температура не найдена
        temperature_value = maxt_element.find("temperature-value")
        if not temperature_value:
            print("Пропущен элемент: значение температуры не найдено.")
            continue
        temperature = temperature_value.text.strip()
        
        # Добавляем данные в список
        weather_data.append((date, temperature))
        print(f"Извлечены данные: Дата={date}, Температура={temperature}")

    # Проверка данных
    if not weather_data:
        print("Данные о погоде не найдены.")
    else:
        print("Данные о погоде успешно извлечены.")


    # Находим первый месяц, чтобы задать начальное значение для last_month
    for date, _ in weather_data:
        parts= date.split()
        if len(parts) >= 2 and parts[1][:3] in month_map:
            last_month = month_map[parts[1][:3]]  # Берём месяц из первой даты
            break
    else:
        # Если ни одна дата не содержит месяца, используем текущий месяц
        last_month = datetime.now().strftime("%m")

    # Преобразуем все даты в формат ДД.ММ.ГГ
    formatted_dates = []
    for date, _ in weather_data:
        formatted_date = format_date(date)
        formatted_dates.append(formatted_date)

    # Извлекаем начальную и конечную даты
    full_start_date = formatted_dates[0]  # Первая дата
    full_end_date = formatted_dates[-1]   # Последняя дата

    # Анализ самых теплых и холодных дней
    max_temp=max(weather_data, key=lambda x: int(x[1].replace("−", "-")))[1]
    min_temp=min(weather_data, key=lambda x: int(x[1].replace("−", "-")))[1]

    # Преобразуем даты для самых теплых и холодных дней в формат ЧЧ.ММ.ГГ
    max_temp_dates=[format_date(date) for date, temp in weather_data if temp == max_temp]
    min_temp_dates=[format_date(date) for date, temp in weather_data if temp == min_temp]

    def format_date_list(dates):
        if len(dates) == 1:
            return dates[0]
        else:
            return ", ".join(dates)

    # Формируем сообщение о самых теплых днях
    if len(max_temp_dates) == 1:
        warmest_days_message = (
            f"Самый теплый день в ближайшем месяце предположительно "
            f"{format_date_list(max_temp_dates)} (температура {max_temp}°C). "
            f"Можно планировать встречу на этот день."
        )
    else:
        warmest_days_message = (
            f"Самые теплые дни в ближайшем месяце предположительно "
            f"{format_date_list(max_temp_dates)} (температура {max_temp}°C). "
            f"Можно планировать встречу в один из этих дней."
        )

    # Формируем сообщение о самых холодных днях
    if len(min_temp_dates) == 1:
        coldest_days_message = (
            f"Самый холодный день в ближайшем месяце предположительно "
            f"{format_date_list(min_temp_dates)} (температура {min_temp}°C). "
            f"Лучше в этот день ничего не планировать."
        )
    else:
        coldest_days_message = (
            f"Самые холодные дни в ближайшем месяце предположительно "
            f"{format_date_list(min_temp_dates)} (температура {min_temp}°C). "
            f"Лучше в эти дни ничего не планировать."
        )

    # Сохраняем данные в файл
    file_path = os.path.join(os.getcwd(), "inform.txt")
    with open(file_path, "w", encoding="utf-8") as file:
        # Заголовок перед таблицей
        file.write(f"Температура за месяц с {full_start_date} по {full_end_date}\n\n")

        # Верхняя граница таблицы (двойная линия)
        file.write("╔════════╦═══════╗\n")
            
        # Заголовок таблицы (с переносом текста)
        file.write("║ {:^8} ║ {:^7} ║\n".format("Дата", "Темпе-"))
        file.write("║ {:^8} ║ {:^7} ║\n".format("", "ратура"))
            
        # Разделитель заголовка и данных
        file.write("╠════════╬═══════╣\n")

        # Записываем данные
        for i, (date, temperature) in enumerate(weather_data):
            # Преобразуем дату в формат ДД.ММ.ГГ
            formatted_date = formatted_dates[i]
                
            # Выравниваем дату по центру, а температуру по правому краю
            file.write("║ {:^8} ║ {:>7} ║\n".format(formatted_date, temperature))
                
            # Добавляем разделитель между строками (кроме последней строки)
            if i < len(weather_data) - 1:
                file.write("╟────────┼───────╢\n")

        # Нижняя граница таблицы (двойная линия)
        file.write("╚════════╩═══════╝\n")

        # Добавляем сообщение о самых теплых и холодных днях
        file.write("\n\n")
        file.write(warmest_days_message + "\n")
        file.write(coldest_days_message + "\n")

    print(f"Данные успешно сохранены в файл: {file_path}")

finally:
    driver.quit()
    print("Браузер закрыт.")    