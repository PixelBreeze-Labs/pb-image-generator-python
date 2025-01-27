import os
import tempfile
import hashlib
import requests
from flask import Flask, request, jsonify
from templates import *
from scraper import is_local_path, scrape_artical
from io import BytesIO
import traceback
from functools import lru_cache

app = Flask(__name__)
BASE_OUTPUT_DIR = "/var/www/html/api.pixelbreeze.xyz/temp"  # Directory to save generated images

# Cache for already processed templates
@lru_cache(maxsize=100)
def cached_template(template_key):
    return os.path.exists(template_key)

def generate_cache_key(template_type, params):
    """Generate a unique cache key based on parameters."""
    key_string = f"{template_type}_{params}"
    return hashlib.md5(key_string.encode()).hexdigest()

def generate_unique_output_path(user_id, extension="png"):
    """Generates a unique output file path based on user_id and timestamp."""
    user_dir = os.path.join(BASE_OUTPUT_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)  # Ensure the directory exists
    filename = f"{uuid.uuid4().hex}.{extension}"
    return os.path.join(user_dir, filename)

def validate_request(form, required_fields):
    """Validate required fields in the request."""
    for field in required_fields:
        if not form.get(field):
            raise ValueError(f"{field} is required.")

def process_article_url(article_url):
    """Handle article scraping logic."""
    title, img_url = scrape_artical(article_url)
    if title is None or img_url is None:
        raise ValueError("Unable to scrape the provided article URL.")
    if is_local_path(img_url):
        with open(img_url, "rb") as img_file:
            img_data = img_file.read()
        os.remove(img_url)
    else:
        response = requests.get(img_url)
        img_data = response.content
    return title, BytesIO(img_data)

@app.route("/generate", methods=["POST"])
def generate_image():
    try:
        # Validate required fields
        validate_request(request.form, ["template_type", "crop_mode"])

        template_type = request.form.get("template_type", "sample")
        crop_mode = request.form.get("crop_mode", "square")
        article_url = request.form.get("artical_url", None)
        session_id = request.form.get("session_id", "default_session")
        output_img_path = generate_unique_output_path(session_id)

        # Log incoming request
        app.logger.debug(f"Processing template: {template_type} with crop mode: {crop_mode}")

        # Process article URL if provided
        title, input_img_path = "", None
        if article_url:
            title, input_img_path = process_article_url(article_url)

        # Default text and input image path
        text = request.form.get("text", title)
        input_img_path = input_img_path or request.form.get("input_img_path")

        # Generate cache key and check for cached results
        cache_key = generate_cache_key(template_type, request.form.to_dict())
        if cached_template(cache_key):
            return jsonify({"output_file_path": cached_template(cache_key)}), 200

        # Route templates for processing
        if template_type.startswith("quotes_writings"):
            process_quotes_writings(template_type, request, output_img_path, crop_mode)

        elif template_type.startswith("reforma"):
            process_reforma_templates(template_type, request, output_img_path, crop_mode)

        else:
            process_misc_templates(template_type, request, output_img_path, crop_mode)

        # Cache the generated file path
        cached_template(cache_key)

        return jsonify({"output_file_path": output_img_path}), 200

    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def process_quotes_writings(template_type, request, output_path, crop_mode):
    """Process quotes and writings templates."""
    text = request.form.get("text", "")
    if template_type == "quotes_writings_art":
        author = request.form.get("sub_text", "")
        quotes_writings_art(text, author, output_path, crop_mode)
    elif template_type == "quotes_writings_morning":
        quotes_writings_morning(text, output_path, crop_mode)
    # Add additional quotes_writings templates here...

def process_reforma_templates(template_type, request, output_path, crop_mode):
    """Process reforma templates."""
    text = request.form.get("text", "")
    sub_text = request.form.get("sub_text", "").upper()
    if template_type == "reforma_quotes_writings":
        arrow = request.form.get("arrow", "")
        reforma_quotes_writings(text, sub_text, output_path, crop_mode, arrow)
    # Add additional reforma templates here...

def process_misc_templates(template_type, request, output_path, crop_mode):
    """Process miscellaneous templates."""
    text = request.form.get("text", "")
    if template_type == "feed_basic":
        arrow = request.form.get("arrow", "")
        feed_basic(text, input_img_path, output_path, crop_mode, arrow)
    # Add additional misc templates here...

if __name__ == "__main__":
    app.run(debug=True)
