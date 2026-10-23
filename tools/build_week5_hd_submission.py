from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "hd"
OUTPUT = ROOT / "output" / "pdf"
TMP = ROOT / "tmp" / "pdfs" / "week5_hd"
DESTINATION = OUTPUT / "FIT5032_Week5_HD_Submission.pdf"

PAGE_W, PAGE_H = landscape(A4)
MARGIN = 38
HEADER_H = 58
FOOTER_H = 26
INK = colors.HexColor("#172033")
MUTED = colors.HexColor("#64748B")
BLUE = colors.HexColor("#2563EB")
PALE = colors.HexColor("#F1F5F9")

REQUIRED_CODE = [
    "src/router/index.js",
    "src/App.vue",
    "src/views/HomeView.vue",
]

SUPPORTING_CODE = [
    "src/main.js",
    "src/services/auth.js",
    "src/components/BHeader.vue",
    "src/views/LoginView.vue",
    "src/views/AccessDeniedView.vue",
    "src/views/AboutView.vue",
]

IMAGE_PAGES = [
    (
        "Screenshot 1 - Modified Library form",
        "Password confirmation validation: mismatched passwords display a clear error.",
        "02-password-mismatch.png",
        "http://127.0.0.1:5173/",
        "app",
    ),
    (
        "Screenshot 2 - Vue DevTools component testing",
        "LibraryRegistrationForm is selected and the reactive confirmPassword error is expanded.",
        "06-vue-devtools.png",
        "http://127.0.0.1:5173/__devtools__/",
        "devtools",
    ),
    (
        "Required screenshot - Home page",
        "Guest state is visible; the About route is marked as protected by a navigation guard.",
        "01-home-guest.png",
        "http://127.0.0.1:5173/",
        "app",
    ),
    (
        "HD evidence - Access denied route",
        "An unauthenticated attempt to open /about is intercepted by the route guard.",
        "03-access-denied.png",
        "http://127.0.0.1:5173/access-denied?redirect=/about",
        "app",
    ),
    (
        "HD evidence - Login route",
        "A guest-only login route provides demonstration credentials and a safe return path.",
        "04-login-route.png",
        "http://127.0.0.1:5173/login?redirect=/about",
        "app",
    ),
    (
        "Required screenshot - About page",
        "The protected About page is available after authentication and displays member status.",
        "05-protected-about.png",
        "http://127.0.0.1:5173/about",
        "app",
    ),
]


def code_chunks(relative_path, lines_per_page=48):
    lines = (ROOT / relative_path).read_text(encoding="utf-8").splitlines()
    return [lines[index : index + lines_per_page] for index in range(0, len(lines), lines_per_page)]


def build_page_manifest():
    manifest = [{"kind": "cover"}]
    for relative_path in REQUIRED_CODE:
        chunks = code_chunks(relative_path)
        for index, lines in enumerate(chunks, start=1):
            manifest.append(
                {
                    "kind": "code",
                    "section": "Required source file",
                    "path": relative_path,
                    "part": index,
                    "parts": len(chunks),
                    "lines": lines,
                    "start_line": (index - 1) * 48 + 1,
                }
            )
    for title, caption, filename, url, crop_mode in IMAGE_PAGES:
        manifest.append(
            {
                "kind": "image",
                "title": title,
                "caption": caption,
                "filename": filename,
                "url": url,
                "crop_mode": crop_mode,
            }
        )
    for relative_path in SUPPORTING_CODE:
        chunks = code_chunks(relative_path)
        for index, lines in enumerate(chunks, start=1):
            manifest.append(
                {
                    "kind": "code",
                    "section": "HD supporting source",
                    "path": relative_path,
                    "part": index,
                    "parts": len(chunks),
                    "lines": lines,
                    "start_line": (index - 1) * 48 + 1,
                }
            )
    return manifest


def draw_header(pdf, title, subtitle=""):
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(MARGIN, PAGE_H - 34, title)
    if subtitle:
        pdf.setFillColor(MUTED)
        pdf.setFont("Helvetica", 9)
        pdf.drawRightString(PAGE_W - MARGIN, PAGE_H - 32, subtitle)
    pdf.setStrokeColor(BLUE)
    pdf.setLineWidth(1.2)
    pdf.line(MARGIN, PAGE_H - HEADER_H, PAGE_W - MARGIN, PAGE_H - HEADER_H)


def draw_footer(pdf, page_number, total_pages):
    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.setLineWidth(0.5)
    pdf.line(MARGIN, FOOTER_H, PAGE_W - MARGIN, FOOTER_H)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(MARGIN, 13, "FIT5032 eFolio Task 5 - Distinction / HD")
    pdf.drawRightString(PAGE_W - MARGIN, 13, f"Page {page_number} of {total_pages}")


def draw_cover(pdf, page_number, total_pages):
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawString(58, PAGE_H - 100, "eFolio Task 5")
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(58, PAGE_H - 137, "Navigation, Security and Routing")
    pdf.setStrokeColor(BLUE)
    pdf.setLineWidth(2)
    pdf.line(58, PAGE_H - 158, PAGE_W - 58, PAGE_H - 158)

    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 13)
    pdf.drawString(58, PAGE_H - 196, "Pass, Credit, Distinction and High Distinction evidence")

    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(58, PAGE_H - 245, "Included")
    items = [
        "Task 5.1 password confirmation validation and Vue DevTools evidence",
        "Required files: src/router/index.js, src/App.vue and src/views/HomeView.vue",
        "Required localhost screenshots: Home and About",
        "HD evidence: route guard, Access Denied, Login and authenticated member state",
        "Supporting source for authentication, conditional navigation and protected views",
    ]
    pdf.setFont("Helvetica", 10)
    y = PAGE_H - 270
    for item in items:
        pdf.drawString(70, y, f"- {item}")
        y -= 24

    pdf.setFillColor(colors.HexColor("#FFF7ED"))
    pdf.roundRect(58, 82, PAGE_W - 116, 55, 6, fill=1, stroke=0)
    pdf.setFillColor(colors.HexColor("#7C2D12"))
    pdf.setFont("Helvetica", 9)
    pdf.drawString(
        72,
        113,
        "Security note: authentication is a client-side coursework simulation for route-guard learning.",
    )
    pdf.drawString(
        72,
        95,
        "Production credentials and authorization decisions must be handled by a trusted backend.",
    )
    draw_footer(pdf, page_number, total_pages)
    pdf.showPage()


def printable_code(line):
    replacements = {
        "📚": "[Library]",
        "🔒": "[Locked]",
        "✅": "[Authenticated]",
    }
    for source, replacement in replacements.items():
        line = line.replace(source, replacement)
    return line


def draw_code_page(pdf, page, page_number, total_pages):
    path = page["path"]
    subtitle = page["section"]
    if page["parts"] > 1:
        subtitle += f" - part {page['part']} of {page['parts']}"
    draw_header(pdf, path, subtitle)

    x_number = MARGIN + 24
    x_code = MARGIN + 35
    y = PAGE_H - HEADER_H - 24
    leading = 9.7
    pdf.setFillColor(PALE)
    pdf.roundRect(MARGIN, FOOTER_H + 12, PAGE_W - 2 * MARGIN, PAGE_H - HEADER_H - FOOTER_H - 26, 5, fill=1, stroke=0)

    pdf.setFont("Courier", 7.2)
    for offset, line in enumerate(page["lines"]):
        line_number = page["start_line"] + offset
        pdf.setFillColor(colors.HexColor("#94A3B8"))
        pdf.drawRightString(x_number, y, str(line_number))
        pdf.setFillColor(INK)
        pdf.drawString(x_code, y, printable_code(line).replace("\t", "    "))
        y -= leading

    draw_footer(pdf, page_number, total_pages)
    pdf.showPage()


def prepare_image(filename, crop_mode):
    source = EVIDENCE / filename
    target = TMP / filename
    with Image.open(source).convert("RGB") as image:
        if crop_mode == "app":
            image = image.crop((0, 0, min(860, image.width), min(820, image.height)))
        image.save(target, quality=95)
    return target


def draw_image_page(pdf, page, page_number, total_pages):
    draw_header(pdf, page["title"], page["url"])
    image_path = prepare_image(page["filename"], page["crop_mode"])

    image_x = MARGIN
    image_y = FOOTER_H + 48
    image_w = PAGE_W - 2 * MARGIN
    image_h = PAGE_H - HEADER_H - FOOTER_H - 90

    with Image.open(image_path) as image:
        source_w, source_h = image.size
    scale = min(image_w / source_w, image_h / source_h)
    draw_w = source_w * scale
    draw_h = source_h * scale
    draw_x = image_x + (image_w - draw_w) / 2
    draw_y = image_y + (image_h - draw_h) / 2
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
    pdf.setFont("Helvetica", 9)
    pdf.drawString(MARGIN, FOOTER_H + 31, page["caption"])
    draw_footer(pdf, page_number, total_pages)
    pdf.showPage()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    manifest = build_page_manifest()
    total_pages = len(manifest)

    pdf = canvas.Canvas(str(DESTINATION), pagesize=(PAGE_W, PAGE_H))
    pdf.setTitle("FIT5032 Week 5 Distinction and HD Submission")
    pdf.setSubject("Navigation, security, validation and conditional routing evidence")

    for page_number, page in enumerate(manifest, start=1):
        if page["kind"] == "cover":
            draw_cover(pdf, page_number, total_pages)
        elif page["kind"] == "code":
            draw_code_page(pdf, page, page_number, total_pages)
        else:
            draw_image_page(pdf, page, page_number, total_pages)

    pdf.save()
    print(DESTINATION)
    print(f"pages={total_pages}")


if __name__ == "__main__":
    main()
