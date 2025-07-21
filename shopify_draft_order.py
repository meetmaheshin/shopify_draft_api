from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

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
    image_url = data.get("image_url")
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
            "note": "Created by AI T-Shirt Designer"
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
