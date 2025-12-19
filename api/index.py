#!/usr/bin/env python3
"""Flask web app for CSV conversion - Vercel compatible."""

import os
from io import BytesIO
from flask import Flask, render_template, request, send_file, jsonify

from convert_appointment import OUTPUT_NAME, convert_content

# When running under Vercel, this file lives in api/, but templates/ is at project root.
# Point Flask to the correct templates directory explicitly.
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
app = Flask(__name__, template_folder=TEMPLATES_DIR)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route("/")
@app.route("/api")
@app.route("/index")
@app.route("/api/index")
def index():
    return render_template("index.html")


# On Vercel, requests arrive at /api/*, and Flask sees the path without the /api prefix.
# So the browser should call /api/convert, and Flask should register /convert here.
@app.route("/convert", methods=["POST"])
@app.route("/api/convert", methods=["POST"])
@app.route("/index/convert", methods=["POST"])
@app.route("/api/index/convert", methods=["POST"])
def api_convert():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        content = file.read().decode("utf-8-sig")
        converted, _ = convert_content(content)

        output = BytesIO(converted.encode("utf-8"))
        output.seek(0)

        return send_file(
            output,
            mimetype="text/csv",
            as_attachment=True,
            download_name=OUTPUT_NAME,
        )
    except Exception as e:  # noqa: BLE001
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
