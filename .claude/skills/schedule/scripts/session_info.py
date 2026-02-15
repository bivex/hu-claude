#!/usr/bin/env python3
"""
Скрипт для запуска сессии со специалистом
Показывает информацию о сессии из расписания и подготавливает контекст
"""
import sys
import yaml
from datetime import datetime
from pathlib import Path

def load_schedule():
    """Загружает расписание"""
    schedule_path = Path('schedule/multiweek-schedule.yaml')
    if not schedule_path.exists():
        print("❌ Расписание не найдено. Сначала сгенерируйте его.")
        return None
    
    with open(schedule_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def find_session(schedule, specialist_id, date_str=None):
    """Находит ближайшую сессию со специалистом"""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    sessions = []
    
    for week in schedule['weeks']:
        for day_name, day_data in week['days'].items():
            if day_data['date'] == date_str:
                for slot in day_data['slots']:
                    if slot['specialist'] == specialist_id:
                        sessions.append({
                            'date': day_data['date'],
                            'day': day_name,
                            'week': week['week_number'],
                            **slot
                        })
    
    return sessions

def find_todays_sessions(schedule):
    """Находит все сессии на сегодня"""
    today = datetime.now().strftime('%Y-%m-%d')
    sessions = []
    
    for week in schedule['weeks']:
        for day_name, day_data in week['days'].items():
            if day_data['date'] == today:
                for slot in day_data['slots']:
                    sessions.append({
                        'date': day_data['date'],
                        'day': day_name,
                        'theme': day_data['theme'],
                        'week': week['week_number'],
                        **slot
                    })
    
    return sorted(sessions, key=lambda x: x['time'])

def find_next_session(schedule):
    """Находит следующую запланированную сессию"""
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%H:%M')
    
    # Сначала ищем сегодняшние сессии после текущего времени
    todays = find_todays_sessions(schedule)
    for session in todays:
        if session['time'] > current_time and session['status'] == 'planned':
            return session
    
    # Если нет, ищем первую сессию следующего дня
    for week in schedule['weeks']:
        for day_name, day_data in week['days'].items():
            if day_data['date'] > today:
                for slot in day_data['slots']:
                    if slot['status'] == 'planned':
                        return {
                            'date': day_data['date'],
                            'day': day_name,
                            'theme': day_data['theme'],
                            'week': week['week_number'],
                            **slot
                        }
    
    return None

def format_session_info(session):
    """Форматирует информацию о сессии"""
    specialist_names = {
        'meditation-guide': '🧘 Гид по медитации',
        'psychologist': '🧠 Психолог',
        'psychotherapist': '💭 Психотерапевт',
        'executive-coach': '💼 Коуч по лидерству',
        'life-coach': '🌟 Лайф-коуч',
        'fitness-trainer': '💪 Фитнес-тренер',
        'nutritionist': '🥗 Нутрициолог',
        'dietitian': '🍎 Диетолог',
        'yoga-instructor': '🧘‍♀️ Инструктор йоги',
        'career-consultant': '📈 Карьерный консультант',
        'business-trainer': '👔 Бизнес-тренер',
        'mentor': '🎓 Ментор',
        'personal-growth-trainer': '🚀 Тренер личностного роста',
        'nlp-practitioner': '🧩 НЛП-практик',
        'hypnologist': '😴 Гипнолог',
        'psychosomatologist': '🌊 Психосоматолог',
        'sexologist': '❤️ Сексолог',
        'lifestyle-consultant': '✨ Лайфстайл-консультант',
        'career-orientation': '🎯 Профориентация',
        'spiritual-guide': '🕉 Духовный наставник',
        'astro-psychologist': '⭐ Астролог-психолог',
        'tarot-consultant': '🔮 Таролог',
        'weekly-review': '📊 Еженедельный обзор'
    }
    
    specialist_name = specialist_names.get(session['specialist'], session['specialist'])
    
    return f"""
╔═══════════════════════════════════════════════════════════════
║ 🎯 СЕССИЯ СО СПЕЦИАЛИСТОМ
╠═══════════════════════════════════════════════════════════════
║ 
║ {specialist_name}
║ 
║ 📅 Дата: {session['date']} ({session['day'].title()})
║ 🕐 Время: {session['time']}
║ ⏱  Длительность: {session['duration']} минут
║ 
║ 📝 Тема: {session['topic']}
║ 🎯 Контекст: {session['week_context']}
║ 
║ 📊 Статус: {session['status']}
║ 
╚═══════════════════════════════════════════════════════════════

💡 Для начала сессии используйте: /{session['specialist']}

📝 Система автоматически сохранит заметки в:
   progress/sessions/{session['date']}-{session['time']}-{session['specialist']}.md
"""

def main():
    if len(sys.argv) < 2:
        print("""
Использование:
  python session_info.py today          # Показать все сессии на сегодня
  python session_info.py next           # Показать следующую сессию
  python session_info.py <specialist>   # Найти сессию со специалистом
  
Примеры:
  python session_info.py today
  python session_info.py next
  python session_info.py meditation-guide
  python session_info.py psychologist
""")
        sys.exit(1)
    
    schedule = load_schedule()
    if not schedule:
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'today':
        sessions = find_todays_sessions(schedule)
        if not sessions:
            print("📅 На сегодня сессий не запланировано")
            
            # Покажем следующую сессию
            next_session = find_next_session(schedule)
            if next_session:
                print("\n⏭ Следующая запланированная сессия:")
                print(format_session_info(next_session))
            return
        
        print(f"\n📅 Сессии на сегодня ({datetime.now().strftime('%d.%m.%Y')})")
        print(f"🎯 Тема дня: {sessions[0]['theme']}\n")
        
        for i, session in enumerate(sessions, 1):
            specialist_names = {
                'meditation-guide': '🧘 Медитация',
                'psychologist': '🧠 Психолог',
                'executive-coach': '💼 Коуч',
                'yoga-instructor': '🧘‍♀️ Йога',
                'fitness-trainer': '💪 Фитнес',
                'nutritionist': '🥗 Нутрициолог',
                'psychotherapist': '💭 Психотерапевт'
            }
            
            name = specialist_names.get(session['specialist'], session['specialist'])
            status_emoji = '✅' if session['status'] == 'completed' else '⏸' if session['status'] == 'in-progress' else '📋'
            
            print(f"{i}. {status_emoji} {session['time']}-{int(session['time'].split(':')[0]) + session['duration']//60}:{int(session['time'].split(':')[1]) + session['duration']%60:02d} | {name}")
            print(f"   📝 {session['topic']}")
            print()
        
        print(f"\n💡 Для начала сессии используйте: /{sessions[0]['specialist']}")
        print(f"📊 Или используйте: /session-manager для управления")
        
    elif command == 'next':
        session = find_next_session(schedule)
        if not session:
            print("📅 Нет запланированных сессий")
            return
        
        print(format_session_info(session))
        
    else:
        # Ищем сессию со специалистом
        sessions = find_session(schedule, command)
        if not sessions:
            print(f"❌ Сессии со специалистом '{command}' не найдены на сегодня")
            
            # Покажем все будущие сессии с этим специалистом
            print(f"\n🔍 Ближайшие сессии с {command}:")
            count = 0
            for week in schedule['weeks']:
                for day_name, day_data in week['days'].items():
                    for slot in day_data['slots']:
                        if slot['specialist'] == command and slot['status'] == 'planned':
                            print(f"  • {day_data['date']} {slot['time']} - {slot['topic']}")
                            count += 1
                            if count >= 5:
                                break
                    if count >= 5:
                        break
                if count >= 5:
                    break
            return
        
        if len(sessions) == 1:
            print(format_session_info(sessions[0]))
        else:
            print(f"\n📅 Найдено {len(sessions)} сессий с {command} на сегодня:\n")
            for i, session in enumerate(sessions, 1):
                print(f"{i}. {session['time']} - {session['topic']}")
            print(f"\n💡 Для начала используйте: /{command}")

if __name__ == "__main__":
    main()
