from flask import Flask, jsonify
import os
import requests
import logging
import json
import time
from prometheus_client import Counter, Histogram, generate_latest
from flask import Response

app = Flask(__name__)

ORDER_SERVICE_URL = os.getenv(
    "ORDER_SERVICE_URL",
    "http://order-service:8081"
)

REQUEST_COUNT = Counter(
    "frontend_requests_total",
    "Total frontend requests"
)

REQUEST_LATENCY = Histogram(
    "frontend_request_latency_seconds",
    "Frontend request latency"
)

logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    REQUEST_COUNT.inc()

    start = time.time()

    try:
        response = requests.get(
            f"{ORDER_SERVICE_URL}/order",
            timeout=5
        )

        logging.info(json.dumps({
            "service": "frontend",
            "event": "order_request",
            "status_code": response.status_code
        }))

        return jsonify({
            "service": "frontend",
            "message": "Request processed successfully",
            "order_response": response.json()
        }), response.status_code

    except Exception as e:
        logging.error(json.dumps({
            "service": "frontend",
            "event": "order_request_failed",
            "error": str(e)
        }))

        return jsonify({
            "error": "Order service unavailable"
        }), 500

    finally:
        REQUEST_LATENCY.observe(time.time() - start)


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
        "service": "frontend"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )