## Notes
pdfXss-gen.py is a Python proof-of-concept that generates a PDF with embedded JavaScript. When opened in a PDF viewer, the file fires `/OpenAction` JavaScript, shows credential prompts via `app.response`, stores the responses in hidden AcroForm fields, and exfiltrates them to a webhook using the PDF's native SubmitForm action — then displays a "GOTCHA" security-awareness message. For authorized testing only.

Read more here: https://portswigger.net/research/portable-data-exfiltration

## Author

[![Follow spy0x1 on X](https://img.shields.io/badge/FOLLOW%20ME-spy0x1-blue?style=for-the-badge&logo=x&logoColor=white)](https://x.com/spy0x1)
