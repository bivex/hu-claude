#!/usr/bin/env python3
"""Генератор ICS-файлов из расписания weekly-schedule.yaml"""
import sys
import yaml
from datetime import datetime, timedelta
from pathlib import Path

DAYS_MAP = {
    'monday': 0, 'tuesday': 1, 'wednesday': 2,
    'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
}

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

def generate_ics(yaml_path: str, output_path: str = 'schedule.ics', weeks: int = 4):
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    meta = data.get('meta', {})
    start_date = datetime.strptime(meta.get('start_date', '2026-02-16'), '%Y-%m-%d')
    tz = meta.get('timezone', 'UTC')

    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//SelfImprovement//Schedule//RU',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        f'X-WR-TIMEZONE:{tz}',
    ]

    uid_counter = 0
    for week in range(weeks):
        week_start = start_date + timedelta(weeks=week)
        for day_name, day_offset in DAYS_MAP.items():
            day_data = data.get(day_name, {})
            slots = day_data.get('slots', [])
            day_date = week_start + timedelta(days=day_offset)

            for slot in slots:
                if slot.get('status') == 'skipped':
                    continue
                h, m = map(int, slot['time'].split(':'))
                dt_start = day_date.replace(hour=h, minute=m)
                dt_end = dt_start + timedelta(minutes=slot.get('duration', 60))
                specialist = SPECIALIST_NAMES.get(slot['specialist'], slot['specialist'])
                uid_counter += 1

                lines.extend([
                    'BEGIN:VEVENT',
                    f'UID:selfimprove-{uid_counter}-{week}@schedule',
                    f'DTSTART:{dt_start.strftime("%Y%m%dT%H%M%S")}',
                    f'DTEND:{dt_end.strftime("%Y%m%dT%H%M%S")}',
                    f'SUMMARY:{specialist}: {slot["topic"]}',
                    f'DESCRIPTION:Специалист: {specialist}\\nТема: {slot["topic"]}\\nДлительность: {slot["duration"]} мин',
                    f'CATEGORIES:{specialist}',
                    'STATUS:CONFIRMED',
                    'END:VEVENT',
                ])

    lines.append('END:VCALENDAR')

    with open(output_path, 'w') as f:
        f.write('\r\n'.join(lines))

    print(f'✅ Создан файл {output_path} ({uid_counter * weeks} событий на {weeks} недель)')
    print(f'   Импортируйте в Google Calendar / Apple Calendar / Outlook')

if __name__ == '__main__':
    yaml_path = sys.argv[1] if len(sys.argv) > 1 else 'schedule/weekly-schedule.yaml'
    output = sys.argv[2] if len(sys.argv) > 2 else 'schedule/schedule.ics'
    weeks = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    generate_ics(yaml_path, output, weeks)
