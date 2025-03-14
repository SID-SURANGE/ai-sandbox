"""
Image Captioning using Llama 3.2 Vision Model

This module implements image captioning functionality using Meta's Llama 3.2 Vision model,
accessed through the Together AI platform. The model combines advanced vision understanding
with natural language generation capabilities to provide detailed image descriptions.

Model Details:
- Name: Llama-3.2-11B-Vision-Instruct-Turbo
- Source: Meta AI (accessed via Together AI platform)
- Size: 11B parameters

API Key Requirements:
- Together AI API key (set in environment variables)
"""

# Import required libraries for image processing, API interaction, and environment variables
import os, base64
import argparse
from together import Together
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

# Load environment variables from .env file
load_dotenv()

# Constants and Configuration
IMAGE_PATH = r".\data\sample.jpg"  # Path to the input image
MODEL_NAME = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo"  # Model identifier
MAX_TOKENS = 200  # Maximum number of tokens in the response
TEMPERATURE = 0.8  # Controls randomness in generation (lower = more deterministic)
TOP_P = 0.8  # Nucleus sampling parameter
TOP_K = 4  # Top-k sampling parameter
REP_PENALTY = 1  # Repetition penalty
STOP_SEQUENCES = ["<|eot_id|>", "<|eom_id|>"]  # Sequences to stop generation

# Initialize the Together API client
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

class ImageCaptionResponse(BaseModel):
    description: str
    keywords: list[str]


def call_model(messages):
    """
    Call the model to generate a response based on the provided messages.

    Args:
        messages (list): The messages to send to the model.

    Returns:
        str: The model's response as a string.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        top_k=TOP_K,
        repetition_penalty=REP_PENALTY,
        stop=STOP_SEQUENCES,
        stream=True
    )

    output = ""
    for token in response:
        if hasattr(token, 'choices') and token.choices:
            try:
                output += token.choices[0].delta.content
            except (IndexError, AttributeError) as error:
                print("Error extracting token content:", error)
    return output


def image_caption(image_path: str):
    """
    Generate a caption for the provided image using the Llama Vision model.

    Args:
        image_path (str): Path to the image file to be captioned

    Returns:
        None: Prints the generated caption and keywords
    """
    # Read and encode the image to base64
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    # Define the prompt template for image captioning
    prompt = """Describe the image, focusing on barista tasks, tools, or coffee preparation processes. Highlight specific actions and techniques visible and also fetch 5 relevant keywords describing the scene or technique or actions as seen inthe image. Only use relevant technical terms.

    Provide your response in the following JSON format:
    {
        "description": "A concise description in 3 sentences.",
        "keywords": ["keyword1", "keyword2", "keyword3", .... "keyword5"]
    }

    Ensure the output is strictly valid JSON without any additional text or explanations."""

    # Create the image URL with base64 encoding
    image_url = f"data:image/png;base64,{encoded_image}"

    # Prepare the API request payload
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }
    ]

    # Attempt to generate a valid JSON response
    for attempt in range(3):
        output = call_model(messages)
        try:
            # Validate the response using Pydantic
            response_data = ImageCaptionResponse.model_validate_json(output)
            print("Final output:", response_data)
            break
        except ValidationError as e:
            print(f"Attempt {attempt + 1}: Invalid JSON response, retrying...")
            if attempt == 2:
                print("Failed to get a valid JSON response after 3 attempts.")


# Script entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate caption for an image.")
    parser.add_argument("--image_path", type=str, default=IMAGE_PATH,
                        help="Path to the image file. If not provided, a default image will be used.")
    args = parser.parse_args()

    image_caption(args.image_path)