#!/usr/bin/env python3
"""
Экспорт расписания самосовершенствования в формат ICS для импорта в календарь
"""

import yaml
import os
from datetime import datetime, timedelta
from icalendar import Calendar, Event, vText
import pytz

def load_schedule():
    """Загружает расписание из YAML файла"""
    schedule_path = 'schedule/weekly-schedule.yaml'
    if not os.path.exists(schedule_path):
        print(f"❌ Файл {schedule_path} не найден")
        return None

    with open(schedule_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def create_ics_event(cal, slot, date, specialist_name):
    """Создает событие в календаре"""
    # Парсим время
    time_obj = datetime.strptime(slot['time'], '%H:%M').time()

    # Создаем datetime объект
    start_datetime = datetime.combine(date, time_obj)

    # Добавляем часовой пояс (из мета данных)
    timezone = pytz.timezone('Asia/Tokyo')  # Можно сделать configurable
    start_datetime = timezone.localize(start_datetime)

    # Вычисляем время окончания
    end_datetime = start_datetime + timedelta(minutes=slot['duration'])

    # Создаем событие
    event = Event()
    event.add('summary', f"{specialist_name}: {slot['topic']}")
    event.add('dtstart', start_datetime)
    event.add('dtend', end_datetime)
    event.add('description', f"Специалист: {specialist_name}\nТема: {slot['topic']}\nСтатус: {slot['status']}")
    if slot.get('notes'):
        event.add('description', event['description'] + f"\nЗаметки: {slot['notes']}")

    # Добавляем в календарь
    cal.add_component(event)

def export_to_ics(schedule):
    """Экспортирует расписание в ICS формат"""
    # Создаем календарь
    cal = Calendar()
    cal.add('prodid', '-//AI Self-Improvement System//hu-claude//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', vText('Программа самосовершенствования'))

    # Получаем стартовую дату
    start_date = datetime.strptime(schedule['meta']['start_date'], '%Y-%m-%d').date()

    # Словарь дней недели
    days_map = {
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6
    }

    # Словарь имен специалистов (можно расширить)
    specialist_names = {
        'meditation-guide': 'Гид медитации',
        'psychologist': 'Психолог',
        'executive-coach': 'Коуч по лидерству',
        'yoga-instructor': 'Инструктор йоги',
        'fitness-trainer': 'Тренер по фитнесу',
        'nutritionist': 'Нутрициолог',
        'psychotherapist': 'Психотерапевт',
        'life-coach': 'Лайф-коуч',
        'career-advisor': 'Карьерный консультант',
        'financial-advisor': 'Финансовый советник',
        'relationship-coach': 'Коуч по отношениям',
        'creativity-coach': 'Коуч по креативности',
        'mindfulness-teacher': 'Учитель осознанности',
        'energy-healer': 'Целитель энергии',
        'spiritual-guide': 'Духовный гид',
        'philosophy-teacher': 'Философ',
        'science-teacher': 'Учитель науки',
        'art-teacher': 'Учитель искусства',
        'music-teacher': 'Учитель музыки',
        'language-teacher': 'Учитель языка',
        'history-teacher': 'Учитель истории',
        'future-planner': 'Планировщик будущего'
    }

    # Обрабатываем каждый день недели
    for day_name, day_data in schedule.items():
        if day_name == 'meta':
            continue

        day_offset = days_map[day_name]
        current_date = start_date + timedelta(days=day_offset)

        for slot in day_data['slots']:
            specialist = slot['specialist']
            specialist_name = specialist_names.get(specialist, specialist)
            create_ics_event(cal, slot, current_date, specialist_name)

    # Сохраняем в файл
    ics_path = 'schedule/weekly-schedule.ics'
    with open(ics_path, 'wb') as f:
        f.write(cal.to_ical())

    print(f"✅ Календарь экспортирован: {ics_path}")
    print(f"📅 Событий создано: {len(cal.subcomponents)}")

    return ics_path

def main():
    print("📤 Экспорт расписания в ICS формат...")

    # Загружаем расписание
    schedule = load_schedule()
    if not schedule:
        return

    # Экспортируем в ICS
    ics_path = export_to_ics(schedule)

    print("\n📋 Инструкции по импорту:")
    print(f"1. Откройте файл {ics_path}")
    print("2. Импортируйте в ваше приложение календаря (Google Calendar, Apple Calendar, Outlook)")
    print("3. Или используйте онлайн-сервисы для конвертации ICS")

if __name__ == "__main__":
    main()