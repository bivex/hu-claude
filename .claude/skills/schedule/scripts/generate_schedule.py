#!/usr/bin/env python3
"""Генератор расписания с указанной даты и времени"""
import sys
import yaml
from datetime import datetime, timedelta
from pathlib import Path

# Базовое расписание занятий (время относительно начала дня)
BASE_SCHEDULE = {
    'monday': {
        'theme': 'Разум и стратегия',
        'slots': [
            {'time_offset': 0, 'duration': 30, 'specialist': 'meditation-guide', 'topic': 'Утренняя медитация осознанности'},
            {'time_offset': 120, 'duration': 60, 'specialist': 'psychologist', 'topic': 'Еженедельная сессия: текущее состояние'},
            {'time_offset': 360, 'duration': 45, 'specialist': 'executive-coach', 'topic': 'Стратегическое планирование недели'},
            {'time_offset': 660, 'duration': 30, 'specialist': 'yoga-instructor', 'topic': 'Вечерняя расслабляющая йога'},
        ]
    },
    'tuesday': {
        'theme': 'Тело и энергия',
        'slots': [
            {'time_offset': -30, 'duration': 60, 'specialist': 'fitness-trainer', 'topic': 'Силовая тренировка'},
            {'time_offset': 120, 'duration': 45, 'specialist': 'nutritionist', 'topic': 'Обзор питания, корректировка рациона'},
            {'time_offset': 300, 'duration': 60, 'specialist': 'psychotherapist', 'topic': 'Глубинная проработка (КПТ/гештальт)'},
            {'time_offset': 600, 'duration': 20, 'specialist': 'meditation-guide', 'topic': 'Дыхательные практики перед сном'},
        ]
    },
    'wednesday': {
        'theme': 'Карьера и рост',
        'slots': [
            {'time_offset': 0, 'duration': 30, 'specialist': 'meditation-guide', 'topic': 'Медитация на фокусировку'},
            {'time_offset': 120, 'duration': 60, 'specialist': 'career-consultant', 'topic': 'Карьерная стратегия и развитие'},
            {'time_offset': 240, 'duration': 60, 'specialist': 'business-trainer', 'topic': 'Навыки лидерства / переговоры'},
            {'time_offset': 360, 'duration': 45, 'specialist': 'life-coach', 'topic': 'Баланс работа-жизнь, ценности'},
            {'time_offset': 660, 'duration': 30, 'specialist': 'yoga-instructor', 'topic': 'Йога для спины и шеи (офисная)'},
        ]
    },
    'thursday': {
        'theme': 'Глубокая работа',
        'slots': [
            {'time_offset': 0, 'duration': 60, 'specialist': 'personal-growth-trainer', 'topic': 'Работа с ограничивающими убеждениями'},
            {'time_offset': 90, 'duration': 45, 'specialist': 'nlp-practitioner', 'topic': 'Техники NLP: якорение / рефрейминг'},
            {'time_offset': 240, 'duration': 60, 'specialist': 'mentor', 'topic': 'Менторская сессия: долгосрочное видение'},
            {'time_offset': 390, 'duration': 60, 'specialist': 'fitness-trainer', 'topic': 'Кардио / функциональная тренировка'},
            {'time_offset': 600, 'duration': 30, 'specialist': 'hypnologist', 'topic': 'Гипно-релаксация для восстановления'},
        ]
    },
    'friday': {
        'theme': 'Интеграция и отношения',
        'slots': [
            {'time_offset': 0, 'duration': 30, 'specialist': 'meditation-guide', 'topic': 'Медитация благодарности'},
            {'time_offset': 120, 'duration': 60, 'specialist': 'psychosomatologist', 'topic': 'Связь тело-разум, зажимы'},
            {'time_offset': 240, 'duration': 45, 'specialist': 'sexologist', 'topic': 'Отношения и близость'},
            {'time_offset': 330, 'duration': 45, 'specialist': 'lifestyle-consultant', 'topic': 'Привычки, среда, распорядок дня'},
            {'time_offset': 480, 'duration': 30, 'specialist': 'yoga-instructor', 'topic': 'Восстановительная йога (инь)'},
        ]
    },
    'saturday': {
        'theme': 'Исследование и вдохновение',
        'slots': [
            {'time_offset': 60, 'duration': 45, 'specialist': 'spiritual-guide', 'topic': 'Духовные практики и рефлексия'},
            {'time_offset': 150, 'duration': 60, 'specialist': 'dietitian', 'topic': 'Meal-prep план на неделю'},
            {'time_offset': 270, 'duration': 45, 'specialist': 'astro-psychologist', 'topic': 'Астро-анализ текущего периода'},
            {'time_offset': 360, 'duration': 45, 'specialist': 'career-orientation', 'topic': 'Профориентация: сильные стороны'},
            {'time_offset': 480, 'duration': 60, 'specialist': 'fitness-trainer', 'topic': 'Активный отдых / растяжка'},
        ]
    },
    'sunday': {
        'theme': 'Обзор и восстановление',
        'slots': [
            {'time_offset': 60, 'duration': 45, 'specialist': 'meditation-guide', 'topic': 'Длинная медитация (визуализация будущего)'},
            {'time_offset': 150, 'duration': 30, 'specialist': 'tarot-consultant', 'topic': 'Расклад на неделю — рефлексия'},
            {'time_offset': 270, 'duration': 60, 'specialist': 'weekly-review', 'topic': 'Еженедельный обзор: что сделано, что дальше'},
            {'time_offset': 480, 'duration': 30, 'specialist': 'yoga-instructor', 'topic': 'Йога-нидра для глубокого отдыха'},
        ]
    }
}

def parse_date_time(date_str: str, time_str: str = "08:00") -> datetime:
    """Парсит дату и время из строки"""
    # Простой парсер для основных форматов
    try:
        # Попробуем разные форматы
        formats = [
            "%d.%m.%Y", "%d %m %Y", "%Y-%m-%d",
            "%d %B %Y", "%d.%m.%y", "%Y.%m.%d"
        ]

        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        else:
            # Если не распарсили, используем ближайший понедельник
            today = datetime.now()
            days_ahead = (7 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            date_obj = today + timedelta(days=days_ahead)

        # Парсим время
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        return datetime.combine(date_obj.date(), time_obj)

    except Exception as e:
        print(f"Ошибка парсинга даты/времени: {e}")
        # Fallback: ближайший понедельник 8:00
        today = datetime.now()
        days_ahead = (7 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        monday = today + timedelta(days=days_ahead)
        return datetime.combine(monday.date(), datetime.strptime("08:00", "%H:%M").time())

def generate_schedule(start_datetime: datetime, output_path: str = 'schedule/weekly-schedule.yaml'):
    """Генерирует полное расписание начиная с указанной даты/времени"""

    # Создаём структуру расписания
    schedule = {
        'meta': {
            'owner': 'user',
            'timezone': 'Asia/Tokyo',  # Можно сделать параметром
            'start_date': start_datetime.strftime('%Y-%m-%d'),
            'week_number': 1
        }
    }

    # Генерируем слоты для каждого дня
    for day_name, day_data in BASE_SCHEDULE.items():
        day_schedule = {
            'theme': day_data['theme'],
            'slots': []
        }

        for slot in day_data['slots']:
            # Вычисляем абсолютное время
            slot_time = start_datetime + timedelta(minutes=slot['time_offset'])

            day_schedule['slots'].append({
                'time': slot_time.strftime('%H:%M'),
                'duration': slot['duration'],
                'specialist': slot['specialist'],
                'topic': slot['topic'],
                'status': 'planned',
                'notes': ''
            })

        schedule[day_name] = day_schedule

    # Сохраняем в YAML
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(schedule, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"✅ Расписание сгенерировано: {output_path}")
    print(f"📅 Начало: {start_datetime.strftime('%d.%m.%Y в %H:%M')}")
    print(f"🕐 Первое занятие: {schedule['monday']['slots'][0]['time']} — {schedule['monday']['slots'][0]['topic']}")

    return schedule

if __name__ == '__main__':
    # Пример использования: python generate_schedule.py "16.02.2026" "08:00"
    date_str = sys.argv[1] if len(sys.argv) > 1 else None
    time_str = sys.argv[2] if len(sys.argv) > 2 else "08:00"

    if date_str:
        start_dt = parse_date_time(date_str, time_str)
    else:
        # По умолчанию: ближайший понедельник 8:00
        start_dt = parse_date_time("", "08:00")

    generate_schedule(start_dt)
