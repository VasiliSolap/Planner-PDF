import os
import calendar
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, portrait, A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# --- ЦВЕТОВЫЕ ТЕМЫ ---
THEMES = {
    "Vanilla": {
        "bg": "#F9F6F0", "accent1": "#D5CABD", "accent2": "#E8E2D9",
        "text": "#5C544D", "tab_bg": "#5C544D", "tab_text": "#FFFFFF", "box_bg": "#FFFFFF"
    },
    "Matcha": {
        "bg": "#F4F7F4", "accent1": "#A3B19B", "accent2": "#C5D1BF",
        "text": "#4A5346", "tab_bg": "#4A5346", "tab_text": "#FFFFFF", "box_bg": "#FFFFFF"
    },
    "Midnight": {
        "bg": "#1C1C1E", "accent1": "#2C2C2E", "accent2": "#3A3A3C",
        "text": "#E5E5EA", "tab_bg": "#E5E5EA", "tab_text": "#1C1C1E", "box_bg": "#2C2C2E"
    },
    "Lavender": {
        "bg": "#F8F6FA", "accent1": "#C8B8D1", "accent2": "#E2D8E8",
        "text": "#4A3F54", "tab_bg": "#4A3F54", "tab_text": "#FFFFFF", "box_bg": "#FFFFFF"
    },
    "Coastal": {
        "bg": "#F0F4F8", "accent1": "#9FB3C8", "accent2": "#C4D4E3",
        "text": "#2B3A4A", "tab_bg": "#2B3A4A", "tab_text": "#FFFFFF", "box_bg": "#FFFFFF"
    }
}

# Инициализируем переменные заглушками (они перезапишутся перед стартом)
BG_COLOR = HexColor("#FFFFFF")
ACCENT_PINK = HexColor("#FFFFFF")
ACCENT_GREEN = HexColor("#FFFFFF")
DARK_BROWN = HexColor("#FFFFFF")
TAB_BG_ACTIVE = HexColor("#FFFFFF")
TAB_TEXT_ACTIVE = HexColor("#FFFFFF")
BOX_BG_COLOR = HexColor("#FFFFFF")

def apply_theme(theme_name):
    """Меняет глобальные переменные цветов перед генерацией."""
    global BG_COLOR, ACCENT_PINK, ACCENT_GREEN, DARK_BROWN, TAB_BG_ACTIVE, TAB_TEXT_ACTIVE, BOX_BG_COLOR
    t = THEMES[theme_name]
    BG_COLOR = HexColor(t["bg"])
    ACCENT_PINK = HexColor(t["accent1"])
    ACCENT_GREEN = HexColor(t["accent2"])
    DARK_BROWN = HexColor(t["text"])
    TAB_BG_ACTIVE = HexColor(t["tab_bg"])
    TAB_TEXT_ACTIVE = HexColor(t["tab_text"])
    BOX_BG_COLOR = HexColor(t["box_bg"])


# Настройки вкладок
TOP_TABS = ["HOME", "GUIDE", "YEAR", "BRAIN DUMP", "DONE LIST", "FOCUS LOG", "HABITS", "WEEKLY RESET", "MONEY", "WIN JAR", "VISION", "STICKERS"]
RIGHT_TABS = ["2028", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
PLANNER_NAME = "MindFlow"
YEAR = 2028

# --- РЕГИСТРАЦИЯ ШРИФТОВ ---
try:
    pdfmetrics.registerFont(TTFont('Montserrat', 'Montserrat-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Montserrat-Bold', 'Montserrat-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('Playfair-Bold', 'PlayfairDisplay-Bold.ttf'))
except Exception as e:
    print(f"Внимание: Шрифты не найдены ({e}). PDF сгенерируется с базовыми шрифтами.")

# --- БАЗОВЫЕ ЭЛЕМЕНТЫ ИНТЕРФЕЙСА ---

def draw_top_tabs(c, width, height, active_tab=""):
    from reportlab.lib.units import mm
    
    margin_x = 0 * mm  
    tab_height = 10 * mm
    margin_y = height - tab_height 
    
    icon_space = 45 * mm if width > 250 * mm else 38 * mm
    available_width = width - icon_space  
    tab_width = available_width / len(TOP_TABS)
    radius = 2 * mm

    font_size = 6 if width > 250 * mm else 5.5
    c.setFont("Montserrat-Bold", font_size)
    
    while max([c.stringWidth(t, "Montserrat-Bold", font_size) for t in TOP_TABS]) > (tab_width - 1.5 * mm):
        font_size -= 0.25
        c.setFont("Montserrat-Bold", font_size)
        if font_size <= 2:  
            break
    
    for i, tab in enumerate(TOP_TABS):
        x = margin_x + (i * tab_width)
        y = margin_y
        
        if tab == active_tab:
            c.setFillColor(TAB_BG_ACTIVE)
            draw_folder_tab_bg(c, x, y, tab_width - 1.5, tab_height, radius, is_top_tab=True)
            c.setFillColor(TAB_TEXT_ACTIVE)
        else:
            bg_color = ACCENT_PINK if i % 2 == 0 else ACCENT_GREEN
            c.setFillColor(bg_color)
            draw_folder_tab_bg(c, x, y, tab_width - 1.5, tab_height, radius, is_top_tab=True)
            c.setFillColor(DARK_BROWN)
        
        text_width = c.stringWidth(tab, "Montserrat-Bold", font_size)
        c.drawString(x + (tab_width - 1.5 - text_width) / 2, y + 3.5 * mm, tab)
        
        # Умный редирект: вкладки с трекерами ведут на первый месяц
        target = tab
        if tab == "HABITS": target = f"HABITS_{RIGHT_TABS[1]}"
        elif tab == "MONEY": target = f"MONEY_{RIGHT_TABS[1]}"
        
        c.linkAbsolute(tab, target, (x, y, x + tab_width - 1.5, y + tab_height))

def draw_right_tabs(c, width, height, active_month="", active_top=""):
    tab_width = 10 * mm
    x = width - tab_width  
    
    tab_height = (height - 25 * mm) / len(RIGHT_TABS)
    radius = 2 * mm
    
    c.setFont("Montserrat-Bold", 6)
    
    for i, tab in enumerate(RIGHT_TABS):
        y = height - 25 * mm - (i + 1) * tab_height
        
        if tab == active_month:
            c.setFillColor(TAB_BG_ACTIVE)
            draw_folder_tab_bg(c, x, y, tab_width, tab_height - 1.5, radius, is_top_tab=False)
            c.setFillColor(TAB_TEXT_ACTIVE)
        else:
            c.setFillColor(ACCENT_PINK)
            draw_folder_tab_bg(c, x, y, tab_width, tab_height - 1.5, radius, is_top_tab=False)
            c.setFillColor(DARK_BROWN)
            
        c.saveState()
        c.translate(x + 5 * mm, y + (tab_height - 1.5) / 2)
        c.rotate(-90)
        text_width = c.stringWidth(tab, "Montserrat-Bold", 6)
        c.drawString(-text_width / 2, -2, tab)
        c.restoreState()
        
        # --- УМНАЯ НАВИГАЦИЯ ---
        if tab == "2028":
            target = "YEAR"
        elif active_top == "HABITS":
            target = f"HABITS_{tab}"  # Переход сразу на привычки этого месяца
        elif active_top == "MONEY":
            target = f"MONEY_{tab}"   # Переход сразу на финансы этого месяца
        else:
            target = f"MONTH_{tab}"   # Обычный переход на календарь
            
        c.linkAbsolute(tab, target, (x, y, x + tab_width, y + tab_height - 1.5))


def draw_utility_icons(c, width, height):
    """Отрисовка безопасных векторных иконок для внешних ссылок (без использования PNG)."""
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    
    is_landscape = width > 250 * mm
    icon_size = 5.5 * mm if is_landscape else 4.5 * mm 
    spacing = 8.5 * mm if is_landscape else 7 * mm
    
    total_icons_width = 4 * spacing
    start_x = width - total_icons_width - 3 * mm 
    y = height - 7.5 * mm if is_landscape else height - 6.5 * mm 
    
    # 1. web_cal - Сетка (Google Calendar)
    # 2. app_cal - День (Apple Calendar)
    # 3. mail - Конверт (Почта)
    # 4. tasks - Галочка (Напоминания)
    icons = [
        ("web_cal", "https://calendar.google.com/"), 
        ("app_cal", "calshow://"),                     
        ("mail", "mailto:"),                       
        ("tasks", "x-apple-reminder://")             
    ]
    
    DARK_BROWN = HexColor("#433D34")
    
    for i, (icon_type, url) in enumerate(icons):
        cx = start_x + i * spacing
        cy = y
        s = icon_size
        
        c.setStrokeColor(DARK_BROWN)
        c.setLineWidth(1)
        
        if icon_type == "web_cal":
            # Иконка: Календарь-сетка
            c.roundRect(cx, cy, s, s, 1 * mm, fill=0, stroke=1)
            c.line(cx, cy + s * 0.7, cx + s, cy + s * 0.7) # Верхняя плашка
            c.setLineWidth(0.5)
            c.line(cx, cy + s * 0.35, cx + s, cy + s * 0.35) # Горизонталь
            c.line(cx + s * 0.33, cy, cx + s * 0.33, cy + s * 0.7) # Вертикаль 1
            c.line(cx + s * 0.66, cy, cx + s * 0.66, cy + s * 0.7) # Вертикаль 2
            
        elif icon_type == "app_cal":
            # Иконка: Календарь-день (с точкой/фокусом)
            c.setLineWidth(1)
            c.roundRect(cx, cy, s, s, 1 * mm, fill=0, stroke=1)
            c.line(cx, cy + s * 0.7, cx + s, cy + s * 0.7)
            c.setFillColor(DARK_BROWN)
            c.circle(cx + s / 2, cy + s * 0.35, s * 0.15, fill=1, stroke=0)
            
        elif icon_type == "mail":
            # Иконка: Конверт
            h_env = s * 0.7
            y_env = cy + s * 0.15
            c.setLineWidth(1)
            c.roundRect(cx, y_env, s, h_env, 0.5 * mm, fill=0, stroke=1)
            p = c.beginPath()
            p.moveTo(cx, y_env + h_env)
            p.lineTo(cx + s / 2, y_env + h_env * 0.4)
            p.lineTo(cx + s, y_env + h_env)
            c.drawPath(p, fill=0, stroke=1)
            
        elif icon_type == "tasks":
            # Иконка: Круглая галочка
            c.setLineWidth(1)
            c.circle(cx + s / 2, cy + s / 2, s / 2, fill=0, stroke=1)
            p = c.beginPath()
            p.moveTo(cx + s * 0.25, cy + s * 0.5)
            p.lineTo(cx + s * 0.45, cy + s * 0.3)
            p.lineTo(cx + s * 0.75, cy + s * 0.7)
            c.drawPath(p, fill=0, stroke=1)
        
        # Невидимая кликабельная область
        rect = (cx, cy, cx + s, cy + s)
        c.linkURL(url, rect, thickness=0, relative=0)

def draw_folder_tab_bg(c, x, y, w, h, radius, is_top_tab=True):
    """Отрисовка формы реалистичной вкладки-папки."""
    c.setStrokeColor(HexColor("#D8D0C5")) # Легкая граница для объема
    c.setLineWidth(0.5)
    p = c.beginPath()
    
    if is_top_tab:
        p.moveTo(x, y) 
        p.lineTo(x, y + h - radius) 
        p.arcTo(x, y + h - 2*radius, x + 2*radius, y + h, 180, -90) 
        p.lineTo(x + w - radius, y + h) 
        p.arcTo(x + w - 2*radius, y + h - 2*radius, x + w, y + h, 90, -90) 
        p.lineTo(x + w, y) 
        p.close()
    else:
        p.moveTo(x, y) 
        p.lineTo(x + w - radius, y) 
        p.arcTo(x + w - 2*radius, y, x + w, y + 2*radius, 270, 90) 
        p.lineTo(x + w, y + h - radius) 
        p.arcTo(x + w - 2*radius, y + h - 2*radius, x + w, y + h, 0, 90) 
        p.lineTo(x, y + h) 
        p.close()
        
    c.drawPath(p, fill=1, stroke=1)

def draw_base_page(c, width, height, active_top="", active_right="", page_name=""):
    if page_name:
        c.bookmarkPage(page_name)
    c.setFillColor(BG_COLOR)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    draw_top_tabs(c, width, height, active_tab=active_top)
    
    # Передаем active_top, чтобы боковые вкладки понимали, где мы находимся
    draw_right_tabs(c, width, height, active_month=active_right, active_top=active_top)
    
    draw_utility_icons(c, width, height)


# --- СТРАНИЦЫ ---
def create_cover(c, width, height, bg_col, accent_col, text_col):
    c.setFillColor(accent_col)
    c.rect(0, 0, width * 0.35, height, fill=1, stroke=0)
    c.setFillColor(bg_col)
    c.rect(width * 0.35, 0, width * 0.65, height, fill=1, stroke=0)
    
    center_x = width * 0.35 + (width * 0.65) / 2
    c.setFillColor(text_col)
    
    c.setFont("Montserrat-Bold", 10)
    c.drawCentredString(center_x, height - 60 * mm, "A LOW-OVERWHELM PLANNER")
    
    # Используем глобальную переменную для названия
    c.setFont("Playfair-Bold", 48)
    c.drawCentredString(center_x, height - 80 * mm, PLANNER_NAME)
    
    c.setFont("Montserrat", 12)
    c.drawCentredString(center_x, height - 95 * mm, "Built for brains that don't do rigid schedules. Year, month,")
    c.drawCentredString(center_x, height - 102 * mm, "week and day all link together — so you're never stuck")
    c.drawCentredString(center_x, height - 109 * mm, "flipping pages to find where you are.")
    
    c.setFont("Montserrat-Bold", 14)
    c.drawCentredString(center_x, height - 130 * mm, str(YEAR))
    c.setFont("Montserrat-Bold", 8)
    c.drawCentredString(center_x, height - 138 * mm, "GOODNOTES / NOTABILITY TEMPLATE")
    
    btn_w = 80 * mm if width < 250 * mm else 120 * mm
    btn_h = 12 * mm
    btn_x = center_x - (btn_w / 2)
    btn_y = height - 160 * mm
    
    # Умная кнопка: если фон темный, кнопка белая, и наоборот
    if text_col == HexColor("#FFFFFF"):
        c.setFillColor(HexColor("#FFFFFF"))
        c.roundRect(btn_x, btn_y, btn_w, btn_h, 4, fill=1, stroke=0)
        c.setFillColor(DARK_BROWN)
    else:
        c.setFillColor(DARK_BROWN)
        c.roundRect(btn_x, btn_y, btn_w, btn_h, 4, fill=1, stroke=0)
        c.setFillColor(HexColor("#FFFFFF"))
        
    c.setFont("Montserrat-Bold", 10)
    c.drawCentredString(center_x, btn_y + 4 * mm, "Enter Planner →")
    c.linkAbsolute("HOME", "HOME", (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h))
    c.showPage()

def create_home_page(c, width, height, is_landscape):
    draw_base_page(c, width, height, active_top="HOME", page_name="HOME")
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    
    # Заголовок страницы
    c.setFillColor(DARK_BROWN)
    title_str = f"WELCOME TO {PLANNER_NAME.upper()}"
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, title_str)
    
    title_w = c.stringWidth(title_str, "Playfair-Bold", 24)
    c.setFont("Montserrat", 10)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(margin_x + title_w + 5 * mm, content_y + 2 * mm, "| Your low-overwhelm life dashboard")
    
    content_y -= 10 * mm
    bottom_margin = 15 * mm
    available_h = content_y - bottom_margin
    gap = 5 * mm
    
    import datetime
    start_date = datetime.date(YEAR, 1, 1)
    iso_y, iso_w, _ = start_date.isocalendar()
    
    link_year = "YEAR"
    link_month = f"MONTH_{RIGHT_TABS[1]}"
    link_week = f"WEEK_{iso_y}_{iso_w}"   
    link_day = f"DAY_{start_date.strftime('%Y-%m-%d')}" 
    
    core_items = [
        ("YEAR OVERVIEW", "All 12 months at a glance", link_year),
        ("MONTHLY PLAN", "High-level goals and dates", link_month),
        ("WEEKLY PLAN", "Your 7-day focus area", link_week),
        ("DAILY PAGES", "Time blocks & priorities", link_day)
    ]
    
    # ИСПРАВЛЕННЫЕ ССЫЛКИ ДЛЯ HABITS И MONEY
    extra_items = [
        ("BRAIN DUMP", "Clear your mind", "BRAIN DUMP"),
        ("DONE LIST", "Celebrate your wins", "DONE LIST"),
        ("FOCUS LOG", "Deep work tracking", "FOCUS LOG"),
        ("HABITS", "Gentle consistency", f"HABITS_{RIGHT_TABS[1]}"),
        ("WEEKLY RESET", "Prepare for success", "WEEKLY RESET"),
        ("MONEY", "Finances without guilt", f"MONEY_{RIGHT_TABS[1]}"),
        ("WIN JAR", "Collect good moments", "WIN JAR"),
        ("VISION", "Your big picture", "VISION"),
        ("STICKERS", "Copy & paste elements", "STICKERS")
    ]
    
    def draw_card(cx, cy, cw, ch, title, desc, target):
        c.setFillColor(BOX_BG_COLOR)
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.roundRect(cx, cy, cw, ch, 3 * mm, fill=1, stroke=1)
        
        padding = 7 * mm
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat-Bold", 10.5)
        c.drawString(cx + padding, cy + ch - padding - 2 * mm, title)
        
        c.setStrokeColor(HexColor("#E07A5F")) 
        c.setLineWidth(1.5)
        c.setLineCap(1)
        c.line(cx + padding, cy + ch - padding - 6 * mm, cx + padding + 12 * mm, cy + ch - padding - 6 * mm)
        
        c.setFont("Montserrat", 8.5)
        c.setFillColor(HexColor("#8C8377"))
        c.drawString(cx + padding, cy + ch - padding - 13 * mm, desc)
        
        btn_r = 4.5 * mm
        btn_cx = cx + cw - padding - btn_r/2 + 2 * mm
        btn_cy = cy + padding + btn_r/2 - 2 * mm
        
        c.setFillColor(DARK_BROWN)
        c.circle(btn_cx, btn_cy, btn_r, fill=1, stroke=0)
        
        c.setStrokeColor(HexColor("#FFFFFF"))
        c.setLineWidth(1.2)
        c.setLineJoin(1)
        
        p = c.beginPath()
        p.moveTo(btn_cx - 1.5 * mm, btn_cy)
        p.lineTo(btn_cx + 1.5 * mm, btn_cy)
        p.moveTo(btn_cx, btn_cy + 1.5 * mm)
        p.lineTo(btn_cx + 1.5 * mm, btn_cy)
        p.lineTo(btn_cx, btn_cy - 1.5 * mm)
        c.drawPath(p, fill=0, stroke=1)
        
        c.linkAbsolute(target, target, (cx, cy, cx + cw, cy + ch))

    if is_landscape:
        core_w = main_area_w * 0.35
        extras_w = main_area_w - core_w - gap
        
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat-Bold", 10)
        c.drawString(margin_x, content_y - 5 * mm, "CORE SYSTEM")
        
        core_h = (available_h - 10 * mm - 3 * gap) / 4
        for i, (title, desc, target) in enumerate(core_items):
            cy = bottom_margin + (3 - i) * (core_h + gap)
            draw_card(margin_x, cy, core_w, core_h, title, desc, target)
            
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat-Bold", 10)
        c.drawString(margin_x + core_w + gap, content_y - 5 * mm, "LIFESTYLE & EXTRAS")
        
        ext_col_w = (extras_w - 2 * gap) / 3
        ext_h = (available_h - 10 * mm - 2 * gap) / 3
        
        for i, (title, desc, target) in enumerate(extra_items):
            col = i % 3
            row = i // 3
            cx = margin_x + core_w + gap + col * (ext_col_w + gap)
            cy = bottom_margin + (2 - row) * (ext_h + gap)
            draw_card(cx, cy, ext_col_w, ext_h, title, desc, target)
            
    else:
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat-Bold", 10)
        c.drawString(margin_x, content_y - 5 * mm, "CORE SYSTEM")
        
        core_area_h = (available_h - 15 * mm) * 0.35
        core_w = (main_area_w - gap) / 2
        core_h = (core_area_h - gap) / 2
        
        core_start_y = content_y - 10 * mm - core_area_h
        
        for i, (title, desc, target) in enumerate(core_items):
            col = i % 2
            row = i // 2
            cx = margin_x + col * (core_w + gap)
            cy = core_start_y + (1 - row) * (core_h + gap)
            draw_card(cx, cy, core_w, core_h, title, desc, target)
            
        extras_start_y = core_start_y - 5 * mm
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat-Bold", 10)
        c.drawString(margin_x, extras_start_y, "LIFESTYLE & EXTRAS")
        
        ext_area_h = extras_start_y - bottom_margin - 5 * mm
        ext_col_w = (main_area_w - 2 * gap) / 3
        ext_h = (ext_area_h - 2 * gap) / 3
        
        for i, (title, desc, target) in enumerate(extra_items):
            col = i % 3
            row = i // 3
            cx = margin_x + col * (ext_col_w + gap)
            cy = bottom_margin + (2 - row) * (ext_h + gap)
            draw_card(cx, cy, ext_col_w, ext_h, title, desc, target)

    c.showPage()


def draw_home_block(c, bx, by, block_w, block_h, title, desc, num):
    c.setFillColor(HexColor("#FFFFFF"))
    c.roundRect(bx, by, block_w, block_h, 4, fill=1, stroke=1)
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 10)
    c.drawString(bx + 5 * mm, by + 12 * mm, title)
    c.setFont("Montserrat", 8)
    c.drawString(bx + 5 * mm, by + 5 * mm, desc)
    c.circle(bx + 9 * mm, by + 19 * mm, 3 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFFFF"))
    c.drawString(bx + 8 * mm, by + 18 * mm, num)
    c.linkAbsolute(f"Link_{title}", title.upper(), (bx, by, bx + block_w, by + block_h))

def create_year_page(c, width, height, is_landscape, sunday_start=False):
    draw_base_page(c, width, height, active_top="YEAR", active_right="2028", page_name="YEAR")
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 35 * mm
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, str(YEAR))
    
    cols = 4 if is_landscape else 3
    rows = 3 if is_landscape else 4
    
    col_w = main_area_w / cols
    row_h = (content_y - 15 * mm) / rows
    
    # --- ЛОГИКА НАЧАЛА НЕДЕЛИ ---
    if sunday_start:
        calendar.setfirstweekday(6) # 6 = Воскресенье
        days = ["Wk", "S", "M", "T", "W", "T", "F", "S"]
    else:
        calendar.setfirstweekday(0) # 0 = Понедельник
        days = ["Wk", "M", "T", "W", "T", "F", "S", "S"]
    
    month_num = 1
    
    for r in range(rows):
        for col in range(cols):
            if month_num > 12: break
            
            x = margin_x + col * col_w
            y = content_y - 15 * mm - r * row_h
            
            c.setFillColor(DARK_BROWN)
            c.setFont("Montserrat-Bold", 10)
            month_label = calendar.month_name[month_num].upper()
            c.drawString(x, y, month_label)
            c.linkAbsolute(f"link_M_{month_num}", f"MONTH_{RIGHT_TABS[month_num]}", (x, y - 2*mm, x + 30*mm, y + 10*mm))
            
            cell_w = (col_w - 10*mm) / 8
            c.setFont("Montserrat-Bold", 6)
            for i, d in enumerate(days):
                c.drawString(x + i * cell_w, y - 6 * mm, d)
                
            month_matrix = calendar.monthcalendar(YEAR, month_num)
            c.setFont("Montserrat", 6)
            
            for week_idx, week in enumerate(month_matrix):
                week_y = y - 11 * mm - week_idx * 4.5 * mm
                
                sample_day = next((d for d in week if d != 0), 1)
                import datetime
                iso_year, iso_week, _ = datetime.date(YEAR, month_num, sample_day).isocalendar()
                
                c.setFillColor(HexColor("#A89F91")) 
                c.drawString(x, week_y, str(iso_week))
                c.linkAbsolute(f"link_W_{iso_week}", f"WEEK_{iso_year}_{iso_week}", (x, week_y - 1*mm, x + cell_w, week_y + 3*mm))

                c.setFillColor(DARK_BROWN)
                for day_idx, day_num in enumerate(week):
                    if day_num != 0:
                        day_x = x + (day_idx + 1) * cell_w
                        c.drawString(day_x, week_y, str(day_num))
                        target_day = f"DAY_{YEAR}-{month_num:02d}-{day_num:02d}"
                        c.linkAbsolute(target_day, target_day, (day_x - 1*mm, week_y - 1*mm, day_x + cell_w - 1*mm, week_y + 3*mm))
                        
            month_num += 1
            
    c.showPage()


def create_month_page(c, width, height, is_landscape, month_num, sunday_start=False):
    import datetime
    month_name = RIGHT_TABS[month_num] 
    draw_base_page(c, width, height, active_right=month_name, page_name=f"MONTH_{month_name}")
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    grid_y_start = height - 38 * mm
    bottom_margin = 15 * mm
    gap = 4 * mm
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Playfair-Bold", 24)
    full_month_name = calendar.month_name[month_num]
    c.drawString(margin_x, grid_y_start + 8 * mm, f"{full_month_name} {YEAR}".upper())
    
    # --- ЛОГИКА НАЧАЛА НЕДЕЛИ ---
    if sunday_start:
        calendar.setfirstweekday(6)
        days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    else:
        calendar.setfirstweekday(0) 
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        
    month_matrix = calendar.monthcalendar(YEAR, month_num)
    rows = len(month_matrix)
    tracker_btn_h = 10 * mm 
    
    if is_landscape:
        notes_w = 65 * mm
        calendar_w = main_area_w - notes_w - gap
        notes_x = margin_x + calendar_w + gap
        notes_y = bottom_margin + tracker_btn_h + gap 
        notes_h = grid_y_start - notes_y
        grid_bottom = bottom_margin
    else:
        notes_h = 40 * mm 
        calendar_w = main_area_w
        notes_x = margin_x
        notes_y = bottom_margin + tracker_btn_h + gap
        grid_bottom = notes_y + notes_h + gap
        
    grid_h = grid_y_start - grid_bottom
    row_height = grid_h / rows
    
    week_col_w = 8 * mm
    day_col_w = (calendar_w - week_col_w) / 7
    
    c.setFillColor(BOX_BG_COLOR)
    c.setStrokeColor(HexColor("#D8D0C5"))
    notes_actual_w = notes_w if is_landscape else main_area_w
    c.roundRect(notes_x, notes_y, notes_actual_w, notes_h, 2 * mm, fill=1, stroke=1)
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 9)
    c.drawString(notes_x + 5 * mm, notes_y + notes_h - 7 * mm, "MONTHLY GOALS & NOTES")
    
    c.setLineWidth(0.5)
    line_y = notes_y + notes_h - 14 * mm
    while line_y > notes_y + 4 * mm:
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.circle(notes_x + 7 * mm, line_y + 1 * mm, 1.5 * mm, fill=0, stroke=1)
        c.setStrokeColor(HexColor("#EAE5DE"))
        c.line(notes_x + 12 * mm, line_y, notes_x + notes_actual_w - 5 * mm, line_y)
        line_y -= 7 * mm

    btn_w = (notes_actual_w - gap) / 2
    btn_y = notes_y - gap - tracker_btn_h
    
    c.setFillColor(ACCENT_GREEN)
    c.roundRect(notes_x, btn_y, btn_w, tracker_btn_h, 2 * mm, fill=1, stroke=0)
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 7.5)
    c.drawCentredString(notes_x + btn_w / 2, btn_y + 4 * mm, "HABITS →")
    c.linkAbsolute(f"HABITS_{month_name}", f"HABITS_{month_name}", (notes_x, btn_y, notes_x + btn_w, btn_y + tracker_btn_h))
    
    c.setFillColor(ACCENT_PINK)
    c.roundRect(notes_x + btn_w + gap, btn_y, btn_w, tracker_btn_h, 2 * mm, fill=1, stroke=0)
    c.setFillColor(DARK_BROWN)
    c.drawCentredString(notes_x + btn_w + gap + btn_w / 2, btn_y + 4 * mm, "FINANCE →")
    c.linkAbsolute(f"MONEY_{month_name}", f"MONEY_{month_name}", (notes_x + btn_w + gap, btn_y, notes_x + btn_w * 2 + gap, btn_y + tracker_btn_h))

    c.setFont("Montserrat-Bold", 7)
    c.setFillColor(HexColor("#A89F91"))
    for i, day in enumerate(days):
        x = margin_x + week_col_w + i * day_col_w
        c.drawCentredString(x + day_col_w / 2, grid_y_start + 2 * mm, day)
    
    cell_gap = 1.5 * mm  
    cell_radius = 1.5 * mm
    for row_idx, week in enumerate(month_matrix):
        y = grid_y_start - (row_idx + 1) * row_height
        
        sample_day = next((d for d in week if d != 0), 1)
        iso_year, iso_week, _ = datetime.date(YEAR, month_num, sample_day).isocalendar()
        week_target = f"WEEK_{iso_year}_{iso_week}"
        
        c.setFillColor(ACCENT_PINK)
        c.roundRect(margin_x, y + cell_gap/2, week_col_w - cell_gap, row_height - cell_gap, cell_radius, fill=1, stroke=0)
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat-Bold", 6)
        
        c.saveState()
        c.translate(margin_x + (week_col_w - cell_gap)/2, y + row_height/2)
        c.rotate(90)
        c.drawCentredString(0, -1.8 * mm, f"W{iso_week}")
        c.restoreState()
        
        c.linkAbsolute(week_target, week_target, (margin_x, y, margin_x + week_col_w, y + row_height))
        
        c.setFont("Montserrat", 9)
        for col_idx, day_num in enumerate(week):
            x = margin_x + week_col_w + col_idx * day_col_w
            c.setStrokeColor(HexColor("#D8D0C5"))
            c.setFillColor(BG_COLOR)
            c.roundRect(x + cell_gap/2, y + cell_gap/2, day_col_w - cell_gap, row_height - cell_gap, cell_radius, fill=1, stroke=1)
            
            if day_num != 0:
                c.setFillColor(DARK_BROWN)
                c.drawString(x + cell_gap + 2 * mm, y + row_height - cell_gap - 4 * mm, str(day_num))
                target_day_name = f"DAY_{YEAR}-{month_num:02d}-{day_num:02d}"
                c.linkAbsolute(target_day_name, target_day_name, (x + cell_gap, y + row_height - cell_gap - 8 * mm, x + cell_gap + 10 * mm, y + row_height - cell_gap))
                
    c.showPage()

def create_weekly_page(c, width, height, is_landscape, iso_year, week_num, sunday_start=False):
    import datetime
    
    # --- ЛОГИКА НАЧАЛА НЕДЕЛИ ---
    first_day_of_week = datetime.date.fromisocalendar(iso_year, week_num, 1)
    if sunday_start:
        first_day_of_week -= datetime.timedelta(days=1)
        
    last_day_of_week = first_day_of_week + datetime.timedelta(days=6)
    
    active_month = RIGHT_TABS[first_day_of_week.month]
    
    page_name = f"WEEK_{iso_year}_{week_num}"
    draw_base_page(c, width, height, active_right=active_month, page_name=page_name)
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    
    c.setFillColor(DARK_BROWN)
    week_str = f"WEEK {week_num}"
    c.setFont("Playfair-Bold", 19)
    c.drawString(margin_x, content_y, week_str)
    
    week_w = c.stringWidth(week_str, "Playfair-Bold", 19)
    
    if first_day_of_week.month == last_day_of_week.month:
        date_range = f"{first_day_of_week.strftime('%B')} {first_day_of_week.day} - {last_day_of_week.day}, {first_day_of_week.year}".upper()
    else:
        date_range = f"{first_day_of_week.strftime('%b %d')} - {last_day_of_week.strftime('%b %d, %Y')}".upper()
        
    c.setFont("Montserrat-Bold", 9)
    c.setFillColor(HexColor("#A89F91")) 
    c.drawString(margin_x + week_w + 5 * mm, content_y + 1.5 * mm, f"|   {date_range}")
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 7)
    c.drawString(margin_x, content_y + 8 * mm, f"← BACK TO {active_month}")
    c.linkAbsolute(f"MONTH_{active_month}", f"MONTH_{active_month}", (margin_x, content_y + 6 * mm, margin_x + 30 * mm, content_y + 12 * mm))
    
    content_y -= 10 * mm
    bottom_margin = 15 * mm
    available_h = content_y - bottom_margin
    gap = 5 * mm
    
    cols, rows = (4, 2) if is_landscape else (2, 4)
        
    box_w = (main_area_w - gap * (cols - 1)) / cols
    box_h = (available_h - gap * (rows - 1)) / rows
    
    for i in range(8):
        col = i % cols
        row = i // cols
        
        bx = margin_x + col * (box_w + gap)
        by = content_y - (row + 1) * box_h - row * gap
        
        if i < 7:
            current_day = first_day_of_week + datetime.timedelta(days=i)
            day_label = current_day.strftime("%A").upper()
            date_label = current_day.strftime("%d %b")
            
            c.setFillColor(BOX_BG_COLOR)
            c.setStrokeColor(HexColor("#D8D0C5"))
            c.roundRect(bx, by, box_w, box_h, 2 * mm, fill=1, stroke=1)
            
            c.setFillColor(DARK_BROWN)
            c.setFont("Montserrat-Bold", 9)
            c.drawString(bx + 5 * mm, by + box_h - 7 * mm, day_label)
            
            c.setFont("Montserrat", 8)
            date_w = c.stringWidth(date_label, "Montserrat", 8)
            c.drawString(bx + box_w - 5 * mm - date_w, by + box_h - 7 * mm, date_label)
            
            line_spacing = 7 * mm
            line_y = by + box_h - 14 * mm
            c.setLineWidth(0.5)
            c.setStrokeColor(HexColor("#EAE5DE"))
            while line_y > by + 2 * mm:
                c.line(bx + 5 * mm, line_y, bx + box_w - 5 * mm, line_y)
                line_y -= line_spacing
            
            if current_day.year == YEAR:
                target_day = f"DAY_{current_day.strftime('%Y-%m-%d')}"
                # Ссылка спрятана строго внутри условия!
                c.linkAbsolute(target_day, target_day, (bx + box_w - 20 * mm, by + box_h - 10 * mm, bx + box_w, by + box_h))

                       
        else:
            c.setFillColor(BOX_BG_COLOR)
            c.setStrokeColor(HexColor("#D8D0C5"))
            c.roundRect(bx, by, box_w, box_h, 2 * mm, fill=1, stroke=1)
            
            focus_h = box_h * 0.55
            c.setFillColor(DARK_BROWN)
            c.setFont("Montserrat-Bold", 9)
            c.drawString(bx + 5 * mm, by + box_h - 7 * mm, "WEEKLY FOCUS")
            
            c.setLineWidth(0.5)
            c.setStrokeColor(HexColor("#EAE5DE"))
            line_y = by + box_h - 14 * mm
            while line_y > by + box_h - focus_h + 2 * mm:
                c.line(bx + 5 * mm, line_y, bx + box_w - 5 * mm, line_y)
                line_y -= 7 * mm
                
            habits_y = by + box_h - focus_h
            c.setFillColor(DARK_BROWN)
            c.setFont("Montserrat-Bold", 9)
            c.drawString(bx + 5 * mm, habits_y - 5 * mm, "WEEKLY HABITS")
            
            habit_lines = 3
            h_spacing = (habits_y - 12 * mm - by) / habit_lines
            
            left_margin = bx + 5 * mm
            right_margin = bx + box_w - 5 * mm
            total_w = right_margin - left_margin
            
            line_w = total_w * 0.40
            circles_area_w = total_w * 0.60
            circles_start_x = right_margin - circles_area_w
            
            circle_radius = min(1.8 * mm, circles_area_w / 25)
            days_gap = (circles_area_w - (7 * circle_radius * 2)) / 6
                
            for h_idx in range(habit_lines):
                hy = by + 4 * mm + h_idx * h_spacing
                
                c.setLineWidth(0.5)
                c.setStrokeColor(HexColor("#EAE5DE"))
                c.line(left_margin, hy, left_margin + line_w - 2 * mm, hy)
                
                c.setLineWidth(0.5)
                c.setStrokeColor(HexColor("#D8D0C5"))
                for d_idx in range(7):
                    cx = circles_start_x + d_idx * (circle_radius * 2 + days_gap) + circle_radius
                    c.setFillColor(HexColor("#FFFFFF"))
                    c.circle(cx, hy + 1 * mm, circle_radius, fill=1, stroke=1)
            
            top_row_y = by + 4 * mm + (habit_lines - 1) * h_spacing 
            letters_y = top_row_y + circle_radius + 3 * mm          
            
            c.setFont("Montserrat-Bold", 5)
            c.setFillColor(HexColor("#A89F91"))
            
            # --- БУКВЫ ДНЕЙ НЕДЕЛИ ---
            if sunday_start: day_letters = ["S", "M", "T", "W", "T", "F", "S"]
            else: day_letters = ["M", "T", "W", "T", "F", "S", "S"]
                
            for d_idx, day_char in enumerate(day_letters):
                cx = circles_start_x + d_idx * (circle_radius * 2 + days_gap) + circle_radius
                c.drawCentredString(cx, letters_y, day_char)

    c.showPage()


def create_placeholder_page(c, width, height, name):
    draw_base_page(c, width, height, active_top=name if name in TOP_TABS else "", page_name=name)
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 20)
    c.drawCentredString(width / 2, height / 2, f"{name} PAGE DESTINATION")
    c.showPage()

def draw_box_with_lines(c, x, y, w, h, title, lines):
    """Вспомогательная функция для отрисовки блоков с линиями для записей."""
    c.setFillColor(HexColor("#FFFFFF"))
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 9)
    c.drawString(x + 5 * mm, y + h - 7 * mm, title)
    
    line_spacing = (h - 12 * mm) / lines
    c.setLineWidth(0.5)
    c.setStrokeColor(HexColor("#EAE5DE"))
    for i in range(lines):
        line_y = y + h - 12 * mm - i * line_spacing
        c.line(x + 5 * mm, line_y, x + w - 5 * mm, line_y)

def draw_box_with_lines(c, x, y, w, h, title):
    """Отрисовка блоков с фиксированным одинаковым расстоянием между линиями."""
    c.setFillColor(BOX_BG_COLOR) 
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 9)
    c.drawString(x + 5 * mm, y + h - 7 * mm, title)
    
    c.setLineWidth(0.5)
    c.setStrokeColor(HexColor("#EAE5DE"))
    
    # Фиксированное расстояние между линиями для всех блоков (7 мм)
    line_spacing = 7 * mm 
    
    # Первая линия начинается под заголовком
    current_y = y + h - 12.5 * mm 
    
    # Рисуем линии, пока не достигнем нижнего края рамки (оставляя отступ 2 мм)
    while current_y > y + 2 * mm:
        c.line(x + 5 * mm, current_y, x + w - 5 * mm, current_y)
        current_y -= line_spacing

def draw_water_tracker(c, x, y, w, h):
    """Отрисовка трекера воды без рамки."""
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 8)
    c.drawString(x, y + h / 2 - 1 * mm, "WATER")
    
    start_x = x + 15 * mm
    for i in range(8):
        cx = start_x + i * 6 * mm
        cy = y + h / 2 + 1 * mm
        c.setStrokeColor(ACCENT_GREEN) 
        c.setFillColor(BOX_BG_COLOR) # Кружочки залиты цветом ячеек
        c.circle(cx, cy, 2 * mm, fill=1, stroke=1)

def draw_mood_tracker(c, x, y, w, h):
    """Отрисовка трекера настроения без рамки."""
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 8)
    c.drawString(x, y + h / 2 - 1 * mm, "MOOD")
    
    start_x = x + 15 * mm
    for i in range(5):
        cx = start_x + i * 8 * mm
        cy = y + h / 2 + 1 * mm
        c.setStrokeColor(ACCENT_PINK)
        c.setFillColor(BOX_BG_COLOR)
        c.circle(cx, cy, 2.5 * mm, fill=1, stroke=1)

def draw_time_blocks_box(c, x, y, w, h, title="TIME BLOCKS"):
    """Блок расписания с американской шкалой 6 AM - 10 PM."""
    c.setFillColor(BOX_BG_COLOR)
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 9)
    c.drawString(x + 5 * mm, y + h - 7 * mm, title)
    
    hours = ["6 AM", "7 AM", "8 AM", "9 AM", "10 AM", "11 AM", "12 PM",
             "1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM", "7 PM", "8 PM", "9 PM", "10 PM"]
    
    available_h = h - 14 * mm
    line_spacing = available_h / len(hours)
    
    c.setLineWidth(0.5)
    for i, hour_str in enumerate(hours):
        line_y = y + h - 12 * mm - (i + 1) * line_spacing
        
        # Время
        c.setFont("Montserrat-Bold", 6.5)
        c.setFillColor(HexColor("#A89F91"))
        c.drawString(x + 4 * mm, line_y + 1.5 * mm, hour_str)
        
        # Линия
        c.setStrokeColor(HexColor("#EAE5DE"))
        c.line(x + 14 * mm, line_y, x + w - 4 * mm, line_y)

def draw_priorities_box(c, x, y, w, h, title="TOP PRIORITIES"):
    """Блок топ-приоритетов с чекбоксами-цифрами 1, 2, 3."""
    c.setFillColor(BOX_BG_COLOR)
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 9)
    c.drawString(x + 5 * mm, y + h - 7 * mm, title)
    
    num_items = 3
    available_h = h - 10 * mm
    line_spacing = available_h / num_items
    
    for i in range(num_items):
        line_y = y + h - 10 * mm - (i + 1) * line_spacing + 3 * mm
        
        # Кружок с цифрой
        c.setFillColor(ACCENT_PINK) # Мягкий розовый цвет
        c.circle(x + 8 * mm, line_y + 1.5 * mm, 3 * mm, fill=1, stroke=0)
        
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat-Bold", 7)
        c.drawCentredString(x + 8 * mm, line_y + 0.3 * mm, str(i + 1))
        
        # Линия
        c.setLineWidth(0.5)
        c.setStrokeColor(HexColor("#EAE5DE"))
        c.line(x + 14 * mm, line_y, x + w - 5 * mm, line_y)

def create_daily_page(c, width, height, is_landscape, current_date):
    day_str = current_date.strftime('%Y-%m-%d')
    page_name = f"DAY_{day_str}"
    active_month = RIGHT_TABS[current_date.month]
    
    draw_base_page(c, width, height, active_right=active_month, page_name=page_name)
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Playfair-Bold", 19) 
    c.drawString(margin_x, content_y, current_date.strftime('%A, %B %d, %Y').upper())
    
    c.setFont("Montserrat-Bold", 7)
    
    # ← BACK TO MONTH
    c.drawString(margin_x, content_y + 8 * mm, f"← BACK TO {active_month}")
    c.linkAbsolute(f"MONTH_{active_month}", f"MONTH_{active_month}", (margin_x, content_y + 6 * mm, margin_x + 30 * mm, content_y + 12 * mm))
    
    # WEEK X →
    iso_year, week_num, _ = current_date.isocalendar()
    week_target = f"WEEK_{iso_year}_{week_num}"
    week_text = f"WEEK {week_num} →"
    text_w = c.stringWidth(week_text, "Montserrat-Bold", 7)
    c.drawString(margin_x + 35 * mm, content_y + 8 * mm, week_text)
    c.linkAbsolute(week_target, week_target, (margin_x + 35 * mm, content_y + 6 * mm, margin_x + 35 * mm + text_w, content_y + 12 * mm))

    content_y -= 10 * mm
    gap = 5 * mm
    bottom_margin = 15 * mm
    
    if is_landscape:
        col_w = (main_area_w - gap) / 2
        col1_x = margin_x
        col2_x = margin_x + col_w + gap
        
        # ЛЕВАЯ КОЛОНКА: Расписание
        draw_time_blocks_box(c, col1_x, bottom_margin, col_w, content_y - bottom_margin, "TIME BLOCKS")
        
        # ПРАВАЯ КОЛОНКА
        goal_h = 15 * mm
        draw_box_with_lines(c, col2_x, content_y - goal_h, col_w, goal_h, "MAIN GOAL")
        
        # Трекеры
        trackers_y = content_y - goal_h - gap - 8 * mm
        draw_water_tracker(c, col2_x, trackers_y, col_w / 2 - gap/2, 8 * mm)
        draw_mood_tracker(c, col2_x + col_w / 2 + gap/2, trackers_y, col_w / 2 - gap/2, 8 * mm)
        
        priorities_y = trackers_y - gap - 35 * mm
        draw_priorities_box(c, col2_x, priorities_y, col_w, 35 * mm, "TOP PRIORITIES")
        
        y_cursor = priorities_y - gap
        remaining_h = y_cursor - bottom_margin
        
        todo_h = (remaining_h - gap) * 0.6
        notes_h = (remaining_h - gap) * 0.4
        
        draw_box_with_lines(c, col2_x, bottom_margin + notes_h + gap, col_w, todo_h, "TO-DO LIST")
        draw_box_with_lines(c, col2_x, bottom_margin, col_w, notes_h, "NOTES")
        
    else:
        # ВЕРТИКАЛЬНАЯ ВЕРСИЯ
        goal_h = 15 * mm
        draw_box_with_lines(c, margin_x, content_y - goal_h, main_area_w, goal_h, "MAIN GOAL FOR TODAY")
        
        trackers_y = content_y - goal_h - gap - 8 * mm
        draw_water_tracker(c, margin_x, trackers_y, main_area_w / 2 - gap/2, 8 * mm)
        draw_mood_tracker(c, margin_x + main_area_w / 2 + gap/2, trackers_y, main_area_w / 2 - gap/2, 8 * mm)
        
        priorities_h = 35 * mm
        priorities_y = trackers_y - gap - priorities_h
        draw_priorities_box(c, margin_x, priorities_y, main_area_w, priorities_h, "TOP PRIORITIES")
        
        col_w = (main_area_w - gap) / 2
        
        y_cursor = priorities_y - gap
        remaining_h = y_cursor - bottom_margin
        
        time_h = remaining_h
        todo_h = (remaining_h - gap) * 0.6
        notes_h = (remaining_h - gap) * 0.4
        
        # Time Blocks слева
        draw_time_blocks_box(c, margin_x, bottom_margin, col_w, time_h, "TIME BLOCKS")
        
        # To-Do и Notes справа
        draw_box_with_lines(c, margin_x + col_w + gap, bottom_margin + notes_h + gap, col_w, todo_h, "TO-DO LIST")
        draw_box_with_lines(c, margin_x + col_w + gap, bottom_margin, col_w, notes_h, "NOTES")
        
    c.showPage()

def create_stickers_page(c, width, height, is_landscape):
    import math

    # ------------------------- палитра (boho chic) -------------------------
    B_TERRA = HexColor("#E07A5F")
    B_SAGE = HexColor("#81B29A")
    B_MUSTARD = HexColor("#F2CC8F")
    B_BLUSH = HexColor("#E5B299")
    B_NAVY = HexColor("#3D405B")
    B_SAND = HexColor("#F4F1DE")
    SHADOW_C = HexColor("#E3DFD5")
    WHITE = BOX_BG_COLOR
    palette = [B_TERRA, B_SAGE, B_MUSTARD, B_BLUSH, B_NAVY, B_SAND]

    def dl_link(f_key):
        return f"https://drive.google.com/uc?export=download&id={f_key}"

    DRIVE_MAIN_URL = "https://drive.google.com/drive/folders/1JmEuBnouxos37hvzh-TDkrNduZ263jny?usp=sharing"

    DRIVE_COLLECTIONS = [
        ("01. FUNCTIONAL", "Labels, frames & checklists", "1nLO3L_cLuH3l2BynVeCwnrP8lLeR3DBt", "1sWMHAKjNHIDZuOSeuD8UUprh93nWctgB", B_TERRA),
        ("02. BOHO & ABSTRACT", "Arches, shapes & line art", "1VrEwXfOplUQEaXDv8LFJZATP_9uouJlo", "1yWlMjuFwT4qsQ7raghdvQwEm9_IZv_C1", B_BLUSH),
        ("03. BOTANICAL", "Leaves, florals & nature", "1_P7hamoHOHzqJzHMC-CHyoTNP1hTrsUA", "1eehK7_oMtFVAMDrQB-Mnr9C64SZPGYuZ", B_SAGE),
        ("04. COZY LIFE", "Coffee, books & warm vibes", "1slK2uJixfXUGRKoeziv12Ut4pj8Ab9xC", "1cOORZVo297cbvQ3TtC8r82drLRRISxsW", B_MUSTARD),
        ("05. FOOD & DRINKS", "Meals, treats & kitchen", "1rpqWtjFfS07G9yYnCX4tFiOpv53HK13A", "1KKl_2Qp-NAMdkcrZ0iqglO1QaR8aq06U", B_TERRA),
        ("06. MEANINGFUL", "Quotes & gentle reminders", "1F9pN539BBVykZTIElQfKf8h-UMQabq-m", "1X4daHYw6kFif8PlzewkorPVGzX773d05", B_NAVY),
        ("07. CUTE ANIMALS", "Pets & woodland friends", "1q89og3gmDAiOfBQolGWfK44hUN7kWlFi", "1GGscKdk12wQA9TriHZcSk8we3XZxiTf-", B_SAGE),
    ]

    LABELS = ["URGENT", "MEETING", "DEADLINE", "APPOINTMENT", "PAY BILL", "WORKOUT",
              "BIRTHDAY", "BILLS DUE", "CALL BACK", "DON'T FORGET", "TODAY", "THIS WEEK"]
    WORDS = ["TODAY", "TO DO", "IMPORTANT", "NOTES", "IDEAS", "GOALS",
             "HEALTH", "WORK", "FAMILY", "TRAVEL", "FOCUS", "DONE"]
    TODOS = ["Top 3 today", "Call back", "Pay bill", "Buy groceries", "Workout", "Read 20 min"]
    MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
              "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    WEEK = ["M", "T", "W", "T", "F", "S", "S"]
    FOCUS = ["YOU GOT THIS", "KEEP GOING", "ONE STEP", "BREATHE", "MAKE IT HAPPEN"]

    def text_on(color):
        return WHITE if color in (B_TERRA, B_NAVY, B_SAGE) else DARK_BROWN

    def draw_shadow(x, y, w, h, radius=0):
        c.setFillColor(SHADOW_C)
        if radius > 0:
            c.roundRect(x + 1.5 * mm, y - 1.5 * mm, w, h, radius, fill=1, stroke=0)
        else:
            c.rect(x + 1.5 * mm, y - 1.5 * mm, w, h, fill=1, stroke=0)

    def title(x, y, text):
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat-Bold", 10)
        c.drawString(x, y, text)
        return y - 8 * mm

    def _star_path(cx, cy, r):
        p = c.beginPath()
        for i in range(10):
            ang = math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.45
            px, py = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
            if i == 0:
                p.moveTo(px, py)
            else:
                p.lineTo(px, py)
        p.close()
        return p

    def pill(x, y, w, h, text, color, hole=True, fs=7):
        draw_shadow(x, y, w, h, h / 2)
        c.setFillColor(color)
        c.roundRect(x, y, w, h, h / 2, fill=1, stroke=0)
        if hole:
            c.setFillColor(WHITE)
            c.circle(x + 4.5 * mm, y + h / 2, 2 * mm, fill=1, stroke=0)
            tx = x + 9 * mm
        else:
            tx = x + 4 * mm
        c.setFillColor(text_on(color))
        c.setFont("Montserrat-Bold", fs)
        c.drawString(tx, y + h / 2 - 1.1 * mm, text)

    def word_tag(x, y, w, h, text, color, fs=7):
        draw_shadow(x, y, w, h, h / 2)
        c.setFillColor(color)
        c.roundRect(x, y, w, h, h / 2, fill=1, stroke=0)
        c.setFillColor(text_on(color))
        c.setFont("Montserrat-Bold", fs)
        c.drawCentredString(x + w / 2, y + h / 2 - 1.1 * mm, text)

    def dot(x, y, r, color, text=None, fs=7):
        c.setFillColor(SHADOW_C)
        c.circle(x + 1 * mm, y - 1 * mm, r, fill=1, stroke=0)
        c.setFillColor(color)
        c.circle(x, y, r, fill=1, stroke=0)
        if text:
            c.setFillColor(text_on(color))
            c.setFont("Montserrat-Bold", fs)
            c.drawCentredString(x, y - 1.2 * mm, text)

    def star(x, y, r, color):
        c.setFillColor(SHADOW_C)
        c.drawPath(_star_path(x + 1 * mm, y - 1 * mm, r), fill=1, stroke=0)
        c.setFillColor(color)
        c.drawPath(_star_path(x, y, r), fill=1, stroke=0)

    def check_badge(x, y, r, color):
        dot(x, y, r, color)
        c.setStrokeColor(text_on(color))
        c.setLineWidth(1.2)
        p = c.beginPath()
        p.moveTo(x - r * 0.35, y)
        p.lineTo(x - r * 0.05, y - r * 0.3)
        p.lineTo(x + r * 0.4, y + r * 0.3)
        c.drawPath(p, fill=0, stroke=1)

    def check_row(x, y, w, label, color):
        s = 5 * mm
        draw_shadow(x, y, w, s, 1 * mm)
        c.setFillColor(WHITE)
        c.roundRect(x, y, w, s, 1 * mm, fill=1, stroke=0)
        c.setStrokeColor(color)
        c.setLineWidth(1)
        c.roundRect(x + 2 * mm, y + 1 * mm, 3 * mm, 3 * mm, 0.8 * mm, fill=0, stroke=1)
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat", 7)
        c.drawString(x + 7 * mm, y + 1.6 * mm, label)
        c.setStrokeColor(HexColor("#D8CFC0"))
        c.setLineWidth(0.4)
        c.line(x + 7 * mm, y + 1 * mm, x + w - 3 * mm, y + 1 * mm)

    def flag(x, y, w, h, color):
        draw_shadow(x, y, w, h)
        c.setFillColor(color)
        c.rect(x, y, w, h, fill=1, stroke=0)
        c.setFillColor(BG_COLOR)
        p = c.beginPath()
        p.moveTo(x, y)
        p.lineTo(x + w / 2, y + 4 * mm)
        p.lineTo(x + w, y)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    def ribbon(x, y, w, h, text, color, fs=7):
        draw_shadow(x, y, w, h, 1 * mm)
        c.setFillColor(color)
        p = c.beginPath()
        p.moveTo(x, y)
        p.lineTo(x + w - 4 * mm, y)
        p.lineTo(x + w, y + h / 2)
        p.lineTo(x + w - 4 * mm, y + h)
        p.lineTo(x, y + h)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.setFillColor(text_on(color))
        c.setFont("Montserrat-Bold", fs)
        c.drawString(x + 4 * mm, y + h / 2 - 1.1 * mm, text)

    def washi(x, y, w, h, color):
        draw_shadow(x, y, w, h)
        c.setFillColor(color)
        c.rect(x, y, w, h, fill=1, stroke=0)
        c.setStrokeColor(WHITE)
        c.setLineWidth(1)
        for lx in range(0, int(w / mm), 4):
            c.line(x + lx * mm, y, x + (lx + 3) * mm, y + h)

    def polaroid(x, y, w=30 * mm, h=35 * mm):
        draw_shadow(x, y, w, h)
        c.setFillColor(WHITE)
        c.rect(x, y, w, h, fill=1, stroke=0)
        c.setFillColor(HexColor("#EAE5DE"))
        c.rect(x + 2.5 * mm, y + 7 * mm, w - 5 * mm, h - 9.5 * mm, fill=1, stroke=0)
        c.setFillColor(B_MUSTARD)
        c.rect(x + w / 2 - 5 * mm, y + h - 5 * mm, 10 * mm, 4 * mm, fill=1, stroke=0)

    def sticky(x, y, w, h, color, lines=3):
        draw_shadow(x, y, w, h, 1 * mm)
        c.setFillColor(color)
        c.roundRect(x, y, w, h, 1 * mm, fill=1, stroke=0)
        c.setStrokeColor(WHITE)
        c.setLineWidth(0.5)
        for l in range(lines):
            ly = y + h - 6 * mm - l * 5 * mm
            c.line(x + 3 * mm, ly, x + w - 3 * mm, ly)

    def draw_sticker_vault_hub(x, y, w, h):
        c.setFillColor(BOX_BG_COLOR)
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.roundRect(x, y, w, h, 3 * mm, fill=1, stroke=1)

        c.setFillColor(B_TERRA)
        c.setFont("Montserrat-Bold", 11)
        c.drawString(x + 6 * mm, y + h - 9 * mm, "1000+ STICKER BOOK & DIRECT DOWNLOADS")

        c.setFillColor(HexColor("#8C8377"))
        c.setFont("Montserrat", 8)
        c.drawString(x + 6 * mm, y + h - 14.5 * mm, "Tap [PDF] to download the ready-to-use GoodNotes Sticker Book, or tap [ZIP]")
        c.drawString(x + 6 * mm, y + h - 18.5 * mm, "to download transparent PNG files directly to your device:")

        # --- ГЛАВНАЯ КНОПКА (Векторная стрелка ↗) ---
        main_btn_h = 10 * mm
        main_btn_y = y + h - 31 * mm
        c.setFillColor(DARK_BROWN)
        c.roundRect(x + 6 * mm, main_btn_y, w - 12 * mm, main_btn_h, 2 * mm, fill=1, stroke=0)
        
        btn_text = "BROWSE ALL 1000+ STICKERS IN CLOUD FOLDER"
        c.setFillColor(WHITE)
        c.setFont("Montserrat-Bold", 8.5)
        c.drawCentredString(x + w / 2 - 3 * mm, main_btn_y + 3.5 * mm, btn_text)
        
        tw = c.stringWidth(btn_text, "Montserrat-Bold", 8.5)
        arr_x = x + w / 2 - 3 * mm + tw / 2 + 4 * mm
        arr_y = main_btn_y + 5 * mm
        
        c.setStrokeColor(WHITE)
        c.setLineWidth(1.2)
        c.setLineCap(1)
        p = c.beginPath()
        p.moveTo(arr_x - 1.5*mm, arr_y - 1.5*mm)
        p.lineTo(arr_x + 1.5*mm, arr_y + 1.5*mm)
        p.moveTo(arr_x - 1.5*mm, arr_y + 1.5*mm)
        p.lineTo(arr_x + 1.5*mm, arr_y + 1.5*mm)
        p.lineTo(arr_x + 1.5*mm, arr_y - 1.5*mm)
        c.drawPath(p, fill=0, stroke=1)
        
        c.linkURL(DRIVE_MAIN_URL, (x + 6 * mm, main_btn_y, x + w - 6 * mm, main_btn_y + main_btn_h), relative=0)

        grid_top = main_btn_y - 4 * mm
        grid_bottom = y + 5 * mm
        grid_h = grid_top - grid_bottom
        gap = 3 * mm
        cols, rows = 2, 4
        card_w = (w - 12 * mm - gap) / cols
        card_h = (grid_h - gap * (rows - 1)) / rows

        for idx, (c_title, c_desc, pdf_key, zip_key, c_color) in enumerate(DRIVE_COLLECTIONS):
            col = idx % cols
            row = idx // cols
            cx = x + 6 * mm + col * (card_w + gap)
            cy = grid_top - (row + 1) * card_h - row * gap

            c.setFillColor(WHITE)
            c.setStrokeColor(HexColor("#D8D0C5"))
            c.roundRect(cx, cy, card_w, card_h, 2 * mm, fill=1, stroke=1)

            c.setFillColor(c_color)
            c.circle(cx + 4.5 * mm, cy + card_h / 2, 2.2 * mm, fill=1, stroke=0)

            c.setFillColor(DARK_BROWN)
            c.setFont("Montserrat-Bold", 7)
            c.drawString(cx + 8.5 * mm, cy + card_h / 2 + 1 * mm, c_title)

            c.setFillColor(HexColor("#A89F91"))
            c.setFont("Montserrat", 6)
            c.drawString(cx + 8.5 * mm, cy + card_h / 2 - 3 * mm, c_desc)

            # --- ВЕКТОРНАЯ КНОПКА PDF (со стрелкой ⬇) ---
            btn_w = 11.5 * mm
            btn_h = 5.5 * mm
            by = cy + (card_h - btn_h) / 2

            pdf_bx = cx + card_w - 25 * mm
            c.setFillColor(ACCENT_PINK)
            c.roundRect(pdf_bx, by, btn_w, btn_h, 1.2 * mm, fill=1, stroke=0)
            
            c.setFillColor(DARK_BROWN)
            c.setFont("Montserrat-Bold", 5.5)
            c.drawString(pdf_bx + 4.5 * mm, by + 1.8 * mm, "PDF")
            
            arr_px = pdf_bx + 2.5 * mm
            arr_py = by + btn_h / 2
            c.setStrokeColor(DARK_BROWN)
            c.setLineWidth(0.8)
            p = c.beginPath()
            p.moveTo(arr_px, arr_py + 1.2*mm)
            p.lineTo(arr_px, arr_py - 1.2*mm)
            p.moveTo(arr_px - 0.8*mm, arr_py - 0.4*mm)
            p.lineTo(arr_px, arr_py - 1.2*mm)
            p.lineTo(arr_px + 0.8*mm, arr_py - 0.4*mm)
            c.drawPath(p, stroke=1, fill=0)
            
            c.linkURL(dl_link(pdf_key), (pdf_bx, by, pdf_bx + btn_w, by + btn_h), relative=0)

            # --- ВЕКТОРНАЯ КНОПКА ZIP (со стрелкой ⬇) ---
            zip_bx = cx + card_w - 12 * mm
            c.setFillColor(ACCENT_GREEN)
            c.roundRect(zip_bx, by, btn_w, btn_h, 1.2 * mm, fill=1, stroke=0)
            
            c.setFillColor(DARK_BROWN)
            c.drawString(zip_bx + 4.5 * mm, by + 1.8 * mm, "ZIP")
            
            arr_zx = zip_bx + 2.5 * mm
            arr_zy = by + btn_h / 2
            p = c.beginPath()
            p.moveTo(arr_zx, arr_zy + 1.2*mm)
            p.lineTo(arr_zx, arr_zy - 1.2*mm)
            p.moveTo(arr_zx - 0.8*mm, arr_zy - 0.4*mm)
            p.lineTo(arr_zx, arr_zy - 1.2*mm)
            p.lineTo(arr_zx + 0.8*mm, arr_zy - 0.4*mm)
            c.drawPath(p, stroke=1, fill=0)
            
            c.linkURL(dl_link(zip_key), (zip_bx, by, zip_bx + btn_w, by + btn_h), relative=0)

        # 8-я ячейка
        tip_cx = x + 6 * mm + 1 * (card_w + gap)
        tip_cy = grid_top - 4 * card_h - 3 * gap
        c.setFillColor(B_SAND)
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.roundRect(tip_cx, tip_cy, card_w, card_h, 2 * mm, fill=1, stroke=1)
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat-Bold", 7)
        c.drawString(tip_cx + 4 * mm, tip_cy + card_h / 2 + 1 * mm, "PRO TIP: SPLIT VIEW")
        c.setFont("Montserrat", 6)
        c.drawString(tip_cx + 4 * mm, tip_cy + card_h / 2 - 3 * mm, "Download PDF, open in 2nd tab & drag!")

    first_sticker_page = [True]
    def page_head(sub):
        p_name = "STICKERS" if first_sticker_page[0] else ""
        first_sticker_page[0] = False
        draw_base_page(c, width, height, active_top="STICKERS", page_name=p_name)
        mx = 15 * mm
        y = height - 25 * mm

        c.setFillColor(DARK_BROWN)
        title_str = "STICKER BOOK"
        c.setFont("Playfair-Bold", 24)
        c.drawString(mx, y, title_str)

        title_w = c.stringWidth(title_str, "Playfair-Bold", 24)
        c.setFont("Montserrat", 10)
        c.setFillColor(HexColor("#A89F91"))
        c.drawString(mx + title_w + 5 * mm, y + 2 * mm, "| " + sub)
        return mx, y - 15 * mm

    # ============================ LANDSCAPE ============================
    if is_landscape:
        col_w = (width - 15 * mm - 25 * mm) / 3
        xs = [15 * mm + i * col_w for i in range(3)]

        # ---------- СТРАНИЦА 1 ----------
        mx, y0 = page_head("Quick-Grab Essentials · Use the Lasso tool to copy & paste")

        y = title(xs[0], y0, "LABELS")
        for i, lab in enumerate(LABELS):
            pill(xs[0], y - 7 * mm, 38 * mm, 7 * mm, lab, palette[i % len(palette)])
            y -= 10 * mm
        y -= 4 * mm
        y = title(xs[0], y, "PRIORITY")
        y -= 6 * mm
        star(xs[0] + 6 * mm, y, 5 * mm, B_MUSTARD)
        dot(xs[0] + 20 * mm, y, 5 * mm, B_TERRA, "!")
        check_badge(xs[0] + 34 * mm, y, 5 * mm, B_SAGE)
        dot(xs[0] + 48 * mm, y, 5 * mm, B_NAVY, "?", fs=8)

        y = title(xs[1], y0, "WORD TAGS")
        for i, w_ in enumerate(WORDS):
            bx = xs[1] + (i % 2) * 40 * mm
            by = y - 7.5 * mm - (i // 2) * 10.5 * mm
            word_tag(bx, by, 37 * mm, 7.5 * mm, w_, palette[i % len(palette)])
        y = y - 6 * 10.5 * mm - 6 * mm
        y = title(xs[1], y, "TO-DO")
        for i, t in enumerate(TODOS):
            check_row(xs[1], y - 5 * mm, 77 * mm, t, palette[i % len(palette)])
            y -= 10 * mm

        y = title(xs[2], y0, "MONTHS")
        for i, m_ in enumerate(MONTHS):
            dot(xs[2] + 8 * mm + (i % 3) * 22 * mm, y - 6 * mm - (i // 3) * 15 * mm,
                6 * mm, palette[i % len(palette)], m_, fs=6)
        y = y - 4 * 15 * mm - 8 * mm
        y = title(xs[2], y, "WEEK")
        for i, d_ in enumerate(WEEK):
            dot(xs[2] + 6 * mm + i * 11 * mm, y - 5 * mm, 4.5 * mm,
                palette[i % len(palette)], d_, fs=7)
        y -= 16 * mm
        y = title(xs[2], y, "FOCUS")
        for i, f in enumerate(FOCUS):
            ribbon(xs[2], y - 8 * mm, 72 * mm, 8 * mm, f, palette[(i + 1) % len(palette)])
            y -= 12 * mm
        c.showPage()

        # ---------- СТРАНИЦА 2 ----------
        mx, y0 = page_head("Decor Widgets & 1000+ Direct Download Vault")

        y = title(xs[0], y0, "BOOKMARKS & WASHI")
        for i in range(4):
            flag(xs[0] + i * 16 * mm, y - 16 * mm, 12 * mm, 16 * mm, palette[i % len(palette)])
        y -= 22 * mm
        for i, col_ in enumerate([B_TERRA, B_MUSTARD, B_SAGE]):
            washi(xs[0], y - 5.5 * mm, 62 * mm, 5.5 * mm, col_)
            y -= 9 * mm
        y -= 3 * mm
        y = title(xs[0], y, "FRAMES & STICKY NOTES")
        polaroid(xs[0], y - 35 * mm)
        sticky(xs[0] + 34 * mm, y - 17 * mm, 28 * mm, 17 * mm, B_BLUSH, lines=2)
        sticky(xs[0] + 34 * mm, y - 35 * mm, 28 * mm, 17 * mm, B_SAGE, lines=2)

        hub_w = col_w * 2 - 5 * mm
        draw_sticker_vault_hub(xs[1], 15 * mm, hub_w, y0 - 15 * mm)
        c.showPage()

    # ============================ PORTRAIT ============================
    else:
        mx, y0 = page_head("Quick-Grab Essentials · Use the Lasso tool to copy & paste")
        W_ = width - mx - 20 * mm

        y = title(mx, y0, "LABELS")
        for i, lab in enumerate(LABELS):
            bx = mx + (i % 3) * (W_ / 3)
            by = y - 7 * mm - (i // 3) * 10 * mm
            pill(bx, by, W_ / 3 - 4 * mm, 7 * mm, lab, palette[i % len(palette)], fs=6)
        y = y - 4 * 10 * mm - 8 * mm

        y = title(mx, y, "WORD TAGS")
        for i, w_ in enumerate(WORDS):
            bx = mx + (i % 3) * (W_ / 3)
            by = y - 7.5 * mm - (i // 3) * 10.5 * mm
            word_tag(bx, by, W_ / 3 - 4 * mm, 7.5 * mm, w_, palette[i % len(palette)], fs=6)
        y = y - 4 * 10.5 * mm - 8 * mm

        y = title(mx, y, "TO-DO")
        for i, t in enumerate(TODOS):
            check_row(mx, y - 5 * mm, W_, t, palette[i % len(palette)])
            y -= 10 * mm
        y -= 4 * mm

        y = title(mx, y, "MONTHS & WEEK")
        for i, m_ in enumerate(MONTHS):
            dot(mx + 8 * mm + (i % 6) * (W_ / 6), y - 6 * mm - (i // 6) * 15 * mm,
                6 * mm, palette[i % len(palette)], m_, fs=6)
        c.showPage()

        # ---------- СТРАНИЦА 2 PORTRAIT ----------
        mx, y0 = page_head("Decor Widgets & 1000+ Direct Download Vault")

        y = title(mx, y0, "DECOR WIDGETS (BOOKMARKS, POLAROID & NOTES)")
        for i in range(4):
            flag(mx + i * 14 * mm, y - 18 * mm, 10 * mm, 18 * mm, palette[i % len(palette)])
        polaroid(mx + 62 * mm, y - 35 * mm)
        sticky(mx + 98 * mm, y - 35 * mm, 32 * mm, 35 * mm, B_BLUSH, lines=4)
        sticky(mx + 135 * mm, y - 35 * mm, 32 * mm, 35 * mm, B_SAGE, lines=4)
        y -= 42 * mm

        draw_sticker_vault_hub(mx, 15 * mm, W_, y - 15 * mm)
        c.showPage()

def create_brain_dump_page(c, width, height, is_landscape):
    draw_base_page(c, width, height, active_top="BRAIN DUMP", page_name="BRAIN DUMP")
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    
    # Заголовок страницы
    c.setFillColor(DARK_BROWN)
    title_str = "BRAIN DUMP"
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, title_str)
    
    # Автоматически вычисляем ширину заголовка
    title_w = c.stringWidth(title_str, "Playfair-Bold", 24)
    
    # Ставим подзаголовок с отступом ровно 5 мм от конца слова "BRAIN DUMP"
    c.setFont("Montserrat", 10)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(margin_x + title_w + 5 * mm, content_y + 2 * mm, "| Unload your mind and organize the chaos")
    
    content_y -= 10 * mm
    bottom_margin = 15 * mm
    available_h = content_y - bottom_margin
    gap = 5 * mm
    
    # Заголовки блоков (на английском для сохранения стилистики планера)
    t_inbox = "MIND CLUTTER / INBOX"
    t_action = "ACTION REQUIRED"
    t_someday = "SOMEDAY / MAYBE"
    t_parking = "IDEA PARKING LOT"
    t_letgo = "LET IT GO (Out of my control)"

    if is_landscape:
        # Горизонтально: 3 колонки
        col_w = (main_area_w - 2 * gap) / 3
        half_h = (available_h - gap) / 2
        
        # Колонка 1: Входящие (на всю высоту)
        draw_box_with_lines(c, margin_x, bottom_margin, col_w, available_h, t_inbox)
        
        # Колонка 2: Action (верх), Someday (низ)
        col2_x = margin_x + col_w + gap
        draw_box_with_lines(c, col2_x, bottom_margin + half_h + gap, col_w, half_h, t_action)
        draw_box_with_lines(c, col2_x, bottom_margin, col_w, half_h, t_someday)
        
        # Колонка 3: Parking (верх), Let It Go (низ)
        col3_x = margin_x + 2 * col_w + 2 * gap
        draw_box_with_lines(c, col3_x, bottom_margin + half_h + gap, col_w, half_h, t_parking)
        draw_box_with_lines(c, col3_x, bottom_margin, col_w, half_h, t_letgo)
        
    else:
        # Вертикально: широкий верхний блок и сетка 2x2 внизу
        top_h = available_h * 0.4 # Inbox занимает верхние 40%
        bottom_area_h = available_h - top_h - gap
        half_h = (bottom_area_h - gap) / 2
        col_w = (main_area_w - gap) / 2
        
        # Верхний блок: Входящие (на всю ширину)
        top_y = bottom_margin + bottom_area_h + gap
        draw_box_with_lines(c, margin_x, top_y, main_area_w, top_h, t_inbox)
        
        # Сетка 2x2 под ним
        col2_x = margin_x + col_w + gap
        row2_y = bottom_margin + half_h + gap
        
        draw_box_with_lines(c, margin_x, row2_y, col_w, half_h, t_action)     # Слева вверху
        draw_box_with_lines(c, margin_x, bottom_margin, col_w, half_h, t_someday)  # Слева внизу
        
        draw_box_with_lines(c, col2_x, row2_y, col_w, half_h, t_parking)      # Справа вверху
        draw_box_with_lines(c, col2_x, bottom_margin, col_w, half_h, t_letgo)      # Справа внизу

    c.showPage()

def draw_done_box(c, x, y, w, h, title):
    """Специальный блок для Done List с заранее проставленными галочками."""
    c.setFillColor(BOX_BG_COLOR)
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 9)
    c.drawString(x + 5 * mm, y + h - 7 * mm, title)
    
    line_spacing = 8 * mm 
    current_y = y + h - 14 * mm 
    
    while current_y > y + 2 * mm:
        # Рисуем линию для записи (начинается с отступом для галочки)
        c.setLineWidth(0.5)
        c.setStrokeColor(HexColor("#EAE5DE"))
        c.line(x + 12 * mm, current_y, x + w - 5 * mm, current_y)
        
        # Координаты галочки
        cx = x + 5 * mm
        cy = current_y + 0.5 * mm
        
        # Фон чекбокса (зеленый акцент)
        c.setFillColor(ACCENT_GREEN) 
        c.roundRect(cx, cy, 4 * mm, 4 * mm, 1 * mm, fill=1, stroke=0)
        
        # Сама галочка (Line-art)
        c.setLineWidth(1)
        c.setStrokeColor(DARK_BROWN)
        p = c.beginPath()
        p.moveTo(cx + 1 * mm, cy + 1.8 * mm)
        p.lineTo(cx + 1.8 * mm, cy + 1 * mm)
        p.lineTo(cx + 3.2 * mm, cy + 3 * mm)
        c.drawPath(p, stroke=1, fill=0)
        
        current_y -= line_spacing

def create_done_list_page(c, width, height, is_landscape):
    draw_base_page(c, width, height, active_top="DONE LIST", page_name="DONE LIST")
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    
    # Заголовок страницы
    c.setFillColor(DARK_BROWN)
    title_str = "DONE LIST"
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, title_str)
    
    # Динамический подзаголовок
    title_w = c.stringWidth(title_str, "Playfair-Bold", 24)
    c.setFont("Montserrat", 10)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(margin_x + title_w + 5 * mm, content_y + 2 * mm, "| Look what I did! (The Anti-To-Do List)")
    
    content_y -= 10 * mm
    bottom_margin = 15 * mm
    available_h = content_y - bottom_margin
    gap = 5 * mm
    
    titles = ["WORK & PROJECTS", "LIFE & ERRANDS", "MICRO WINS (The little things)"]
    
    if is_landscape:
        # Горизонтально: 3 колонки рядом
        col_w = (main_area_w - 2 * gap) / 3
        for i in range(3):
            cx = margin_x + i * (col_w + gap)
            draw_done_box(c, cx, bottom_margin, col_w, available_h, titles[i])
    else:
        # Вертикально: 3 ряда друг под другом
        row_h = (available_h - 2 * gap) / 3
        for i in range(3):
            cy = bottom_margin + (2 - i) * (row_h + gap)
            draw_done_box(c, margin_x, cy, main_area_w, row_h, titles[i])
            
    c.showPage()

def draw_focus_block(c, x, y, w, h):
    """Отрисовка отдельного блока фокус-сессии с трекером в виде бохо-арок."""
    c.setFillColor(BOX_BG_COLOR)
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
    
    # 1. ЗАДАЧА / ЦЕЛЬ ФОКУСА
    c.setFillColor(DARK_BROWN)
    target_str = "FOCUS TARGET:"
    c.setFont("Montserrat-Bold", 9)
    c.drawString(x + 5 * mm, y + h - 8 * mm, target_str)
    
    # Автоматически вычисляем ширину заголовка и рисуем линию после него
    target_w = c.stringWidth(target_str, "Montserrat-Bold", 9)
    c.setLineWidth(0.5)
    c.setStrokeColor(HexColor("#EAE5DE"))
    c.line(x + 5 * mm + target_w + 3 * mm, y + h - 8 * mm, x + w - 5 * mm, y + h - 8 * mm)
    
    # 2. ЗАМЕТКИ И ОТВЛЕЧЕНИЯ
    notes_str = "NOTES & DISTRACTIONS:"
    c.setFont("Montserrat-Bold", 8)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(x + 5 * mm, y + h - 17 * mm, notes_str)
    
    # Автоматически вычисляем ширину подзаголовка для первой линии
    notes_w = c.stringWidth(notes_str, "Montserrat-Bold", 8)
    line_y = y + h - 17 * mm
    c.line(x + 5 * mm + notes_w + 3 * mm, line_y, x + w - 5 * mm, line_y)
    
    # Рисуем остальные линии, оставляя место внизу для арок (около 24 мм)
    line_y -= 8 * mm
    while line_y > y + 24 * mm:
        c.line(x + 5 * mm, line_y, x + w - 5 * mm, line_y)
        line_y -= 8 * mm
    
    # 3. ПОМОДОРО ТРЕКЕР (BOHO ARCHES)
    # ИСПРАВЛЕНИЕ: Переносим текст ВЫШЕ арок, чтобы они никогда не пересекались
    c.setFont("Montserrat-Bold", 7)
    c.setFillColor(DARK_BROWN)
    c.drawString(x + 5 * mm, y + 16 * mm, "DEEP WORK (25 MINS):")
    
    arch_w = 6 * mm
    arch_h = 9 * mm
    spacing = 2 * mm
    num_arches = 8 # 8 сессий = 4 часа глубокой работы
    
    # ИСПРАВЛЕНИЕ: Начинаем рисовать арки строго слева, под заголовком
    start_x = x + 5 * mm
    
    c.setLineWidth(1)
    c.setStrokeColor(HexColor("#D8D0C5"))
    
    for i in range(num_arches):
        ax = start_x + i * (arch_w + spacing)
        ay = y + 4 * mm
        
        c.setFillColor(HexColor("#FFFFFF"))
        p = c.beginPath()
        r = arch_w / 2
        p.moveTo(ax, ay)                     
        p.lineTo(ax + arch_w, ay)            
        p.lineTo(ax + arch_w, ay + arch_h - r) 
        p.arcTo(ax, ay + arch_h - arch_w, ax + arch_w, ay + arch_h, 0, 180)
        p.lineTo(ax, ay)                     
        
        c.drawPath(p, fill=1, stroke=1)

def create_focus_log_page(c, width, height, is_landscape):
    draw_base_page(c, width, height, active_top="FOCUS LOG", page_name="FOCUS LOG")
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    
    # Заголовок страницы
    c.setFillColor(DARK_BROWN)
    title_str = "FOCUS LOG"
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, title_str)
    
    # Динамический подзаголовок
    title_w = c.stringWidth(title_str, "Playfair-Bold", 24)
    c.setFont("Montserrat", 10)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(margin_x + title_w + 5 * mm, content_y + 2 * mm, "| Highlight an arch for every 25 mins of deep work")
    
    content_y -= 10 * mm
    bottom_margin = 15 * mm
    available_h = content_y - bottom_margin
    gap = 5 * mm
    
    # Сетка блоков (9 блоков для горизонтали, 10 для вертикали)
    if is_landscape:
        cols, rows = 3, 3 
    else:
        cols, rows = 2, 5 
        
    box_w = (main_area_w - gap * (cols - 1)) / cols
    box_h = (available_h - gap * (rows - 1)) / rows
    
    for r in range(rows):
        for col in range(cols):
            bx = margin_x + col * (box_w + gap)
            by = content_y - (r + 1) * box_h - r * gap
            draw_focus_block(c, bx, by, box_w, box_h)
            
    c.showPage()

def draw_habit_block(c, x, y, w, h):
    c.setFillColor(BOX_BG_COLOR)
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 9)
    title_str = "HABIT:"
    c.drawString(x + 5 * mm, y + h - 9 * mm, title_str)
    
    title_w = c.stringWidth(title_str, "Montserrat-Bold", 9)
    c.setLineWidth(0.5)
    c.setStrokeColor(HexColor("#EAE5DE"))
    c.line(x + 5 * mm + title_w + 2 * mm, y + h - 9 * mm, x + w - 5 * mm, y + h - 9 * mm)
    
    c.setFillColor(HexColor("#A89F91"))
    c.setFont("Montserrat-Bold", 7)
    why_str = "WHY:"
    c.drawString(x + 5 * mm, y + h - 17 * mm, why_str)
    
    why_w = c.stringWidth(why_str, "Montserrat-Bold", 7)
    c.line(x + 5 * mm + why_w + 2 * mm, y + h - 17 * mm, x + w - 5 * mm, y + h - 17 * mm)
    
    cols = 8
    rows = 4
    radius = 2.5 * mm
    gap = 2 * mm
    
    grid_w = cols * (radius * 2) + (cols - 1) * gap
    offset_x = (w - grid_w) / 2  
    
    start_x = x + offset_x + radius
    start_y = y + h - 28 * mm - radius
    
    c.setLineWidth(1)
    c.setStrokeColor(HexColor("#E3DFD5"))
    c.setFillColor(HexColor("#FFFFFF"))
    
    count = 1
    for r in range(rows):
        for col in range(cols):
            if count > 31: 
                break
            cx = start_x + col * (radius * 2 + gap)
            cy = start_y - r * (radius * 2 + gap)
            c.circle(cx, cy, radius, fill=1, stroke=1)
            count += 1

def create_habits_page(c, width, height, is_landscape, month_num):
    month_name = RIGHT_TABS[month_num]
    page_name = f"HABITS_{month_name}"
    draw_base_page(c, width, height, active_top="HABITS", active_right=month_name, page_name=page_name)
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    
    c.setFillColor(DARK_BROWN)
    title_str = f"{calendar.month_name[month_num].upper()} HABITS"
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, title_str)
    
    title_w = c.stringWidth(title_str, "Playfair-Bold", 24)
    c.setFont("Montserrat", 10)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(margin_x + title_w + 5 * mm, content_y + 2 * mm, "| Progress over perfection")
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 7)
    c.drawString(margin_x, content_y + 8 * mm, f"← BACK TO {month_name}")
    c.linkAbsolute(f"MONTH_{month_name}", f"MONTH_{month_name}", (margin_x, content_y + 6 * mm, margin_x + 30 * mm, content_y + 12 * mm))
    
    content_y -= 10 * mm
    bottom_margin = 15 * mm
    available_h = content_y - bottom_margin
    gap = 5 * mm
    
    cols, rows = (4, 2) if is_landscape else (2, 4)
    box_w = (main_area_w - gap * (cols - 1)) / cols
    box_h = (available_h - gap * (rows - 1)) / rows
    
    for r in range(rows):
        for col in range(cols):
            bx = margin_x + col * (box_w + gap)
            by = content_y - (r + 1) * box_h - r * gap
            draw_habit_block(c, bx, by, box_w, box_h)
            
    c.showPage()


def create_habits_page(c, width, height, is_landscape, month_num):
    month_name = RIGHT_TABS[month_num]
    page_name = f"HABITS_{month_name}"
    draw_base_page(c, width, height, active_top="HABITS", active_right=month_name, page_name=page_name)
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    
    c.setFillColor(DARK_BROWN)
    title_str = f"{calendar.month_name[month_num].upper()} HABITS"
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, title_str)
    
    title_w = c.stringWidth(title_str, "Playfair-Bold", 24)
    c.setFont("Montserrat", 10)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(margin_x + title_w + 5 * mm, content_y + 2 * mm, "| Progress over perfection")
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 7)
    c.drawString(margin_x, content_y + 8 * mm, f"← BACK TO {month_name}")
    c.linkAbsolute(f"MONTH_{month_name}", f"MONTH_{month_name}", (margin_x, content_y + 6 * mm, margin_x + 30 * mm, content_y + 12 * mm))
    
    content_y -= 10 * mm
    bottom_margin = 15 * mm
    available_h = content_y - bottom_margin
    gap = 5 * mm
    
    cols, rows = (4, 2) if is_landscape else (2, 4)
    box_w = (main_area_w - gap * (cols - 1)) / cols
    box_h = (available_h - gap * (rows - 1)) / rows
    
    for r in range(rows):
        for col in range(cols):
            bx = margin_x + col * (box_w + gap)
            by = content_y - (r + 1) * box_h - r * gap
            draw_habit_block(c, bx, by, box_w, box_h)
            
    c.showPage()


# Деньги
def draw_money_box(c, x, y, w, h, title):
    """Базовый блок для финансовой страницы."""
    c.setFillColor(BOX_BG_COLOR)
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 9)
    c.drawString(x + 5 * mm, y + h - 8 * mm, title)
    
    title_w = c.stringWidth(title, "Montserrat-Bold", 9)
    c.setLineWidth(0.5)
    c.setStrokeColor(HexColor("#EAE5DE"))
    c.line(x + 5 * mm + title_w + 3 * mm, y + h - 8 * mm, x + w - 5 * mm, y + h - 8 * mm)

def draw_bills_box(c, x, y, w, h):
    """Блок обязательных платежей и подписок."""
    draw_money_box(c, x, y, w, h, "FIXED BILLS & SUBSCRIPTIONS")
    
    line_y = y + h - 18 * mm
    c.setLineWidth(0.5)
    
    while line_y > y + 5 * mm:
        c.setFillColor(HexColor("#FFFFFF"))
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.rect(x + 5 * mm, line_y, 4 * mm, 4 * mm, fill=1, stroke=1)
        
        c.setStrokeColor(HexColor("#EAE5DE"))
        c.line(x + 12 * mm, line_y, x + w - 5 * mm, line_y)
        
        c.setFont("Montserrat", 6)
        c.setFillColor(HexColor("#A89F91"))
        c.drawString(x + w - 25 * mm, line_y + 1 * mm, "AMOUNT:")
        c.drawString(x + w - 45 * mm, line_y + 1 * mm, "DUE:")
        
        line_y -= 8 * mm

def draw_jars_box(c, x, y, w, h):
    """Визуальные стеклянные баночки для накоплений."""
    draw_money_box(c, x, y, w, h, "SAVINGS JARS")
    
    num_jars = 3
    jar_area_w = w / num_jars
    jar_w = min(28 * mm, jar_area_w - 10 * mm)
    jar_h = h - 35 * mm
    
    for i in range(num_jars):
        cx = x + i * jar_area_w + jar_area_w / 2
        jx = cx - jar_w / 2
        jy = y + 15 * mm
        
        c.setLineWidth(1.5)
        c.setStrokeColor(DARK_BROWN)
        c.setFillColor(HexColor("#FFFFFF"))
        c.roundRect(jx, jy, jar_w, jar_h - 2 * mm, 3 * mm, fill=1, stroke=1)
        
        c.rect(jx - 1.5 * mm, jy + jar_h - 4 * mm, jar_w + 3 * mm, 4 * mm, fill=1, stroke=1)
        
        c.setLineWidth(0.5)
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.setDash(2, 2)
        level_gap = (jar_h - 6 * mm) / 5
        for l in range(1, 5):
            ly = jy + l * level_gap
            c.line(jx + 1.5 * mm, ly, jx + jar_w - 1.5 * mm, ly)
        
        c.setDash() 
        
        c.setLineWidth(0.5)
        c.setStrokeColor(HexColor("#EAE5DE"))
        c.line(cx - 15 * mm, jy - 6 * mm, cx + 15 * mm, jy - 6 * mm)
        c.setFont("Montserrat-Bold", 7)
        c.setFillColor(HexColor("#A89F91"))
        c.drawCentredString(cx, jy - 10 * mm, "GOAL / REWARD")

def draw_no_spend_box(c, x, y, w, h):
    """Трекер дней без импульсивных трат."""
    draw_money_box(c, x, y, w, h, "NO-SPEND CHALLENGE")
    
    c.setFont("Montserrat", 7)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(x + 5 * mm, y + h - 14 * mm, "Color a box for every day with $0 impulse spending")
    
    cols, rows = 7, 5
    available_w = w - 10 * mm
    available_h = h - 25 * mm 
    gap = 2 * mm
    
    item_w = (available_w - (cols - 1) * gap) / cols
    item_h = (available_h - (rows - 1) * gap) / rows
    size = min(item_w, item_h, 12 * mm) 
    
    grid_w = cols * size + (cols - 1) * gap
    grid_h = rows * size + (rows - 1) * gap
    
    start_x = x + (w - grid_w) / 2
    start_y = y + (h - 15 * mm - grid_h) / 2 + grid_h - size 
    
    count = 1
    for r in range(rows):
        for col in range(cols):
            if count > 31: break
            cx = start_x + col * (size + gap)
            cy = start_y - r * (size + gap)
            
            c.setLineWidth(1)
            c.setStrokeColor(HexColor("#D8D0C5"))
            c.setFillColor(HexColor("#FFFFFF"))
            c.roundRect(cx, cy, size, size, 2 * mm, fill=1, stroke=1)
            
            c.setFont("Montserrat-Bold", 6)
            c.setFillColor(HexColor("#D8D0C5"))
            c.drawCentredString(cx + size/2, cy + size/2 - 2 * mm, str(count))
            count += 1

def draw_overview_box(c, x, y, w, h):
    """Общие итоги месяца."""
    draw_money_box(c, x, y, w, h, "MONTHLY OVERVIEW")
    
    labels = ["TOTAL INCOME:", "TOTAL SAVED:", "TOTAL EXPENSES:", "LEFT FOR FUN:"]
    line_spacing = (h - 20 * mm) / 4
    
    for i, label in enumerate(labels):
        ly = y + h - 20 * mm - i * line_spacing
        
        c.setFont("Montserrat-Bold", 8)
        c.setFillColor(DARK_BROWN)
        c.drawString(x + 5 * mm, ly, label)
        
        c.setLineWidth(0.5)
        c.setStrokeColor(HexColor("#EAE5DE"))
        lw = c.stringWidth(label, "Montserrat-Bold", 8)
        c.line(x + 5 * mm + lw + 3 * mm, ly, x + w - 5 * mm, ly)

def create_money_page(c, width, height, is_landscape, month_num):
    """Сборка страницы финансов."""
    month_name = RIGHT_TABS[month_num]
    page_name = f"MONEY_{month_name}"
    draw_base_page(c, width, height, active_top="MONEY", active_right=month_name, page_name=page_name)
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    
    c.setFillColor(DARK_BROWN)
    title_str = f"{calendar.month_name[month_num].upper()} BUDGET"
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, title_str)
    
    title_w = c.stringWidth(title_str, "Playfair-Bold", 24)
    c.setFont("Montserrat", 10)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(margin_x + title_w + 5 * mm, content_y + 2 * mm, "| Finance without the overwhelm")
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 7)
    c.drawString(margin_x, content_y + 8 * mm, f"← BACK TO {month_name}")
    c.linkAbsolute(f"MONTH_{month_name}", f"MONTH_{month_name}", (margin_x, content_y + 6 * mm, margin_x + 30 * mm, content_y + 12 * mm))
    
    content_y -= 10 * mm
    bottom_margin = 15 * mm
    available_h = content_y - bottom_margin
    gap = 5 * mm
    
    if is_landscape:
        col_w = (main_area_w - gap) / 2
        top_h = available_h * 0.60
        bottom_h = available_h - top_h - gap
        draw_bills_box(c, margin_x, bottom_margin + bottom_h + gap, col_w, top_h)
        draw_no_spend_box(c, margin_x, bottom_margin, col_w, bottom_h)
        col2_x = margin_x + col_w + gap
        draw_jars_box(c, col2_x, bottom_margin + bottom_h + gap, col_w, top_h)
        draw_overview_box(c, col2_x, bottom_margin, col_w, bottom_h)
    else:
        row_h = (available_h - 2 * gap) / 3
        draw_bills_box(c, margin_x, bottom_margin + 2 * (row_h + gap), main_area_w, row_h)
        draw_jars_box(c, margin_x, bottom_margin + row_h + gap, main_area_w, row_h)
        col_w = (main_area_w - gap) / 2
        draw_no_spend_box(c, margin_x, bottom_margin, col_w, row_h)
        draw_overview_box(c, margin_x + col_w + gap, bottom_margin, col_w, row_h)
        
    c.showPage()


def draw_reset_box(c, x, y, w, h, title, subtitle, items):
    """Отрисовка блока еженедельной перезагрузки с чекбоксами."""
    c.setFillColor(BOX_BG_COLOR)
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 10)
    c.drawString(x + 5 * mm, y + h - 8 * mm, title)
    
    title_w = c.stringWidth(title, "Montserrat-Bold", 10)
    c.setLineWidth(0.5)
    c.setStrokeColor(HexColor("#EAE5DE"))
    c.line(x + 5 * mm + title_w + 3 * mm, y + h - 8 * mm, x + w - 5 * mm, y + h - 8 * mm)
    
    c.setFont("Montserrat", 8)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(x + 5 * mm, y + h - 14 * mm, subtitle)
    
    line_y = y + h - 24 * mm
    for item in items:
        if item.startswith(">"):
            prompt_txt = item[1:].strip()
            c.setFont("Montserrat-Bold", 8)
            c.setFillColor(DARK_BROWN)
            c.drawString(x + 5 * mm, line_y + 1.2 * mm, prompt_txt)
            
            pw = c.stringWidth(prompt_txt, "Montserrat-Bold", 8)
            c.setLineWidth(0.5)
            c.setStrokeColor(HexColor("#EAE5DE"))
            c.line(x + 5 * mm + pw + 2 * mm, line_y + 1.2 * mm, x + w - 5 * mm, line_y + 1.2 * mm)
        else:
            c.setFillColor(HexColor("#FFFFFF"))
            c.setStrokeColor(HexColor("#D8D0C5"))
            c.setLineWidth(1)
            c.rect(x + 5 * mm, line_y, 4 * mm, 4 * mm, fill=1, stroke=1)
            
            if item:
                c.setFont("Montserrat", 8)
                c.setFillColor(DARK_BROWN)
                c.drawString(x + 12 * mm, line_y + 1.2 * mm, item)
            else:
                c.setLineWidth(0.5)
                c.setStrokeColor(HexColor("#EAE5DE"))
                c.line(x + 12 * mm, line_y + 1 * mm, x + w - 5 * mm, line_y + 1 * mm)
                
        line_y -= 8 * mm

    while line_y > y + 5 * mm:
        c.setFillColor(HexColor("#FFFFFF"))
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.setLineWidth(1)
        c.rect(x + 5 * mm, line_y, 4 * mm, 4 * mm, fill=1, stroke=1)
        
        c.setLineWidth(0.5)
        c.setStrokeColor(HexColor("#EAE5DE"))
        c.line(x + 12 * mm, line_y + 1 * mm, x + w - 5 * mm, line_y + 1 * mm)
        line_y -= 8 * mm

def create_weekly_reset_page(c, width, height, is_landscape):
    """Страница Weekly Reset."""
    draw_base_page(c, width, height, active_top="WEEKLY RESET", page_name="WEEKLY RESET")
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    
    c.setFillColor(DARK_BROWN)
    title_str = "WEEKLY RESET"
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, title_str)
    
    title_w = c.stringWidth(title_str, "Playfair-Bold", 24)
    c.setFont("Montserrat", 10)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(margin_x + title_w + 5 * mm, content_y + 2 * mm, "| Close the loops and start fresh")
    
    content_y -= 10 * mm
    bottom_margin = 15 * mm
    available_h = content_y - bottom_margin
    gap = 5 * mm
    
    space_items = [
        "Clear physical workspace", 
        "Empty trash & recycling", 
        "Tame the email inbox", 
        "Close unnecessary browser tabs", 
        "Organize downloads folder", 
        "Prep clothes for Monday"
    ]
    
    mind_items = [
        "Brain dump lingering thoughts", 
        "Forgive myself for what I didn't do", 
        "Reflect on what went well", 
        "> BIGGEST WIN:", 
        "> I AM GRATEFUL FOR:", 
        ">", 
        ">"
    ]
    
    schedule_items = [
        "Review upcoming appointments", 
        "Migrate unfinished tasks", 
        "Cancel or say 'no' to one thing", 
        "Schedule deep work blocks", 
        "Schedule guilt-free rest time", 
        "Plan meals for the week"
    ]
    
    if is_landscape:
        col_w = (main_area_w - 2 * gap) / 3
        draw_reset_box(c, margin_x, bottom_margin, col_w, available_h, "1. CLEAR SPACE", "Tidy your physical and digital environment", space_items)
        draw_reset_box(c, margin_x + col_w + gap, bottom_margin, col_w, available_h, "2. CLEAR MIND", "Process the past week and let it go", mind_items)
        draw_reset_box(c, margin_x + 2 * col_w + 2 * gap, bottom_margin, col_w, available_h, "3. CLEAR SCHEDULE", "Set boundaries and intentions for next week", schedule_items)
    else:
        row_h = (available_h - 2 * gap) / 3
        draw_reset_box(c, margin_x, bottom_margin + 2 * (row_h + gap), main_area_w, row_h, "1. CLEAR SPACE", "Tidy your physical and digital environment", space_items)
        draw_reset_box(c, margin_x, bottom_margin + row_h + gap, main_area_w, row_h, "2. CLEAR MIND", "Process the past week and let it go", mind_items)
        draw_reset_box(c, margin_x, bottom_margin, main_area_w, row_h, "3. CLEAR SCHEDULE", "Set boundaries and intentions for next week", schedule_items)

    c.showPage()



def draw_habit_block(c, x, y, w, h):
    """Карточка привычки с трекером частоты (без привязки к датам)."""
    c.setFillColor(BOX_BG_COLOR)
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 9)
    title_str = "HABIT:"
    c.drawString(x + 5 * mm, y + h - 9 * mm, title_str)
    
    title_w = c.stringWidth(title_str, "Montserrat-Bold", 9)
    c.setLineWidth(0.5)
    c.setStrokeColor(HexColor("#EAE5DE"))
    c.line(x + 5 * mm + title_w + 2 * mm, y + h - 9 * mm, x + w - 5 * mm, y + h - 9 * mm)
    
    c.setFillColor(HexColor("#A89F91"))
    c.setFont("Montserrat-Bold", 7)
    why_str = "WHY:"
    c.drawString(x + 5 * mm, y + h - 17 * mm, why_str)
    
    why_w = c.stringWidth(why_str, "Montserrat-Bold", 7)
    c.line(x + 5 * mm + why_w + 2 * mm, y + h - 17 * mm, x + w - 5 * mm, y + h - 17 * mm)
    
    cols = 8
    rows = 4
    radius = 2.5 * mm
    gap = 2 * mm
    
    grid_w = cols * (radius * 2) + (cols - 1) * gap
    offset_x = (w - grid_w) / 2  
    
    start_x = x + offset_x + radius
    start_y = y + h - 28 * mm - radius
    
    c.setLineWidth(1)
    c.setStrokeColor(HexColor("#E3DFD5"))
    c.setFillColor(HexColor("#FFFFFF"))
    
    count = 1
    for r in range(rows):
        for col in range(cols):
            if count > 31: 
                break
            cx = start_x + col * (radius * 2 + gap)
            cy = start_y - r * (radius * 2 + gap)
            c.circle(cx, cy, radius, fill=1, stroke=1)
            count += 1

def create_habits_page(c, width, height, is_landscape, month_num):
    month_name = RIGHT_TABS[month_num]
    page_name = f"HABITS_{month_name}"
    draw_base_page(c, width, height, active_top="HABITS", active_right=month_name, page_name=page_name)
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    
    c.setFillColor(DARK_BROWN)
    title_str = f"{calendar.month_name[month_num].upper()} HABITS"
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, title_str)
    
    title_w = c.stringWidth(title_str, "Playfair-Bold", 24)
    c.setFont("Montserrat", 10)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(margin_x + title_w + 5 * mm, content_y + 2 * mm, "| Progress over perfection")
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 7)
    c.drawString(margin_x, content_y + 8 * mm, f"← BACK TO {month_name}")
    c.linkAbsolute(f"MONTH_{month_name}", f"MONTH_{month_name}", (margin_x, content_y + 6 * mm, margin_x + 30 * mm, content_y + 12 * mm))
    
    content_y -= 10 * mm
    bottom_margin = 15 * mm
    available_h = content_y - bottom_margin
    gap = 5 * mm
    
    cols, rows = (4, 2) if is_landscape else (2, 4)
    box_w = (main_area_w - gap * (cols - 1)) / cols
    box_h = (available_h - gap * (rows - 1)) / rows
    
    for r in range(rows):
        for col in range(cols):
            bx = margin_x + col * (box_w + gap)
            by = content_y - (r + 1) * box_h - r * gap
            draw_habit_block(c, bx, by, box_w, box_h)
            
    c.showPage()

def draw_word_of_the_year(c, x, y, w, h):
    draw_vision_box(c, x, y, w, h, "WORD OF THE YEAR")
    c.setLineWidth(0.5)
    c.setStrokeColor(HexColor("#EAE5DE"))
    c.line(x + 10 * mm, y + 10 * mm, x + w - 10 * mm, y + 10 * mm)

def draw_core_values(c, x, y, w, h):
    draw_vision_box(c, x, y, w, h, "CORE VALUES")
    line_y = y + h - 20 * mm
    c.setLineWidth(0.5)
    c.setStrokeColor(HexColor("#EAE5DE"))
    while line_y > y + 5 * mm:
        c.circle(x + 10 * mm, line_y + 1 * mm, 1 * mm, fill=1, stroke=0) # Буллет
        c.line(x + 15 * mm, line_y, x + w - 10 * mm, line_y)
        line_y -= 7 * mm

def draw_bucket_list(c, x, y, w, h):
    """Список желаний / Bucket List вместо банки на странице Vision."""
    draw_vision_box(c, x, y, w, h, "BUCKET LIST")
    
    c.setFont("Montserrat", 7)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(x + 5 * mm, y + h - 13 * mm, "Things I want to do, see, or experience")
    
    line_y = y + h - 22 * mm
    c.setLineWidth(0.5)
    
    while line_y > y + 5 * mm:
        c.setFillColor(HexColor("#FFFFFF"))
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.rect(x + 5 * mm, line_y, 3 * mm, 3 * mm, fill=1, stroke=1)
        
        c.setStrokeColor(HexColor("#EAE5DE"))
        c.line(x + 10 * mm, line_y, x + w - 5 * mm, line_y)
        line_y -= 6.5 * mm

def draw_vision_box(c, x, y, w, h, title):
    """Базовый блок для страницы визуализации."""
    c.setFillColor(BOX_BG_COLOR)
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
    
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 10)
    c.drawString(x + 5 * mm, y + h - 8 * mm, title)
    
    title_w = c.stringWidth(title, "Montserrat-Bold", 10)
    c.setLineWidth(0.5)
    c.setStrokeColor(HexColor("#EAE5DE"))
    c.line(x + 5 * mm + title_w + 3 * mm, y + h - 8 * mm, x + w - 5 * mm, y + h - 8 * mm)

def draw_vision_board(c, x, y, w, h):
    """Область для мудборда / доски визуализации."""
    c.setFillColor(BOX_BG_COLOR)
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
    
    c.setDash(4, 4)
    c.setLineWidth(1)
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.roundRect(x + 5 * mm, y + 5 * mm, w - 10 * mm, h - 10 * mm, 2 * mm, fill=0, stroke=1)
    c.setDash() 
    
    c.setFillColor(HexColor("#A89F91"))
    c.setFont("Montserrat-Bold", 12)
    c.drawCentredString(x + w/2, y + h/2, "+ ADD PHOTOS, QUOTES & STICKERS HERE")
    c.setFont("Montserrat", 8)
    c.drawCentredString(x + w/2, y + h/2 - 5 * mm, "Use the image tool in GoodNotes")

def draw_word_of_the_year(c, x, y, w, h):
    draw_vision_box(c, x, y, w, h, "WORD OF THE YEAR")
    c.setLineWidth(0.5)
    c.setStrokeColor(HexColor("#EAE5DE"))
    c.line(x + 10 * mm, y + 10 * mm, x + w - 10 * mm, y + 10 * mm)

def draw_core_values(c, x, y, w, h):
    draw_vision_box(c, x, y, w, h, "CORE VALUES")
    line_y = y + h - 20 * mm
    c.setLineWidth(0.5)
    c.setStrokeColor(HexColor("#EAE5DE"))
    while line_y > y + 5 * mm:
        c.circle(x + 10 * mm, line_y + 1 * mm, 1 * mm, fill=1, stroke=0) 
        c.line(x + 15 * mm, line_y, x + w - 10 * mm, line_y)
        line_y -= 7 * mm

def draw_bucket_list(c, x, y, w, h):
    """Список желаний / Bucket List вместо банки на странице Vision."""
    draw_vision_box(c, x, y, w, h, "BUCKET LIST")
    
    c.setFont("Montserrat", 7)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(x + 5 * mm, y + h - 13 * mm, "Things I want to do, see, or experience")
    
    line_y = y + h - 22 * mm
    c.setLineWidth(0.5)
    
    while line_y > y + 5 * mm:
        c.setFillColor(HexColor("#FFFFFF"))
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.rect(x + 5 * mm, line_y, 3 * mm, 3 * mm, fill=1, stroke=1)
        
        c.setStrokeColor(HexColor("#EAE5DE"))
        c.line(x + 10 * mm, line_y, x + w - 5 * mm, line_y)
        line_y -= 6.5 * mm

def create_vision_page(c, width, height, is_landscape, active_tab="VISION"):
    draw_base_page(c, width, height, active_top=active_tab, page_name=active_tab)
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    
    c.setFillColor(DARK_BROWN)
    title_str = "VISION BOARD"
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, title_str)
    
    title_w = c.stringWidth(title_str, "Playfair-Bold", 24)
    c.setFont("Montserrat", 10)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(margin_x + title_w + 5 * mm, content_y + 2 * mm, "| Dream big, make it happen")
    
    content_y -= 10 * mm
    bottom_margin = 15 * mm
    available_h = content_y - bottom_margin
    gap = 5 * mm
    
    if is_landscape:
        left_w = main_area_w * 0.35
        right_w = main_area_w - left_w - gap
        
        word_h = available_h * 0.15
        values_h = available_h * 0.35 - gap
        bucket_h = available_h * 0.50 - gap
        
        draw_word_of_the_year(c, margin_x, bottom_margin + values_h + bucket_h + 2*gap, left_w, word_h)
        draw_core_values(c, margin_x, bottom_margin + bucket_h + gap, left_w, values_h)
        draw_bucket_list(c, margin_x, bottom_margin, left_w, bucket_h)
        
        draw_vision_board(c, margin_x + left_w + gap, bottom_margin, right_w, available_h)
    else:
        top_h = available_h * 0.15
        mid_h = available_h * 0.45 - gap
        bot_h = available_h * 0.40 - gap
        
        col_w = (main_area_w - gap) / 2
        draw_word_of_the_year(c, margin_x, bottom_margin + mid_h + bot_h + 2*gap, col_w, top_h)
        draw_core_values(c, margin_x + col_w + gap, bottom_margin + mid_h + bot_h + 2*gap, col_w, top_h)
        
        draw_vision_board(c, margin_x, bottom_margin + bot_h + gap, main_area_w, mid_h)
        draw_bucket_list(c, margin_x, bottom_margin, main_area_w, bot_h)
        
    c.showPage()


def create_guide_page(c, width, height, is_landscape):
    draw_base_page(c, width, height, active_top="GUIDE", page_name="GUIDE")
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    
    c.setFillColor(DARK_BROWN)
    title_str = "WELCOME & GUIDE"
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, title_str)
    
    title_w = c.stringWidth(title_str, "Playfair-Bold", 24)
    c.setFont("Montserrat", 10)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(margin_x + title_w + 5 * mm, content_y + 2 * mm, "| How to use your low-overwhelm planner")
    
    content_y -= 10 * mm
    bottom_margin = 15 * mm
    available_h = content_y - bottom_margin
    gap = 5 * mm
    
    manifesto_title = "THIS IS A SAFE SPACE FOR YOUR THOUGHTS & GOALS."
    manifesto_body = "Traditional planners can feel like a test you're bound to fail. This one is different. There are no 'broken chains' or empty spaces to feel guilty about. If you miss a day, a week, or a habit—simply start again whenever you are ready. This planner bends to your life, not the other way around."
    
    tips = [
        ("TAP ANYTHING TO NAVIGATE", "Every tab on the top and right is a live hyperlink. Tap individual days on Monthly or Weekly layouts to jump to Daily pages. Use '← BACK' to return."),
        ("DOUBLE YOUR PAGES", "Need more space? Tap 'Add Page' → 'Current Template' in GoodNotes to duplicate any page without breaking links."),
        ("USE THE LASSO FOR STICKERS", "Go to the STICKERS page, use the Lasso tool to select any element, copy it, and paste it anywhere to decorate.")
    ]

    palette = [
        ("TERRACOTTA", "#E07A5F", "Warm focus & headers"),
        ("SAGE", "#81B29A", "Tasks & habit dots"),
        ("MUSTARD", "#F2CC8F", "Highlights & wins"),
        ("BLUSH ROSE", "#E5B299", "Notes & stickers"),
        ("DEEP NAVY", "#3D405B", "Bold priorities"),
        ("OATMEAL", "#F4F1DE", "Soft backgrounds")
    ]

    def draw_palette_card(cx, cy, cw, ch, name, hex_val, desc):
        c.setFillColor(BOX_BG_COLOR)
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.roundRect(cx, cy, cw, ch, 2*mm, fill=1, stroke=1)
        
        c.setFillColor(HexColor(hex_val))
        c.circle(cx + 8 * mm, cy + ch/2, 4.5 * mm, fill=1, stroke=0)
        
        text_x = cx + 15 * mm
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat-Bold", 7)
        c.drawString(text_x, cy + ch/2 + 2 * mm, name)
        
        c.setFont("Montserrat", 6.5)
        c.setFillColor(HexColor("#A89F91"))
        c.drawString(text_x, cy + ch/2 - 1.5 * mm, hex_val)
        
        c.setFillColor(DARK_BROWN)
        c.drawString(text_x, cy + ch/2 - 5.5 * mm, desc)

    def draw_wrapped_text(c, text, font, size, x, y, max_w, line_height):
        c.setFont(font, size) # <-- ИСПРАВЛЕНИЕ ЗДЕСЬ: Жестко применяем нужный шрифт
        words = text.split()
        lines, current_line = [], ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, font, size) < max_w:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
            
        for line in lines:
            c.drawString(x, y, line)
            y -= line_height
        return y

    if is_landscape:
        col_w = (main_area_w - gap) / 2
        
        # === ЛЕВАЯ КОЛОНКА ===
        manifest_h = available_h * 0.35
        tips_h = available_h - manifest_h - gap
        
        # Manifesto
        c.setFillColor(BOX_BG_COLOR)
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.roundRect(margin_x, bottom_margin + tips_h + gap, col_w, manifest_h, 2*mm, fill=1, stroke=1)
        
        start_y = bottom_margin + tips_h + gap + manifest_h - 12 * mm
        c.setFillColor(HexColor("#E07A5F")) 
        next_y = draw_wrapped_text(c, manifesto_title, "Montserrat-Bold", 8, margin_x + 8 * mm, start_y, col_w - 18 * mm, 4.5 * mm)
        
        next_y -= 1 * mm 
        c.setFillColor(DARK_BROWN)
        draw_wrapped_text(c, manifesto_body, "Montserrat", 8.5, margin_x + 8 * mm, next_y, col_w - 18 * mm, 4 * mm)
            
        # Tips (динамический отступ)
        c.setFillColor(BOX_BG_COLOR)
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.roundRect(margin_x, bottom_margin, col_w, tips_h, 2*mm, fill=1, stroke=1)
        
        ty = bottom_margin + tips_h - 10 * mm
        for title, body in tips:
            c.setFillColor(DARK_BROWN)
            c.setFont("Montserrat-Bold", 8.5)
            c.drawString(margin_x + 8 * mm, ty, title)
            
            c.setFillColor(HexColor("#8C8377"))
            ty = draw_wrapped_text(c, body, "Montserrat", 8, margin_x + 8 * mm, ty - 4.5 * mm, col_w - 18 * mm, 3.8 * mm)
            ty -= 3 * mm

        # === ПРАВАЯ КОЛОНКА ===
        col2_x = margin_x + col_w + gap
        c.setFillColor(BOX_BG_COLOR)
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.roundRect(col2_x, bottom_margin, col_w, available_h, 2*mm, fill=1, stroke=1)
        
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat-Bold", 10)
        c.drawString(col2_x + 8 * mm, bottom_margin + available_h - 12 * mm, "CUSTOM COLOR PALETTE")
        c.setFont("Montserrat", 8.5)
        c.setFillColor(HexColor("#A89F91"))
        c.drawString(col2_x + 8 * mm, bottom_margin + available_h - 18 * mm, "Copy these HEX codes to customize your pens:")
        
        card_h = (available_h - 30 * mm - 5 * gap) / 6
        for i, (name, hex_val, desc) in enumerate(palette):
            cy = bottom_margin + available_h - 28 * mm - (i + 1) * card_h - i * gap
            draw_palette_card(col2_x + 8 * mm, cy, col_w - 16 * mm, card_h, name, hex_val, desc)
            
    else:
        # Вертикально
        manifest_h = available_h * 0.28 
        tips_h = available_h * 0.44
        palette_h = available_h - manifest_h - tips_h - 2 * gap
        
        # Manifesto
        c.setFillColor(BOX_BG_COLOR)
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.roundRect(margin_x, bottom_margin + tips_h + palette_h + 2 * gap, main_area_w, manifest_h, 2*mm, fill=1, stroke=1)
        
        start_y = bottom_margin + tips_h + palette_h + 2 * gap + manifest_h - 12 * mm
        c.setFillColor(HexColor("#E07A5F"))
        next_y = draw_wrapped_text(c, manifesto_title, "Montserrat-Bold", 8.5, margin_x + 8 * mm, start_y, main_area_w - 18 * mm, 4.5 * mm)
        
        next_y -= 1 * mm
        c.setFillColor(DARK_BROWN)
        draw_wrapped_text(c, manifesto_body, "Montserrat", 8.5, margin_x + 8 * mm, next_y, main_area_w - 18 * mm, 4 * mm)

        # Tips
        c.setFillColor(BOX_BG_COLOR)
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.roundRect(margin_x, bottom_margin + palette_h + gap, main_area_w, tips_h, 2*mm, fill=1, stroke=1)
        
        ty = bottom_margin + palette_h + gap + tips_h - 10 * mm
        for title, body in tips:
            c.setFillColor(DARK_BROWN)
            c.setFont("Montserrat-Bold", 8.5)
            c.drawString(margin_x + 8 * mm, ty, title)
            
            c.setFillColor(HexColor("#8C8377"))
            ty = draw_wrapped_text(c, body, "Montserrat", 8, margin_x + 8 * mm, ty - 4.5 * mm, main_area_w - 18 * mm, 3.8 * mm)
            ty -= 3 * mm

        # Palette
        c.setFillColor(BOX_BG_COLOR)
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.roundRect(margin_x, bottom_margin, main_area_w, palette_h, 2*mm, fill=1, stroke=1)
        
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat-Bold", 9)
        c.drawString(margin_x + 8 * mm, bottom_margin + palette_h - 10 * mm, "CUSTOM COLOR PALETTE")
        
        card_w = (main_area_w - 21 * mm) / 2
        card_h = (palette_h - 16 * mm - 2 * gap) / 3
        
        for i, (name, hex_val, desc) in enumerate(palette):
            col = i % 2
            row = i // 2
            cx = margin_x + 8 * mm + col * (card_w + gap)
            cy = bottom_margin + palette_h - 15 * mm - (row + 1) * card_h - row * gap
            draw_palette_card(cx, cy, card_w, card_h, name, hex_val, desc)

    c.showPage()


def create_notes_pages(c, width, height, is_landscape, num_sets=3):
    """Генерирует раздел заметок (Линейка, Клетка, Точка, Пустые листы)."""
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor

    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    top_y = height - 35 * mm
    bottom_y = 15 * mm
    
    styles = [
        ("LINED", 7 * mm),   # Линейка (шаг 7 мм)
        ("GRID", 5 * mm),    # Клетка (шаг 5 мм)
        ("DOTTED", 5 * mm),  # Точка (шаг 5 мм)
        ("BLANK", 0)         # Пустой лист
    ]
    
    first_page = True
    
    for _ in range(num_sets):
        for style, step in styles:
            # Вешаем закладку "NOTES" только на самую первую страницу раздела
            page_name = "NOTES" if first_page else ""
            first_page = False
            
            draw_base_page(c, width, height, active_top="NOTES", page_name=page_name)
            
            c.setFillColor(DARK_BROWN)
            c.setFont("Playfair-Bold", 24)
            c.drawString(margin_x, height - 25 * mm, f"NOTES · {style}")
            
            c.setStrokeColor(HexColor("#EAE5DE"))
            c.setFillColor(HexColor("#D8D0C5"))
            c.setLineWidth(0.5)
            
            if style == "LINED":
                y = top_y
                while y > bottom_y:
                    c.line(margin_x, y, margin_x + main_area_w, y)
                    y -= step
                    
            elif style == "GRID":
                y = top_y
                while y > bottom_y:
                    c.line(margin_x, y, margin_x + main_area_w, y)
                    y -= step
                x = margin_x
                while x < margin_x + main_area_w:
                    c.line(x, top_y, x, bottom_y)
                    x += step
                    
            elif style == "DOTTED":
                y = top_y
                while y > bottom_y:
                    x = margin_x
                    while x < margin_x + main_area_w:
                        c.circle(x, y, 0.5 * mm, fill=1, stroke=0)
                        x += step
                    y -= step
                    
            c.showPage()

def create_win_jar_page(c, width, height, is_landscape):
    draw_base_page(c, width, height, active_top="WIN JAR", page_name="WIN JAR")
    
    margin_x = 15 * mm
    main_area_w = width - margin_x - (25 * mm if is_landscape else 20 * mm)
    content_y = height - 25 * mm
    bottom_margin = 15 * mm
    
    c.setFillColor(DARK_BROWN)
    title_str = "THE WIN JAR"
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, title_str)
    
    title_w = c.stringWidth(title_str, "Playfair-Bold", 24)
    c.setFont("Montserrat", 10)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(margin_x + title_w + 5 * mm, content_y + 2 * mm, "| Celebrate your progress, big and small")
    
    content_y -= 10 * mm
    available_h = content_y - bottom_margin
    gap = 4 * mm
    
    if is_landscape: 
        cols, rows = 4, 3
    else: 
        cols, rows = 3, 4
        
    card_w = (main_area_w - gap * (cols - 1)) / cols
    card_h = (available_h - gap * (rows - 1)) / rows
    
    import calendar
    for i in range(12):
        col = i % cols
        row = i // cols
        
        cx = margin_x + col * (card_w + gap)
        cy = content_y - (row + 1) * card_h - row * gap
        
        # Параметры банки
        jw = card_w * 0.85
        jh = card_h - 10 * mm
        jx = cx + (card_w - jw) / 2
        jy = cy + 2 * mm
        
        c.setLineWidth(1.2)
        c.setStrokeColor(DARK_BROWN)
        c.setFillColor(BOX_BG_COLOR)
        
        # Отрисовка банки
        lid_w = jw - 10 * mm
        c.roundRect(jx + (jw - lid_w)/2, jy + jh - 3 * mm, lid_w, 3 * mm, 1 * mm, fill=1, stroke=1)
        
        neck_w = jw - 16 * mm
        c.rect(jx + (jw - neck_w)/2, jy + jh - 6 * mm, neck_w, 3 * mm, fill=1, stroke=1)
        
        c.roundRect(jx, jy, jw, jh - 6 * mm, 3 * mm, fill=1, stroke=1)
        
        # Плашка с названием месяца внутри банки
        c.setFillColor(ACCENT_PINK)
        c.roundRect(jx + 2 * mm, jy + jh - 13 * mm, jw - 4 * mm, 6 * mm, 1 * mm, fill=1, stroke=0)
        c.setFillColor(DARK_BROWN)
        c.setFont("Montserrat-Bold", 7)
        c.drawCentredString(jx + jw / 2, jy + jh - 11 * mm, calendar.month_name[i+1].upper())
        
        # Линии для записи побед
        c.setLineWidth(0.5)
        c.setStrokeColor(HexColor("#EAE5DE"))
        ly = jy + jh - 18 * mm
        while ly > jy + 4 * mm:
            c.line(jx + 4 * mm, ly, jx + jw - 4 * mm, ly)
            ly -= 5.5 * mm
            
    c.showPage()


def build_planner(filename, is_landscape=True, sunday_start=False):
    width, height = landscape(A4) if is_landscape else portrait(A4)
    c = canvas.Canvas(filename, pagesize=(width, height))
    
    # 1. ВСТУПЛЕНИЕ И ОБЛОЖКИ (6 вариантов)
    # Формат палитры: (Основной фон, Левая панель, Цвет текста)
    cover_palettes = [
        (BG_COLOR, ACCENT_PINK, DARK_BROWN),                                 # 1. Оригинальная (Светлая овсянка)
        (HexColor("#3D405B"), HexColor("#2F3247"), HexColor("#FFFFFF")),     # 2. Deep Navy (Темно-синяя)
        (HexColor("#81B29A"), HexColor("#6B9982"), HexColor("#FFFFFF")),     # 3. Sage Green (Шалфей)
        (HexColor("#E07A5F"), HexColor("#C7664D"), HexColor("#FFFFFF")),     # 4. Terracotta (Терракота)
        (HexColor("#F2CC8F"), HexColor("#E0BC84"), DARK_BROWN),              # 5. Mustard (Горчичная)
        (HexColor("#E5B299"), HexColor("#D4A58E"), DARK_BROWN),              # 6. Blush Rose (Пыльная роза)
    ]
    
    for i, (bg, acc, txt) in enumerate(cover_palettes):
        if i == 0:
            c.bookmarkPage("COVER") # Закладка ставится только на самую первую обложку
        create_cover(c, width, height, bg, acc, txt)
        
    create_home_page(c, width, height, is_landscape)
    
    # 2. ГЛОБАЛЬНЫЕ СТРАНИЦЫ
    create_year_page(c, width, height, is_landscape, sunday_start) 
    create_brain_dump_page(c, width, height, is_landscape)
    create_done_list_page(c, width, height, is_landscape) 
    create_focus_log_page(c, width, height, is_landscape)
    create_weekly_reset_page(c, width, height, is_landscape)
    
    # --- ТОЛЬКО ОДНА WIN JAR И ОДНА VISION ---
    create_win_jar_page(c, width, height, is_landscape)
    create_vision_page(c, width, height, is_landscape, active_tab="VISION")
    # -----------------------------------------
    
    create_guide_page(c, width, height, is_landscape)
    create_notes_pages(c, width, height, is_landscape, num_sets=3)
    create_stickers_page(c, width, height, is_landscape)

    # 3. КАЛЕНДАРНАЯ ЧАСТЬ И ЕЖЕМЕСЯЧНЫЕ ТРЕКЕРЫ
    for month_num in range(1, 13):
        create_month_page(c, width, height, is_landscape, month_num, sunday_start)
        create_habits_page(c, width, height, is_landscape, month_num)
        create_money_page(c, width, height, is_landscape, month_num)

    import datetime
    start_date = datetime.date(YEAR, 1, 1)
    end_date = datetime.date(YEAR, 12, 31)
    
    unique_weeks = set()
    temp_date = start_date
    while temp_date <= end_date:
        iso_y, iso_w, _ = temp_date.isocalendar()
        unique_weeks.add((iso_y, iso_w))
        temp_date += datetime.timedelta(days=1)
        
    for iso_y, iso_w in sorted(list(unique_weeks)):
        create_weekly_page(c, width, height, is_landscape, iso_y, iso_w, sunday_start)

    current_date = start_date
    delta = datetime.timedelta(days=1)
    while current_date <= end_date:
        create_daily_page(c, width, height, is_landscape, current_date)
        current_date += delta
        
    c.save()
    print(f"PDF успешно сгенерирован: {filename}")



if __name__ == "__main__":
    # Импортируем модуль для создания папок (если их нет)
    import os
    
    for theme_name in THEMES.keys():
        print(f"\n=== Стартуем генерацию темы: {theme_name.upper()} ===")
        apply_theme(theme_name)
        
        # Создаем папку для темы, чтобы файлы не перемешались
        if not os.path.exists(theme_name):
            os.makedirs(theme_name)
            
        # Версии с Понедельника (MONDAY START)
        f_horiz_mon = os.path.join(theme_name, f"{PLANNER_NAME}_{theme_name}_Landscape_Mon_2028.pdf")
        f_vert_mon = os.path.join(theme_name, f"{PLANNER_NAME}_{theme_name}_Portrait_Mon_2028.pdf")
        build_planner(f_horiz_mon, is_landscape=True, sunday_start=False)
        build_planner(f_vert_mon, is_landscape=False, sunday_start=False)
        
        # Версии с Воскресенья (SUNDAY START)
        f_horiz_sun = os.path.join(theme_name, f"{PLANNER_NAME}_{theme_name}_Landscape_Sun_2028.pdf")
        f_vert_sun = os.path.join(theme_name, f"{PLANNER_NAME}_{theme_name}_Portrait_Sun_2028.pdf")
        build_planner(f_horiz_sun, is_landscape=True, sunday_start=True)
        build_planner(f_vert_sun, is_landscape=False, sunday_start=True)
        
    print("\n✅ Все 20 файлов успешно сгенерированы и разложены по папкам!")

