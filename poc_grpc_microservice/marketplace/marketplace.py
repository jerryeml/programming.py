import os

from flask import Flask, render_template
import grpc

from recommendations_pb2 import BookCategory, RecommendationRequest
from recommendations_pb2_grpc import RecommendationsStub


app = Flask(__name__)
app.config["DEBUG"] = True

recommendations_host = os.getenv("RECOMMENDATIONS_HOST", "localhost")
recommendations_channel = grpc.insecure_channel(
    f"{recommendations_host}:50051"
)
recommendations_client = RecommendationsStub(recommendations_channel)


@app.route("/", methods=['GET'])
def render_homepage():
    recommendations_request = RecommendationRequest(
        user_id=1, category=BookCategory.MYSTERY, max_results=3
    )
    recommendations_response = recommendations_client.Recommend(
        recommendations_request
    )
    return render_template(
        "homepage.html",
        recommendations=recommendations_response.recommendations,
    )


def init_api():
    app.run(debug=False, use_reloader=False)


if __name__ == '__main__':
    init_api()