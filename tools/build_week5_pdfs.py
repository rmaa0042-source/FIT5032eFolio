from pathlib import Path

from PIL import Image, ImageChops
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUTPUT = ROOT / "output" / "pdf"
TMP = ROOT / "tmp" / "pdfs"

PAGE_W, PAGE_H = A4
NAVY = colors.HexColor("#173B69")
BLUE = colors.HexColor("#0D6EFD")
INK = colors.HexColor("#172033")
MUTED = colors.HexColor("#64748B")
PALE = colors.HexColor("#EAF3FF")


def page_frame(pdf, title, subtitle, page_number, total_pages):
    pdf.setFillColor(NAVY)
    pdf.rect(0, PAGE_H - 76, PAGE_W, 76, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 17)
    pdf.drawString(40, PAGE_H - 38, title)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, PAGE_H - 56, subtitle)

    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.line(40, 34, PAGE_W - 40, 34)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(40, 21, "FIT5032 - Week 5 eFolio")
    pdf.drawRightString(PAGE_W - 40, 21, f"Page {page_number} of {total_pages}")


def draw_wrapped(pdf, text, x, y, max_width, font="Helvetica", size=9, leading=13):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    pdf.setFont(font, size)
    for line in lines:
        pdf.drawString(x, y, line)
        y -= leading
    return y


def crop_page_evidence(source, target, mode):
    with Image.open(source).convert("RGB") as image:
        if mode == "home":
            # The Home capture contains a blank browser canvas below the application.
            image = image.crop((0, 0, min(860, image.width), min(730, image.height)))
        elif mode == "app":
            # The in-app browser reserves a white area to the right of the page viewport.
            background = Image.new("RGB", image.size, "white")
            bounds = ImageChops.difference(image, background).getbbox()
            if bounds:
                left, top, right, bottom = bounds
                right = min(right + 12, image.width)
                bottom = min(bottom + 12, image.height)
                image = image.crop((0, 0, right, bottom))
        elif mode == "validation":
            # Keep the application viewport and omit the duplicate DevTools host footer.
            image = image.crop((0, 0, min(843, image.width), min(750, image.height)))
        image.save(target, quality=95)


def draw_image_page(pdf, title, subtitle, image_path, caption, page_number, total_pages):
    page_frame(pdf, title, subtitle, page_number, total_pages)

    box_x = 40
    box_y = 92
    box_w = PAGE_W - 80
    box_h = PAGE_H - 196
    pdf.setFillColor(PALE)
    pdf.roundRect(box_x, box_y, box_w, box_h, 8, fill=1, stroke=0)

    with Image.open(image_path) as image:
        image_w, image_h = image.size
    scale = min((box_w - 18) / image_w, (box_h - 18) / image_h)
    draw_w = image_w * scale
    draw_h = image_h * scale
    draw_x = box_x + (box_w - draw_w) / 2
    draw_y = box_y + (box_h - draw_h) / 2
    pdf.drawImage(
        ImageReader(str(image_path)),
        draw_x,
        draw_y,
        width=draw_w,
        height=draw_h,
        preserveAspectRatio=True,
        mask="auto",
    )

    pdf.setFillColor(INK)
    draw_wrapped(pdf, caption, 40, 69, PAGE_W - 80, size=9, leading=11)
    pdf.showPage()


def draw_code_page(pdf, title, relative_path, page_number, total_pages):
    page_frame(
        pdf,
        title,
        f"Required source file: {relative_path}",
        page_number,
        total_pages,
    )

    source = (ROOT / relative_path).read_text(encoding="utf-8").splitlines()
    code_x = 50
    code_y = PAGE_H - 103
    code_bottom = 50
    available_height = code_y - code_bottom
    leading = min(13, available_height / max(len(source), 1))
    font_size = min(8.5, max(6.5, leading - 2.2))

    pdf.setFillColor(colors.HexColor("#F8FAFC"))
    pdf.roundRect(40, 47, PAGE_W - 80, PAGE_H - 137, 7, fill=1, stroke=0)
    pdf.setFont("Courier", font_size)
    for number, line in enumerate(source, start=1):
        pdf.setFillColor(colors.HexColor("#94A3B8"))
        pdf.drawRightString(code_x + 19, code_y, f"{number:>2}")
        pdf.setFillColor(INK)
        safe_line = line.replace("\t", "  ")
        pdf.drawString(code_x + 29, code_y, safe_line)
        code_y -= leading
    pdf.showPage()


def build_task_51(validation_image, devtools_image):
    destination = OUTPUT / "FIT5032_Week5_Task5.1_Evidence.pdf"
    pdf = canvas.Canvas(str(destination), pagesize=A4)
    pdf.setTitle("FIT5032 Week 5 Task 5.1 Evidence")

    draw_image_page(
        pdf,
        "Task 5.1 - Password confirmation validation",
        "Screenshot 1: Modified Library form",
        validation_image,
        "Test evidence: two different passwords were entered. The form displayed the clear error message: "
        '"Passwords do not match. Please try again."',
        1,
        2,
    )
    draw_image_page(
        pdf,
        "Task 5.1 - Vue DevTools component testing",
        "Screenshot 2: LibraryRegistrationForm reactive state",
        devtools_image,
        "Vue DevTools confirms that LibraryRegistrationForm exposes reactive formData and errors refs. "
        "The expanded confirmPassword error matches the message shown in the user interface.",
        2,
        2,
    )
    pdf.save()
    return destination


def build_task_52(home_image, about_image):
    destination = OUTPUT / "FIT5032_Week5_Task5.2_Submission.pdf"
    pdf = canvas.Canvas(str(destination), pagesize=A4)
    pdf.setTitle("FIT5032 Week 5 Task 5.2 Submission")

    draw_code_page(pdf, "router/index.js", "src/router/index.js", 1, 5)
    draw_code_page(pdf, "src/App.vue", "src/App.vue", 2, 5)
    draw_code_page(pdf, "src/views/HomeView.vue", "src/views/HomeView.vue", 3, 5)
    draw_image_page(
        pdf,
        "Screenshot - App open on Home page",
        "Working local route: http://127.0.0.1:4173/",
        home_image,
        "The Home navigation item is active, the route banner displays '/', and the Library Registration Form is rendered.",
        4,
        5,
    )
    draw_image_page(
        pdf,
        "Screenshot - App open on About page",
        "Working local route: http://127.0.0.1:4173/about",
        about_image,
        "The About navigation item is active and the page explains the named, lazy-loaded route and fallback redirect.",
        5,
        5,
    )
    pdf.save()
    return destination


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)

    validation_cropped = TMP / "task5-1-password-validation-cropped.png"
    home_cropped = TMP / "task5-2-home-route-cropped.png"
    about_cropped = TMP / "task5-2-about-route-cropped.png"
    crop_page_evidence(
        EVIDENCE / "task5-1-password-validation.png", validation_cropped, "validation"
    )
    crop_page_evidence(EVIDENCE / "task5-2-home-route.png", home_cropped, "home")
    crop_page_evidence(EVIDENCE / "task5-2-about-route.png", about_cropped, "app")

    task_51 = build_task_51(
        validation_cropped,
        EVIDENCE / "task5-1-vue-devtools.png",
    )
    task_52 = build_task_52(home_cropped, about_cropped)
    print(task_51)
    print(task_52)


if __name__ == "__main__":
    main()
