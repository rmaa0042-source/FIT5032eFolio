from __future__ import annotations

import os
import textwrap
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "FIT5032_Week9-10_Progress_Report_HD.pdf"

PAGE_W, PAGE_H = A4
MARGIN_X = 18 * mm
CONTENT_W = PAGE_W - 2 * MARGIN_X

INK = colors.HexColor("#101820")
MUTED = colors.HexColor("#5F6368")
BLUE = colors.HexColor("#1769AA")
LIGHT_BLUE = colors.HexColor("#EAF3FB")
GREEN = colors.HexColor("#247A4B")
LIGHT_GREEN = colors.HexColor("#EAF6EF")
AMBER = colors.HexColor("#9A6700")
LIGHT_AMBER = colors.HexColor("#FFF4D6")
LIGHT_GREY = colors.HexColor("#F4F6F8")
MID_GREY = colors.HexColor("#D6DADF")


def register_fonts() -> tuple[str, str, str]:
    candidates = [
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "arial.ttf",
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "segoeui.ttf",
    ]
    bold_candidates = [
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "arialbd.ttf",
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "segoeuib.ttf",
    ]
    mono_candidates = [
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "consola.ttf",
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "cour.ttf",
    ]

    regular = next((p for p in candidates if p.exists()), None)
    bold = next((p for p in bold_candidates if p.exists()), None)
    mono = next((p for p in mono_candidates if p.exists()), None)

    if regular and bold and mono:
        pdfmetrics.registerFont(TTFont("ReportSans", str(regular)))
        pdfmetrics.registerFont(TTFont("ReportSansBold", str(bold)))
        pdfmetrics.registerFont(TTFont("ReportMono", str(mono)))
        return "ReportSans", "ReportSansBold", "ReportMono"

    return "Helvetica", "Helvetica-Bold", "Courier"


FONT, FONT_BOLD, FONT_MONO = register_fonts()


class Report:
    def __init__(self, output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.c = canvas.Canvas(str(output_path), pagesize=A4)
        self.page = 0
        self.y = PAGE_H - 30 * mm

    def footer(self):
        self.c.setStrokeColor(MID_GREY)
        self.c.setLineWidth(0.5)
        self.c.line(MARGIN_X, 16 * mm, PAGE_W - MARGIN_X, 16 * mm)
        self.c.setFillColor(MUTED)
        self.c.setFont(FONT, 8)
        self.c.drawCentredString(
            PAGE_W / 2,
            10 * mm,
            f"FIT5032 eFolio Tasks 9 and 10  |  Page {self.page}",
        )

    def finish_page(self):
        self.footer()
        self.c.showPage()

    def start_page(self, title: str, subtitle: str = ""):
        if self.page:
            self.finish_page()
        self.page += 1
        self.c.setFillColor(INK)
        self.c.setFont(FONT_BOLD, 17)
        self.c.drawString(MARGIN_X, PAGE_H - 20 * mm, title)
        self.y = PAGE_H - 28 * mm
        if subtitle:
            self.c.setFillColor(MUTED)
            self.c.setFont(FONT, 10)
            self.c.drawString(MARGIN_X, self.y, subtitle)
            self.y -= 8 * mm
        else:
            self.y -= 3 * mm

    def paragraph(self, text: str, size: float = 10, leading: float = 14, gap: float = 7):
        style = ParagraphStyle(
            "body",
            fontName=FONT,
            fontSize=size,
            leading=leading,
            textColor=INK,
        )
        p = Paragraph(text, style)
        _, h = p.wrap(CONTENT_W, PAGE_H)
        p.drawOn(self.c, MARGIN_X, self.y - h)
        self.y -= h + gap

    def heading(self, text: str, size: float = 13, gap: float = 5):
        self.c.setFillColor(INK)
        self.c.setFont(FONT_BOLD, size)
        self.c.drawString(MARGIN_X, self.y, text)
        self.y -= (size + gap)

    def bullet(self, text: str, size: float = 9.6):
        style = ParagraphStyle(
            "bullet",
            fontName=FONT,
            fontSize=size,
            leading=13,
            leftIndent=12,
            firstLineIndent=-8,
            textColor=INK,
        )
        p = Paragraph(f"&#8226;&nbsp; {text}", style)
        _, h = p.wrap(CONTENT_W, PAGE_H)
        p.drawOn(self.c, MARGIN_X, self.y - h)
        self.y -= h + 3

    def callout(self, heading: str, text: str, tone: str = "blue"):
        palette = {
            "blue": (LIGHT_BLUE, BLUE),
            "green": (LIGHT_GREEN, GREEN),
            "amber": (LIGHT_AMBER, AMBER),
        }
        fill, accent = palette[tone]
        style = ParagraphStyle(
            "callout",
            fontName=FONT,
            fontSize=9.4,
            leading=13,
            textColor=INK,
        )
        p = Paragraph(f"<b>{heading}</b> {text}", style)
        _, h = p.wrap(CONTENT_W - 20, PAGE_H)
        box_h = h + 18
        self.c.setFillColor(fill)
        self.c.roundRect(MARGIN_X, self.y - box_h, CONTENT_W, box_h, 5, fill=1, stroke=0)
        self.c.setFillColor(accent)
        self.c.rect(MARGIN_X, self.y - box_h, 5, box_h, fill=1, stroke=0)
        p.drawOn(self.c, MARGIN_X + 13, self.y - box_h + 9)
        # Leave enough optical space for the next heading; the calculated
        # rectangle height includes font metrics that sit slightly above the
        # visible rounded border.
        self.y -= box_h + 44

    def code_block(self, code: str, label: str = "", font_size: float = 7.4, max_chars: int = 104):
        lines: list[str] = []
        for raw in code.strip("\n").splitlines():
            expanded = raw.expandtabs(2)
            if len(expanded) <= max_chars:
                lines.append(expanded)
            else:
                wrapped = textwrap.wrap(
                    expanded,
                    width=max_chars,
                    subsequent_indent="    ",
                    replace_whitespace=False,
                    drop_whitespace=False,
                )
                lines.extend(wrapped or [""])

        leading = font_size + 2.2
        label_h = 18 if label else 0
        box_h = len(lines) * leading + 18 + label_h
        self.c.setFillColor(LIGHT_GREY)
        self.c.setStrokeColor(MID_GREY)
        self.c.roundRect(MARGIN_X, self.y - box_h, CONTENT_W, box_h, 6, fill=1, stroke=1)

        cursor_y = self.y - 13
        if label:
            self.c.setFillColor(BLUE)
            self.c.setFont(FONT_BOLD, 8.5)
            self.c.drawString(MARGIN_X + 10, cursor_y, label)
            cursor_y -= 18

        self.c.setFillColor(INK)
        self.c.setFont(FONT_MONO, font_size)
        for line in lines:
            self.c.drawString(MARGIN_X + 10, cursor_y, line)
            cursor_y -= leading

        self.y -= box_h + 10

    def table(self, data, widths, row_heights=None, font_size=8.4):
        t = Table(data, colWidths=widths, rowHeights=row_heights, repeatRows=1)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
                    ("FONTNAME", (0, 1), (-1, -1), FONT),
                    ("FONTSIZE", (0, 0), (-1, -1), font_size),
                    ("LEADING", (0, 0), (-1, -1), font_size + 3),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.5, MID_GREY),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        _, h = t.wrap(CONTENT_W, PAGE_H)
        t.drawOn(self.c, MARGIN_X, self.y - h)
        self.y -= h + 10

    def save(self):
        self.finish_page()
        self.c.save()


def make_report():
    report = Report(OUTPUT)

    # 1 - Cover
    report.start_page("FIT5032 eFolio Tasks 9 and 10")
    report.c.setFillColor(BLUE)
    report.c.rect(MARGIN_X, PAGE_H - 58 * mm, CONTENT_W, 4, fill=1, stroke=0)
    report.c.setFillColor(INK)
    report.c.setFont(FONT_BOLD, 24)
    report.c.drawString(MARGIN_X, PAGE_H - 80 * mm, "Week 9-10 Progress Report")
    report.c.setFillColor(MUTED)
    report.c.setFont(FONT, 13)
    report.c.drawString(MARGIN_X, PAGE_H - 93 * mm, "Cloud Functions, Firestore Automation, and APIs")
    report.c.setFont(FONT, 11)
    report.c.drawString(MARGIN_X, PAGE_H - 115 * mm, "Student ID: 35286288")
    report.c.drawString(MARGIN_X, PAGE_H - 124 * mm, "Target level: High Distinction")
    report.c.drawString(MARGIN_X, PAGE_H - 133 * mm, f"Prepared: {date(2026, 10, 4).strftime('%d %B %Y')}")
    report.y = PAGE_H - 158 * mm
    report.callout(
        "Scope.",
        "This progress report records the Week 9-10 implementation completed in the existing NoMash-Library project. It follows the teacher's code structure and maps every section to the published HD evidence criteria.",
        "blue",
    )
    report.callout(
        "Evidence integrity.",
        "Firebase Console, deployed URL, Firestore result, and live OpenWeather screenshots must be captured from the student's own accounts before the final Moodle submission. Teacher tutorial screenshots are not presented as student evidence.",
        "amber",
    )

    # 2 - Rubric map
    report.start_page(
        "HD Requirements and Current Progress",
        "Direct mapping to eFolio Tasks 9.1, 9.2, 10.1, and 10.2",
    )
    rows = [
        ["Task", "Required evidence", "Implementation", "Status"],
        ["9.1", "Deployed function visible in Firebase; account visible", "functions/index.js", "Code ready; deployment screenshot required"],
        ["9.1", "Code and browser obtain total number of books", "countBooks + GetBookCountView.vue", "Implemented; live URL required"],
        ["9.2 HD", "New Firestore book is capitalised by a Function", "capitalizeBookFields trigger", "Implemented; before/after screenshot required"],
        ["10.1", "Current-location weather in code and browser", "WeatherView.vue geolocation", "Implemented; API key and browser screenshot required"],
        ["10.2 HD", "City search, Celsius temperature, and icon", "WeatherView.vue city search", "Implemented; live API screenshot required"],
        ["10.2 HD", "All books shown as JSON on GetAllBookAPI", "getAllBooksAPI + GetAllBookAPIView.vue", "Implemented; deployed API screenshot required"],
    ]
    pstyle = ParagraphStyle("cell", fontName=FONT, fontSize=7.7, leading=10)
    pdata = [[Paragraph(str(cell), pstyle) for cell in row] for row in rows]
    report.table(pdata, [24 * mm, 58 * mm, 50 * mm, 44 * mm], font_size=7.7)
    report.callout(
        "HD focus.",
        "The four core capabilities are covered in code. The remaining gap is evidence capture from real services. Clear, readable screenshots must show both the relevant code and the working browser or Firebase result.",
        "green",
    )

    # 3 - architecture
    report.start_page("Week 9-10 Solution Structure", "How the Vue app, Firebase, Firestore, and OpenWeather work together")
    report.heading("Week 9: Cloud Functions")
    report.paragraph(
        "The existing Vue application writes books to Cloud Firestore. Firebase Cloud Functions count the collection, capitalise string fields when a new book is created, and expose all books through a JSON endpoint."
    )
    report.code_block(
        "Vue AddBookView -> Cloud Firestore books collection\n"
        "                         |\n"
        "                         +-> capitalizeBookFields trigger -> uppercase string fields\n"
        "                         +-> countBooks HTTP function -> { count: number }\n"
        "                         +-> getAllBooksAPI HTTP function -> { count, books[] }",
        "Week 9 data flow",
        font_size=8.2,
    )
    report.y -= 12
    report.heading("Week 10: API consumption")
    report.paragraph(
        "WeatherView uses Axios to call OpenWeather by geolocation or city name. GetAllBookAPIView calls the deployed Firebase endpoint on mount and renders formatted JSON inside a pre element."
    )
    report.code_block(
        "Browser geolocation or city input -> Axios -> OpenWeather current weather endpoint\n"
        "                                         -> city/country, Celsius, description, icon\n\n"
        "GetAllBookAPIView onMounted -> Axios -> getAllBooksAPI -> formatted JSON",
        "Week 10 data flow",
        font_size=8.2,
    )
    report.callout(
        "Configuration.",
        "Secrets and deployment URLs are stored in a local .env file based on .env.example. The API key is not hard-coded or included in this report.",
        "blue",
    )

    # 4 - setup
    report.start_page("eFolio Task 9.1 - Node.js and Firebase Setup", "Teacher-template server structure and deployment preparation")
    report.paragraph(
        "The root package uses ES modules and includes a start script for server.js. Axios and Express are installed. The Firebase functions package is separated under functions/ for deployment."
    )
    report.code_block(
        "import express from 'express'\n\n"
        "const app = express()\n"
        "const port = process.env.PORT || 3000\n\n"
        "app.get('/', (_request, response) => {\n"
        "  response.send('Hello from Node.js!')\n"
        "})\n\n"
        "app.listen(port, () => {\n"
        "  console.log(`Server is running on port ${port}`)\n"
        "})",
        "server.js",
        font_size=8.2,
    )
    report.code_block(
        '"type": "module",\n'
        '"scripts": { "start": "node server.js", "dev": "vite", "build": "vite build" },\n'
        '"dependencies": { "axios": "^1.12.2", "express": "^5.1.0" }',
        "package.json - relevant entries",
        font_size=8.0,
    )
    report.callout(
        "External step.",
        "Run firebase login, firebase init firestore, firebase init functions, and firebase deploy from the student's authenticated terminal. Capture the successful deployment and account identity for Screenshot Set 1.",
        "amber",
    )

    # 5 - count function
    report.start_page("eFolio Task 9.1 - Count Books Cloud Function", "HTTP function returns the current Firestore collection count")
    report.code_block(
        "exports.countBooks = onRequest((request, response) => {\n"
        "  cors(request, response, async () => {\n"
        "    try {\n"
        "      const snapshot = await db.collection('books').count().get()\n"
        "      response.status(200).json({ count: snapshot.data().count })\n"
        "    } catch (error) {\n"
        "      logger.error('Unable to count books', error)\n"
        "      response.status(500).json({ error: 'Unable to count books' })\n"
        "    }\n"
        "  })\n"
        "})",
        "functions/index.js - countBooks",
        font_size=8.2,
    )
    report.y -= 12
    report.heading("Implementation decisions")
    report.bullet("Firestore's aggregate count query avoids downloading every book document.")
    report.bullet("CORS is enabled so the Vite browser client can call the HTTPS endpoint.")
    report.bullet("Success returns a small JSON object; failures return HTTP 500 and a safe error message.")
    report.bullet("The default region is australia-southeast2, matching the tutorial setup.")
    report.callout(
        "Required evidence.",
        "One clear Firebase Console screenshot must show countBooks as deployed with the student's account visible. A second paired code/browser screenshot must show the returned total number of books.",
        "green",
    )

    # 6 - count page
    report.start_page("eFolio Task 9.1 - Book Counter Client", "Vue page requests countBooks and displays the returned value")
    report.code_block(
        "const count = ref(null)\n"
        "const isLoading = ref(false)\n"
        "const errorMessage = ref('')\n\n"
        "const getBookCount = async () => {\n"
        "  const endpoint = import.meta.env.VITE_COUNT_BOOKS_FUNCTION_URL\n"
        "  if (!endpoint) {\n"
        "    errorMessage.value = 'Add VITE_COUNT_BOOKS_FUNCTION_URL to .env...'\n"
        "    return\n"
        "  }\n"
        "  try {\n"
        "    isLoading.value = true\n"
        "    const response = await axios.get(endpoint)\n"
        "    count.value = Number(response.data.count)\n"
        "  } finally {\n"
        "    isLoading.value = false\n"
        "  }\n"
        "}",
        "src/views/GetBookCountView.vue - script",
        font_size=7.7,
    )
    report.code_block(
        "<button @click=\"getBookCount\">Get Book Count</button>\n"
        "<p v-if=\"count !== null\">\n"
        "  Total number of books: <strong>{{ count }}</strong>\n"
        "</p>",
        "src/views/GetBookCountView.vue - template",
        font_size=8.2,
    )
    report.paragraph(
        "A loading state prevents repeated requests, and an explicit error message helps distinguish missing deployment configuration from a failed HTTP request."
    )

    # 7 - capitalization HD
    report.start_page("eFolio Task 9.2 - Firestore Capitalisation", "HD function automatically capitalises new book string fields")
    report.code_block(
        "exports.capitalizeBookFields = onDocumentCreated(\n"
        "  'books/{bookId}',\n"
        "  async (event) => {\n"
        "    const snapshot = event.data\n"
        "    if (!snapshot) return\n\n"
        "    const original = snapshot.data()\n"
        "    const capitalized = Object.fromEntries(\n"
        "      Object.entries(original).map(([key, value]) => [\n"
        "        key,\n"
        "        typeof value === 'string' ? value.toUpperCase() : value\n"
        "      ])\n"
        "    )\n\n"
        "    await snapshot.ref.update(capitalized)\n"
        "  }\n"
        ")",
        "functions/index.js - capitalizeBookFields",
        font_size=7.7,
    )
    report.y -= 12
    report.heading("Why this meets the HD criterion")
    report.bullet("The trigger runs automatically when a document is added to books.")
    report.bullet("Every string value is uppercased; numeric ISBN and Firestore timestamps remain unchanged.")
    report.bullet("onDocumentCreated does not retrigger after the update, preventing an update loop.")
    report.callout(
        "Best evidence layout.",
        "Use one readable screenshot containing the Add Book browser form and Firestore result, or two sequential screenshots on separate pages: first the lowercase input, then the uppercase stored document. Include the relevant function code in a separate VS Code screenshot.",
        "green",
    )

    # 8 - week 9 evidence checklist
    report.start_page("Week 9 Evidence Capture Checklist", "Screenshots still required from the student's own Firebase project")
    evidence_rows = [
        ["Page header", "What must be visible", "Suggested caption"],
        ["Task 9.1 - Deployed Function", "Firebase Functions list, countBooks, project/account identity", "Deployed Firebase Cloud Function and authenticated project account"],
        ["Task 9.1 - Count Books Code", "functions/index.js or GetBookCountView.vue at readable zoom", "Cloud Function and Axios client used to obtain the book count"],
        ["Task 9.1 - Count Books Browser", "Book Counter page and returned total", "Running project displays the current number of Firestore books"],
        ["Task 9.2 - Capitalisation Code", "capitalizeBookFields trigger", "Firestore create trigger capitalises all string fields"],
        ["Task 9.2 - Capitalised Result", "New input and uppercase Firestore document", "New book data is automatically capitalised by the deployed Function"],
    ]
    estyle = ParagraphStyle("evidence", fontName=FONT, fontSize=8.0, leading=10.5)
    epdata = [[Paragraph(str(cell), estyle) for cell in row] for row in evidence_rows]
    report.table(epdata, [48 * mm, 66 * mm, 62 * mm], font_size=8.0)
    report.callout(
        "Screenshot quality.",
        "Use native-resolution captures, keep the relevant code/result large enough to read, remove unrelated windows, and place one evidence image on each PDF page with the header naming the task and screenshot set.",
        "blue",
    )

    # 9 - weather script
    report.start_page("eFolio Tasks 10.1-10.2 - Weather API Client", "Current location and city search implemented with Axios")
    report.code_block(
        "const apiKey = import.meta.env.VITE_OPENWEATHER_API_KEY\n"
        "const city = ref('Clayton')\n"
        "const weatherData = ref(null)\n\n"
        "const temperature = computed(() =>\n"
        "  weatherData.value ? Math.round(weatherData.value.main.temp - 273.15) : null\n"
        ")\n\n"
        "const iconUrl = computed(() =>\n"
        "  weatherData.value\n"
        "    ? `https://openweathermap.org/img/wn/${weatherData.value.weather[0].icon}@2x.png`\n"
        "    : ''\n"
        ")",
        "src/views/WeatherView.vue - reactive state and computed display",
        font_size=7.5,
    )
    report.code_block(
        "const requestWeather = async (params) => {\n"
        "  const response = await axios.get(\n"
        "    'https://api.openweathermap.org/data/2.5/weather',\n"
        "    { params: { ...params, appid: apiKey } }\n"
        "  )\n"
        "  weatherData.value = response.data\n"
        "}\n\n"
        "const searchByCity = () => requestWeather({ q: city.value.trim() })",
        "Weather request and city search",
        font_size=7.8,
    )

    # 10 - location and template
    report.start_page("eFolio Task 10.1 - Current Location Weather", "Geolocation request plus complete browser output")
    report.code_block(
        "const searchCurrentLocation = () => {\n"
        "  navigator.geolocation.getCurrentPosition(\n"
        "    ({ coords }) => requestWeather({\n"
        "      lat: coords.latitude,\n"
        "      lon: coords.longitude\n"
        "    }),\n"
        "    () => {\n"
        "      errorMessage.value = 'Location permission was not granted...'\n"
        "    }\n"
        "  )\n"
        "}\n\n"
        "onMounted(searchCurrentLocation)",
        "src/views/WeatherView.vue - current location",
        font_size=8.0,
    )
    report.code_block(
        "<h2>{{ weatherData.name }}, {{ weatherData.sys.country }}</h2>\n"
        "<img :src=\"iconUrl\" alt=\"Current weather icon\" />\n"
        "<p>{{ temperature }} C</p>\n"
        "<p>{{ weatherData.weather[0].description }}</p>",
        "Browser output required by the rubric",
        font_size=8.2,
    )
    report.callout(
        "Required evidence.",
        "Capture readable VS Code and browser screenshots showing current-location weather. For HD, also search Clayton, AU (or another city) and show the city/country, Celsius temperature, description, and matching icon.",
        "green",
    )

    # 11 - JSON function
    report.start_page("eFolio Task 10.2 - Get All Books API", "Cloud Function returns Firestore books as JSON")
    report.code_block(
        "exports.getAllBooksAPI = onRequest((request, response) => {\n"
        "  cors(request, response, async () => {\n"
        "    if (request.method !== 'GET') {\n"
        "      response.status(405).json({ error: 'Method not allowed' })\n"
        "      return\n"
        "    }\n\n"
        "    try {\n"
        "      const snapshot = await db.collection('books').orderBy('name').get()\n"
        "      const books = snapshot.docs.map((document) => ({\n"
        "        id: document.id, ...document.data()\n"
        "      }))\n"
        "      response.status(200).json({ count: books.length, books })\n"
        "    } catch (error) {\n"
        "      response.status(500).json({ error: 'Unable to retrieve books' })\n"
        "    }\n"
        "  })\n"
        "})",
        "functions/index.js - getAllBooksAPI",
        font_size=7.4,
    )
    report.y -= 12
    report.heading("API behaviour")
    report.bullet("GET returns a stable JSON object containing count and books.")
    report.bullet("Each book includes its Firestore document ID and stored fields.")
    report.bullet("Unsupported methods receive HTTP 405; server failures receive HTTP 500.")

    # 12 - JSON page
    report.start_page("eFolio Task 10.2 - GetAllBookAPI Page", "Vue route automatically loads and displays the API response")
    report.code_block(
        "const jsonData = ref(null)\n\n"
        "const getAllBooks = async () => {\n"
        "  const endpoint = import.meta.env.VITE_GET_ALL_BOOKS_FUNCTION_URL\n"
        "  const response = await axios.get(endpoint)\n"
        "  jsonData.value = response.data\n"
        "}\n\n"
        "onMounted(getAllBooks)",
        "src/views/GetAllBookAPIView.vue - script",
        font_size=8.2,
    )
    report.code_block(
        "<h1>Get All Book API</h1>\n"
        "<pre v-if=\"jsonData\">{{ JSON.stringify(jsonData, null, 2) }}</pre>",
        "src/views/GetAllBookAPIView.vue - template",
        font_size=8.2,
    )
    report.code_block(
        "const route = useRoute()\n"
        "const showHeader = computed(() => route.name !== 'GetAllBookAPI')\n\n"
        "<header v-if=\"showHeader\"><BHeader /></header>",
        "src/App.vue - hide navigation on the raw API display page",
        font_size=8.2,
    )
    report.callout(
        "Required evidence.",
        "Capture the Get All Book API page with the browser URL visible and the full JSON response readable. Pair it with the function and Vue code screenshots.",
        "green",
    )

    # 13 - routes and validation
    report.start_page("Routing, Configuration, and Build Verification", "Integration into the existing NoMash-Library application")
    report.code_block(
        "{ path: '/get-book-count', name: 'GetBookCount', component: GetBookCountView },\n"
        "{ path: '/weather-check', name: 'GetWeather', component: WeatherView },\n"
        "{ path: '/get-all-book-api', name: 'GetAllBookAPI', component: GetAllBookAPIView }",
        "src/router/index.js - new routes",
        font_size=8.0,
    )
    report.code_block(
        "VITE_OPENWEATHER_API_KEY=replace_with_your_openweather_key\n"
        "VITE_COUNT_BOOKS_FUNCTION_URL=https://REGION-PROJECT_ID.cloudfunctions.net/countBooks\n"
        "VITE_GET_ALL_BOOKS_FUNCTION_URL=https://REGION-PROJECT_ID.cloudfunctions.net/getAllBooksAPI",
        ".env.example - local configuration contract",
        font_size=7.6,
    )
    verification = [
        ["Check", "Result"],
        ["Vite production build", "Passed - 283 modules transformed"],
        ["server.js syntax", "Passed - node --check"],
        ["functions/index.js syntax", "Passed - node --check"],
        ["Secrets in source", "OpenWeather key excluded; .env.example contains placeholders"],
        ["External deployment", "Pending authenticated Firebase CLI and Blaze-plan project"],
        ["Live weather request", "Pending student's OpenWeather API key"],
    ]
    vstyle = ParagraphStyle("verify", fontName=FONT, fontSize=8.4, leading=11)
    vpdata = [[Paragraph(str(cell), vstyle) for cell in row] for row in verification]
    report.table(vpdata, [65 * mm, 111 * mm], font_size=8.4)

    # 14 - final checklist
    report.start_page("Final HD Submission Checklist", "Complete these account-specific steps before exporting the final evidence PDF")
    checklist = [
        "Create .env from .env.example and add the OpenWeather key plus both deployed Function URLs.",
        "Install functions dependencies, authenticate Firebase CLI, and deploy countBooks, capitalizeBookFields, and getAllBooksAPI.",
        "Add a lowercase book and verify the Firestore document becomes uppercase automatically.",
        "Open Book Counter and show the returned Firestore total in the browser.",
        "Allow browser location access and capture current-location weather.",
        "Search Clayton, AU and show the Celsius temperature, weather description, and icon.",
        "Open /get-all-book-api and capture the full JSON result with the URL visible.",
        "Capture code at readable zoom; keep one screenshot per page with a task-specific header and one-sentence caption.",
        "Check that Firebase account/project identity is visible where Task 9.1 requires it.",
        "Combine Tasks 9 and 10 into one PDF and review every page at 100% zoom before Moodle submission.",
    ]
    for index, item in enumerate(checklist, start=1):
        report.paragraph(f"<b>{index}.</b> {item}", size=9.6, leading=13, gap=6)
    report.callout(
        "Current conclusion.",
        "The Week 9-10 code is implemented and builds successfully. HD-level completion now depends on deploying with the student's accounts and replacing this progress report's pending-evidence notes with clear, authentic screenshots of the working services.",
        "amber",
    )

    report.save()
    print(OUTPUT)


if __name__ == "__main__":
    make_report()
