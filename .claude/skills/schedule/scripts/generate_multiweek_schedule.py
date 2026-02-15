#!/usr/bin/env python3
"""
Генератор детального расписания на несколько недель с прогрессией
Использует базовую структуру и добавляет вариацию тем для прогресса
"""
import sys
import yaml
from datetime import datetime, timedelta
from pathlib import Path

# Базовое расписание с временными смещениями
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
            {'time_offset': 300, 'duration': 60, 'specialist': 'psychotherapist', 'topic': 'Глубинная проработка'},
            {'time_offset': 600, 'duration': 20, 'specialist': 'meditation-guide', 'topic': 'Дыхательные практики'},
        ]
    },
    'wednesday': {
        'theme': 'Карьера и рост',
        'slots': [
            {'time_offset': 0, 'duration': 30, 'specialist': 'meditation-guide', 'topic': 'Медитация на фокусировку'},
            {'time_offset': 120, 'duration': 60, 'specialist': 'career-consultant', 'topic': 'Карьерная стратегия'},
            {'time_offset': 240, 'duration': 60, 'specialist': 'business-trainer', 'topic': 'Навыки лидерства'},
            {'time_offset': 360, 'duration': 45, 'specialist': 'life-coach', 'topic': 'Баланс и ценности'},
            {'time_offset': 660, 'duration': 30, 'specialist': 'yoga-instructor', 'topic': 'Йога для спины'},
        ]
    },
    'thursday': {
        'theme': 'Глубокая работа',
        'slots': [
            {'time_offset': 0, 'duration': 60, 'specialist': 'personal-growth-trainer', 'topic': 'Работа с убеждениями'},
            {'time_offset': 90, 'duration': 45, 'specialist': 'nlp-practitioner', 'topic': 'Техники NLP'},
            {'time_offset': 240, 'duration': 60, 'specialist': 'mentor', 'topic': 'Менторская сессия'},
            {'time_offset': 390, 'duration': 60, 'specialist': 'fitness-trainer', 'topic': 'Кардио тренировка'},
            {'time_offset': 600, 'duration': 30, 'specialist': 'hypnologist', 'topic': 'Гипно-релаксация'},
        ]
    },
    'friday': {
        'theme': 'Интеграция и отношения',
        'slots': [
            {'time_offset': 0, 'duration': 30, 'specialist': 'meditation-guide', 'topic': 'Медитация благодарности'},
            {'time_offset': 120, 'duration': 60, 'specialist': 'psychosomatologist', 'topic': 'Связь тело-разум'},
            {'time_offset': 240, 'duration': 45, 'specialist': 'sexologist', 'topic': 'Отношения и близость'},
            {'time_offset': 330, 'duration': 45, 'specialist': 'lifestyle-consultant', 'topic': 'Привычки и среда'},
            {'time_offset': 480, 'duration': 30, 'specialist': 'yoga-instructor', 'topic': 'Инь-йога'},
        ]
    },
    'saturday': {
        'theme': 'Исследование и вдохновение',
        'slots': [
            {'time_offset': 60, 'duration': 45, 'specialist': 'spiritual-guide', 'topic': 'Духовные практики'},
            {'time_offset': 150, 'duration': 60, 'specialist': 'dietitian', 'topic': 'Meal-prep план'},
            {'time_offset': 270, 'duration': 45, 'specialist': 'astro-psychologist', 'topic': 'Астро-анализ'},
            {'time_offset': 360, 'duration': 45, 'specialist': 'career-orientation', 'topic': 'Профориентация'},
            {'time_offset': 480, 'duration': 60, 'specialist': 'fitness-trainer', 'topic': 'Активный отдых'},
        ]
    },
    'sunday': {
        'theme': 'Обзор и восстановление',
        'slots': [
            {'time_offset': 60, 'duration': 45, 'specialist': 'meditation-guide', 'topic': 'Длинная медитация'},
            {'time_offset': 150, 'duration': 30, 'specialist': 'tarot-consultant', 'topic': 'Расклад на неделю'},
            {'time_offset': 270, 'duration': 60, 'specialist': 'weekly-review', 'topic': 'Еженедельный обзор'},
            {'time_offset': 480, 'duration': 30, 'specialist': 'yoga-instructor', 'topic': 'Йога-нидра'},
        ]
    }
}

# Прогрессия тем по неделям для каждого специалиста
TOPIC_PROGRESSION = {
    'psychologist': [
        'Знакомство и диагностика состояния',
        'Работа с эмоциями и стрессом',
        'Когнитивные паттерны и убеждения',
        'Самооценка и уверенность',
        'Отношения с окружающими',
        'Интеграция и закрепление',
        'Работа с будущим',
        'Подведение итогов и план на будущее'
    ],
    'meditation-guide': [
        'Основы осознанности',
        'Работа с дыханием',
        'Сканирование тела',
        'Метта-медитация (любящая доброта)',
        'Визуализация',
        'Работа с мыслями',
        'Глубокая медитация',
        'Интегративная практика'
    ],
    'fitness-trainer': [
        'Оценка физической формы',
        'Базовые силовые упражнения',
        'Кардио и выносливость',
        'Функциональный тренинг',
        'Работа над слабыми зонами',
        'Интенсивная тренировка',
        'Активное восстановление',
        'Персональный тренировочный план'
    ],
    'executive-coach': [
        'Аудит текущей ситуации',
        'Определение целей и приоритетов',
        'Стратегия достижения',
        'Навыки делегирования',
        'Управление временем',
        'Лидерские качества',
        'Командная работа',
        'Долгосрочное видение'
    ],
    'life-coach': [
        'Колесо жизненного баланса',
        'Ценности и приоритеты',
        'Постановка целей SMART',
        'Преодоление препятствий',
        'Формирование привычек',
        'Работа с прокрастинацией',
        'Поиск смысла',
        'План личностного роста'
    ]
}

def get_progressive_topic(specialist: str, base_topic: str, week_num: int) -> str:
    """Получает прогрессирующую тему для специалиста"""
    if specialist in TOPIC_PROGRESSION:
        topics = TOPIC_PROGRESSION[specialist]
        topic_index = (week_num - 1) % len(topics)
        return topics[topic_index]
    return base_topic

def parse_date_time(date_str: str, time_str: str = "08:00") -> datetime:
    """Парсит дату и время"""
    # Пробуем разные форматы
    formats = [
        "%d.%m.%Y %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d %H:%M",
        "%d %B %Y %H:%M",
        "%d %b %Y %H:%M",
    ]
    
    full_str = f"{date_str} {time_str}"
    
    for fmt in formats:
        try:
            return datetime.strptime(full_str, fmt)
        except ValueError:
            continue
    
    # Если не удалось распарсить, возвращаем текущую дату
    print(f"⚠️  Не удалось распарсить дату '{date_str}', используем текущую")
    return datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

def generate_multiweek_schedule(start_date: datetime, num_weeks: int, timezone: str = "Europe/Kiev") -> dict:
    """Генерирует расписание на несколько недель"""
    
    schedule = {
        'meta': {
            'owner': 'user',
            'timezone': timezone,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'num_weeks': num_weeks,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'weeks': []
    }
    
    days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for week_num in range(1, num_weeks + 1):
        week_data = {
            'week_number': week_num,
            'start_date': (start_date + timedelta(weeks=week_num-1)).strftime('%Y-%m-%d'),
            'days': {}
        }
        
        for day_index, day_name in enumerate(days_order):
            current_date = start_date + timedelta(weeks=week_num-1, days=day_index)
            day_template = BASE_SCHEDULE[day_name]
            
            day_data = {
                'date': current_date.strftime('%Y-%m-%d'),
                'theme': day_template['theme'],
                'slots': []
            }
            
            for slot_template in day_template['slots']:
                slot_time = start_date + timedelta(minutes=slot_template['time_offset'])
                
                # Получаем прогрессирующую тему
                specialist = slot_template['specialist']
                base_topic = slot_template['topic']
                progressive_topic = get_progressive_topic(specialist, base_topic, week_num)
                
                slot = {
                    'time': slot_time.strftime('%H:%M'),
                    'duration': slot_template['duration'],
                    'specialist': specialist,
                    'topic': progressive_topic,
                    'week_context': f"Неделя {week_num}",
                    'status': 'planned',
                    'notes': ''
                }
                
                day_data['slots'].append(slot)
            
            week_data['days'][day_name] = day_data
        
        schedule['weeks'].append(week_data)
    
    return schedule

def main():
    if len(sys.argv) < 3:
        print("Использование: python generate_multiweek_schedule.py <дата> <время> <количество_недель> [часовой_пояс]")
        print("Пример: python generate_multiweek_schedule.py '16.02.2026' '08:00' 8 'Europe/Kiev'")
        sys.exit(1)
    
    date_str = sys.argv[1]
    time_str = sys.argv[2]
    num_weeks = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    timezone = sys.argv[4] if len(sys.argv) > 4 else "Europe/Kiev"
    
    start_datetime = parse_date_time(date_str, time_str)
    
    print(f"📅 Генерация расписания на {num_weeks} недель")
    print(f"🕐 Начало: {start_datetime.strftime('%d.%m.%Y в %H:%M')}")
    print(f"🌍 Часовой пояс: {timezone}")
    
    schedule = generate_multiweek_schedule(start_datetime, num_weeks, timezone)
    
    # Сохраняем в файл
    schedule_path = Path('schedule/multiweek-schedule.yaml')
    schedule_path.parent.mkdir(exist_ok=True)
    
    with open(schedule_path, 'w', encoding='utf-8') as f:
        yaml.dump(schedule, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    end_date = start_datetime + timedelta(weeks=num_weeks)
    
    print(f"\n✅ Расписание сгенерировано: {schedule_path}")
    print(f"📆 Период: {start_datetime.strftime('%d.%m.%Y')} — {end_date.strftime('%d.%m.%Y')}")
    print(f"📊 Недель: {num_weeks}")
    
    # Подсчитываем общее количество сессий
    total_sessions = sum(len(week['days'][day]['slots']) 
                         for week in schedule['weeks'] 
                         for day in week['days'])
    print(f"🎯 Всего сессий: {total_sessions}")
    
    return schedule_path

if __name__ == "__main__":
    main()
