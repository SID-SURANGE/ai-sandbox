# Standard library imports
import os, logging
from typing import Dict
from io import BytesIO
import base64
from dotenv import load_dotenv
load_dotenv()

# Third-party imports
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from together import Together
from pydantic import BaseModel, ValidationError

# OpenAI imports
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_ID = "hermes-3-llama-3.2-3b"
CAPTION_MODEL_ID = "llava-v1.5-7b"
BASE_URL = "http://localhost:1234/v1"
API_KEY = "lm-studio"
TEMPERATURE = 0.2

# Constants and Configuration
MODEL_NAME = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo"  # Model identifier
MAX_TOKENS = 200  # Maximum number of tokens in the response
TEMPERATURE_CAPTION = 0.8  # Controls randomness in generation (lower = more deterministic)
TOP_P = 0.8  # Nucleus sampling parameter
TOP_K = 4  # Top-k sampling parameter
REP_PENALTY = 1  # Repetition penalty
STOP_SEQUENCES = ["<|eot_id|>", "<|eom_id|>"]  # Sequences to stop generation

class ImageCaptionResponse(BaseModel):
    description: str
    keywords: list[str]

# Initialize the Together API client
togetherai_client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
openai_client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

def run_llm(user_query:str, context: str) -> JSONResponse:
    """
    Function to interact with the LLM (Language Model) and fetch a response.

    Args:
        query (str): The user's query to be processed by the LLM.

    Returns:
        JSONResponse: A JSON response containing the LLM's output.
    """
    try:        
        # Define the chat completion request
        completion = openai_client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": """You are an AI assistant that helps analyze information STRICTLY from the provided documents. 
                
                IMPORTANT RULES:
                1. ONLY use information that is explicitly present in the provided documents
                2. If the provided documents don't contain enough information to fully answer the query, say so clearly
                3. DO NOT use any external knowledge or make assumptions beyond what's in the documents
                4. If an image is provided, only describe what the image shows and its caption - do not make inferences beyond this
                5. If the information in the documents is not relevant to the query, state that you cannot help with that specific topic
                6. Never reference the documents themselves in your response
                7. If you're unsure about any information, err on the side of saying you don't have enough information
                
                Remember: It's better to say you don't have enough information than to provide information not supported by the documents."""},
                
                {"role": "user", "content": f"""User Query: {user_query}

                Retrieved Documents:
                {context}

                Please provide a response using ONLY the information from these documents. If the information is not sufficient or relevant, say so."""}
            ],
            temperature=TEMPERATURE,
        )
        
        # Extract the response from the LLM's output
        response_message = completion.choices[0].message.content
        
        # Log the response for debugging purposes
        logger.info(f"LLM Response: {response_message}")
        
        return response_message
    
    except Exception as e:
        # Log the error and raise an HTTPException for FastAPI to handle
        logger.error(f"Error in LLM completion: {e}")
        raise HTTPException(status_code=500, detail=f"Error in LLM completion: {str(e)}")


def call_caption_model(messages):
    """
    Call the model to generate a response based on the provided messages.

    Args:
        messages (list): The messages to send to the model.

    Returns:
        str: The model's response as a string.
    """
    response = togetherai_client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE_CAPTION,
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
    
def run_caption_model(image: Image.Image, file_path: str) -> str:
    """
    Generate a descriptive caption for the given PIL Image using LLM.
    Args:
        image: PIL Image object
    Returns:
        str: Generated caption describing the image
    """
    try:
        # Read and encode the image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Define the prompt template for image captioning
        prompt = """Describe the image, focusing on barista tasks, tools, or coffee preparation processes. Highlight specific actions and techniques visible and also fetch 5 relevant keywords describing the scene or technique or actions as seen inthe image. Only use relevant technical terms.

        Provide your response in the following JSON format:
        {
            "description": "A concise description in 3 sentences.",
            "keywords": ["keyword1", "keyword2", "keyword3", .... "keyword5"]
        }

        Ensure the output is strictly valid JSON without any additional text or explanations."""

        # Create the image URL with base64 encoding
        image_url = f"data:image/png;base64,{img_str}"

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
            output = call_caption_model(messages)
            try:
                # Validate the response using Pydantic
                response_data = ImageCaptionResponse.model_validate_json(output)
                print("Final output:", response_data)
                break
            except ValidationError as e:
                print(f"Attempt {attempt + 1}: Invalid JSON response, retrying...")
                if attempt == 2:
                    return "Failed to get a valid JSON response after 3 attempts."

        print(f"\nGenerated caption for file {file_path}: {response_data}")
        return response_data

    except Exception as e:
        logger.error(f"\nError generating image caption: {str(e)}")
        return "Error generating image description"

# def run_caption_model(image: Image.Image, file_path: str) -> str:
#     """
#     Generate a descriptive caption for the given PIL Image using LLM.
#     Args:
#         image: PIL Image object
#     Returns:
#         str: Generated caption describing the image
#     """
#     try:
#         # Convert PIL Image to base64 if required by the model
#         buffered = BytesIO()
#         image.save(buffered, format="PNG")
#         img_str = base64.b64encode(buffered.getvalue()).decode()

#         # Truncate the input context if it exceeds the model's maximum context length
#         max_context_length = 4000
#         user_content = f"Describe the image focusing on the objects and their interactions if any. Image data: data:image/png;base64,{img_str}"
#         if len(user_content) > max_context_length:
#             user_content = user_content[:max_context_length]

#         # Use the image directly if the model supports it
#         completion = client.chat.completions.create(
#             model=CAPTION_MODEL_ID,
#             messages=[
#                 {"role": "system", "content": """You are an expert caption generator focused on providing descriptive captions that emphasize both the objects identified in the image and any interactions between them. When analyzing an image:
#                 1. Identify the main objects present.
#                 2. Describe the interactions, actions, or relationships between these objects if any.
#                 3. Provide a concise and natural description without technical jargon.
#                 4. Ensure the caption directly reflects what is visible in the image."""},
#                 {"role": "user", "content": user_content}
#             ],
#             temperature=0.2,
#         )

#         caption = completion.choices[0].message.content
#         print(f"\nGenerated caption for file {file_path}: {caption}")
#         logger.info(f"\nGenerated caption {file_path}: {caption}")

#         return caption

#     except Exception as e:
#         logger.error(f"\nError generating image caption: {str(e)}")
#         return "Error generating image description"
