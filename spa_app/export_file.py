from flask import make_response, render_template, current_app
import pdfkit

def export_pdf_from_url(template, **context):
    config = pdfkit.configuration(
        wkhtmltopdf=current_app.config["PDF_KIT"].wkhtmltopdf,
    )

    options = {
        "encoding": "utf-8",
        "enable-local-file-access": None
    }

    html = render_template(template, **context)

    return pdfkit.from_string(
        html,
        False,
        configuration=config,
        options=options
    )



