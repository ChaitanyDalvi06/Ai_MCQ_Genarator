"""
AI MCQ Generator Backend
FastAPI server that extracts text from PDFs and generates MCQs using local Ollama
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import re
import requests
import io

# PDF processing
try:
    import pdfplumber
    PDF_LIBRARY = "pdfplumber"
except ImportError:
    import PyPDF2
    PDF_LIBRARY = "PyPDF2"

app = FastAPI(title="AI MCQ Generator")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# CONFIGURATION - Modify these settings as needed
# ============================================================================

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"  # Change to your model: llama2, mistral, gemma, etc.
OLLAMA_TEMPERATURE = 0.3  # Lower = more focused, Higher = more creative (0.0 - 1.0)
OLLAMA_TIMEOUT = 120  # Request timeout in seconds

# Text Processing
MAX_CHUNK_SIZE = 2500  # Approximate tokens per chunk (1 token ≈ 4 chars)
MAX_QUESTIONS_PER_CHUNK = 5  # Maximum questions to generate per chunk

# ============================================================================
# PROMPT TEMPLATE
# ============================================================================

OLLAMA_PROMPT = """You are an expert educator creating multiple-choice questions.

Given the following text, generate {n_questions} multiple-choice questions at {difficulty} difficulty level.

TEXT:
{text}

REQUIREMENTS:
- Generate exactly {n_questions} questions
- Difficulty: {difficulty}
- Each question must have exactly 4 options (A, B, C, D)
- One option must be correct
- Include a brief explanation for the correct answer

OUTPUT FORMAT (CRITICAL - MUST BE VALID JSON):
Return ONLY a JSON array with this exact structure, no other text:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": 0,
    "explanation": "Brief explanation of why this is correct"
  }}
]

The "answer" field must be the zero-based index (0-3) of the correct option.
Return ONLY the JSON array, no markdown, no code blocks, no additional text."""

# ============================================================================
# MODELS
# ============================================================================

class MCQRequest(BaseModel):
    text: str
    n_questions: int = 5
    difficulty: str = "medium"

class MCQ(BaseModel):
    question: str
    options: List[str]
    answer: int
    explanation: Optional[str] = None

class MCQResponse(BaseModel):
    mcqs: List[MCQ]

class PDFResponse(BaseModel):
    text: str
    pages: int

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF using available library"""
    try:
        if PDF_LIBRARY == "pdfplumber":
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text.strip()
        else:  # PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF extraction failed: {str(e)}")

def chunk_text(text: str, max_size: int = MAX_CHUNK_SIZE) -> List[str]:
    """Split text into manageable chunks for processing"""
    # Simple chunking by sentences/paragraphs
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        word_size = len(word) + 1  # +1 for space
        if current_size + word_size > max_size * 4:  # Rough token estimate
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_size = 0
        current_chunk.append(word)
        current_size += word_size
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks if chunks else [text]

def call_ollama_generate(prompt: str) -> str:
    """Call Ollama API to generate text"""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": OLLAMA_TEMPERATURE,
                }
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Ollama API error: {response.status_code} - {response.text}"
            )
        
        result = response.json()
        return result.get("response", "")
    
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Ollama. Make sure Ollama is running (ollama serve)"
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Ollama request timed out. Try with shorter text or fewer questions."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

def extract_json_from_response(response: str) -> List[dict]:
    """Extract and parse JSON from Ollama response"""
    # Try direct parse first
    try:
        data = json.loads(response)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON array from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON array in text
    json_match = re.search(r'\[.*\]', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    return []

def validate_mcq(mcq_dict: dict) -> Optional[MCQ]:
    """Validate and convert dict to MCQ model"""
    try:
        # Check required fields
        if not all(key in mcq_dict for key in ["question", "options", "answer"]):
            return None
        
        # Validate structure
        if not isinstance(mcq_dict["options"], list) or len(mcq_dict["options"]) != 4:
            return None
        
        if not isinstance(mcq_dict["answer"], int) or not (0 <= mcq_dict["answer"] <= 3):
            return None
        
        return MCQ(
            question=mcq_dict["question"],
            options=mcq_dict["options"],
            answer=mcq_dict["answer"],
            explanation=mcq_dict.get("explanation", "")
        )
    except Exception:
        return None

def generate_mcqs_from_text(text: str, n_questions: int, difficulty: str) -> List[MCQ]:
    """Generate MCQs from text using Ollama"""
    chunks = chunk_text(text)
    all_mcqs = []
    
    # Calculate questions per chunk
    questions_per_chunk = min(
        MAX_QUESTIONS_PER_CHUNK,
        max(1, n_questions // len(chunks))
    )
    
    for chunk_idx, chunk in enumerate(chunks):
        # Adjust for last chunk to reach target
        remaining = n_questions - len(all_mcqs)
        if remaining <= 0:
            break
        
        chunk_questions = min(remaining, questions_per_chunk)
        
        # Generate prompt
        prompt = OLLAMA_PROMPT.format(
            n_questions=chunk_questions,
            difficulty=difficulty,
            text=chunk[:3000]  # Limit chunk size further for prompt
        )
        
        # Call Ollama
        response = call_ollama_generate(prompt)
        
        # Parse response
        mcq_dicts = extract_json_from_response(response)
        
        # Validate and add MCQs
        for mcq_dict in mcq_dicts:
            mcq = validate_mcq(mcq_dict)
            if mcq and len(all_mcqs) < n_questions:
                all_mcqs.append(mcq)
        
        # If we didn't get valid MCQs, try one more time with explicit JSON instruction
        if len(all_mcqs) == 0 and chunk_idx == 0:
            retry_prompt = prompt + "\n\nIMPORTANT: Return ONLY valid JSON array, nothing else."
            response = call_ollama_generate(retry_prompt)
            mcq_dicts = extract_json_from_response(response)
            for mcq_dict in mcq_dicts:
                mcq = validate_mcq(mcq_dict)
                if mcq and len(all_mcqs) < n_questions:
                    all_mcqs.append(mcq)
    
    return all_mcqs

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "ollama_url": OLLAMA_BASE_URL,
        "model": OLLAMA_MODEL,
        "pdf_library": PDF_LIBRARY
    }

@app.post("/upload_pdf", response_model=PDFResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and extract text
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Read file content
    content = await file.read()
    
    # Extract text
    text = extract_text_from_pdf(content)
    
    if not text:
        raise HTTPException(status_code=400, detail="No text could be extracted from PDF")
    
    # Estimate page count (rough)
    pages = len(content) // 2048  # Very rough estimate
    
    return PDFResponse(text=text, pages=max(1, pages))

@app.post("/generate_mcq", response_model=MCQResponse)
async def generate_mcq(request: MCQRequest):
    """
    Generate multiple-choice questions from text
    """
    # Validate input
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if request.n_questions < 1 or request.n_questions > 20:
        raise HTTPException(status_code=400, detail="Number of questions must be between 1 and 20")
    
    if request.difficulty not in ["easy", "medium", "hard"]:
        raise HTTPException(status_code=400, detail="Difficulty must be easy, medium, or hard")
    
    # Generate MCQs
    mcqs = generate_mcqs_from_text(request.text, request.n_questions, request.difficulty)
    
    if not mcqs:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate valid MCQs. Check Ollama model or try different text."
        )
    
    return MCQResponse(mcqs=mcqs)

if __name__ == "__main__":
    import uvicorn
    # Run with: python main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)

