import os
import uuid
import boto3
import pdfplumber
import io
import google.generativeai as genai
import snowflake.connector
from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv
from PIL import Image
from flask_cors import CORS

# --- 1. SETUP & CONFIGURATION ---
load_dotenv()

# Note: We aren't serving the frontend from here anymore,
# but Flask setup is the same.
app = Flask(__name__)
CORS(app) # Allow cross-origin requests (from your Next.js app)

# Configure Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    embedding_model = genai.GenerativeModel('models/embedding-001')
    vision_model = genai.GenerativeModel('models/gemini-2.5-flash')
except Exception as e:
    print(f"Error configuring Gemini: {e}")

# Configure DigitalOcean Spaces Client
try:
    session = boto3.session.Session()
    s3_client = session.client(
        's3',
        region_name=os.getenv("DO_SPACES_REGION"),
        endpoint_url=f"https://{os.getenv('DO_SPACES_REGION')}.digitaloceanspaces.com",
        aws_access_key_id=os.getenv("DO_SPACES_KEY"),
        aws_secret_access_key=os.getenv("DO_SPACES_SECRET")
    )
    BUCKET_NAME = os.getenv("DO_SPACES_BUCKET")
except Exception as e:
    print(f"Error configuring DigitalOcean Spaces: {e}")


# --- 2. HELPER FUNCTIONS ---

def get_snowflake_conn():
    """Establishes a connection to Snowflake."""
    try:
        return snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE")
        )
    except Exception as e:
        app.logger.error(f"Snowflake Connection Error: {e}")
        return None

def rag_search(case_id, query_text, top_k=5):
    """
    Performs RAG search on Snowflake using vector similarity.
    
    Args:
        case_id: The case ID to search within
        query_text: The text to search for (will be embedded)
        top_k: Number of top results to return
    
    Returns:
        List of dicts with text_chunk, source_url, and similarity score
    """
    try:
        # Step 1: Embed the query text using Snowflake
        query_vector = embed_text_snowflake(query_text)
        if query_vector is None:
            app.logger.error("Failed to embed query text for RAG search")
            return []
        
        # Step 2: Connect to Snowflake for the query
        conn = get_snowflake_conn()
        if not conn:
            app.logger.error("Failed to connect to Snowflake for RAG search")
            return []
        
        cursor = conn.cursor()
        
        try:
            # Step 3: Query using vector cosine similarity
            # Snowflake's VECTOR_COSINE_SIMILARITY returns a score between -1 and 1
            # Higher scores mean more similar
            query = """
                SELECT 
                    text_chunk,
                    source_url,
                    VECTOR_COSINE_SIMILARITY(vector_embedding, %s) AS similarity_score
                FROM case_data
                WHERE case_id = %s
                ORDER BY similarity_score DESC
                LIMIT %s
            """
            
            cursor.execute(query, (query_vector, case_id, top_k))
            results = cursor.fetchall()
            
            # Step 4: Format results
            formatted_results = []
            for row in results:
                formatted_results.append({
                    'text_chunk': row[0],
                    'source_url': row[1],
                    'similarity_score': float(row[2])
                })
            
            app.logger.info(f"RAG search found {len(formatted_results)} results for case {case_id}")
            return formatted_results
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        app.logger.error(f"RAG Search Error: {e}")
        return []

def embed_text_snowflake(text):
    """
    Generates an embedding for a text chunk using Snowflake's native EMBED_TEXT_768.
    This runs entirely in Snowflake - no external API needed!
    
    Args:
        text: Text to embed
    
    Returns:
        768-dimension vector embedding as a list
    """
    try:
        conn = get_snowflake_conn()
        if not conn:
            app.logger.error("Failed to connect to Snowflake for embedding")
            return None
            
        cursor = conn.cursor()
        try:
            # Use Snowflake's native embedding function
            # snowflake-arctic-embed-m is optimized for retrieval tasks
            cursor.execute(
                """
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', %s) AS embedding
                """,
                (text,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        app.logger.error(f"Snowflake Embedding Error: {e}")
        return None

def generate_case_number():
    """
    Generates a unique case number in format: MM-YYYY-NNNNN
    MM = Morgan & Morgan
    YYYY = Current year
    NNNNN = Sequential number (padded to 5 digits)
    
    Returns:
        str: Case number like "MM-2025-00001"
    """
    try:
        from datetime import datetime
        year = datetime.now().year
        
        conn = get_snowflake_conn()
        if not conn:
            # Fallback to UUID-based if DB connection fails
            return f"MM-{year}-{str(uuid.uuid4())[:5].upper()}"
        
        cursor = conn.cursor()
        try:
            # Get the highest case number for this year
            cursor.execute(
                """
                SELECT MAX(case_number) 
                FROM case_data 
                WHERE case_number LIKE %s
                """,
                (f"MM-{year}-%",)
            )
            result = cursor.fetchone()
            
            if result and result[0]:
                # Extract the number part and increment
                last_number = int(result[0].split('-')[-1])
                new_number = last_number + 1
            else:
                # First case of the year
                new_number = 1
            
            return f"MM-{year}-{new_number:05d}"
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        app.logger.error(f"Error generating case number: {e}")
        # Fallback to timestamp-based
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"MM-{timestamp}"

def get_image_description(image_bytes, context=""):
    """
    Gets a text description of an image using Gemini Vision.
    
    Args:
        image_bytes: Raw image data as bytes
        context: Optional context about where this image came from (e.g., "from page 3 of police report")
    
    Returns:
        Text description of the image for legal case analysis
    """
    try:
        # Enhanced prompt for legal case analysis
        base_prompt = """Analyze this image from a legal case perspective. Focus on:
- Physical evidence (injuries, property damage, accidents)
- Documents or text visible in the image
- People, vehicles, or objects that may be relevant
- Timestamps, locations, or other contextual details
- Any other legally significant information

Provide a detailed description that would help a lawyer understand the evidence."""
        
        if context:
            prompt = f"{context}\n\n{base_prompt}"
        else:
            prompt = base_prompt
        
        # Convert bytes to PIL Image for Gemini
        img = Image.open(io.BytesIO(image_bytes))
        
        # Use the Gemini API - pass PIL Image directly
        response = vision_model.generate_content([prompt, img])
        
        # Extract text from response candidates
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                return candidate.content.parts[0].text
        
        # Fallback if structure is different
        return str(response.text) if hasattr(response, 'text') else "Could not analyze image."
        
    except Exception as e:
        app.logger.error(f"Gemini Vision Error: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        return "Could not analyze image."

def store_in_snowflake(case_id, source_url, text_chunk, vector, case_metadata=None):
    """
    Inserts the processed data into our Snowflake table.
    Now uses a provided connection instead of creating a new one.
    
    Args:
        case_id: Unique case identifier
        source_url: URL or filename of the source
        text_chunk: Text content to store
        vector: Vector embedding (768 dimensions)
        case_metadata: Optional dict with case_name, case_number, client_name, client_phone, client_email
    """
    if vector is None:
        app.logger.warning(f"Skipping Snowflake insert for {source_url} due to missing vector.")
        return False

    conn = get_snowflake_conn()
    if not conn:
        app.logger.error("Could not connect to Snowflake. Data not stored.")
        return False

    cursor = conn.cursor()
    try:
        app.logger.info(f"Attempting to insert into Snowflake: case_id={case_id}, source={source_url[:50]}...")
        
        # Convert Python list to Snowflake array literal format: [1.1, 2.2, 3.3, ...]
        # Snowflake expects array format like [val1, val2, val3]
        vector_str = '[' + ','.join(str(v) for v in vector) + ']'
        
        # Build query with metadata if provided
        if case_metadata:
            cursor.execute(
                f"""
                INSERT INTO case_data (
                    case_id, source_url, text_chunk, vector_embedding,
                    case_name, case_number, client_name, client_phone, client_email
                )
                SELECT %s, %s, %s, {vector_str}::VECTOR(FLOAT, 768), %s, %s, %s, %s, %s
                """,
                (
                    case_id, source_url, text_chunk,
                    case_metadata.get('case_name'),
                    case_metadata.get('case_number'),
                    case_metadata.get('client_name'),
                    case_metadata.get('client_phone'),
                    case_metadata.get('client_email')
                )
            )
        else:
            cursor.execute(
                f"""
                INSERT INTO case_data (case_id, source_url, text_chunk, vector_embedding)
                SELECT %s, %s, %s, {vector_str}::VECTOR(FLOAT, 768)
                """,
                (case_id, source_url, text_chunk)
            )
        
        conn.commit()  # ⭐ IMPORTANT: Commit the transaction!
        app.logger.info(f"✅ Successfully stored chunk for {case_id} in Snowflake.")
        return True
    except Exception as e:
        app.logger.error(f"❌ Snowflake Insert Error: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


# --- 3. MAIN API ENDPOINT (THE "SMART INGESTION") ---

@app.route('/api/create-case', methods=['POST'])
def create_case():
    """
    Creates a new case with client metadata and optional files.
    Supports two-step workflow:
    - Step 1 & 2 together: Submit metadata + files in one request
    - Step 1 only: Submit metadata without files (can add files later)
    
    Form data:
        case_name: Name/title of the case (required)
        client_name: Client's full name (required)
        client_phone: Client's phone number (optional)
        client_email: Client's email address (optional)
        files: List of files to upload (optional)
    
    Returns:
        JSON with case_id, case_number, and success message
    """
    app.logger.info("Received request for /api/create-case")
    try:
        # Extract metadata from form
        case_name = request.form.get('case_name')
        client_name = request.form.get('client_name')
        client_phone = request.form.get('client_phone', '')
        client_email = request.form.get('client_email', '')
        files = request.files.getlist('files')

        # Validate required fields
        if not case_name or not client_name:
            return jsonify({
                "message": "Missing required fields: case_name and client_name are required"
            }), 400

        # Generate unique IDs
        case_id = f"case-{uuid.uuid4()}"
        case_number = generate_case_number()
        
        # Prepare metadata
        case_metadata = {
            'case_name': case_name,
            'case_number': case_number,
            'client_name': client_name,
            'client_phone': client_phone,
            'client_email': client_email
        }
        
        app.logger.info(f"Creating case: {case_number} - {case_name} for {client_name}")
        
        # If no files provided, create a placeholder entry to store metadata
        if not files or len(files) == 0:
            app.logger.info("No files provided. Creating case metadata entry only.")
            
            # Store a minimal placeholder entry with metadata
            placeholder_text = f"Case created: {case_name} for {client_name}. No files uploaded yet."
            vector = embed_text_snowflake(placeholder_text)
            
            if vector:
                success = store_in_snowflake(
                    case_id,
                    "metadata-only",
                    placeholder_text,
                    vector,
                    case_metadata
                )
                
                if success:
                    return jsonify({
                        "message": "Case created successfully! You can add files later.",
                        "case_id": case_id,
                        "case_number": case_number
                    }), 201
                else:
                    return jsonify({"message": "Failed to create case in database"}), 500
            else:
                return jsonify({"message": "Failed to process case metadata"}), 500

        # Process files if provided
        files_processed = 0
        for file in files:
            filename = file.filename
            
            # --- Step A: Read file ONCE into memory ---
            file.seek(0)
            file_bytes = file.read()

            # --- Step B: Upload to DigitalOcean Spaces ---
            file_key = f"{case_id}/{filename}"
            
            s3_client.upload_fileobj(
                io.BytesIO(file_bytes),
                BUCKET_NAME,
                file_key
            )
            source_url = f"https://{BUCKET_NAME}.{os.getenv('DO_SPACES_REGION')}.digitaloceanspaces.com/{file_key}"
            app.logger.info(f"Uploaded {filename} to {source_url}")

            # --- Step C: Process file based on type ---
            if filename.lower().endswith(('.pdf', '.txt', '.eml')):
                app.logger.info(f"Processing text file: {filename}")
                text = ""
                pdf_images = []
                
                if filename.lower().endswith('.pdf'):
                    # Use io.BytesIO to create a new stream for pdfplumber
                    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                        # Extract text from each page
                        text_pages = []
                        for page_num, page in enumerate(pdf.pages):
                            page_text = page.extract_text()
                            if page_text:
                                text_pages.append(page_text)
                            else:
                                # No text on this page - it might be an image-only page
                                # Convert page to image and analyze with Gemini
                                try:
                                    app.logger.info(f"Page {page_num + 1} has no text, converting to image...")
                                    img_obj = page.to_image(resolution=150)
                                    pil_image = img_obj.original
                                    
                                    # Convert PIL image to bytes for Gemini
                                    img_byte_arr = io.BytesIO()
                                    pil_image.save(img_byte_arr, format='PNG')
                                    img_bytes = img_byte_arr.getvalue()
                                    
                                    pdf_images.append({
                                        'bytes': img_bytes,
                                        'page': page_num + 1,
                                        'index': 1
                                    })
                                    app.logger.info(f"Converted page {page_num + 1} to image for analysis")
                                except Exception as img_error:
                                    app.logger.warning(f"Could not convert page {page_num + 1} to image: {img_error}")
                        
                        text = "\n".join(text_pages)
                else: 
                    # Just decode the bytes we already have
                    text = file_bytes.decode('utf-8', errors='ignore')

                app.logger.info(f"Extracted {len(text)} characters of text from {filename}")
                app.logger.info(f"Extracted {len(pdf_images)} images from {filename}")
                
                # Process text chunks
                chunks = [chunk.strip() for chunk in text.split('\n\n') if len(chunk.strip()) > 50]
                app.logger.info(f"Created {len(chunks)} text chunks from {filename}")
                
                if len(chunks) == 0 and len(text.strip()) > 0:
                    app.logger.warning(f"No chunks created for {filename}! Using entire text as one chunk.")
                    chunks = [text]

                for i, chunk in enumerate(chunks):
                    app.logger.info(f"Processing text chunk {i+1}/{len(chunks)}: {len(chunk)} chars")
                    vector = embed_text_snowflake(chunk)
                    if vector is None:
                        app.logger.error(f"❌ Failed to create embedding for text chunk {i+1}")
                        continue
                    app.logger.info(f"✅ Created embedding ({len(vector)} dimensions)")
                    
                    # Store with metadata (only first chunk gets full metadata to avoid duplication)
                    metadata_to_store = case_metadata if i == 0 and files_processed == 0 else None
                    success = store_in_snowflake(case_id, source_url, chunk, vector, metadata_to_store)
                    if success:
                        app.logger.info(f"✅ Stored text chunk {i+1}/{len(chunks)} for {filename}")
                        if i == 0:
                            files_processed += 1
                    else:
                        app.logger.error(f"❌ Failed to store text chunk {i+1}/{len(chunks)} for {filename}")
                
                # Process images extracted from PDF
                for img_data in pdf_images:
                    img_description = get_image_description(
                        img_data['bytes'],
                        context=f"This image is from page {img_data['page']} of a legal case document: {filename}"
                    )
                    app.logger.info(f"Got description for PDF image (page {img_data['page']}): {img_description[:100]}...")
                    
                    vector = embed_text_snowflake(img_description)
                    if vector is None:
                        app.logger.error(f"❌ Failed to create embedding for PDF image description")
                        continue
                    
                    app.logger.info(f"✅ Created embedding ({len(vector)} dimensions) for PDF image")
                    
                    # Store with metadata indicating it's from a PDF
                    image_source_url = f"{source_url}#page={img_data['page']}&image={img_data['index']}"
                    success = store_in_snowflake(case_id, image_source_url, img_description, vector)
                    if success:
                        app.logger.info(f"✅ Stored PDF image description (page {img_data['page']})")
                    else:
                        app.logger.error(f"❌ Failed to store PDF image description")

            elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                app.logger.info(f"Processing standalone image file: {filename}")
                
                # We already have the bytes! Pass them directly with context
                description = get_image_description(
                    file_bytes,
                    context=f"This is a standalone evidence photo: {filename}"
                )
                app.logger.info(f"Got image description: {description[:100]}...")
                
                vector = embed_text_snowflake(description)
                if vector is None:
                    app.logger.error(f"❌ Failed to create embedding for image description")
                else:
                    app.logger.info(f"✅ Created embedding ({len(vector)} dimensions)")
                    success = store_in_snowflake(case_id, source_url, description, vector)
                    if success:
                        app.logger.info(f"✅ Stored image description for {filename}")
                        files_processed += 1
                    else:
                        app.logger.error(f"❌ Failed to store image description for {filename}")

        return jsonify({
            "message": "Case created successfully!", 
            "case_id": case_id,
            "case_number": case_number,
            "files_processed": files_processed
        }), 201

    except Exception as e:
        app.logger.error(f"Error in /create-case: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({"message": f"An internal error occurred: {e}"}), 500

@app.route('/api/add-case-files', methods=['POST'])
def add_case_files():
    """
    Add files to an existing case and build/update the RAG knowledge base.
    
    Form data:
        case_id: The case ID to add files to (required)
        files: List of files to upload (required)
    
    Returns:
        JSON with success message and files_processed count
    """
    app.logger.info("Received request for /api/add-case-files")
    try:
        case_id = request.form.get('case_id')
        files = request.files.getlist('files')

        # Validate inputs
        if not case_id:
            return jsonify({"message": "Missing required field: case_id"}), 400
        
        if not files or len(files) == 0:
            return jsonify({"message": "No files provided"}), 400
        
        app.logger.info(f"Adding {len(files)} files to case {case_id}")
        
        files_processed = 0
        
        # Process each file (same logic as create-case)
        for file in files:
            filename = file.filename
            
            # Read file into memory
            file.seek(0)
            file_bytes = file.read()

            # Upload to DigitalOcean Spaces
            file_key = f"{case_id}/{filename}"
            s3_client.upload_fileobj(
                io.BytesIO(file_bytes),
                BUCKET_NAME,
                file_key
            )
            source_url = f"https://{BUCKET_NAME}.{os.getenv('DO_SPACES_REGION')}.digitaloceanspaces.com/{file_key}"
            app.logger.info(f"Uploaded {filename} to {source_url}")

            # Process file based on type
            if filename.lower().endswith(('.pdf', '.txt', '.eml')):
                app.logger.info(f"Processing text file: {filename}")
                text = ""
                pdf_images = []
                
                if filename.lower().endswith('.pdf'):
                    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                        text_pages = []
                        for page_num, page in enumerate(pdf.pages):
                            page_text = page.extract_text()
                            if page_text:
                                text_pages.append(page_text)
                            else:
                                try:
                                    app.logger.info(f"Page {page_num + 1} has no text, converting to image...")
                                    img_obj = page.to_image(resolution=150)
                                    pil_image = img_obj.original
                                    
                                    img_byte_arr = io.BytesIO()
                                    pil_image.save(img_byte_arr, format='PNG')
                                    img_bytes = img_byte_arr.getvalue()
                                    
                                    pdf_images.append({
                                        'bytes': img_bytes,
                                        'page': page_num + 1,
                                        'index': 1
                                    })
                                    app.logger.info(f"Converted page {page_num + 1} to image for analysis")
                                except Exception as img_error:
                                    app.logger.warning(f"Could not convert page {page_num + 1} to image: {img_error}")
                        
                        text = "\n".join(text_pages)
                else:
                    text = file_bytes.decode('utf-8', errors='ignore')

                app.logger.info(f"Extracted {len(text)} characters of text from {filename}")
                
                # Process text chunks
                chunks = [chunk.strip() for chunk in text.split('\n\n') if len(chunk.strip()) > 50]
                app.logger.info(f"Created {len(chunks)} text chunks from {filename}")
                
                if len(chunks) == 0 and len(text.strip()) > 0:
                    chunks = [text]

                for i, chunk in enumerate(chunks):
                    vector = embed_text_snowflake(chunk)
                    if vector is None:
                        app.logger.error(f"❌ Failed to create embedding for text chunk {i+1}")
                        continue
                    
                    # No metadata for additional files (metadata already exists from create-case)
                    success = store_in_snowflake(case_id, source_url, chunk, vector, None)
                    if success:
                        app.logger.info(f"✅ Stored text chunk {i+1}/{len(chunks)} for {filename}")
                        if i == 0:
                            files_processed += 1
                    else:
                        app.logger.error(f"❌ Failed to store text chunk {i+1}/{len(chunks)}")
                
                # Process PDF images
                for img_data in pdf_images:
                    img_description = get_image_description(
                        img_data['bytes'],
                        context=f"This image is from page {img_data['page']} of a legal case document: {filename}"
                    )
                    
                    vector = embed_text_snowflake(img_description)
                    if vector is None:
                        continue
                    
                    image_source_url = f"{source_url}#page={img_data['page']}&image={img_data['index']}"
                    success = store_in_snowflake(case_id, image_source_url, img_description, vector, None)
                    if success:
                        app.logger.info(f"✅ Stored PDF image description (page {img_data['page']})")

            elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                app.logger.info(f"Processing standalone image file: {filename}")
                
                description = get_image_description(
                    file_bytes,
                    context=f"This is a standalone evidence photo: {filename}"
                )
                
                vector = embed_text_snowflake(description)
                if vector:
                    success = store_in_snowflake(case_id, source_url, description, vector, None)
                    if success:
                        app.logger.info(f"✅ Stored image description for {filename}")
                        files_processed += 1

        return jsonify({
            "message": f"Successfully added {files_processed} files to case {case_id}",
            "case_id": case_id,
            "files_processed": files_processed
        }), 200

    except Exception as e:
        app.logger.error(f"Error in /add-case-files: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({"message": f"An internal error occurred: {e}"}), 500

# --- 4. TEST & UTILITY ROUTES ---

@app.route('/')
def root():
    """A simple test route to show the backend is running."""
    return "Backend server is running!"

@app.route('/api/test-rag', methods=['POST'])
def test_rag():
    """
    Test endpoint to verify RAG search is working.
    
    Expected JSON body:
    {
        "case_id": "case-xxx-xxx-xxx",
        "query": "What happened in the accident?"
    }
    """
    try:
        data = request.get_json()
        case_id = data.get('case_id')
        query = data.get('query')
        top_k = data.get('top_k', 5)
        
        if not case_id or not query:
            return jsonify({"error": "Missing case_id or query"}), 400
        
        # Perform RAG search
        results = rag_search(case_id, query, top_k)
        
        return jsonify({
            "case_id": case_id,
            "query": query,
            "results_count": len(results),
            "results": results
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error in /test-rag: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/view-case-data/<case_id>', methods=['GET'])
def view_case_data(case_id):
    """
    View all data stored in Snowflake for a specific case.
    Useful for debugging and verification.
    """
    try:
        conn = get_snowflake_conn()
        if not conn:
            return jsonify({"error": "Failed to connect to Snowflake"}), 500
        
        cursor = conn.cursor()
        
        try:
            # Get all data for this case
            cursor.execute(
                """
                SELECT 
                    case_id,
                    source_url,
                    text_chunk
                FROM case_data
                WHERE case_id = %s
                ORDER BY source_url
                """,
                (case_id,)
            )
            
            results = cursor.fetchall()
            
            formatted_results = []
            for row in results:
                formatted_results.append({
                    'case_id': row[0],
                    'source_url': row[1],
                    'text_chunk': row[2][:200] + '...' if len(row[2]) > 200 else row[2],  # Truncate for display
                    'text_length': len(row[2]),
                    'vector_size': 768  # We know it's always 768
                })
            
            return jsonify({
                "case_id": case_id,
                "total_chunks": len(formatted_results),
                "data": formatted_results
            }), 200
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        app.logger.error(f"Error in /view-case-data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/list-cases', methods=['GET'])
def list_cases():
    """
    List all cases with metadata (case_number, case_name, client info).
    Returns cases sorted by case_number descending (newest first).
    """
    try:
        conn = get_snowflake_conn()
        if not conn:
            return jsonify({"error": "Failed to connect to Snowflake"}), 500
        
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT 
                    case_id,
                    MAX(case_number) as case_number,
                    MAX(case_name) as case_name,
                    MAX(client_name) as client_name,
                    MAX(client_phone) as client_phone,
                    MAX(client_email) as client_email,
                    COUNT(*) as chunk_count,
                    MIN(source_url) as first_file
                FROM case_data
                GROUP BY case_id
                ORDER BY MAX(case_number) DESC
                """
            )
            
            results = cursor.fetchall()
            
            cases = []
            for row in results:
                cases.append({
                    'case_id': row[0],
                    'case_number': row[1],
                    'case_name': row[2],
                    'client_name': row[3],
                    'client_phone': row[4],
                    'client_email': row[5],
                    'chunk_count': row[6],
                    'first_file': row[7]
                })
            
            return jsonify({
                "total_cases": len(cases),
                "cases": cases
            }), 200
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        app.logger.error(f"Error in /list-cases: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/snowflake', methods=['GET'])
def debug_snowflake():
    """
    Debug endpoint to test Snowflake connection and configuration.
    """
    try:
        # Check environment variables
        env_status = {
            "SNOWFLAKE_USER": "✅ Set" if os.getenv("SNOWFLAKE_USER") else "❌ Missing",
            "SNOWFLAKE_PASSWORD": "✅ Set" if os.getenv("SNOWFLAKE_PASSWORD") else "❌ Missing",
            "SNOWFLAKE_ACCOUNT": "✅ Set" if os.getenv("SNOWFLAKE_ACCOUNT") else "❌ Missing",
            "SNOWFLAKE_WAREHOUSE": os.getenv("SNOWFLAKE_WAREHOUSE", "❌ Missing"),
            "SNOWFLAKE_DATABASE": os.getenv("SNOWFLAKE_DATABASE", "❌ Missing"),
            "SNOWFLAKE_SCHEMA": os.getenv("SNOWFLAKE_SCHEMA", "❌ Missing"),
            "SNOWFLAKE_ROLE": os.getenv("SNOWFLAKE_ROLE", "❌ Missing"),
        }
        
        # Try to connect
        conn = get_snowflake_conn()
        if not conn:
            return jsonify({
                "status": "error",
                "message": "Failed to connect to Snowflake",
                "env_variables": env_status
            }), 500
        
        cursor = conn.cursor()
        
        try:
            # Test query
            cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
            result = cursor.fetchone()
            
            # Count rows in case_data
            cursor.execute("SELECT COUNT(*) FROM case_data")
            count = cursor.fetchone()[0]
            
            return jsonify({
                "status": "success",
                "message": "✅ Snowflake connection working!",
                "env_variables": env_status,
                "connection_info": {
                    "user": result[0],
                    "role": result[1],
                    "database": result[2],
                    "schema": result[3]
                },
                "case_data_rows": count
            }), 200
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "env_variables": env_status if 'env_status' in locals() else {}
        }), 500

@app.route('/api/test-embedding', methods=['GET'])
def test_embedding():
    """Test if Snowflake embedding function is working and check permissions."""
    try:
        test_text = "The plaintiff suffered injuries in a car accident."
        
        app.logger.info(f"Testing embedding for text: {test_text}")
        
        # Test the embedding function
        embedding = embed_text_snowflake(test_text)
        
        if embedding is None:
            return jsonify({
                "status": "error",
                "message": "❌ Embedding function returned None",
                "help": "Check Flask logs for detailed error. This might be a permissions issue.",
                "next_steps": [
                    "Check Flask terminal for error messages",
                    "Verify you've granted CORTEX_EMBED_USER role in Snowflake",
                    "Run: USE ROLE ACCOUNTADMIN; GRANT DATABASE ROLE SNOWFLAKE.CORTEX_EMBED_USER TO ROLE TENDER_APP_ROLE;"
                ]
            }), 500
        
        # Check if vectors exist in database
        conn = get_snowflake_conn()
        cursor = conn.cursor()
        
        try:
            # Count total rows
            cursor.execute("SELECT COUNT(*) FROM case_data")
            total_rows = cursor.fetchone()[0]
            
            # Count rows with vectors
            cursor.execute("SELECT COUNT(*) FROM case_data WHERE vector_embedding IS NOT NULL")
            rows_with_vectors = cursor.fetchone()[0]
            
            # Get a sample if exists
            sample_data = None
            if total_rows > 0:
                cursor.execute("SELECT case_id, source_url, LENGTH(text_chunk), vector_embedding IS NOT NULL FROM case_data LIMIT 1")
                row = cursor.fetchone()
                sample_data = {
                    "case_id": row[0],
                    "source_url": row[1],
                    "text_length": row[2],
                    "has_vector": row[3]
                }
            
            return jsonify({
                "status": "success",
                "message": "✅ Embedding function is working!",
                "test_embedding": {
                    "text": test_text,
                    "vector_dimensions": len(embedding),
                    "first_5_values": embedding[:5],
                    "last_5_values": embedding[-5:]
                },
                "database_status": {
                    "total_rows": total_rows,
                    "rows_with_vectors": rows_with_vectors,
                    "rows_without_vectors": total_rows - rows_with_vectors,
                    "sample": sample_data
                },
                "diagnosis": {
                    "embedding_works": True,
                    "data_exists": total_rows > 0,
                    "vectors_stored": rows_with_vectors > 0,
                    "issue": None if rows_with_vectors == total_rows else "Some rows don't have vectors"
                }
            }), 200
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        error_msg = str(e)
        
        # Check for permission errors
        is_permission_error = any(keyword in error_msg.lower() for keyword in 
            ['permission', 'authorized', 'privilege', 'access denied'])
        
        return jsonify({
            "status": "error",
            "message": f"❌ Error: {error_msg}",
            "is_permission_error": is_permission_error,
            "help": "This is likely a permissions issue. You need to grant CORTEX_EMBED_USER role." if is_permission_error else "Check the error message above.",
            "next_steps": [
                "Log into Snowflake web UI",
                "Run these commands:",
                "  USE ROLE ACCOUNTADMIN;",
                "  GRANT DATABASE ROLE SNOWFLAKE.CORTEX_EMBED_USER TO ROLE TENDER_APP_ROLE;",
                "Then try this endpoint again"
            ] if is_permission_error else ["Check Flask logs for detailed error"]
        }), 500


# --- 5. AI AGENT ORCHESTRATION ---

@app.route('/api/agent/process', methods=['POST'])
def process_with_agent():
    """
    Process a task using the AI orchestrator
    
    Request: {"case_id": "123", "query": "Draft email to client about settlement"}
    Response: {"status": "success", "result": {...}}
    """
    try:
        from agents.orchistrator_agent.agent import orchestrator
        
        data = request.json
        case_id = data.get('case_id')
        query = data.get('query')
        
        if not case_id or not query:
            return jsonify({"status": "error", "message": "Missing case_id or query"}), 400
        
        # Get case context from RAG if available
        case_context = ""
        try:
            # Simple context retrieval - you can enhance this
            case_context = f"Case {case_id} context"
        except:
            pass
        
        # Run orchestrator
        result = orchestrator(case_id, query, case_context)
        
        return jsonify({"status": "success", "result": result}), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in process_with_agent: {error_details}")
        return jsonify({"status": "error", "message": str(e)}), 500


# --- 6. RUN THE SERVER ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)