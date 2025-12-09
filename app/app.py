import logging
from flask import Flask

app = Flask(__name__)

# Configure logging
log_file = "logs/pipeline_logs/app.log"
logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

@app.route("/")
def hello():
    return "Hello, Self-Healing CI/CD!"

@app.route("/fail")
def fail():
    try:
        raise Exception("Simulated failure for testing CI/CD pipeline.")
    except Exception as e:
        app.logger.error(f"Failure occurred: {str(e)}")
        raise   # still raise so the test gets 500 response

if __name__ == "__main__":
    import os
    os.makedirs("logs/pipeline_logs", exist_ok=True)  # make sure logs dir exists
    app.run(host="0.0.0.0", port=5000)
