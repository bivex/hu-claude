#!/bin/bash
# Скрипт для добавления интеграции с расписанием во все SKILL.md

SKILLS_DIR=".claude/skills"

# Список всех специалистов
SPECIALISTS=(
    "meditation-guide"
    "psychotherapist"
    "hypnologist"
    "nlp-practitioner"
    "psychosomatologist"
    "sexologist"
    "life-coach"
    "executive-coach"
    "mentor"
    "personal-growth-trainer"
    "business-trainer"
    "dietitian"
    "nutritionist"
    "fitness-trainer"
    "yoga-instructor"
    "career-consultant"
    "lifestyle-consultant"
    "career-orientation"
    "spiritual-guide"
    "astro-psychologist"
    "tarot-consultant"
)

INTEGRATION_TEXT='
## 🎯 ВАЖНО: Интеграция с программой

### При начале сессии:

1. **Проверь расписание** на сегодня:
```bash
cat schedule/multiweek-schedule.yaml | grep -A 20 "$(date +%Y-%m-%d)" | grep -A 5 "specialist: SPECIALIST_ID"
```

2. **Используй тему из расписания** для структуры сессии

3. **Прочитай предыдущие заметки** (если есть):
```bash
ls -t progress/sessions/*-SPECIALIST_ID.md 2>/dev/null | head -1
```

4. **После сессии сохрани заметки** в:
   `progress/sessions/YYYY-MM-DD-HH-MM-SPECIALIST_ID.md`

Формат заметок:
```markdown
# Сессия с SPECIALIST_NAME

**Дата:** [DATE] [TIME]
**Неделя:** [N]
**Тема:** [Тема из расписания]

## Ход сессии
[Описание]

## Ключевые инсайты
- [инсайт 1]

## Домашнее задание
- [ ] [задание]

## Следующая сессия
[Дата из расписания]
```
'

echo "🔧 Добавление интеграции с расписанием в SKILL.md файлы..."
echo ""

for specialist in "${SPECIALISTS[@]}"; do
    SKILL_FILE="$SKILLS_DIR/$specialist/SKILL.md"
    
    if [ -f "$SKILL_FILE" ]; then
        # Проверяем, есть ли уже интеграция
        if grep -q "ВАЖНО: Интеграция с программой" "$SKILL_FILE"; then
            echo "⏭  $specialist: интеграция уже добавлена"
        else
            # Добавляем allowed-tools если их нет
            if ! grep -q "allowed-tools:" "$SKILL_FILE"; then
                sed -i '' '/^argument-hint:/a\
allowed-tools: Read, Write, Bash(cat *), Bash(grep *), Bash(date *), Bash(ls *)
' "$SKILL_FILE"
            fi
            
            # Добавляем текст интеграции после заголовка
            TEXT=$(echo "$INTEGRATION_TEXT" | sed "s/SPECIALIST_ID/$specialist/g" | sed "s/SPECIALIST_NAME/$(echo $specialist | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')/g")
            
            # Находим первый ## заголовок и вставляем перед ним
            awk -v text="$TEXT" '
                /^## [^🎯]/ && !inserted { 
                    print text
                    inserted=1
                }
                { print }
            ' "$SKILL_FILE" > "$SKILL_FILE.tmp"
            
            mv "$SKILL_FILE.tmp" "$SKILL_FILE"
            
            echo "✅ $specialist: интеграция добавлена"
        fi
    else
        echo "❌ $specialist: файл не найден ($SKILL_FILE)"
    fi
done

echo ""
echo "✨ Готово!"
echo ""
echo "Теперь все специалисты будут:"
echo "- Читать расписание для получения темы недели"
echo "- Проверять предыдущие заметки для контекста"
echo "- Сохранять заметки после каждой сессии"
