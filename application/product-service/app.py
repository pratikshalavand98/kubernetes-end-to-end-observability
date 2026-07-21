from flask import Flask, jsonify, Response
from prometheus_client import Counter, generate_latest
import logging
import json

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "product_requests_total",
    "Total product requests"
)

logging.basicConfig(level=logging.INFO)


@app.route("/product")
def product():

    REQUEST_COUNT.inc()

    logging.info(json.dumps({
        "service": "product-service",
        "event": "product_fetched"
    }))

    return jsonify({
        "product_id": "P1001",
        "product_name": "Cloud Observability Product",
        "price": 999
    })


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
        "service": "product-service"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8082
    )