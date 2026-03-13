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
    waiting_parent_id = State()  # Новое состояние для ID родителя

# ================ НОВОЕ: РОДИТЕЛЬСКИЙ КОНТРОЛЬ ================
class ParentStates(StatesGroup):
    waiting_child_id = State()
    waiting_task_description = State()
    waiting_task_reward = State()

# ================ ОБРАЗОВАТЕЛЬНЫЕ КУРСЫ ================
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
        "description": "5 уроков об основами инвестирования",
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

💡 *Совет:* Начинай с облигации, потом добавляй акции""",
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

# Таблица для прогресса курсов и родительского контроля
def init_db():
    """Создаем базу данных с таблицами"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    # Удаляем старые таблицы если есть
    c.execute("DROP TABLE IF EXISTS transactions")
    c.execute("DROP TABLE IF EXISTS goals")
    c.execute("DROP TABLE IF EXISTS course_progress")
    c.execute("DROP TABLE IF EXISTS parent_child")  # НОВАЯ таблица
    c.execute("DROP TABLE IF EXISTS parent_tasks")  # НОВАЯ таблица
    
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
            parent_approved INTEGER DEFAULT 0,
            parent_id INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    
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
    
    # НОВЫЕ ТАБЛИЦЫ ДЛЯ РОДИТЕЛЬСКОГО КОНТРОЛЯ
    c.execute('''
        CREATE TABLE parent_child (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER UNIQUE,
            child_id INTEGER UNIQUE,
            child_name TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE parent_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER,
            parent_id INTEGER,
            description TEXT,
            reward REAL,
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных с родительским контролем создана")

init_db()

# Функции для работы с родительским контролем
def link_parent_child(parent_id, child_id, child_name):
    """Связываем родителя и ребенка"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    try:
        c.execute(
            "INSERT OR REPLACE INTO parent_child (parent_id, child_id, child_name) VALUES (?, ?, ?)",
            (parent_id, child_id, child_name)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка при связывании: {e}")
        return False
    finally:
        conn.close()

def get_child_info(parent_id):
    """Получаем информацию о ребенке"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute(
        "SELECT child_id, child_name FROM parent_child WHERE parent_id = ?",
        (parent_id,)
    )
    child = c.fetchone()
    conn.close()
    
    if child:
        return {"child_id": child[0], "child_name": child[1]}
    return None

def get_parent_info(child_id):
    """Получаем информацию о родителе"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute(
        "SELECT parent_id FROM parent_child WHERE child_id = ?",
        (child_id,)
    )
    parent = c.fetchone()
    conn.close()
    
    if parent:
        return parent[0]
    return None

def create_parent_task(child_id, parent_id, description, reward):
    """Создаем задание от родителя"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO parent_tasks (child_id, parent_id, description, reward) VALUES (?, ?, ?, ?)",
        (child_id, parent_id, description, reward)
    )
    conn.commit()
    conn.close()

def get_child_tasks(child_id):
    """Получаем задания для ребенка"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute(
        "SELECT id, description, reward, completed FROM parent_tasks WHERE child_id = ?",
        (child_id,)
    )
    tasks = c.fetchall()
    conn.close()
    return tasks

def get_parent_tasks(parent_id):
    """Получаем задания, созданные родителем"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute(
        "SELECT id, child_id, description, reward, completed FROM parent_tasks WHERE parent_id = ?",
        (parent_id,)
    )
    tasks = c.fetchall()
    conn.close()
    return tasks

def complete_task(task_id, child_id):
    """Отмечаем задание как выполненное"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    # Получаем информацию о задании
    c.execute(
        "SELECT reward FROM parent_tasks WHERE id = ? AND child_id = ?",
        (task_id, child_id)
    )
    task = c.fetchone()
    
    if task:
        reward = task[0]
        
        # Отмечаем задание как выполненное
        c.execute(
            "UPDATE parent_tasks SET completed = 1 WHERE id = ?",
            (task_id,)
        )
        
        # Добавляем награду как доход
        c.execute(
            "INSERT INTO transactions (user_id, amount, category, type, description) VALUES (?, ?, ?, ?, ?)",
            (child_id, reward, "🎁 Награда за задание", "income", "Выполнение задания от родителя")
        )
        
        conn.commit()
        conn.close()
        return reward
    
    conn.close()
    return None

def approve_child_goal(goal_id, parent_id):
    """Родитель одобряет цель ребенка"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    c.execute(
        "UPDATE goals SET parent_approved = 1 WHERE id = ? AND parent_id = ?",
        (goal_id, parent_id)
    )
    
    conn.commit()
    conn.close()

def get_child_goals(parent_id):
    """Получаем цели ребенка для родителя"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    # Получаем ID ребенка
    c.execute(
        "SELECT child_id FROM parent_child WHERE parent_id = ?",
        (parent_id,)
    )
    child = c.fetchone()
    
    if child:
        child_id = child[0]
        c.execute(
            "SELECT id, name, target, saved, parent_approved FROM goals WHERE user_id = ?",
            (child_id,)
        )
        goals = c.fetchall()
        conn.close()
        return goals
    
    conn.close()
    return []

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

def add_goal(user_id, name, target, parent_id=None):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO goals (user_id, name, target, parent_id) VALUES (?, ?, ?, ?)",
        (user_id, name, target, parent_id)
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
    c.execute("SELECT id, name, target, saved, parent_approved FROM goals WHERE user_id = ?", (user_id,))
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
        [KeyboardButton(text="💡 Совет"), KeyboardButton(text="👨‍👦 Родители")]  # НОВАЯ КНОПКА
    ],
    resize_keyboard=True
)

parent_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👶 Мои дети"), KeyboardButton(text="📋 Задания")],
        [KeyboardButton(text="🎯 Цели детей"), KeyboardButton(text="💰 Вознаграждения")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

child_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Мои задания"), KeyboardButton(text="✅ Выполнить задание")],
        [KeyboardButton(text="👨‍👦 Мой родитель"), KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

# Храним состояния пользователей
user_states = {}

# ================ КОМАНДЫ ================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        f"""🤖 *Финансовый помощник с родительским контролем*

Привет, {message.from_user.first_name}! 
Я помогу тебе не только учитывать деньги, но и научиться управлять ими!

✨ *Новые возможности:*
• 📝 Учет доходов и расходов
• 📊 Аналитика и графики
• 🎯 Финансовые цели
• 🎓 Обучающие курсы
• 👨‍👦 *Родительский контроль* 🆕

*Родители могут:*
• Видеть цели ребенка
• Одобрять или отклонять цели
• Давать задания
• Выплачивать вознаграждения

Выбери действие 👇""",
        parse_mode="Markdown",
        reply_markup=main_kb
    )

# ================ РОДИТЕЛЬСКИЙ КОНТРОЛЬ ================
@dp.message(lambda msg: msg.text == "👨‍👦 Родители")
async def parent_menu(message: types.Message):
    """Меню родительского контроля"""
    # Проверяем, родитель или ребенок
    parent_info = get_child_info(message.from_user.id)  # Является ли родителем?
    child_info = get_parent_info(message.from_user.id)  # Является ли ребенком?
    
    if parent_info:
        # Это родитель
        await message.answer(
            f"👨‍👦 *Режим родителя*\n\n"
            f"Приветствую, {message.from_user.first_name}!\n"
            f"Ваш ребенок: {parent_info['child_name']}\n\n"
            f"Что вы хотите сделать?",
            parse_mode="Markdown",
            reply_markup=parent_kb
        )
    elif child_info:
        # Это ребенок
        await message.answer(
            "👶 *Режим ребенка*\n\n"
            "У вас есть подключенный родитель!\n"
            "Вы можете:\n"
            "• Получать задания\n"
            "• Получать вознаграждения\n"
            "• Показывать цели родителю\n\n"
            "Что вы хотите сделать?",
            parse_mode="Markdown",
            reply_markup=child_kb
        )
    else:
        # Пока не определено
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👶 Я ребенок", callback_data="mode_child")],
            [InlineKeyboardButton(text="👨‍👦 Я родитель", callback_data="mode_parent")]
        ])
        
        await message.answer(
            "👨‍👦 *Родительский контроль*\n\n"
            "Выберите ваш режим:\n\n"
            "👶 *Ребенок* - будете получать задания от родителей\n"
            "👨‍👦 *Родитель* - будете давать задания детям\n\n"
            "После выбора режима его нельзя будет изменить!",
            parse_mode="Markdown",
            reply_markup=kb
        )

@dp.callback_query(lambda c: c.data == "mode_child")
async def set_mode_child(callback: types.CallbackQuery):
    """Режим ребенка - просим ID родителя"""
    await callback.message.answer(
        "👶 *Режим ребенка*\n\n"
        "Чтобы подключить родителя, попросите его отправить вам его ID.\n"
        "ID можно получить командой /myid\n\n"
        "Введите ID вашего родителя:",
        parse_mode="Markdown"
    )
    
    # Устанавливаем состояние ожидания ID родителя
    await callback.answer()

@dp.callback_query(lambda c: c.data == "mode_parent")
async def set_mode_parent(callback: types.CallbackQuery):
    """Режим родителя - просим ID ребенка"""
    await callback.message.answer(
        "👨‍👦 *Режим родителя*\n\n"
        "Чтобы подключить ребенка, попросите его отправить вам его ID.\n"
        "ID можно получить командой /myid\n\n"
        "Введите ID вашего ребенка:",
        parse_mode="Markdown"
    )
    
    # Устанавливаем состояние ожидания ID ребенка
    await callback.answer()

@dp.message(Command("myid"))
async def myid_cmd(message: types.Message):
    """Показать свой ID для подключения"""
    await message.answer(
        f"🆔 *Ваш ID:* `{message.from_user.id}`\n\n"
        f"Отправьте этот ID вашему родителю/ребенку для подключения.\n"
        f"⚠️ *Важно:* Никому больше не сообщайте этот ID!",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text and msg.text.isdigit() and len(msg.text) >= 6)
async def process_id(message: types.Message, state: FSMContext):
    """Обработка введенного ID"""
    try:
        target_id = int(message.text)
        
        # Проверяем, существует ли такой пользователь
        try:
            chat = await bot.get_chat(target_id)
        except:
            await message.answer("❌ Пользователь с таким ID не найден!")
            return
        
        # Определяем, кто кого пытается подключить
        # Пытаемся понять по контексту - простой способ
        if message.text == "⬅️ Назад":
            return
            
        # Если ранее был режим ребенка
        if "mode_child" in str(message):
            # Ребенок добавляет родителя
            success = link_parent_child(target_id, message.from_user.id, message.from_user.first_name)
            if success:
                await message.answer(
                    f"✅ *Родитель подключен!*\n\n"
                    f"Теперь {chat.first_name} может:\n"
                    f"• Видеть ваши цели\n"
                    f"• Одобрять цели\n"
                    f"• Давать задания\n"
                    f"• Выплачивать вознаграждения\n\n"
                    f"Используйте меню '👨‍👦 Родители' для управления.",
                    parse_mode="Markdown",
                    reply_markup=main_kb
                )
                
                # Уведомляем родителя
                await bot.send_message(
                    target_id,
                    f"👶 *Новый ребенок подключен!*\n\n"
                    f"{message.from_user.first_name} теперь ваш ребенок в финансовом помощнике!\n\n"
                    f"Вы можете:\n"
                    f"• Смотреть его цели в '👨‍👦 Родители' → '🎯 Цели детей'\n"
                    f"• Давать задания в '👨‍👦 Родители' → '📋 Задания'\n"
                    f"• Выплачивать вознаграждения\n\n"
                    f"Помогите вашему ребенку научиться управлять финансами!",
                    parse_mode="Markdown"
                )
            else:
                await message.answer("❌ Ошибка при подключении!")
        else:
            # Предполагаем, что это родитель добавляет ребенка
            success = link_parent_child(message.from_user.id, target_id, chat.first_name)
            if success:
                await message.answer(
                    f"✅ *Ребенок подключен!*\n\n"
                    f"Теперь {chat.first_name} ваш ребенок в системе.\n\n"
                    f"Вы можете:\n"
                    f"• Смотреть его цели\n"
                    f"• Одобрять цели\n"
                    f"• Давать задания\n"
                    f"• Выплачивать вознаграждения\n\n"
                    f"Используйте меню '👨‍👦 Родители' для управления.",
                    parse_mode="Markdown",
                    reply_markup=main_kb
                )
                
                # Уведомляем ребенка
                await bot.send_message(
                    target_id,
                    f"👨‍👦 *Родитель подключен!*\n\n"
                    f"{message.from_user.first_name} теперь ваш родитель в финансовом помощнике!\n\n"
                    f"Теперь вы можете:\n"
                    f"• Показывать цели родителю\n"
                    f"• Получать задания\n"
                    f"• Получать вознаграждения\n\n"
                    f"Используйте меню '👨‍👦 Родители' для управления.",
                    parse_mode="Markdown"
                )
            else:
                await message.answer("❌ Ошибка при подключении!")
                
    except ValueError:
        await message.answer("❌ Введите корректный числовой ID!")

# Меню родителя
@dp.message(lambda msg: msg.text == "👶 Мои дети")
async def my_children(message: types.Message):
    """Показать информацию о ребенке"""
    child_info = get_child_info(message.from_user.id)
    
    if child_info:
        await message.answer(
            f"👶 *Информация о ребенке*\n\n"
            f"Имя: {child_info['child_name']}\n"
            f"ID: `{child_info['child_id']}`\n\n"
            f"Что вы хотите сделать?\n"
            f"1. Дать задание\n"
            f"2. Посмотреть цели\n"
            f"3. Выплатить вознаграждение\n\n"
            f"Используйте меню ниже ⬇️",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "❌ У вас нет подключенных детей.\n\n"
            "Чтобы подключить ребенка:\n"
            "1. Попросите ребенка отправить вам его ID командой /myid\n"
            "2. Введите этот ID в чат",
            parse_mode="Markdown"
        )

@dp.message(lambda msg: msg.text == "📋 Задания")
async def parent_tasks_menu(message: types.Message, state: FSMContext):
    """Меню заданий для родителя"""
    child_info = get_child_info(message.from_user.id)
    
    if not child_info:
        await message.answer("❌ У вас нет подключенных детей!")
        return
    
    # Показываем существующие задания
    tasks = get_parent_tasks(message.from_user.id)
    
    if tasks:
        text = "📋 *Задания для ребенка*\n\n"
        
        for i, (task_id, child_id, description, reward, completed) in enumerate(tasks, 1):
            status = "✅ Выполнено" if completed else "⏳ Ожидает"
            text += f"*{i}. {description}*\n"
            text += f"   Награда: {reward:.2f} ₽\n"
            text += f"   Статус: {status}\n\n"
    else:
        text = "📋 *Задания для ребенка*\n\nУ вас пока нет заданий."
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать задание", callback_data="create_task")],
        [InlineKeyboardButton(text="🔄 Обновить список", callback_data="refresh_tasks")]
    ])
    
    await message.answer(text, parse_mode="Markdown", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "create_task")
async def create_task_start(callback: types.CallbackQuery, state: FSMContext):
    """Начало создания задания"""
    child_info = get_child_info(callback.from_user.id)
    
    if not child_info:
        await callback.answer("❌ Нет подключенного ребенка!")
        return
    
    await state.set_state(ParentStates.waiting_task_description)
    await state.update_data(child_id=child_info['child_id'])
    
    await callback.message.answer(
        f"📝 *Создание задания для {child_info['child_name']}*\n\n"
        f"Опишите задание:\n\n"
        f"Примеры:\n"
        f"• Помыть посуду\n"
        f"• Сделать уроки\n"
        f"• Убрать в комнате\n"
        f"• Прочитать книгу",
        parse_mode="Markdown"
    )
    
    await callback.answer()

@dp.message(ParentStates.waiting_task_description)
async def process_task_description(message: types.Message, state: FSMContext):
    """Обработка описания задания"""
    if message.text == "⬅️ Назад":
        await state.clear()
        await message.answer("❌ Создание задания отменено", reply_markup=parent_kb)
        return
    
    await state.update_data(task_description=message.text)
    await state.set_state(ParentStates.waiting_task_reward)
    
    await message.answer(
        f"✅ Описание: *{message.text}*\n\n"
        f"Теперь укажите размер вознаграждения (в рублях):\n\n"
        f"Пример: 100, 200, 500",
        parse_mode="Markdown"
    )

@dp.message(ParentStates.waiting_task_reward)
async def process_task_reward(message: types.Message, state: FSMContext):
    """Обработка вознаграждения за задание"""
    if message.text == "⬅️ Назад":
        await state.clear()
        await message.answer("❌ Создание задания отменено", reply_markup=parent_kb)
        return
    
    try:
        reward = float(message.text.replace(",", "."))
        
        if reward <= 0:
            await message.answer("❌ Вознаграждение должно быть больше 0!")
            return
        
        # Получаем данные из состояния
        data = await state.get_data()
        child_id = data.get('child_id')
        task_description = data.get('task_description')
        
        # Создаем задание
        create_parent_task(child_id, message.from_user.id, task_description, reward)
        
        await state.clear()
        
        # Уведомляем ребенка
        child_info = get_child_info(message.from_user.id)
        if child_info:
            await bot.send_message(
                child_id,
                f"📝 *Новое задание от родителя!*\n\n"
                f"📋 *Задание:* {task_description}\n"
                f"💰 *Вознаграждение:* {reward:.2f} ₽\n\n"
                f"Чтобы выполнить задание, перейдите в:\n"
                f"'👨‍👦 Родители' → '✅ Выполнить задание'",
                parse_mode="Markdown"
            )
        
        await message.answer(
            f"✅ *Задание создано!*\n\n"
            f"📋 Задание: {task_description}\n"
            f"💰 Вознаграждение: {reward:.2f} ₽\n\n"
            f"Ребенок получил уведомление о новом задании.",
            parse_mode="Markdown",
            reply_markup=parent_kb
        )
        
    except ValueError:
        await message.answer("❌ Введите число!")

@dp.message(lambda msg: msg.text == "🎯 Цели детей")
async def child_goals_menu(message: types.Message):
    """Цели ребенка для родителя"""
    goals = get_child_goals(message.from_user.id)
    
    if not goals:
        await message.answer(
            "🎯 *Цели вашего ребенка*\n\n"
            "У вашего ребенка пока нет целей, или он еще не создал их.\n\n"
            "Попросите ребенка создать цель в разделе '🎯 Цели'",
            parse_mode="Markdown"
        )
        return
    
    text = "🎯 *Цели вашего ребенка*\n\n"
    
    for i, (goal_id, name, target, saved, approved) in enumerate(goals, 1):
        progress = (saved / target * 100) if target > 0 else 0
        bars_count = int(progress / 5)
        bars = "█" * bars_count + "░" * (20 - bars_count)
        remaining = target - saved
        status = "✅ Одобрено" if approved else "⏳ Ожидает одобрения"
        
        text += f"*{i}. {name}*\n"
        text += f"   Цель: {target:.2f} ₽\n"
        text += f"   Накоплено: {saved:.2f} ₽ ({progress:.1f}%)\n"
        text += f"   Осталось: {remaining:.2f} ₽\n"
        text += f"   Статус: {status}\n"
        
        if not approved:
            text += f"   [{bars}]\n\n"
            
            # Кнопка для одобрения
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"✅ Одобрить '{name}'", callback_data=f"approve_goal_{goal_id}")]
            ])
            await message.answer(text, parse_mode="Markdown", reply_markup=kb)
            text = ""
        else:
            text += f"   [{bars}]\n\n"
    
    if text:
        await message.answer(text, parse_mode="Markdown")

@dp.callback_query(lambda c: c.data.startswith("approve_goal_"))
async def approve_goal_cmd(callback: types.CallbackQuery):
    """Родитель одобряет цель ребенка"""
    goal_id = int(callback.data.split("_")[2])
    
    # Одобряем цель
    approve_child_goal(goal_id, callback.from_user.id)
    
    # Получаем информацию о цели
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute("SELECT user_id, name FROM goals WHERE id = ?", (goal_id,))
    goal_info = c.fetchone()
    conn.close()
    
    if goal_info:
        child_id, goal_name = goal_info
        
        # Уведомляем ребенка
        await bot.send_message(
            child_id,
            f"✅ *Цель одобрена!*\n\n"
            f"Родитель одобрил вашу цель: *{goal_name}*\n\n"
            f"Теперь вы можете получать задания для достижения этой цели!",
            parse_mode="Markdown"
        )
    
    await callback.message.answer(
        "✅ *Цель одобрена!*\n\n"
        "Ребенок получил уведомление. "
        "Теперь вы можете давать ему задания для достижения этой цели.",
        parse_mode="Markdown"
    )
    
    await callback.answer()

@dp.message(lambda msg: msg.text == "💰 Вознаграждения")
async def rewards_menu(message: types.Message):
    """Меню вознаграждений"""
    child_info = get_child_info(message.from_user.id)
    
    if not child_info:
        await message.answer("❌ У вас нет подключенных детей!")
        return
    
    # Получаем статистику по вознаграждениям
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute(
        "SELECT SUM(reward) FROM parent_tasks WHERE parent_id = ? AND completed = 1",
        (message.from_user.id,)
    )
    total_paid = c.fetchone()[0] or 0
    
    c.execute(
        "SELECT SUM(reward) FROM parent_tasks WHERE parent_id = ? AND completed = 0",
        (message.from_user.id,)
    )
    total_pending = c.fetchone()[0] or 0
    conn.close()
    
    await message.answer(
        f"💰 *Вознаграждения*\n\n"
        f"👶 Ребенок: {child_info['child_name']}\n"
        f"💵 Всего выплачено: {total_paid:.2f} ₽\n"
        f"⏳ Ожидает выплаты: {total_pending:.2f} ₽\n\n"
        f"*Совет:* Давайте небольшие, но регулярные вознаграждения "
        f"за выполнение повседневных задач.",
        parse_mode="Markdown"
    )

# Меню ребенка
@dp.message(lambda msg: msg.text == "📝 Мои задания")
async def my_tasks_child(message: types.Message):
    """Задания для ребенка"""
    tasks = get_child_tasks(message.from_user.id)
    
    if not tasks:
        await message.answer(
            "📝 *Мои задания*\n\n"
            "У вас пока нет заданий от родителей.\n\n"
            "Попросите родителей создать для вас задание!",
            parse_mode="Markdown"
        )
        return
    
    text = "📝 *Мои задания*\n\n"
    
    for i, (task_id, description, reward, completed) in enumerate(tasks, 1):
        status = "✅ Выполнено" if completed else "⏳ Ожидает выполнения"
        text += f"*{i}. {description}*\n"
        text += f"   Награда: {reward:.2f} ₽\n"
        text += f"   Статус: {status}\n\n"
    
    await message.answer(text, parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "✅ Выполнить задание")
async def complete_task_menu(message: types.Message):
    """Меню выполнения заданий"""
    tasks = get_child_tasks(message.from_user.id)
    
    if not tasks:
        await message.answer("❌ У вас нет заданий для выполнения!")
        return
    
    # Создаем клавиатуру с заданиями
    keyboard = []
    for task_id, description, reward, completed in tasks:
        if not completed:  # Показываем только невыполненные задания
            short_desc = description[:30] + "..." if len(description) > 30 else description
            keyboard.append([
                InlineKeyboardButton(
                    text=f"✅ {short_desc} ({reward:.0f}₽)",
                    callback_data=f"complete_task_{task_id}"
                )
            ])
    
    if not keyboard:
        await message.answer("🎉 У вас нет невыполненных заданий!")
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(
        "✅ *Выполнить задание*\n\n"
        "Выберите задание, которое вы выполнили:",
        parse_mode="Markdown",
        reply_markup=kb
    )

@dp.callback_query(lambda c: c.data.startswith("complete_task_"))
async def complete_task_cmd(callback: types.CallbackQuery):
    """Ребенок выполняет задание"""
    task_id = int(callback.data.split("_")[2])
    
    # Отмечаем задание как выполненное и начисляем вознаграждение
    reward = complete_task(task_id, callback.from_user.id)
    
    if reward:
        # Получаем информацию о задании
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute("SELECT parent_id, description FROM parent_tasks WHERE id = ?", (task_id,))
        task_info = c.fetchone()
        conn.close()
        
        if task_info:
            parent_id, description = task_info
            
            # Уведомляем родителя
            await bot.send_message(
                parent_id,
                f"✅ *Задание выполнено!*\n\n"
                f"Ваш ребенок выполнил задание:\n"
                f"*{description}*\n\n"
                f"💰 Вознаграждение {reward:.2f} ₽ было зачислено на счет ребенка.",
                parse_mode="Markdown"
            )
        
        await callback.message.answer(
            f"🎉 *Задание выполнено!*\n\n"
            f"💰 Вы получили вознаграждение: *{reward:.2f} ₽*\n\n"
            f"Деньги зачислены на ваш счет. "
            f"Вы можете посмотреть баланс в разделе '📊 Статистика'",
            parse_mode="Markdown"
        )
    else:
        await callback.message.answer("❌ Ошибка при выполнении задания!")
    
    await callback.answer()

@dp.message(lambda msg: msg.text == "👨‍👦 Мой родитель")
async def my_parent_info(message: types.Message):
    """Информация о родителе"""
    parent_id = get_parent_info(message.from_user.id)
    
    if not parent_id:
        await message.answer(
            "❌ У вас нет подключенного родителя.\n\n"
            "Чтобы подключить родителя:\n"
            "1. Попросите родителя отправить вам его ID командой /myid\n"
            "2. Введите этот ID в чат",
            parse_mode="Markdown"
        )
        return
    
    try:
        chat = await bot.get_chat(parent_id)
        
        # Получаем статистику по заданиям
        tasks = get_child_tasks(message.from_user.id)
        completed = sum(1 for _, _, _, comp in tasks if comp)
        total = len(tasks)
        total_reward = sum(reward for _, _, reward, comp in tasks if comp)
        
        await message.answer(
            f"👨‍👦 *Мой родитель*\n\n"
            f"👤 Имя: {chat.first_name}\n"
            f"🆔 ID: `{parent_id}`\n\n"
            f"📊 *Статистика:*\n"
            f"• Заданий выполнено: {completed}/{total}\n"
            f"• Всего заработано: {total_reward:.2f} ₽\n\n"
            f"💡 *Совет:* Регулярно показывайте родителю свои цели "
            f"и просите задания для их достижения!",
            parse_mode="Markdown"
        )
    except:
        await message.answer("❌ Не удалось получить информацию о родителе")

# ================ ОБРАЗОВАТЕЛЬНЫЕ КУРСЫ ================
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
    # Проверяем, есть ли у ребенка родитель
    parent_id = get_parent_info(message.from_user.id)
    
    text = "🎯 *Финансовые цели*\n\n"
    
    if parent_id:
        text += "👨‍👦 У вас есть подключенный родитель!\n"
        text += "Родитель может одобрять ваши цели и давать задания.\n\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Новая цель", callback_data="new_goal")],
        [InlineKeyboardButton(text="📋 Мои цели", callback_data="my_goals")]
    ])
    
    await message.answer(text, parse_mode="Markdown", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "new_goal")
async def new_goal_start(callback: types.CallbackQuery, state: FSMContext):
    # Проверяем, есть ли родитель
    parent_id = get_parent_info(callback.from_user.id)
    
    await state.set_state(GoalStates.waiting_goal_name)
    
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )
    
    text = "🎯 *Создание новой цели*\n\nВведите название цели:\n\nПример: 'Новый телефон', 'Ноутбук', 'Путешествие'\n\n"
    
    if parent_id:
        text += "👨‍👦 Ваш родитель увидит эту цель и сможет ее одобрить!"
    
    await callback.message.answer(
        text,
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
        
        for i, (goal_id, name, target, saved, approved) in enumerate(goals, 1):
            progress = (saved / target * 100) if target > 0 else 0
            bars_count = int(progress / 5)
            bars = "█" * bars_count + "░" * (20 - bars_count)
            remaining = target - saved
            
            text += f"*{i}. {name}*\n"
            text += f"   Цель: {target:.2f} ₽\n"
            text += f"   Накоплено: {saved:.2f} ₽ ({progress:.1f}%)\n"
            text += f"   Осталось: {remaining:.2f} ₽\n"
            
            # Добавляем статус одобрения
            parent_id = get_parent_info(user_id)
            if parent_id:
                status = "✅ Одобрена родителем" if approved else "⏳ Ожидает одобрения"
                text += f"   Статус: {status}\n"
            
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
        
        # Проверяем, есть ли родитель
        parent_id = get_parent_info(message.from_user.id)
        
        # Сохраняем цель в БД
        add_goal(message.from_user.id, goal_name, target, parent_id)
        
        await state.clear()
        
        response_text = f"🎯 *Цель создана!*\n\n"
        response_text += f"📋 Название: {goal_name}\n"
        response_text += f"💰 Цель: {target:.2f} ₽\n"
        
        if parent_id:
            response_text += f"👨‍👦 *Родитель уведомлен!*\n"
            response_text += f"Ваш родитель может одобрить эту цель и давать задания.\n\n"
            
            # Уведомляем родителя
            try:
                await bot.send_message(
                    parent_id,
                    f"👶 *Новая цель у ребенка!*\n\n"
                    f"Ваш ребенок создал новую цель:\n"
                    f"📋 *{goal_name}*\n"
                    f"💰 *Сумма:* {target:.2f} ₽\n\n"
                    f"Одобрите цель в разделе:\n"
                    f"'👨‍👦 Родители' → '🎯 Цели детей'",
                    parse_mode="Markdown"
                )
            except:
                pass
        else:
            response_text += f"💪 Удачи в достижении цели!\n\n"
        
        response_text += f"Следи за прогрессом в разделе '🎯 Цели' → '📋 Мои цели'"
        
        await message.answer(
            response_text,
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
            [KeyboardButton(text="👨‍👦 От родителя"), KeyboardButton(text="⬅️ Назад")]  # НОВАЯ КНОПКА
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

@dp.message(lambda msg: msg.text in ["💰 Карманные", "🎯 Подработка", "🏆 Премия", "🎁 Подарок", "👨‍👦 От родителя",
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
        
        if category in ["💰 Карманные", "🎯 Подработка", "🏆 Премия", "🎁 Подарок", "👨‍👦 От родителя"]:
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
    
    # Добавляем информацию о родительском контроле
    parent_id = get_parent_info(user_id)
    if parent_id:
        tasks = get_child_tasks(user_id)
        completed_tasks = sum(1 for _, _, _, comp in tasks if comp)
        total_reward = sum(reward for _, _, reward, comp in tasks if comp)
        
        text += f"\n👨‍👦 *Родительский контроль:*\n"
        text += f"• Заданий выполнено: {completed_tasks}\n"
        text += f"• Заработано от родителей: {total_reward:.2f} ₽"
    
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
        "🏦 *Финансовая подушка:* Стремись иметь запас на 3-6 месяцев расходов",
        "👨‍👦 *Родители — первые финансисты:* Проси задания и учись зарабатывать!",
        "✅ *Выполняй задания вовремя:* Так ты заработаешь доверие и деньги",
        "💪 *Самодисциплина:* Начинай с малого, но будь последовательным"
    ]
    
    await message.answer(f"*💡 Финансовый совет:*\n\n{random.choice(advice_list)}", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "⬅️ Назад")
async def back_cmd(message: types.Message):
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]
    
    # Проверяем, в каком меню находимся
    if message.text == "⬅️ Назад":
        # Проверяем, родитель или ребенок
        parent_info = get_child_info(message.from_user.id)
        child_info = get_parent_info(message.from_user.id)
        
        if parent_info:
            # Возвращаемся в меню родителя
            await message.answer("👨‍👦 Меню родителя:", reply_markup=parent_kb)
        elif child_info:
            # Возвращаемся в меню ребенка
            await message.answer("👶 Меню ребенка:", reply_markup=child_kb)
        else:
            # Возвращаемся в главное меню
            await message.answer("Главное меню:", reply_markup=main_kb)

# ================ ЗАПУСК ================
async def main():
    print("=" * 60)
    print("🤖 ФИНАНСОВЫЙ ПОМОЩНИК С РОДИТЕЛЬСКИМ КОНТРОЛЕМ")
    print("📊 Проект для 10 класса - УЛУЧШЕННАЯ ВЕРСИЯ")
    print("=" * 60)
    print("✨ НОВАЯ ФУНКЦИЯ:")
    print("• 👨‍👦 Родительский контроль за целями")
    print("• ✅ Одобрение целей родителями")
    print("• 📋 Система заданий и вознаграждений")
    print("• 💰 Мотивация детей к достижению целей")
    print("=" * 60)
    print("🎓 ДОСТУПНЫЕ КУРСЫ:")
    print("• 📚 Финансы для начинающих")
    print("• 📈 Инвестиции для школьников")
    print("=" * 60)
    
    try:
        bot_info = await bot.get_me()
        print(f"✅ Бот запущен: @{bot_info.username}")
        print(f"📱 Ссылка: https://t.me/{bot_info.username}")
        print("=" * 60)
        print("👨‍👦 ДЛЯ ПОДКЛЮЧЕНИЯ РОДИТЕЛЕЙ И ДЕТЕЙ:")
        print("• Используйте команду /myid чтобы получить свой ID")
        print("• Обменяйтесь ID для подключения")
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

