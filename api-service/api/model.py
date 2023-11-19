from google.cloud import aiplatform
import base64


def make_prediction_vertexai(image_path):
    print("Predict using Vertex AI endpoint")

    # Get the endpoint
    # Endpoint format: endpoint_name="projects/{PROJECT_NUMBER}/locations/us-central1/endpoints/{ENDPOINT_ID}"
    endpoint = aiplatform.Endpoint(
        "projects/551792351994/locations/us-central1/endpoints/1274186642034262016"
    )

    with open(image_path, "rb") as f:
        data = f.read()
    b64str = base64.b64encode(data).decode("utf-8")
    # The format of each instance should conform to the deployed model's prediction input schema.
    instances = [{"bytes_inputs": {"b64": b64str}}]

    result = endpoint.predict(instances=instances)

    print("Result:", result)
    prediction = result.predictions[0]
    print(prediction)

    return {
        "calories": prediction[0],
        "total_mass_g": prediction[1],
        "fat_g": prediction[2],
        "carbs_g": prediction[3],
        "protein_g": prediction[4],
    }
