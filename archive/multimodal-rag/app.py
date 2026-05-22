import streamlit as st
import requests
import hashlib
from pathlib import Path
import logging
import chromadb
import os

# local imports
from utils.custom_styling import apply_custom_css

# --- Constants ---
TITLE = "Barista Bot: Your Coffee Crafting Companion ☕️"
SUBTITLE = "Guide to Perfecting Recipes!"
INPUT_PLACEHOLDER = "Ask anything about coffee:"
API_CONFIG = {
    "BARISTA_URL": "http://127.0.0.1:8000/api/v1/ask-barista-bot",
    "DATA_LOADER_URL": "http://127.0.0.1:8000/api/v1/load-data",
}
ADMIN_PASSWORD = "bd94dcda26fccb4e68d6a31f9b5aac0b571ae266d822620e901ef7ebe3a11d4f"
UPLOAD_PATH = "data"

# --- Initialization ---
def initialize_session_state():
    """Initialize or reset session state variables."""
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "doc_loaded" not in st.session_state:
        st.session_state.doc_loaded = False
    if "files_processed" not in st.session_state:
        st.session_state.files_processed = False
    if "messages" not in st.session_state:
        st.session_state.messages = []

def clear_chat():
    st.session_state.conversation_history = []
    st.session_state.messages = []

# --- Caching Decorators ---
@st.cache_resource
def get_chromadb_client():
    """Create a persistent ChromaDB client with caching."""
    return chromadb.PersistentClient(path="./chromadb")

@st.cache_data
def verify_password(input_password):
    """Verify admin password with caching."""
    hashed_input = hashlib.sha256(input_password.encode()).hexdigest()
    return hashed_input == ADMIN_PASSWORD

# --- Page Configuration ---
def setup_page_config():
    """Set up Streamlit page configuration."""
    st.set_page_config(
        page_title="Coffee Bot",
        page_icon="🤖",
    )

# --- Admin Features ---
def show_admin_features():
    """Display admin-specific features."""
    st.sidebar.success("Admin access granted!")
    try:
        # Initialize ChromaDB client and collection
        client = get_chromadb_client()
        collection = client.get_collection(name="multimodal_data_new")
        
        # Check if collection exists or is empty and display persistent messages
        if collection is None or collection.count() == 0:
            st.sidebar.warning("No collection/data found! Please upload documents to the database.")
                    
            # Button to load documents into DB
            if st.button("Load Documents to DB", key="load_db_button"):
                try:
                    res = requests.post(API_CONFIG["DATA_LOADER_URL"], timeout=600)
                    res.raise_for_status()
                    data = res.json()
                    if data["status"] == "success":
                        st.success(data["response"])
                        st.session_state.doc_loaded = True
                        st.sidebar.info("Documents loaded successfully!")
                    else:
                        st.error(data.get("response", "Error loading documents"))
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.sidebar.info("Collection found! You can upload new documents.")
            # File uploader and processing in the sidebar
            st.sidebar.subheader("Upload Custom Documents")
            uploaded_files = st.sidebar.file_uploader(
                "Choose files to add to the knowledge base",
                accept_multiple_files=True,
                type=['pdf', 'txt', 'docx'],
                key="custom_document_uploader"
            )
            if uploaded_files:
                if st.sidebar.button("Process Uploaded Files", key="process_files_button"):
                    for file in uploaded_files:
                        file_path = Path(UPLOAD_PATH) / file.name
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())
                    try:
                        res = requests.post(API_CONFIG["DATA_LOADER_URL"], timeout=600)
                        res.raise_for_status()
                        data = res.json()
                        if data["status"] == "success":
                            st.success(data["response"])
                            st.session_state.files_processed = True
                            st.sidebar.info("Uploaded files processed successfully!")
                            # Optionally display processing stats:
                            stats = data["data"]
                            st.write(f"Processed: {stats.get('processed', 0)} files")
                            if stats.get('failed', 0) > 0:
                                st.warning(f"Failed: {stats.get('failed', 0)} files")
                            if stats.get('unsupported', 0) > 0:
                                st.info(f"Unsupported: {stats.get('unsupported', 0)} files")
                        else:
                            st.error(data.get("response", "Unknown error occurred"))
                    except Exception as e:
                        st.error("Failed to process files. Please try again.")
                        logging.error(f"Error processing files: {str(e)}")
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")

# --- Chat Functions ---
def initialize_chat_history():
    """Initialize chat history in session state."""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

def display_search_results(results):
    """Display search results in a clean format with images."""
    if not results:
        return
        
    st.write("---")
    st.subheader("Related Information")
    
    # Base paths
    data_dir = Path("data").resolve()
    st.write(f"Debug - Data directory: {data_dir}")
    
    # Verify data directory exists
    if not data_dir.exists():
        st.error(f"Data directory not found: {data_dir}")
        return
        
    # List files in data directory
    st.write("Debug - Files in data directory:")
    for file in data_dir.glob("*"):
        if file.is_file():
            st.write(f"- {file.name} ({file.stat().st_size} bytes)")
    
    for result in results:
        st.write(f"Source: {result.get('filename', 'unknown')}")
        
        if result.get('content_type') == 'image':
            try:
                # Get the filename
                filename = result.get('filename')
                if not filename:
                    st.error("No filename in result")
                    continue
                
                st.write(f"Debug - Processing image: {filename}")
                    
                # Try local file path first
                local_path = data_dir / filename
                st.write(f"Debug - Full local path: {local_path}")
                st.write(f"Debug - Path exists: {local_path.exists()}")
                st.write(f"Debug - Is file: {local_path.is_file() if local_path.exists() else 'N/A'}")
                
                if local_path.exists() and local_path.is_file():
                    st.write(f"Debug - File size: {local_path.stat().st_size} bytes")
                    try:
                        st.image(str(local_path), caption=result.get('description', ''))
                        st.write("Debug - Successfully displayed local image")
                    except Exception as e:
                        st.error(f"Error displaying local image: {str(e)}")
                else:
                    st.error(f"Local file not found or not accessible: {local_path}")
                    
                    # Try API URL as fallback
                    api_path = result.get('file_path', '')
                    if api_path:
                        api_url = "http://localhost:8000"
                        full_url = f"{api_url}{api_path}"
                        st.write(f"Debug - Trying API URL: {full_url}")
                        
                        try:
                            response = requests.head(full_url)
                            st.write(f"Debug - API response status: {response.status_code}")
                            st.write(f"Debug - API response headers: {dict(response.headers)}")
                            
                            if response.status_code == 200:
                                st.image(full_url, caption=result.get('description', ''))
                                st.write("Debug - Successfully displayed API image")
                            else:
                                st.error(f"API URL not accessible (status {response.status_code}): {full_url}")
                        except Exception as e:
                            st.error(f"Error accessing API URL: {str(e)}")
                    else:
                        st.error("No API path available")
                
            except Exception as e:
                st.error(f"Error displaying image: {str(e)}")
                st.write("Debug - Result data:", result)
        
        st.write(result.get('description', ''))
        st.write("---")

def generate_response(prompt, history):
    """Generate bot response and update conversation history."""
    try:
        with st.spinner("Thinking... 🤔"):
            response = requests.post(
                API_CONFIG["BARISTA_URL"],
                json={"query": prompt, "history": history},
                timeout=600
            )
            
            print("\n=== API Response ===")
            print(f"Status Code: {response.status_code}")
            print(f"Raw Response: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                print("\n=== Parsed Response Data ===")
                print(f"Full response_data: {response_data}")
                
                # Extract LLM response and display results from the correct structure
                llm_response = response_data.get("response", {}).get("llm_response")
                display_results = response_data.get("response", {}).get("display_results", [])
                
                if not llm_response:
                    st.error("No response received from the bot. Please try again.")
                    return
                
                print("\n=== Extracted Data ===")
                print(f"LLM Response: {llm_response}")
                print(f"Display Results: {display_results}")
                
                # Add assistant response to chat
                st.session_state.messages.append({"role": "assistant", "content": llm_response})
                st.markdown(llm_response)
                
                # Display the retrieved context items
                if display_results:
                    st.write("### Related Content:")
                    for item in display_results:
                        with st.expander(f"Source: {item.get('filename', 'Unknown')}"):
                            # If it's an image, display it
                            if item.get('type') == 'image':
                                if item.get('path'):
                                    st.image(item['path'], caption=item.get('description', 'No description available'))
                                else:
                                    st.write("Image path not available")
                            # If it's text, display the description
                            else:
                                st.write(item.get('description', 'No description available'))
                            
                            # Display keywords if available
                            if item.get('keywords'):
                                st.write("**Keywords:** ", item['keywords'])
                            
                            # Display similarity score if available
                            if item.get('similarity_score') is not None:
                                st.write(f"**Similarity Score:** {item['similarity_score']:.2f}")
                
                # Update conversation history
                st.session_state.conversation_history.append(
                    {"role": "user", "content": prompt}
                )
                st.session_state.conversation_history.append(
                    {"role": "assistant", "content": llm_response}
                )
                
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        st.error(error_msg)
        st.session_state.conversation_history.extend([
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": error_msg}
        ])

def display_chat_history(container):
    """Display chat history with improved formatting."""
    for message in st.session_state.conversation_history:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            container.write(f"You: {content}")
        else:
            container.write(f"Bot: {content}")
        container.write("---")

def clear_input():
    """Clear the input field after submission."""
    st.session_state["user_input"] = st.session_state["widget"]
    st.session_state["widget"] = ""

def display_chat_messages():
    """Display chat messages with icons."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "☕"):
            st.markdown(message["content"])

# --- Main Application ---
def main():
    # Initialization
    initialize_session_state()
    setup_page_config()
    apply_custom_css()

    # User/Admin Selection in sidebar
    with st.sidebar:
        st.title("Access Level")
        user_type = st.radio("Select User Type:", ["User", "Admin"], index=0, key="user_role_selection")
        if user_type == "Admin":
            if not st.session_state.is_admin:
                password = st.text_input("Enter Admin Password:", type="password", key="admin_password")
                if password:
                    if verify_password(password):
                        st.session_state.is_admin = True
                    else:
                        st.error("Incorrect password!")
            if st.session_state.is_admin:
                show_admin_features()
                if st.button("Clear Chat History"):
                    clear_chat()
                    st.rerun()

    # Header
    st.image('static/images/Coffee_shop.jpg', use_container_width=True)
    st.title(TITLE)
    st.write(SUBTITLE)

    # Chat Interface
    initialize_chat_history()
    chat_container = st.container()
    
    # Display chat messages
    display_chat_messages()

    # Chat input
    if prompt := st.chat_input("Ask me anything about coffee making! ☕"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Add assistant response
        with st.chat_message("assistant", avatar="☕"):
            try:
                # Get conversation history in the format expected by the API
                history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.conversation_history[-5:]  # Only use last 5 messages
                ]

                # Make API request
                response = requests.post(
                    API_CONFIG["BARISTA_URL"],
                    json={"query": prompt, "history": history},
                    timeout=600
                )
                
                print("\n=== API Response ===")
                print(f"Status Code: {response.status_code}")
                print(f"Raw Response: {response.text}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    print("\n=== Parsed Response Data ===")
                    print(f"Full response_data: {response_data}")
                    
                    # Extract LLM response and display results from the correct structure
                    llm_response = response_data.get("response", {}).get("llm_response")
                    display_results = response_data.get("response", {}).get("display_results", [])
                    
                    if not llm_response:
                        st.error("No response received from the bot. Please try again.")
                        return
                    
                    print("\n=== Extracted Data ===")
                    print(f"LLM Response: {llm_response}")
                    print(f"Display Results: {display_results}")
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({"role": "assistant", "content": llm_response})
                    st.markdown(llm_response)
                    
                    # Display the retrieved context items
                    if display_results:
                        st.write("### Related Content:")
                        for item in display_results:
                            with st.expander(f"Source: {item.get('filename', 'Unknown')}"):
                                # If it's an image, display it
                                if item.get('type') == 'image':
                                    if item.get('path'):
                                        st.image(item['path'], caption=item.get('description', 'No description available'))
                                    else:
                                        st.write("Image path not available")
                                # If it's text, display the description
                                else:
                                    st.write(item.get('description', 'No description available'))
                                
                                # Display keywords if available
                                if item.get('keywords'):
                                    st.write("**Keywords:** ", item['keywords'])
                                
                                # Display similarity score if available
                                if item.get('similarity_score') is not None:
                                    st.write(f"**Similarity Score:** {item['similarity_score']:.2f}")
                    
                    # Update conversation history
                    st.session_state.conversation_history.append(
                        {"role": "user", "content": prompt}
                    )
                    st.session_state.conversation_history.append(
                        {"role": "assistant", "content": llm_response}
                    )
                    
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.conversation_history.extend([
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": error_msg}
                ])

if __name__ == "__main__":
    main()
