from flask import Flask, jsonify, Response
from prometheus_client import Counter, generate_latest
import logging
import json

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "payment_requests_total",
    "Total payment requests"
)

logging.basicConfig(level=logging.INFO)


@app.route("/payment")
def payment():

    REQUEST_COUNT.inc()

    logging.info(json.dumps({
        "service": "payment-service",
        "event": "payment_processed"
    }))

    return jsonify({
        "payment_id": "PAY1001",
        "payment_status": "successful"
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
        "service": "payment-service"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8083
    )