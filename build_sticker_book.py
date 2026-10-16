import os
import io
import zipfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Проверяем и регистрируем шрифты явно
font_paths = {
    'Montserrat': 'fonts/Montserrat-Regular.ttf',
    'Montserrat-Bold': 'fonts/Montserrat-Bold.ttf',
    'Playfair-Bold': 'fonts/PlayfairDisplay-Bold.ttf'
}

for font_name, path in font_paths.items():
    if os.path.exists(path):
        pdfmetrics.registerFont(TTFont(font_name, path))
        print(f"Шрифт успешно зарегистрирован: {font_name} ({path})")
    else:
        # Если файл не найден в папке fonts/, пробуем искать в корне проекта
        root_path = os.path.basename(path)
        if os.path.exists(root_path):
            pdfmetrics.registerFont(TTFont(font_name, root_path))
            print(f"Шрифт успешно зарегистрирован из корня: {font_name} ({root_path})")
        else:
            print(f"❌ ОШИБКА: Не найден файл шрифта для {font_name} по пути '{path}'!")




try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("ВНИМАНИЕ: Библиотека Pillow не найдена. Установите её: pip install Pillow")

# Фирменная палитра EasyFocus
BG_COLOR = HexColor("#F6F2EB")
ACCENT_PINK = HexColor("#F1E4DC")
ACCENT_GREEN = HexColor("#E2EBE5")
DARK_BROWN = HexColor("#433D34")
TAB_BG_ACTIVE = HexColor("#433D34")
TAB_TEXT_ACTIVE = HexColor("#FFFFFF")
BOX_BG_COLOR = HexColor("#FCFAF5")
B_TERRA = HexColor("#E07A5F")

# 7 категорий вашего бандла на 1000 стикеров:
# (Код вкладки, Полное название, Описание, Варианты названий папок или .zip архивов)
CATEGORIES = [
    ("INDEX", "COLLECTION INDEX", "All 7 sticker collections at a glance", []),
    ("FUNCTIONAL", "FUNCTIONAL STICKERS", "Labels, reminders, frames & planning essentials", ["functional", "Functional"]),
    ("BOHO", "BOHO & ABSTRACT", "Minimalist shapes, arches, rainbows & line art", ["boho", "Boho-Abstract", "boho-abstract"]),
    ("BOTANICAL", "BOTANICAL GARDEN", "Pressed leaves, wildflowers & organic nature", ["botanical", "Botanical"]),
    ("COZY", "COZY LIFE", "Warm coffee, books, candles & home aesthetics", ["cozy", "Cozy"]),
    ("FOOD", "FOOD & DRINKS", "Healthy meals, sweet treats & kitchen icons", ["food", "Food"]),
    ("MEANINGFUL", "MEANINGFUL QUOTES", "Mindfulness, gentle affirmations & positivity", ["meaningful", "Meaningful"]),
    ("ANIMALS", "CUTE ANIMALS", "Playful pets, woodland creatures & companions", ["animals", "Animals"]),
]


def draw_folder_tab_bg(c, x, y, w, h, radius):
    """Отрисовка реалистичной верхней вкладки-папки."""
    c.setStrokeColor(HexColor("#D8D0C5"))
    c.setLineWidth(0.5)
    p = c.beginPath()
    p.moveTo(x, y)
    p.lineTo(x, y + h - radius)
    p.arcTo(x, y + h - 2 * radius, x + 2 * radius, y + h, 180, -90)
    p.lineTo(x + w - radius, y + h)
    p.arcTo(x + w - 2 * radius, y + h - 2 * radius, x + w, y + h, 90, -90)
    p.lineTo(x + w, y)
    p.close()
    c.drawPath(p, fill=1, stroke=1)


def draw_top_category_tabs(c, width, height, active_tab=""):
    """Верхнее меню навигации по 7 категориям стикеров + INDEX."""
    tab_height = 10 * mm
    margin_y = height - tab_height
    margin_x = 15 * mm
    available_width = width - 30 * mm
    tab_width = available_width / len(CATEGORIES)
    radius = 2 * mm

    c.setFont("Montserrat-Bold", 7)
    for i, (tab_id, _, _, _) in enumerate(CATEGORIES):
        x = margin_x + i * tab_width
        y = margin_y

        if tab_id == active_tab:
            c.setFillColor(TAB_BG_ACTIVE)
            draw_folder_tab_bg(c, x, y, tab_width - 1.5 * mm, tab_height, radius)
            c.setFillColor(TAB_TEXT_ACTIVE)
        else:
            bg_color = ACCENT_PINK if i % 2 == 0 else ACCENT_GREEN
            c.setFillColor(bg_color)
            draw_folder_tab_bg(c, x, y, tab_width - 1.5 * mm, tab_height, radius)
            c.setFillColor(DARK_BROWN)

        c.drawCentredString(x + (tab_width - 1.5 * mm) / 2, y + 3.5 * mm, tab_id)
        c.linkAbsolute(f"CAT_{tab_id}", f"CAT_{tab_id}", (x, y, x + tab_width - 1.5 * mm, y + tab_height))


def load_category_stickers(base_dir, candidates):
    """
    Находит все PNG для категории:
    1) Сначала проверяет распакованные папки (включая подпапки).
    2) Если папки нет, проверяет наличие .zip архива и читает PNG прямо из него!
    Возвращает список кортежей: (имя_файла, байты_или_путь)
    """
    items = []

    # 1. Поиск в обычных папках
    for cand in candidates:
        folder_path = os.path.join(base_dir, cand)
        if os.path.isdir(folder_path):
            for root, _, files in os.walk(folder_path):
                for f in sorted(files):
                    if f.lower().endswith(".png") and not f.startswith("._") and "__MACOSX" not in root:
                        items.append((f, os.path.join(root, f)))
            if items:
                return items

    # 2. Поиск в .zip архивах (если не распакованы)
    for cand in candidates:
        for zip_Location in [
            os.path.join(base_dir, f"{cand}.zip"),
            os.path.join(base_dir, cand, f"{cand.lower()}.zip")
        ]:
            if os.path.isfile(zip_Location):
                try:
                    with zipfile.ZipFile(zip_Location, 'r') as zf:
                        for name in sorted(zf.namelist()):
                            if name.lower().endswith(".png") and not os.path.basename(name).startswith("._") and "__MACOSX" not in name:
                                items.append((os.path.basename(name), zf.read(name)))
                    if items:
                        return items
                except Exception as e:
                    print(f"Ошибка чтения архива {zip_Location}: {e}")

    return items


def draw_compressed_sticker(c, source, x, y, size, max_px=280):
    """Отрисовывает PNG (из пути на диске или из байтов ZIP) с умным сжатием."""
    try:
        if HAS_PIL:
            if isinstance(source, bytes):
                im = Image.open(io.BytesIO(source))
            else:
                im = Image.open(source)

            with im:
                im = im.convert("RGBA")
                im.thumbnail((max_px, max_px), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                im.save(buf, format="PNG", optimize=True)
                buf.seek(0)
                c.drawImage(ImageReader(buf), x, y, width=size, height=size, mask='auto', preserveAspectRatio=True)
        else:
            if not isinstance(source, bytes):
                c.drawImage(source, x, y, width=size, height=size, mask='auto', preserveAspectRatio=True)
    except Exception as e:
        print(f"Пропущен поврежденный файл стикера: {e}")


def build_sticker_book(output_filename="EasyFocus_Sticker_Book_1000.pdf"):
    width, height = landscape(A4)
    c = canvas.Canvas(output_filename, pagesize=(width, height))
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # Предварительно сканируем все категории, чтобы знать точное число стикеров
    loaded_data = {}
    total_found = 0
    for tab_id, full_name, desc, cands in CATEGORIES[1:]:
        stickers = load_category_stickers(base_dir, cands)
        loaded_data[tab_id] = stickers
        total_found += len(stickers)
        print(f"Категория [{tab_id}]: найдено {len(stickers)} PNG стикеров")

    # ================= 1. ОБЛОЖКА СТИКЕРБУКА =================
    c.bookmarkPage("COVER")
    c.setFillColor(ACCENT_PINK)
    c.rect(0, 0, width * 0.35, height, fill=1, stroke=0)
    c.setFillColor(BG_COLOR)
    c.rect(width * 0.35, 0, width * 0.65, height, fill=1, stroke=0)

    center_x = width * 0.35 + (width * 0.65) / 2
    c.setFillColor(DARK_BROWN)
    c.setFont("Montserrat-Bold", 10)
    c.drawCentredString(center_x, height - 60 * mm, "MINDFLOW COMPANION STICKER BOOK")
    
    c.setFont("Playfair-Bold", 44)
    c.drawCentredString(center_x, height - 80 * mm, "1000+ Aesthetic Stickers")
    
    c.setFont("Montserrat", 12)
    c.drawCentredString(center_x, height - 96 * mm, "7 Curated Collections: Functional, Boho, Botanical, Cozy,")
    c.drawCentredString(center_x, height - 103 * mm, "Food, Meaningful & Animals. Optimized for GoodNotes & Notability.")

    btn_w, btn_h = 110 * mm, 12 * mm
    btn_x, btn_y = center_x - btn_w / 2, height - 145 * mm
    c.setFillColor(DARK_BROWN)
    c.roundRect(btn_x, btn_y, btn_w, btn_h, 4, fill=1, stroke=0)
    c.setFillColor(TAB_TEXT_ACTIVE)
    c.setFont("Montserrat-Bold", 10)
    c.drawCentredString(center_x, btn_y + 4 * mm, "Open Sticker Index →")
    c.linkAbsolute("CAT_INDEX", "CAT_INDEX", (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h))
    c.showPage()


    # ================= 2. ОГЛАВЛЕНИЕ (INDEX) =================
    c.bookmarkPage("CAT_INDEX")
    c.setFillColor(BG_COLOR)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    draw_top_category_tabs(c, width, height, active_tab="INDEX")

    margin_x = 15 * mm
    content_y = height - 25 * mm
    c.setFillColor(DARK_BROWN)
    c.setFont("Playfair-Bold", 24)
    c.drawString(margin_x, content_y, "STICKER COLLECTIONS")
    c.setFont("Montserrat", 10)
    c.setFillColor(HexColor("#A89F91"))
    c.drawString(margin_x + 98 * mm, content_y + 2 * mm, f"| Tap any pack to browse ({total_found} stickers loaded)")

    # Сетка карточек для 7 категорий
    cols, rows = 4, 2
    gap = 6 * mm
    area_w = width - 30 * mm
    area_h = content_y - 30 * mm
    card_w = (area_w - gap * (cols - 1)) / cols
    card_h = (area_h - gap * (rows - 1)) / rows

    for idx, (tab_id, full_name, desc, _) in enumerate(CATEGORIES[1:]):
        col = idx % cols
        row = idx // cols
        cx = margin_x + col * (card_w + gap)
        cy = content_y - 12 * mm - (row + 1) * card_h - row * gap

        c.setFillColor(BOX_BG_COLOR)
        c.setStrokeColor(HexColor("#D8D0C5"))
        c.roundRect(cx, cy, card_w, card_h, 3 * mm, fill=1, stroke=1)

        c.setFillColor(B_TERRA)
        c.setFont("Montserrat-Bold", 8)
        count = len(loaded_data.get(tab_id, []))
        c.drawString(cx + 5 * mm, cy + card_h - 8 * mm, f"COLLECTION 0{idx + 1}  ·  {count} PNGs")

        c.setFillColor(DARK_BROWN)
        c.setFont("Playfair-Bold", 14)
        c.drawString(cx + 5 * mm, cy + card_h - 16 * mm, full_name)

        c.setFont("Montserrat", 8)
        c.setFillColor(HexColor("#8C8377"))
        c.drawString(cx + 5 * mm, cy + card_h - 23 * mm, desc[:42])

        # Превью первых 3 стикеров внутри карточки оглавления
        preview_stickers = loaded_data.get(tab_id, [])[:3]
        for p_idx, (_, src) in enumerate(preview_stickers):
            px = cx + 6 * mm + p_idx * 18 * mm
            py = cy + 6 * mm
            draw_compressed_sticker(c, src, px, py, 15 * mm, max_px=160)

        c.linkAbsolute(f"CAT_{tab_id}", f"CAT_{tab_id}", (cx, cy, cx + card_w, cy + card_h))

    c.showPage()

    # ================= 3. АВТО-ПАГИНАЦИЯ ВСЕХ КАТЕГОРИЙ =================
    cols_per_page = 7
    rows_per_page = 5
    per_page = cols_per_page * rows_per_page  # 35 стикеров на страницу

    for tab_id, full_name, desc, _ in CATEGORIES[1:]:
        stickers = loaded_data.get(tab_id, [])
        total_pages = max(1, (len(stickers) + per_page - 1) // per_page)

        for page_idx in range(total_pages):
            if page_idx == 0:
                c.bookmarkPage(f"CAT_{tab_id}")

            c.setFillColor(BG_COLOR)
            c.rect(0, 0, width, height, fill=1, stroke=0)
            draw_top_category_tabs(c, width, height, active_tab=tab_id)

            # Заголовок страницы категории
            c.setFillColor(DARK_BROWN)
            c.setFont("Playfair-Bold", 22)
            c.drawString(margin_x, content_y, full_name)
            tw = c.stringWidth(full_name, "Playfair-Bold", 22)

            c.setFont("Montserrat", 10)
            c.setFillColor(HexColor("#A89F91"))
            c.drawString(margin_x + tw + 5 * mm, content_y + 1.5 * mm, f"| Page {page_idx + 1} of {total_pages}  ·  Use Lasso tool to copy")

            # Подложка под стикеры
            grid_top = content_y - 8 * mm
            grid_bottom = 15 * mm
            grid_w = width - 30 * mm
            grid_h = grid_top - grid_bottom

            c.setFillColor(BOX_BG_COLOR)
            c.setStrokeColor(HexColor("#D8D0C5"))
            c.roundRect(margin_x, grid_bottom, grid_w, grid_h, 3 * mm, fill=1, stroke=1)

            page_slice = stickers[page_idx * per_page : (page_idx + 1) * per_page]

            if not page_slice:
                c.setFont("Montserrat", 10)
                c.setFillColor(HexColor("#A89F91"))
                c.drawCentredString(width / 2, height / 2, f"Put '{tab_id.lower()}' folder or .zip into project folder to populate this section.")
            else:
                cell_w = (grid_w - 10 * mm) / cols_per_page
                cell_h = (grid_h - 10 * mm) / rows_per_page
                icon_size = min(cell_w, cell_h) - 5 * mm

                for s_idx, (fname, src) in enumerate(page_slice):
                    scol = s_idx % cols_per_page
                    srow = s_idx // cols_per_page

                    sx = margin_x + 5 * mm + scol * cell_w + (cell_w - icon_size) / 2
                    sy = grid_top - 5 * mm - (srow + 1) * cell_h + (cell_h - icon_size) / 2

                    draw_compressed_sticker(c, src, sx, sy, icon_size, max_px=280)

            c.showPage()

    c.save()
    print(f"Готово! Каталог стикеров успешно сохранен: {output_filename}")


if __name__ == "__main__":
    build_sticker_book()
