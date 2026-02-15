#!/usr/bin/env python3
"""Генератор ICS-файлов из multiweek-schedule.yaml"""
import yaml
from pathlib import Path

SPECIALIST_NAMES = {
    'psychologist': 'Психолог',
    'psychotherapist': 'Психотерапевт',
    'life-coach': 'Лайф-коуч',
    'executive-coach': 'Экзекьютив-коуч',
    'mentor': 'Ментор',
    'personal-growth-trainer': 'Тренер личностного роста',
    'business-trainer': 'Бизнес-тренер',
    'nlp-practitioner': 'НЛП-практик',
    'hypnologist': 'Гипнолог',
    'psychosomatologist': 'Психосоматолог',
    'dietitian': 'Диетолог',
    'nutritionist': 'Нутрициолог',
    'fitness-trainer': 'Фитнес-тренер',
    'yoga-instructor': 'Инструктор йоги',
    'meditation-guide': 'Гид по медитации',
    'sexologist': 'Сексолог',
    'career-consultant': 'Карьерный консультант',
    'lifestyle-consultant': 'Лайфстайл-консультант',
    'career-orientation': 'Профориентация',
    'spiritual-guide': 'Духовный наставник',
    'astro-psychologist': 'Астролог-психолог',
    'tarot-consultant': 'Таролог',
    'weekly-review': 'Еженедельный обзор',
}

def parse_datetime(date_str: str, time_str: str):
    """Парсит дату и время"""
    from datetime import datetime
    return datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')

def generate_ics_from_multiweek(yaml_path: str, output_path: str = 'schedule/multiweek-schedule.ics'):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    meta = data.get('meta', {})
    tz = meta.get('timezone', 'Europe/Kiev')
    weeks = data.get('weeks', [])

    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//SelfImprovement//MultiweekSchedule//RU',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        f'X-WR-TIMEZONE:{tz}',
        f'X-WR-CALNAME:Программа самосовершенствования',
        f'X-WR-CALDESC:8-недельная программа с командой специалистов',
    ]

    uid_counter = 0
    total_events = 0

    for week in weeks:
        week_num = week.get('week_number', 1)
        days = week.get('days', {})

        for day_name, day_data in days.items():
            date_str = day_data.get('date', '')
            theme = day_data.get('theme', '')
            slots = day_data.get('slots', [])

            for slot in slots:
                if slot.get('status') == 'skipped':
                    continue

                time_str = slot.get('time', '08:00')
                duration = slot.get('duration', 60)
                specialist_id = slot.get('specialist', '')
                topic = slot.get('topic', '')
                week_context = slot.get('week_context', '')

                dt_start = parse_datetime(date_str, time_str)
                from datetime import timedelta
                dt_end = dt_start + timedelta(minutes=duration)

                specialist = SPECIALIST_NAMES.get(specialist_id, specialist_id)
                uid_counter += 1
                total_events += 1

                # Формируем описание события
                description = f"Специалист: {specialist}\\n"
                description += f"Тема: {topic}\\n"
                description += f"Неделя: {week_context}\\n"
                description += f"Длительность: {duration} мин\\n"
                description += f"Тема дня: {theme}"

                lines.extend([
                    'BEGIN:VEVENT',
                    f'UID:selfimprove-{uid_counter}@multiweek-schedule',
                    f'DTSTART:{dt_start.strftime("%Y%m%dT%H%M%S")}',
                    f'DTEND:{dt_end.strftime("%Y%m%dT%H%M%S")}',
                    f'SUMMARY:{specialist}: {topic}',
                    f'DESCRIPTION:{description}',
                    f'CATEGORIES:{specialist}',
                    f'X-WEEK-NUMBER:{week_num}',
                    'STATUS:CONFIRMED',
                    'END:VEVENT',
                ])

    lines.append('END:VCALENDAR')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\r\n'.join(lines))

    print(f'✅ Создан файл: {output_path}')
    print(f'📊 Всего событий: {total_events}')
    print(f'📅 Период: {weeks[0].get("start_date")} — {weeks[-1].get("days", {}).get("sunday", {}).get("date", "")}')
    print(f'🌍 Часовой пояс: {tz}')
    print(f'\\n📲 Импортируйте файл в:')
    print(f'   • Google Calendar (Настройки → Импорт)')
    print(f'   • Apple Calendar (Файл → Импорт)')
    print(f'   • Outlook (Файл → Открыть и экспортировать)')

if __name__ == '__main__':
    yaml_path = 'schedule/multiweek-schedule.yaml'
    output = 'schedule/multiweek-schedule.ics'
    generate_ics_from_multiweek(yaml_path, output)
