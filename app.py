import os
import shutil
import requests
from flask import Flask, request, jsonify, send_file
from templates import *
from scraper import is_local_path, scrape_artical
from io import BytesIO
import traceback
import uuid
from datetime import datetime 
app = Flask(__name__)

BASE_OUTPUT_DIR = "/var/www/html/api.pixelbreeze.xyz/temp"  # Directory to save generated images

def generate_unique_output_path(user_id, extension="png"):
    """
    Generates a unique output file path based on user_id and timestamp.
    """
    user_dir = os.path.join(BASE_OUTPUT_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)  # Ensure the directory exists
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}.{extension}"
    return os.path.join(user_dir, filename)

@app.route("/generate", methods=["POST"])
def generate_image():
    try:
        
        session_id = request.form.get("session_id", None)
        if not session_id:
            response = {"error": "session_id is required"}
            app.logger.error("session_id not provided.")
            return jsonify(response), 400

        artical_url = request.form.get("artical_url",None)
        app.logger.debug(f'Artical URL: {artical_url}')

        output_img_path = request.form.get("output_img_path")
        template_type = request.form.get("template_type", "sample")
        crop_mode = request.form.get("crop_mode", "square")
        app.logger.debug(f'Template Type: {template_type}, Crop Mode: {crop_mode}')

        # Generate a unique output path for this user
        output_img_path = generate_unique_output_path(session_id)

        if template_type in ["quotes_writings_art", "quotes_writings_morning", "quotes_writings_citim", "quotes_writings_thonjeza", "reforma_quotes_writings", "reforma_new_quote", "reforma_feed_swipe"]:
            text = request.form.get("text","")
            input_img_path_url = None
            input_img_path = request.form.get("input_img_path",input_img_path_url)

            if template_type == "quotes_writings_art":
                author = request.form.get("sub_text","")
                quotes_writings_art(text, author, output_img_path, crop_mode)
                
            elif template_type == "quotes_writings_morning":
                quotes_writings_morning(text, output_img_path, crop_mode)

            elif template_type == "quotes_writings_thonjeza":
                arrow = request.form.get("arrow","")
                quotes_writings_thonjeza(text, output_img_path, crop_mode, arrow)

            elif template_type == "quotes_writings_citim":
                sub_text = request.form.get("sub_text","").upper()
                arrow = request.form.get("arrow")
                quotes_writings_citim(text,sub_text, output_img_path, crop_mode, arrow)

            # reforma templates
            elif template_type == "reforma_quotes_writings":
                sub_text = request.form.get("sub_text","").upper()
                arrow = request.form.get("arrow")
                reforma_quotes_writings(text,sub_text, output_img_path, crop_mode, arrow)

            elif template_type == "reforma_new_quote":
                sub_text = request.form.get("sub_text","").upper()
                arrow = request.form.get("arrow")
                reforma_new_quote(text, sub_text, output_img_path, crop_mode, arrow)

            elif template_type == "reforma_feed_swipe":
                arrow = request.form.get("arrow")
                reforma_feed_swipe(text, input_img_path, output_img_path, crop_mode, arrow)

        else:
            title = ""
            input_img_path_url = None
            if artical_url:
                title, img_url = scrape_artical(artical_url)

                if title == None or img_url == None:
                    response = {"error": "can not scrape given URL"}
                    app.logger.error(f"error: can not scrape given URL")
                    return jsonify(response), 500
                if is_local_path(img_url):
                    print(f"The path {img_url} is a local file.")
                    with open(img_url, "rb") as img_file:
                            img_data = img_file.read()
                    input_img_path_url = BytesIO(img_data)
                    os.remove(img_url)
                else:
                    print(f"The path {img_url} is not a local file.")
                    response = requests.get(img_url)
                    input_img_path_url = BytesIO(response.content)

            text = request.form.get("text",title)
            print('text: ', text, title)
            input_img_path = request.form.get("input_img_path",input_img_path_url)
            if input_img_path == '':
                input_img_path = input_img_path_url

            if template_type == "feed_basic":
                arrow = request.form.get("arrow")
                feed_basic(text, input_img_path, output_img_path, crop_mode, arrow)

            elif template_type == "feed_swipe":
                arrow = request.form.get("arrow")
                feed_swipe(text, input_img_path, output_img_path, crop_mode, arrow)

            elif template_type == "highlight":
                text_to_hl = request.form.get('text_to_hl', "")
                arrow = request.form.get("arrow")
                highlight_template(text, input_img_path, output_img_path, crop_mode, arrow, text_to_hl)

            elif template_type == "logo_only":
                logo_position = int(request.form.get("logo_position"))
                logo_only(input_img_path, output_img_path, crop_mode, logo_position)

            elif template_type == "web_news":
                sub_text = request.form.get("sub_text","LAJME").upper()
                sub_text="LAJME" if len(sub_text)==0 else sub_text

                text_to_hl = request.form.get("text_to_hl", "")
                arrow = request.form.get("arrow")
                web_news(text, sub_text, text_to_hl, input_img_path, output_img_path, crop_mode, arrow)

            elif template_type == "citim":
                author = request.form.get("sub_text")
                sub_text = author.upper()
                citim(text, sub_text, input_img_path, output_img_path, crop_mode)

            elif template_type == "citim_version_2":
                sub_text = request.form.get("sub_text","").upper()
                arrow = request.form.get("arrow")
                citim_version_2(text,sub_text, input_img_path, output_img_path, crop_mode, arrow)

            elif template_type == "iconic_location":
                iconic_location(text, input_img_path, output_img_path, crop_mode)

            elif template_type == "feed_location":
                location = request.form.get("location", "")
                arrow = request.form.get("arrow")
                feed_location(text, input_img_path, output_img_path, crop_mode, location, arrow)

            elif template_type == "web_news_story":
                cat = request.form.get("sub_text","LAJME")
                category = cat.upper()
                web_news_story(text, category, input_img_path, output_img_path, crop_mode)
            
            elif template_type == "feed_headline":
                sub_text = request.form.get("sub_text")
                arrow = request.form.get("arrow")
                feed_headline(text, sub_text, input_img_path, output_img_path, crop_mode, arrow)

            elif template_type == "web_news_story_2":
                sub_text = request.form.get("sub_text","")
                category = request.form.get("category","LAJME").upper()
                category="LAJME" if len(category)==0 else category
                crop_mode = "square"
                web_news_story_2(text,sub_text, category, input_img_path, output_img_path, crop_mode)

            elif template_type == "reforma_web_news_story_2":
                if text == '':
                    text = title
                sub_text = request.form.get("sub_text","")
                category = request.form.get("category","LAJME").upper()
                category="LAJME" if len(category)==0 else category
                crop_mode = "square"
                reforma_web_news_story_2(text,sub_text, category, input_img_path, output_img_path, crop_mode)

            elif template_type == "reforma_news_feed":
                sub_text = request.form.get("sub_text","").upper()
                arrow = request.form.get("arrow")
                reforma_news_feed(text,sub_text, input_img_path, output_img_path, crop_mode, arrow)

            elif template_type == "reforma_web_news_story1":
                if text == '':
                    text = title
                sub_text = request.form.get("sub_text","")
                category = request.form.get("category","LAJME").upper()
                category="LAJME" if len(category)==0 else category
                crop_mode = "square"
                reforma_web_news_story1(text,sub_text, category, input_img_path, output_img_path, crop_mode)

            elif template_type == "reforma_web_news_story2":
                if text == '':
                    text = title
                category = request.form.get("sub_text","LAJME").upper()
                category="LAJME" if len(category)==0 else category
                crop_mode = "story"
                print('reforma_web_news_story2: ', title, input_img_path, category)
                reforma_web_news_story2(text, category, input_img_path, output_img_path, crop_mode)
                
            elif template_type == "reforma_logo_only":
                pos = request.form.get("pos","").upper()
                reforma_logo_only(pos, input_img_path, output_img_path, crop_mode)

            elif template_type == "story_2":
                category = request.form.get("sub_text","LAJME").upper()
                category="LAJME" if len(category)==0 else category
                crop_mode = "story"
                story_2(text, category, input_img_path, output_img_path, crop_mode)

            else:
                response = {"Invalid Template": template_type}
                return jsonify(response)


        # Return the filename of the generated image as a response
        response = {"output_file_path": output_img_path}
        
        return jsonify(response), 200

    except Exception as e:
        response = {"error": str(e)}
        app.logger.error(f"Error: {e}")
        traceback.print_exc()
        return jsonify(response), 500

if __name__ == "__main__":
    app.run(debug=True)
