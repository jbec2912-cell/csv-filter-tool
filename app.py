#!/usr/bin/env python3
"""Flask web app for CSV conversion."""

from io import BytesIO
from flask import Flask, render_template, request, send_file, jsonify

from convert_appointment import OUTPUT_NAME, convert_content

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/convert", methods=["POST"])
def api_convert():
    """API endpoint for CSV conversion."""
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
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
