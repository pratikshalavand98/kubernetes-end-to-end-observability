from flask import Flask, jsonify
import requests
import os
import logging
import json
import time
from prometheus_client import Counter, Histogram, generate_latest
from flask import Response

app = Flask(__name__)

PRODUCT_SERVICE_URL = os.getenv(
    "PRODUCT_SERVICE_URL",
    "http://product-service:8082"
)

PAYMENT_SERVICE_URL = os.getenv(
    "PAYMENT_SERVICE_URL",
    "http://payment-service:8083"
)

REQUEST_COUNT = Counter(
    "order_requests_total",
    "Total order requests"
)

REQUEST_LATENCY = Histogram(
    "order_request_latency_seconds",
    "Order request latency"
)

logging.basicConfig(level=logging.INFO)


@app.route("/order")
def create_order():

    REQUEST_COUNT.inc()

    start = time.time()

    try:

        product_response = requests.get(
            f"{PRODUCT_SERVICE_URL}/product",
            timeout=5
        )

        payment_response = requests.get(
            f"{PAYMENT_SERVICE_URL}/payment",
            timeout=5
        )

        logging.info(json.dumps({
            "service": "order-service",
            "event": "order_created",
            "product_status": product_response.status_code,
            "payment_status": payment_response.status_code
        }))

        return jsonify({
            "service": "order-service",
            "order_status": "created",
            "product": product_response.json(),
            "payment": payment_response.json()
        })

    except Exception as e:

        logging.error(json.dumps({
            "service": "order-service",
            "event": "order_failed",
            "error": str(e)
        }))

        return jsonify({
            "error": "Order processing failed"
        }), 500

    finally:

        REQUEST_LATENCY.observe(
            time.time() - start
        )


@app.route("/metrics")
def metrics():

    return Response(
        generate_latest(),
        mimetype="text/plain"
    )


@app.route("/health")
def health():

    return jsonify({
        "status": "healthy",
        "service": "order-service"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8081
    )