from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app) 

import os

SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")


HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}


@app.route('/create-draft-order', methods=['POST'])
def create_draft_order():
    data = request.json
    image_path = data.get("image_url", "").lstrip("/")  # remove leading slash just in case
    frontend_domain = "https://ai-tshirt-frontend.onrender.com"  # ← replace this with your real frontend domain
    image_url = f"{frontend_domain}/{image_path}"

    size = data.get("size")
    color = data.get("color")

    draft_order_payload = {
        "draft_order": {
            "line_items": [
                {
                    "title": f"Custom AI T-Shirt - {color} / {size}",
                    "price": "19.99",
                    "quantity": 1,
                    "properties": [
                        {"name": "Size", "value": size},
                        {"name": "Color", "value": color},
                        {"name": "Design URL", "value": image_url}
                    ]
                }
            ],
            "note": f"Created by AI T-Shirt Designer\nImage: {image_url}"
        }
    }

    response = requests.post(
        f"https://{SHOPIFY_STORE_URL}/admin/api/2023-04/draft_orders.json",
        headers=HEADERS,
        json=draft_order_payload
    )

    if response.status_code == 201:
        invoice_url = response.json()["draft_order"]["invoice_url"]
        return jsonify({"invoice_url": invoice_url})
    else:
        print("Error:", response.status_code)
        print(response.text)
        return jsonify({"error": "Failed to create draft order"}), 400
    

from werkzeug.utils import secure_filename

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    static_folder = os.path.join(app.root_path, "static")
    os.makedirs(static_folder, exist_ok=True)  # ✅ Ensure static/ folder exists

    unique_name = f"user_{os.urandom(4).hex()}_{filename}"
    file_path = os.path.join(static_folder, unique_name)
    file.save(file_path)

    print(f"📸 Image uploaded: {file_path}")
    return jsonify({ "image_url": f"https://shopify-draft-api.onrender.com/static/{unique_name}" })  # ✅ Updated path


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
