from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "docx" / "FIT5032_Week9-10_Progress_Report_HD_Editable.docx"

BLUE = "1769AA"
PALE_BLUE = "EAF3FB"
PALE_GREY = "F4F6F8"
GRID = "D9D9D9"
BLACK = RGBColor(0, 0, 0)
GREY = RGBColor(95, 99, 104)


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_border(cell, color=GRID, size="6"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:color"), color)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_page_field(paragraph):
    run = paragraph.add_run()
    fld_char = OxmlElement("w:fldChar")
    fld_char.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char, instr, separate, text, end])


def add_code(doc, label, code):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Cm(16.4)
    cell = table.cell(0, 0)
    cell.width = Cm(16.4)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    set_cell_shading(cell, PALE_GREY)
    set_cell_border(cell)
    cell.margin_top = Cm(0.18)
    cell.margin_bottom = Cm(0.18)
    cell.margin_left = Cm(0.25)
    cell.margin_right = Cm(0.25)

    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(label)
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(9)
    r.font.color.rgb = RGBColor(23, 105, 170)

    p = cell.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(code.strip())
    r.font.name = "Consolas"
    r._element.rPr.rFonts.set(qn("w:ascii"), "Consolas")
    r._element.rPr.rFonts.set(qn("w:hAnsi"), "Consolas")
    r.font.size = Pt(7.8)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_note(doc, lead, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(lead + " ")
    r.bold = True
    p.add_run(text)


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(2)
        p.add_run(item)


def add_table(doc, headers, rows, widths):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_repeat_table_header(table.rows[0])

    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.width = widths[index]
        set_cell_shading(cell, BLUE)
        set_cell_border(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(header)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(8.5)

    for row_index, row_data in enumerate(rows, start=1):
        cells = table.add_row().cells
        for index, value in enumerate(row_data):
            cells[index].width = widths[index]
            set_cell_border(cells[index])
            if row_index % 2 == 0:
                set_cell_shading(cells[index], PALE_BLUE)
            cells[index].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cells[index].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(value)
            r.font.size = Pt(8.2)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def page(doc, title, subtitle=""):
    if len(doc.paragraphs) > 0:
        doc.add_page_break()
    p = doc.add_paragraph(style="Heading 1")
    p.paragraph_format.keep_with_next = True
    p.add_run(title)
    if subtitle:
        p = doc.add_paragraph(subtitle)
        p.style = doc.styles["Subtitle"]
        p.paragraph_format.keep_with_next = True


def build():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(1.8)
    section.bottom_margin = Cm(1.8)
    section.left_margin = Cm(2.1)
    section.right_margin = Cm(2.1)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10)
    normal.font.color.rgb = BLACK
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.08

    title_style = doc.styles["Title"]
    title_style.font.name = "Arial"
    title_style.font.size = Pt(26)
    title_style.font.bold = True
    title_style.font.color.rgb = BLACK
    title_ppr = title_style.element.get_or_add_pPr()
    title_border = title_ppr.find(qn("w:pBdr"))
    if title_border is not None:
        title_ppr.remove(title_border)

    subtitle = doc.styles["Subtitle"]
    subtitle.font.name = "Arial"
    subtitle.font.size = Pt(11)
    subtitle.font.color.rgb = BLACK
    subtitle.paragraph_format.space_after = Pt(12)

    h1 = doc.styles["Heading 1"]
    h1.font.name = "Arial"
    h1.font.size = Pt(17)
    h1.font.bold = True
    h1.font.color.rgb = BLACK
    h1.paragraph_format.space_before = Pt(0)
    h1.paragraph_format.space_after = Pt(5)

    h2 = doc.styles["Heading 2"]
    h2.font.name = "Arial"
    h2.font.size = Pt(13)
    h2.font.bold = True
    h2.font.color.rgb = BLACK
    h2.paragraph_format.space_before = Pt(8)
    h2.paragraph_format.space_after = Pt(4)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.text = "FIT5032 eFolio Tasks 9 and 10"
    header.runs[0].font.name = "Arial"
    header.runs[0].font.size = Pt(8)
    header.runs[0].font.color.rgb = GREY

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("FIT5032 eFolio Tasks 9 and 10  |  Page ")
    add_page_field(footer)
    for run in footer.runs:
        run.font.name = "Arial"
        run.font.size = Pt(8)
        run.font.color.rgb = GREY

    # Cover
    p = doc.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.add_run("FIT5032 Week 9 and 10 Progress Report")
    p.paragraph_format.space_before = Pt(72)
    p.paragraph_format.space_after = Pt(12)
    p = doc.add_paragraph("Cloud Functions Firestore Automation and APIs", style="Subtitle")
    p.paragraph_format.space_after = Pt(36)
    doc.add_paragraph("Student ID 35286288")
    doc.add_paragraph("Target level High Distinction")
    doc.add_paragraph("Prepared 5 October 2026")
    doc.add_paragraph().paragraph_format.space_after = Pt(18)
    add_note(doc, "Scope.", "This progress report records the Week 9 and 10 implementation in the existing NoMash-Library project. It follows the teacher's code structure and maps every section to the published HD evidence criteria.")
    add_note(doc, "Evidence integrity.", "Firebase Console, deployed URL, Firestore result, and live OpenWeather screenshots must be captured from the student's own accounts before the final Moodle submission. Teacher tutorial screenshots are not presented as student evidence.")

    page(doc, "HD Requirements and Current Progress", "Direct mapping to Tasks 9.1 9.2 10.1 and 10.2")
    add_table(doc, ["Task", "Required evidence", "Implementation", "Status"], [
        ["9.1", "Deployed function visible in Firebase and account visible", "functions/index.js", "Code ready; deployment screenshot required"],
        ["9.1", "Code and browser obtain total number of books", "countBooks and GetBookCountView.vue", "Implemented; live URL required"],
        ["9.2 HD", "New Firestore book is capitalised by a Function", "capitalizeBookFields trigger", "Implemented; before and after screenshot required"],
        ["10.1", "Current-location weather in code and browser", "WeatherView.vue geolocation", "Implemented; API key and screenshot required"],
        ["10.2 HD", "City search Celsius temperature and icon", "WeatherView.vue city search", "Implemented; live API screenshot required"],
        ["10.2 HD", "All books shown as JSON on GetAllBookAPI", "getAllBooksAPI and GetAllBookAPIView.vue", "Implemented; deployed API screenshot required"],
    ], [Cm(2.0), Cm(5.1), Cm(4.6), Cm(4.7)])
    add_note(doc, "HD focus.", "The four core capabilities are covered in code. The remaining gap is evidence capture from real services. Clear screenshots must show both the relevant code and the working browser or Firebase result.")

    page(doc, "Week 9 and 10 Solution Structure", "How the Vue app Firebase Firestore and OpenWeather work together")
    doc.add_heading("Week 9 Cloud Functions", level=2)
    doc.add_paragraph("The existing Vue application writes books to Cloud Firestore. Firebase Cloud Functions count the collection, capitalise string fields when a new book is created, and expose all books through a JSON endpoint.")
    add_code(doc, "Week 9 data flow", "Vue AddBookView -> Cloud Firestore books collection\n                         |\n                         +-> capitalizeBookFields trigger -> uppercase string fields\n                         +-> countBooks HTTP function -> { count: number }\n                         +-> getAllBooksAPI HTTP function -> { count, books[] }")
    doc.add_heading("Week 10 API Consumption", level=2)
    doc.add_paragraph("WeatherView uses Axios to call OpenWeather by geolocation or city name. GetAllBookAPIView calls the deployed Firebase endpoint on mount and renders formatted JSON inside a pre element.")
    add_code(doc, "Week 10 data flow", "Browser geolocation or city input -> Axios -> OpenWeather current weather endpoint\n                                         -> city country Celsius description icon\n\nGetAllBookAPIView onMounted -> Axios -> getAllBooksAPI -> formatted JSON")
    add_note(doc, "Configuration.", "Secrets and deployment URLs are stored in a local .env file based on .env.example. The API key is not hard-coded or included in this report.")

    page(doc, "eFolio Task 9.1 Node.js and Firebase Setup", "Teacher template server structure and deployment preparation")
    doc.add_paragraph("The root package uses ES modules and includes a start script for server.js. Axios and Express are installed. The Firebase functions package is separated under functions for deployment.")
    add_code(doc, "server.js", "import express from 'express'\n\nconst app = express()\nconst port = process.env.PORT || 3000\n\napp.get('/', (_request, response) => {\n  response.send('Hello from Node.js!')\n})\n\napp.listen(port, () => {\n  console.log(`Server is running on port ${port}`)\n})")
    add_code(doc, "package.json relevant entries", '"type": "module",\n"scripts": { "start": "node server.js", "dev": "vite", "build": "vite build" },\n"dependencies": { "axios": "^1.12.2", "express": "^5.1.0" }')
    add_note(doc, "External step.", "Run firebase login, firebase init firestore, firebase init functions, and firebase deploy from the student's authenticated terminal. Capture the successful deployment and account identity for Screenshot Set 1.")

    page(doc, "eFolio Task 9.1 Count Books Cloud Function", "HTTP function returns the current Firestore collection count")
    add_code(doc, "functions/index.js countBooks", "exports.countBooks = onRequest((request, response) => {\n  cors(request, response, async () => {\n    try {\n      const snapshot = await db.collection('books').count().get()\n      response.status(200).json({ count: snapshot.data().count })\n    } catch (error) {\n      logger.error('Unable to count books', error)\n      response.status(500).json({ error: 'Unable to count books' })\n    }\n  })\n})")
    doc.add_heading("Implementation Decisions", level=2)
    add_bullets(doc, ["Firestore's aggregate count query avoids downloading every book document.", "CORS is enabled so the Vite browser client can call the HTTPS endpoint.", "Success returns a small JSON object; failures return HTTP 500 and a safe error message.", "The default region is australia-southeast2, matching the tutorial setup."])
    add_note(doc, "Required evidence.", "A clear Firebase Console screenshot must show countBooks as deployed with the student's account visible. A paired code and browser screenshot must show the returned total number of books.")

    page(doc, "eFolio Task 9.1 Book Counter Client", "Vue page requests countBooks and displays the returned value")
    add_code(doc, "src/views/GetBookCountView.vue script", "const count = ref(null)\nconst isLoading = ref(false)\nconst errorMessage = ref('')\n\nconst getBookCount = async () => {\n  const endpoint = import.meta.env.VITE_COUNT_BOOKS_FUNCTION_URL\n  if (!endpoint) {\n    errorMessage.value = 'Add VITE_COUNT_BOOKS_FUNCTION_URL to .env...'\n    return\n  }\n  try {\n    isLoading.value = true\n    const response = await axios.get(endpoint)\n    count.value = Number(response.data.count)\n  } finally {\n    isLoading.value = false\n  }\n}")
    add_code(doc, "src/views/GetBookCountView.vue template", '<button @click="getBookCount">Get Book Count</button>\n<p v-if="count !== null">\n  Total number of books: <strong>{{ count }}</strong>\n</p>')
    doc.add_paragraph("A loading state prevents repeated requests, and an explicit error message distinguishes missing deployment configuration from a failed HTTP request.")

    page(doc, "eFolio Task 9.2 Firestore Capitalisation", "HD function automatically capitalises new book string fields")
    add_code(doc, "functions/index.js capitalizeBookFields", "exports.capitalizeBookFields = onDocumentCreated(\n  'books/{bookId}',\n  async (event) => {\n    const snapshot = event.data\n    if (!snapshot) return\n\n    const original = snapshot.data()\n    const capitalized = Object.fromEntries(\n      Object.entries(original).map(([key, value]) => [\n        key,\n        typeof value === 'string' ? value.toUpperCase() : value\n      ])\n    )\n\n    await snapshot.ref.update(capitalized)\n  }\n)")
    doc.add_heading("Why This Meets the HD Criterion", level=2)
    add_bullets(doc, ["The trigger runs automatically when a document is added to books.", "Every string value is uppercased; numeric ISBN and Firestore timestamps remain unchanged.", "onDocumentCreated does not retrigger after the update, preventing an update loop."])
    add_note(doc, "Best evidence layout.", "Use one readable screenshot containing the Add Book browser form and Firestore result, or two sequential screenshots on separate pages: first the lowercase input, then the uppercase stored document. Include the function code in a separate VS Code screenshot.")

    page(doc, "Week 9 Evidence Capture Checklist", "Screenshots required from the student's own Firebase project")
    add_table(doc, ["Page header", "What must be visible", "Suggested caption"], [
        ["Task 9.1 Deployed Function", "Firebase Functions list countBooks project and account identity", "Deployed Firebase Cloud Function and authenticated project account"],
        ["Task 9.1 Count Books Code", "functions/index.js or GetBookCountView.vue at readable zoom", "Cloud Function and Axios client used to obtain the book count"],
        ["Task 9.1 Count Books Browser", "Book Counter page and returned total", "Running project displays the current number of Firestore books"],
        ["Task 9.2 Capitalisation Code", "capitalizeBookFields trigger", "Firestore create trigger capitalises all string fields"],
        ["Task 9.2 Capitalised Result", "New input and uppercase Firestore document", "New book data is automatically capitalised by the deployed Function"],
    ], [Cm(4.3), Cm(6.1), Cm(6.0)])
    add_note(doc, "Screenshot quality.", "Use native-resolution captures, keep relevant code and results large enough to read, remove unrelated windows, and place one evidence image on each PDF page with a task-specific header and one-sentence caption.")

    page(doc, "eFolio Tasks 10.1 and 10.2 Weather API Client", "Current location and city search implemented with Axios")
    add_code(doc, "src/views/WeatherView.vue reactive state", "const apiKey = import.meta.env.VITE_OPENWEATHER_API_KEY\nconst city = ref('Clayton')\nconst weatherData = ref(null)\n\nconst temperature = computed(() =>\n  weatherData.value ? Math.round(weatherData.value.main.temp - 273.15) : null\n)\n\nconst iconUrl = computed(() =>\n  weatherData.value\n    ? `https://openweathermap.org/img/wn/${weatherData.value.weather[0].icon}@2x.png`\n    : ''\n)")
    add_code(doc, "Weather request and city search", "const requestWeather = async (params) => {\n  const response = await axios.get(\n    'https://api.openweathermap.org/data/2.5/weather',\n    { params: { ...params, appid: apiKey } }\n  )\n  weatherData.value = response.data\n}\n\nconst searchByCity = () => requestWeather({ q: city.value.trim() })")

    page(doc, "eFolio Task 10.1 Current Location Weather", "Geolocation request and complete browser output")
    add_code(doc, "src/views/WeatherView.vue current location", "const searchCurrentLocation = () => {\n  navigator.geolocation.getCurrentPosition(\n    ({ coords }) => requestWeather({\n      lat: coords.latitude,\n      lon: coords.longitude\n    }),\n    () => {\n      errorMessage.value = 'Location permission was not granted...'\n    }\n  )\n}\n\nonMounted(searchCurrentLocation)")
    add_code(doc, "Browser output required by the rubric", '<h2>{{ weatherData.name }}, {{ weatherData.sys.country }}</h2>\n<img :src="iconUrl" alt="Current weather icon" />\n<p>{{ temperature }} C</p>\n<p>{{ weatherData.weather[0].description }}</p>')
    add_note(doc, "Required evidence.", "Capture readable VS Code and browser screenshots showing current-location weather. For HD, search Clayton, AU or another city and show city and country, Celsius temperature, description, and matching icon.")

    page(doc, "eFolio Task 10.2 Get All Books API", "Cloud Function returns Firestore books as JSON")
    add_code(doc, "functions/index.js getAllBooksAPI", "exports.getAllBooksAPI = onRequest((request, response) => {\n  cors(request, response, async () => {\n    if (request.method !== 'GET') {\n      response.status(405).json({ error: 'Method not allowed' })\n      return\n    }\n\n    try {\n      const snapshot = await db.collection('books').orderBy('name').get()\n      const books = snapshot.docs.map((document) => ({\n        id: document.id, ...document.data()\n      }))\n      response.status(200).json({ count: books.length, books })\n    } catch (error) {\n      response.status(500).json({ error: 'Unable to retrieve books' })\n    }\n  })\n})")
    doc.add_heading("API Behaviour", level=2)
    add_bullets(doc, ["GET returns a stable JSON object containing count and books.", "Each book includes its Firestore document ID and stored fields.", "Unsupported methods receive HTTP 405; server failures receive HTTP 500."])

    page(doc, "eFolio Task 10.2 GetAllBookAPI Page", "Vue route automatically loads and displays the API response")
    add_code(doc, "src/views/GetAllBookAPIView.vue script", "const jsonData = ref(null)\n\nconst getAllBooks = async () => {\n  const endpoint = import.meta.env.VITE_GET_ALL_BOOKS_FUNCTION_URL\n  const response = await axios.get(endpoint)\n  jsonData.value = response.data\n}\n\nonMounted(getAllBooks)")
    add_code(doc, "src/views/GetAllBookAPIView.vue template", '<h1>Get All Book API</h1>\n<pre v-if="jsonData">{{ JSON.stringify(jsonData, null, 2) }}</pre>')
    add_code(doc, "src/App.vue header visibility", "const route = useRoute()\nconst showHeader = computed(() => route.name !== 'GetAllBookAPI')\n\n<header v-if=\"showHeader\"><BHeader /></header>")
    add_note(doc, "Required evidence.", "Capture the Get All Book API page with the browser URL visible and the full JSON response readable. Pair it with the Function and Vue code screenshots.")

    page(doc, "Routing Configuration and Build Verification", "Integration into the existing NoMash-Library application")
    add_code(doc, "src/router/index.js new routes", "{ path: '/get-book-count', name: 'GetBookCount', component: GetBookCountView },\n{ path: '/weather-check', name: 'GetWeather', component: WeatherView },\n{ path: '/get-all-book-api', name: 'GetAllBookAPI', component: GetAllBookAPIView }")
    add_code(doc, ".env.example configuration", "VITE_OPENWEATHER_API_KEY=replace_with_your_openweather_key\nVITE_COUNT_BOOKS_FUNCTION_URL=https://REGION-PROJECT_ID.cloudfunctions.net/countBooks\nVITE_GET_ALL_BOOKS_FUNCTION_URL=https://REGION-PROJECT_ID.cloudfunctions.net/getAllBooksAPI")
    add_table(doc, ["Check", "Result"], [
        ["Vite production build", "Passed - 283 modules transformed"],
        ["Node.js server runtime", "Passed - returned Hello from Node.js on port 3000"],
        ["functions/index.js syntax", "Passed - node --check"],
        ["Secrets in source", "OpenWeather key excluded; .env.example contains placeholders"],
        ["External deployment", "Pending authenticated Firebase CLI and Blaze-plan project"],
        ["Live weather request", "Pending student's OpenWeather API key"],
    ], [Cm(6.0), Cm(10.4)])

    page(doc, "Final HD Submission Checklist", "Account specific steps before exporting the final evidence PDF")
    checklist = [
        "Create .env from .env.example and add the OpenWeather key plus both deployed Function URLs.",
        "Install functions dependencies, authenticate Firebase CLI, and deploy countBooks, capitalizeBookFields, and getAllBooksAPI.",
        "Add a lowercase book and verify the Firestore document becomes uppercase automatically.",
        "Open Book Counter and show the returned Firestore total in the browser.",
        "Allow browser location access and capture current-location weather.",
        "Search Clayton, AU and show the Celsius temperature, weather description, and icon.",
        "Open /get-all-book-api and capture the full JSON result with the URL visible.",
        "Capture code at readable zoom; keep one screenshot per page with a task-specific header and one-sentence caption.",
        "Check that Firebase account and project identity are visible where Task 9.1 requires it.",
        "Combine Tasks 9 and 10 into one PDF and review every page at 100 percent zoom before Moodle submission.",
    ]
    for item in checklist:
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.space_after = Pt(4)
        p.add_run(item)
    add_note(doc, "Current conclusion.", "The Week 9 and 10 code is implemented and builds successfully. HD-level completion now depends on deploying with the student's accounts and replacing pending-evidence notes with clear, authentic screenshots of the working services.")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
