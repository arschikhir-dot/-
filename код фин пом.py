import asyncio
import sqlite3
import random
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ================ НАСТРОЙКИ ================
BOT_TOKEN = "8008754527:AAFKWiH0LTAL62ey6DBa8W-pLZf3Imy7GI0"

# ================ СОСТОЯНИЯ ДЛЯ ЦЕЛЕЙ ================
class GoalStates(StatesGroup):
    waiting_goal_name = State()
    waiting_goal_target = State()

# ================ НОВОЕ: ОБРАЗОВАТЕЛЬНЫЕ КУРСЫ ================
FINANCIAL_COURSES = {
    "beginner": {
        "name": "📚 Финансы для начинающих",
        "description": "5 уроков об основах управления деньгами",
        "lessons": [
            {
                "title": "Урок 1: Что такое бюджет",
                "content": """💰 *Что такое бюджет и зачем он нужен?*
                
Бюджет — это план твоих доходов и расходов на определенный период.

✅ *Зачем вести бюджет:*
• Понимать, куда уходят деньги
• Контролировать расходы
• Копить на цели
• Избегать долгов

🎯 *Простое правило:* Доходы должны быть больше расходов!""",
                "task": "Посчитай свои карманные деньги за неделю"
            },
            {
                "title": "Урок 2: Доходы vs Расходы",
                "content": """💸 *Доходы и расходы*
                
*Доходы* — это деньги, которые ты получаешь:
• Карманные деньги
• Подработка
• Подарки
• Стипендия

*Расходы* — это деньги, которые ты тратишь:
• Еда и транспорт
• Развлечения
• Учеба
• Личные нужды

📊 *Задание:* Раздели свои траты на 4 категории""",
                "task": "Запиши 3 своих дохода и 3 расхода"
            },
            {
                "title": "Урок 3: Как ставить финансовые цели",
                "content": """🎯 *SMART-цели*
                
Цели должны быть:
• S — Конкретные (Новый телефон)
• M — Измеримые (30 000 рублей)
• A — Достижимые (За 6 месяцев)
• R — Релевантные (Тебе это нужно)
• T — Ограниченные по времени (К 1 сентября)

Пример: "Накопить 30 000₽ на новый телефон к 1 сентября, откладывая по 5 000₽ в месяц" """,
                "task": "Поставь одну финансовую цель по SMART"
            },
            {
                "title": "Урок 4: Первые накопления",
                "content": """💰 *Правило 50/30/20*
                
Разделяй деньги на:
• 50% — Обязательные расходы (еда, транспорт)
• 30% — Желания (развлечения, хобби)
• 20% — Накопления (цели, подушка безопасности)

💡 *Совет:* Откладывай 10% сразу при получении денег!

Пример: Если получил 1000₽:
• 500₽ — на еду и проезд
• 300₽ — на кино или игры
• 200₽ — на накопления""",
                "task": "Примени правило 50/30/20 к своим деньгам"
            },
            {
                "title": "Урок 5: Защита от мошенников",
                "content": """🛡️ *Финансовая безопасность*
                
*Никогда не сообщай:*
• Номер банковской карты
• CVV-код (3 цифры на обороте)
• СМС-коды из банка
• Пароли от интернет-банка

⚠️ *Опасные ситуации:*
• "Срочно переведи деньги"
• "Вы выиграли приз"
• "Ваша карта заблокирована"

✅ *Что делать:* 
• Проверяй отправителя
• Звони в банк
• Не торопись""",
                "task": "Проверь, знают ли твои други эти правила"
            }
        ],
        "duration": "5 дней",
        "completed_emoji": "✅",
        "in_progress_emoji": "⏳"
    },
    "investment": {
        "name": "📈 Инвестиции для школьников",
        "description": "5 уроков об основах инвестирования",
        "lessons": [
            {
                "title": "Урок 1: Что такое инвестиции",
                "content": """📈 *Основы инвестирования*
                
Инвестиции — это вложение денег для получения дохода.

*Зачем инвестировать:*
• Деньги работают на тебя
• Защита от инфляции
• Финансовая независимость

💰 *Правило:* Начинай с малого, изучай, диверсифицируй!""",
                "task": "Изучи 3 вида инвестиций"
            },
            {
                "title": "Урок 2: Акции и облигации",
                "content": """🏢 *Акции vs Облигации*
                
*Акции* — доля в компании
• Высокий риск, высокая доходность
• Можно получать дивиденды
• Цена меняется

*Облигации* — долг компании или государства
• Низкий риск, низкая доходность
• Фиксированный процент
• Срок погашения

💡 *Совет:* Начинай с облигаций, потом добавляй акции""",
                "task": "Сравни доходность акций и облигаций"
            },
            {
                "title": "Урок 3: Депозиты и накопительные счета",
                "content": """🏦 *Банковские продукты*
                
*Депозит* (вклад):
• Фиксированный срок
• Нельзя снимать досрочно
• Высокий процент
• Страхование вкладов

*Накопительный счет*:
• Можно снимать в любой момент
• Низкий процент
• Удобно для накоплений

📊 *Пример:* 100 000₽ под 5% = 105 000₽ через год""",
                "task": "Посчитай, сколько накопится за год"
            },
            {
                "title": "Урок 4: Риски и доходность",
                "content": """⚖️ *Риск vs Доходность*
                
*Золотое правило:* Чем выше доходность, тем выше риск!

📉 *Виды рисков:*
• Рыночный (цена падает)
• Кредитный (компания банкрот)
• Инфляционный (деньги обесцениваются)

✅ *Как снизить риски:*
• Диверсификация (разные активы)
• Долгосрочные инвестиции
• Регулярные вложения""",
                "task": "Составь портфель с разными рисками"
            },
            {
                "title": "Урок 5: Создание портфеля",
                "content": """🎯 *Инвестиционный портфель*
                
*Пример портфеля для начинающих:*
• 50% — Облигации (низкий риск)
• 30% — Акции (средний риск)
• 20% — Депозит (минимальный риск)

💰 *Стратегия:*
1. Определи цель
2. Оцени риски
3. Начни с малого
4. Регулярно пополняй
5. Анализируй результаты

💡 *Правило:* Не клади все яйца в одну корзину!""",
                "task": "Создай свой первый виртуальный портфель"
            }
        ],
        "duration": "5 дней",
        "completed_emoji": "✅",
        "in_progress_emoji": "⏳"
    }
}

# Таблица для прогресса курсов
def init_db():
    """Создаем базу данных с таблицей для курсов"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    # Удаляем старые таблицы если есть
    c.execute("DROP TABLE IF EXISTS transactions")
    c.execute("DROP TABLE IF EXISTS goals")
    c.execute("DROP TABLE IF EXISTS course_progress")
    
    # Основные таблицы
    c.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            type TEXT,
            description TEXT,
            date TEXT DEFAULT (datetime('now'))
        )
    ''')
    
    c.execute('''
        CREATE TABLE goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            target REAL,
            saved REAL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    
    # НОВАЯ ТАБЛИЦА: Прогресс по курсам
    c.execute('''
        CREATE TABLE course_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            course_id TEXT,
            current_lesson INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            started_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных с курсами создана")

init_db()

# Функции для работы с курсами
def get_course_progress(user_id, course_id):
    """Получаем прогресс по курсу"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute(
        "SELECT current_lesson, completed FROM course_progress WHERE user_id = ? AND course_id = ?",
        (user_id, course_id)
    )
    progress = c.fetchone()
    conn.close()
    
    if progress:
        return {"current_lesson": progress[0], "completed": bool(progress[1])}
    return None

def start_course(user_id, course_id):
    """Начинаем курс"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    # Проверяем, не начат ли уже курс
    c.execute(
        "SELECT COUNT(*) FROM course_progress WHERE user_id = ? AND course_id = ?",
        (user_id, course_id)
    )
    exists = c.fetchone()[0]
    
    if not exists:
        c.execute(
            "INSERT INTO course_progress (user_id, course_id) VALUES (?, ?)",
            (user_id, course_id)
        )
    
    conn.commit()
    conn.close()

def complete_lesson(user_id, course_id, lesson_number):
    """Завершаем урок"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    # Обновляем прогресс
    c.execute(
        "UPDATE course_progress SET current_lesson = ? WHERE user_id = ? AND course_id = ?",
        (lesson_number, user_id, course_id)
    )
    
    # Проверяем, завершен ли курс
    course = FINANCIAL_COURSES[course_id]
    if lesson_number >= len(course["lessons"]):
        c.execute(
            "UPDATE course_progress SET completed = 1 WHERE user_id = ? AND course_id = ?",
            (user_id, course_id)
        )
    
    conn.commit()
    conn.close()

# Функции БД
def add_transaction(user_id, amount, category, type_, description=""):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO transactions (user_id, amount, category, type, description) VALUES (?, ?, ?, ?, ?)",
        (user_id, amount, category, type_, description)
    )
    conn.commit()
    conn.close()

def add_goal(user_id, name, target):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO goals (user_id, name, target) VALUES (?, ?, ?)",
        (user_id, name, target)
    )
    conn.commit()
    conn.close()

def get_stats(user_id):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    c.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'income'", (user_id,))
    income = c.fetchone()[0] or 0
    
    c.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'expense'", (user_id,))
    expense = c.fetchone()[0] or 0
    
    c.execute('''
        SELECT category, SUM(amount) as total 
        FROM transactions 
        WHERE user_id = ? AND type = 'expense' 
        GROUP BY category 
        ORDER BY total DESC
    ''', (user_id,))
    expenses_by_cat = c.fetchall()
    
    conn.close()
    return income, expense, expenses_by_cat

def get_goals(user_id):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute("SELECT name, target, saved FROM goals WHERE user_id = ?", (user_id,))
    goals = c.fetchall()
    conn.close()
    return goals

# ================ БОТ ================
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ================ КЛАВИАТУРЫ ================
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Доход"), KeyboardButton(text="💸 Расход")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🎯 Цели")],
        [KeyboardButton(text="📈 График"), KeyboardButton(text="🎓 Курсы")],
        [KeyboardButton(text="💡 Совет")]
    ],
    resize_keyboard=True
)

# Храним состояния пользователей
user_states = {}

# ================ КОМАНДЫ ================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        f"""🤖 *Финансовый помощник с курсами*

Привет, {message.from_user.first_name}! 
Я помогу тебе не только учитывать деньги, но и научиться управлять ими!

✨ *Новые возможности:*
• 📝 Учет доходов и расходов
• 📊 Аналитика и графики
• 🎯 Финансовые цели
• 🎓 *Обучающие курсы* 🆕

Выбери действие 👇""",
        parse_mode="Markdown",
        reply_markup=main_kb
    )

# ================ НОВАЯ КОМАНДА: ОБУЧАЮЩИЕ КУРСЫ ================
@dp.message(lambda msg: msg.text == "🎓 Курсы")
async def courses_menu(message: types.Message):
    text = "🎓 *Обучающие курсы по финансовой грамотности*\n\n"
    text += "Выбери курс для обучения:\n\n"
    
    for course_id, course in FINANCIAL_COURSES.items():
        # Проверяем прогресс пользователя
        progress = get_course_progress(message.from_user.id, course_id)
        
        if progress:
            if progress["completed"]:
                status = f"{course['completed_emoji']} Завершен"
            else:
                status = f"{course['in_progress_emoji']} Урок {progress['current_lesson'] + 1}/{len(course['lessons'])}"
        else:
            status = "▶️ Начать"
        
        text += f"{course['name']}\n"
        text += f"   {course['description']}\n"
        text += f"   {course['duration']} • {status}\n\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Финансы для начинающих", callback_data="course_beginner")],
        [InlineKeyboardButton(text="📈 Инвестиции для школьников", callback_data="course_investment")],
        [InlineKeyboardButton(text="📋 Мои курсы", callback_data="my_courses")]
    ])
    
    await message.answer(text, parse_mode="Markdown", reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("course_"))
async def start_course_cmd(callback: types.CallbackQuery):
    course_id = callback.data.split("_")[1]
    
    if course_id in FINANCIAL_COURSES:
        course = FINANCIAL_COURSES[course_id]
        
        # Начинаем курс
        start_course(callback.from_user.id, course_id)
        
        # Получаем прогресс
        progress = get_course_progress(callback.from_user.id, course_id)
        lesson_number = progress["current_lesson"] if progress else 0
        
        # Показываем первый урок
        if lesson_number < len(course["lessons"]):
            lesson = course["lessons"][lesson_number]
            
            text = f"🎓 *{course['name']}*\n\n"
            text += f"📖 {lesson['title']}\n\n"
            text += f"{lesson['content']}\n\n"
            text += f"📝 *Задание:* {lesson['task']}\n\n"
            text += f"📊 Прогресс: {lesson_number + 1}/{len(course['lessons'])}"
            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Выполнил задание", callback_data=f"complete_{course_id}_{lesson_number}")],
                [InlineKeyboardButton(text="➡️ Следующий урок", callback_data=f"next_{course_id}_{lesson_number}")],
                [InlineKeyboardButton(text="📋 Содержание курса", callback_data=f"contents_{course_id}")]
            ])
            
            await callback.message.answer(text, parse_mode="Markdown", reply_markup=kb)
        else:
            await callback.message.answer(
                f"🎉 *Поздравляем!*\n\n"
                f"Ты завершил курс '{course['name']}'!\n\n"
                f"Теперь ты знаешь основы финансовой грамотности. "
                f"Продолжай применять знания на практике!",
                parse_mode="Markdown"
            )
    
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("complete_"))
async def complete_lesson_cmd(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    course_id = parts[1]
    lesson_number = int(parts[2])
    
    # Отмечаем урок как выполненный
    complete_lesson(callback.from_user.id, course_id, lesson_number + 1)
    
    await callback.message.answer(
        "✅ *Отлично! Задание выполнено!*\n\n"
        "Ты становишься лучше с каждым уроком! "
        "Переходи к следующему уроку или повтори материал.",
        parse_mode="Markdown"
    )
    
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("next_"))
async def next_lesson_cmd(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    course_id = parts[1]
    current_lesson = int(parts[2])
    
    if course_id in FINANCIAL_COURSES:
        course = FINANCIAL_COURSES[course_id]
        
        # Проверяем, есть ли следующий урок
        if current_lesson + 1 < len(course["lessons"]):
            next_lesson = course["lessons"][current_lesson + 1]
            
            text = f"🎓 *{course['name']}*\n\n"
            text += f"📖 {next_lesson['title']}\n\n"
            text += f"{next_lesson['content']}\n\n"
            text += f"📝 *Задание:* {next_lesson['task']}\n\n"
            text += f"📊 Прогресс: {current_lesson + 2}/{len(course['lessons'])}"
            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Выполнил задание", callback_data=f"complete_{course_id}_{current_lesson + 1}")],
                [InlineKeyboardButton(text="➡️ Следующий урок", callback_data=f"next_{course_id}_{current_lesson + 1}")],
                [InlineKeyboardButton(text="⬅️ Предыдущий урок", callback_data=f"prev_{course_id}_{current_lesson + 1}")]
            ])
            
            await callback.message.answer(text, parse_mode="Markdown", reply_markup=kb)
        else:
            await callback.message.answer(
                "🎉 *Это был последний урок курса!*\n\n"
                "Ты завершил все уроки. Молодец! "
                "Применяй полученные знания на практике.",
                parse_mode="Markdown"
            )
    
    await callback.answer()

@dp.callback_query(lambda c: c.data == "my_courses")
async def my_courses_cmd(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    c.execute("SELECT course_id, current_lesson, completed FROM course_progress WHERE user_id = ?", (user_id,))
    user_courses = c.fetchall()
    conn.close()
    
    if not user_courses:
        await callback.message.answer(
            "📚 *Твои курсы*\n\n"
            "Ты еще не начал ни одного курса.\n"
            "Выбери курс из меню и начни обучение!",
            parse_mode="Markdown"
        )
    else:
        text = "📚 *Твои курсы*\n\n"
        
        for course_id, current_lesson, completed in user_courses:
            if course_id in FINANCIAL_COURSES:
                course = FINANCIAL_COURSES[course_id]
                
                if completed:
                    status = f"{course['completed_emoji']} Завершен"
                else:
                    status = f"{course['in_progress_emoji']} В процессе ({current_lesson}/{len(course['lessons'])})"
                
                text += f"{course['name']}\n"
                text += f"   Статус: {status}\n"
                
                if not completed:
                    text += f"   [{'█' * current_lesson}{'░' * (len(course['lessons']) - current_lesson)}]\n"
                
                text += "\n"
        
        await callback.message.answer(text, parse_mode="Markdown")
    
    await callback.answer()

# ================ ОБРАБОТКА ЦЕЛЕЙ ================
@dp.message(lambda msg: msg.text == "🎯 Цели")
async def goals_cmd(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Новая цель", callback_data="new_goal")],
        [InlineKeyboardButton(text="📋 Мои цели", callback_data="my_goals")]
    ])
    
    await message.answer(
        "🎯 *Финансовые цели*\n\nВыберите действие:",
        parse_mode="Markdown",
        reply_markup=kb
    )

@dp.callback_query(lambda c: c.data == "new_goal")
async def new_goal_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(GoalStates.waiting_goal_name)
    
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )
    
    await callback.message.answer(
        "🎯 *Создание новой цели*\n\nВведите название цели:\n\nПример: 'Новый телефон', 'Ноутбук', 'Путешествие'",
        parse_mode="Markdown",
        reply_markup=kb
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "my_goals")
async def show_goals(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    goals = get_goals(user_id)
    
    if not goals:
        await callback.message.answer(
            "🎯 *У вас пока нет финансовых целей!*\n\n"
            "Создайте свою первую цель, нажав '➕ Новая цель'",
            parse_mode="Markdown"
        )
    else:
        text = "🎯 *Ваши цели:*\n\n"
        
        for i, (name, target, saved) in enumerate(goals, 1):
            progress = (saved / target * 100) if target > 0 else 0
            bars_count = int(progress / 5)
            bars = "█" * bars_count + "░" * (20 - bars_count)
            remaining = target - saved
            
            text += f"*{i}. {name}*\n"
            text += f"   Цель: {target:.2f} ₽\n"
            text += f"   Накоплено: {saved:.2f} ₽ ({progress:.1f}%)\n"
            text += f"   Осталось: {remaining:.2f} ₽\n"
            text += f"   [{bars}]\n\n"
        
        text += "💡 *Совет:* Откладывайте хотя бы 10% от любого дохода на свои цели!"
        
        await callback.message.answer(text, parse_mode="Markdown")
    
    await callback.answer()

@dp.message(GoalStates.waiting_goal_name)
async def process_goal_name(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Создание цели отменено", reply_markup=main_kb)
        return
    
    await state.update_data(goal_name=message.text)
    await state.set_state(GoalStates.waiting_goal_target)
    
    await message.answer(
        f"✅ Название: *{message.text}*\n\n"
        f"Теперь введите сумму цели (в рублях):\n\n"
        f"Пример: 30000 (для 30 000 рублей)",
        parse_mode="Markdown"
    )

@dp.message(GoalStates.waiting_goal_target)
async def process_goal_target(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Создание цели отменено", reply_markup=main_kb)
        return
    
    try:
        target = float(message.text.replace(",", "."))
        
        if target <= 0:
            await message.answer("❌ Сумма должна быть больше 0!")
            return
        
        # Получаем данные из состояния
        data = await state.get_data()
        goal_name = data.get("goal_name", "Без названия")
        
        # Сохраняем цель в БД
        add_goal(message.from_user.id, goal_name, target)
        
        await state.clear()
        
        await message.answer(
            f"🎯 *Цель создана!*\n\n"
            f"📋 Название: {goal_name}\n"
            f"💰 Цель: {target:.2f} ₽\n"
            f"💪 Удачи в достижении цели!\n\n"
            f"Следи за прогрессом в разделе '🎯 Цели' → '📋 Мои цели'",
            parse_mode="Markdown",
            reply_markup=main_kb
        )
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число!")

# ================ ОСТАЛЬНЫЕ КОМАНДЫ ================

@dp.message(lambda msg: msg.text == "💰 Доход")
async def income_menu(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💰 Карманные"), KeyboardButton(text="🎯 Подработка")],
            [KeyboardButton(text="🏆 Премия"), KeyboardButton(text="🎁 Подарок")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите категорию дохода:", reply_markup=kb)

@dp.message(lambda msg: msg.text == "💸 Расход")
async def expense_menu(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍔 Еда"), KeyboardButton(text="🚌 Транспорт")],
            [KeyboardButton(text="🎮 Развлечения"), KeyboardButton(text="📚 Учеба")],
            [KeyboardButton(text="👕 Одежда"), KeyboardButton(text="💊 Здоровье")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите категорию расхода:", reply_markup=kb)

@dp.message(lambda msg: msg.text in ["💰 Карманные", "🎯 Подработка", "🏆 Премия", "🎁 Подарок",
                                     "🍔 Еда", "🚌 Транспорт", "🎮 Развлечения", "📚 Учеба", 
                                     "👕 Одежда", "💊 Здоровье"])
async def ask_amount(message: types.Message):
    user_states[message.from_user.id] = {
        "action": "waiting_amount",
        "category": message.text
    }
    
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )
    
    await message.answer(
        f"💵 Введите сумму для *{message.text}*:\n\nПример: 1500",
        parse_mode="Markdown",
        reply_markup=kb
    )

@dp.message(lambda msg: msg.from_user.id in user_states and user_states[msg.from_user.id]["action"] == "waiting_amount")
async def save_transaction(message: types.Message):
    if message.text == "❌ Отмена":
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        await message.answer("Отменено", reply_markup=main_kb)
        return
    
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0!")
            return
        
        user_id = message.from_user.id
        category = user_states[user_id]["category"]
        
        if category in ["💰 Карманные", "🎯 Подработка", "🏆 Премия", "🎁 Подарок"]:
            type_ = "income"
            emoji = "💰"
        else:
            type_ = "expense"
            emoji = "💸"
        
        add_transaction(user_id, amount, category, type_)
        del user_states[user_id]
        
        income, expense, _ = get_stats(user_id)
        balance = income - expense
        
        await message.answer(
            f"{emoji} *Успешно!*\n\n"
            f"📋 Категория: {category}\n"
            f"💵 Сумма: {amount:.2f} ₽\n"
            f"📊 Баланс: {balance:.2f} ₽",
            parse_mode="Markdown",
            reply_markup=main_kb
        )
        
    except ValueError:
        await message.answer("❌ Введите число!")

@dp.message(lambda msg: msg.text == "📊 Статистика")
async def show_stats_cmd(message: types.Message):
    user_id = message.from_user.id
    income, expense, expenses = get_stats(user_id)
    
    text = f"""📊 *Статистика*

💰 Доходы: {income:.2f} ₽
💸 Расходы: {expense:.2f} ₽
📈 Баланс: {income - expense:.2f} ₽

🎯 Топ расходов:\n"""
    
    if expenses:
        for category, total in expenses[:5]:
            text += f"• {category}: {total:.2f} ₽\n"
    else:
        text += "Нет данных"
    
    await message.answer(text, parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "📈 График")
async def show_chart(message: types.Message):
    user_id = message.from_user.id
    _, _, expenses = get_stats(user_id)
    
    if not expenses:
        await message.answer("❌ Нет данных для графика")
        return
    
    categories = []
    amounts = []
    for cat, amount in expenses[:6]:
        if ' ' in cat:
            clean_cat = cat.split(' ', 1)[1]
        else:
            clean_cat = cat
        categories.append(clean_cat)
        amounts.append(amount)
    
    plt.figure(figsize=(10, 8))
    colors = ['#FF6B6B', '#4ECDC4', '#FFD166', '#06D6A0', '#118AB2', '#EF476F']
    
    plt.pie(
        amounts, 
        labels=categories, 
        autopct='%1.1f%%',
        colors=colors[:len(categories)],
        shadow=True,
        startangle=90
    )
    
    plt.title('Структура расходов', fontsize=16, pad=20)
    plt.axis('equal')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    await message.answer_photo(
        types.BufferedInputFile(buf.read(), filename="chart.png"),
        caption="📊 Визуализация ваших расходов"
    )

@dp.message(lambda msg: msg.text == "💡 Совет")
async def advice_cmd(message: types.Message):
    advice_list = [
        "💰 *Правило 50/30/20:* 50% на нужды, 30% на желания, 20% на сбережения",
        "🎯 *SMART-цели:* Конкретные, Измеримые, Достижимые, Релевантные цели со Сроком",
        "📊 *Анализируйте расходы:* Раз в неделю смотри, куда уходят деньги",
        "💸 *Правило 24 часов:* Перед покупкой подожди сутки",
        "🔄 *Автоматизируйте сбережения:* Откладывай 10% сразу при получении денег",
        "📱 *Цифровая копилка:* Этот бот — твой первый шаг к финансовой независимости!",
        "🎓 *Образование — лучшая инвестиция:* Финансовая грамотность пригодится всегда",
        "🏦 *Финансовая подушка:* Стремись иметь запас на 3-6 месяцев расходов"
    ]
    
    await message.answer(f"*💡 Финансовый совет:*\n\n{random.choice(advice_list)}", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "⬅️ Назад")
async def back_cmd(message: types.Message):
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]
    await message.answer("Главное меню:", reply_markup=main_kb)

# ================ ЗАПУСК ================
async def main():
    print("=" * 60)
    print("🤖 ФИНАНСОВЫЙ ПОМОЩНИК С ОБУЧАЮЩИМИ КУРСАМИ")
    print("📊 Проект для 10 класса - УЛУЧШЕННАЯ ВЕРСИЯ")
    print("=" * 60)
    print("✨ НОВАЯ ФУНКЦИЯ:")
    print("• 🎓 2 обучающих курса по финансовой грамотности")
    print("• 📚 5 уроков в каждом курсе")
    print("• ✅ Система прогресса и заданий")
    print("• 📈 Практические знания для школьников")
    print("=" * 60)
    
    try:
        bot_info = await bot.get_me()
        print(f"✅ Бот запущен: @{bot_info.username}")
        print(f"📱 Ссылка: https://t.me/{bot_info.username}")
        print("=" * 60)
        print("🎓 КУРСЫ ДОСТУПНЫ В МЕНЮ '🎓 КУРСЫ'")
        print("=" * 60)
        
        await dp.start_polling(bot)
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        print("Проверьте токен бота и подключение к интернету!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
