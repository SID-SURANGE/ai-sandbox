# Standard library imports
from pathlib import Path
import logging
# third party library imports
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

# local imports
from src.loaders.text_loader import process_text, process_pdf, process_docx
from src.loaders.image_loader import process_image
# from src.loaders.video_loader import process_video

# Create a router for the parser endpoints
router = APIRouter(tags=["data_loader"])

@router.post("/load-data")
async def add_knowledge(request: Request, folder_path: str = "data") -> JSONResponse:
    """
    Load and process files from the specified folder into the knowledge base.
    """
    processed_files = {
        "success": [],
        "failed": [],
        "unsupported": []
    }
        
    try:
        for file in Path(folder_path).glob("*"):
            if not file.is_file():
                continue
                
            file_type = file.suffix.lower()
            # if file_type == ".txt":
            #     if process_text(file):
            #         processed_files["success"].append(str(file))
            #     else:
            #         processed_files["failed"].append(str(file))
            # elif file_type == ".pdf":
            #     if process_pdf(file):
            #         processed_files["success"].append(str(file))
            #     else:
            #         processed_files["failed"].append(str(file))
            # elif file_type == ".docx":
            #     if process_docx(file):
            #         processed_files["success"].append(str(file))
            #     else:
            #         processed_files["failed"].append(str(file))
            if file_type in [".jpg", ".jpeg", ".png"]:
                if process_image(file):
                    processed_files["success"].append(str(file))
                else:
                    processed_files["failed"].append(str(file))
            else:
                processed_files["unsupported"].append(str(file))
                logging.info(f"Unsupported file type: {file}")
                
        # Prepare response message
        total_files = len(processed_files["success"]) + len(processed_files["failed"]) + len(processed_files["unsupported"])
        response_message = f"Processed {total_files} files:\n"
        response_message += f"- Successfully processed: {len(processed_files['success'])} files\n"
        response_message += f"- Failed to process: {len(processed_files['failed'])} files\n"
        response_message += f"- Unsupported files: {len(processed_files['unsupported'])} files"
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "response": response_message,
                "details": processed_files
            }
        )
            
    except Exception as e:
        logging.error(f"Error in add_knowledge: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "response": f"Error processing files: {str(e)}"
            }
        )
