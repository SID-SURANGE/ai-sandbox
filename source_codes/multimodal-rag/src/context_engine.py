# Standard library imports
from typing import Dict, List, Union
from pathlib import Path

# Local imports
from src.model import run_llm
from src.retriever import query_db

TOP_RESULTS = 5

def process_result_for_display(result: Dict) -> Dict:
    """
    Process a search result for display.
    
    Args:
        result (Dict): Raw search result
        
    Returns:
        Dict: Processed result with display-ready fields
    """
    print(f"\nProcessing result: {result}\n")
    
    display_result = {
        "type": result.get("content_type", "unknown"),  # Map content_type to type for display
        "filename": result.get("filename", "unknown"),
        "file_path": result.get("file_path", ""),
        "description": result.get("description", "") or result.get("content", "No description available")
    }
    
    # Only include what's needed for display
    if display_result["type"] == "image":
        display_result["caption"] = display_result["description"]
    
    return display_result

async def get_contextualized_llm_response(query: str) -> Dict[str, Union[str, List[Dict]]]:
    """
    Process query and return LLM response with relevant context and display info.
    
    Args:
        query (str): User's query
        
    Returns:
        Dict with:
            - llm_response (str): LLM's response
            - display_results (List[Dict]): Results prepared for display
    """
    try:
        print("\nProcessing query:", query)
        
        # 1. Query the database
        results = query_db(query, limit=TOP_RESULTS)
        
        # If no relevant results found, return early
        if not results:
            return {
                "llm_response": "I apologize, but I don't have any relevant information in my knowledge base to answer your question about that topic.",
                "display_results": []
            }
        
        # 2. Prepare context and display results
        context = []
        display_results = []
        
        for result in results:
            # Prepare result for display
            display_result = process_result_for_display(result)
            display_results.append(display_result)
            
            # Add to context for LLM
            if display_result["type"] != "image":
                context.append(display_result["description"])
            else:
                # For images, add their captions to context
                context.append(f"There is an image '{display_result['filename']}' with caption: {display_result['description']}")
        
        # 3. Get LLM response using context
        context_text = "\n".join(context)
        llm_response = run_llm(query, context_text)
        
        print(f'LLM response: {llm_response}')
        print(f'Display results: {display_results}')

        # 4. Return both LLM response and display results
        return {
            "llm_response": llm_response,
            "display_results": display_results
        }
        
    except Exception as e:
        print(f"Error in context engine: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {
            "llm_response": f"Error processing query: {str(e)}",
            "display_results": []
        }