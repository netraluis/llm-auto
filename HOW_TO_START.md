# How to Start the Project

## 1. Create Virtual Environment

### Option A: Using Python venv
```bash
# Create virtual environment
python -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

### Option B: Using conda
```bash
# Create conda environment
conda create -n llm-auto python=3.11
conda activate llm-auto
```

## 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## 3. Configure Environment Variables
```bash
# Copy the example file
cp env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Fill in your credentials in `.env`:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

## 4. Run the Server
```bash
python main.py
```

The server will start at `http://localhost:8000`

## 5. Test the API
- Open your browser and go to `http://localhost:8000/docs`
- You'll see the automatic Swagger documentation
- Test the `/chat` endpoint with your messages

## 6. Deactivate Virtual Environment (when done)
```bash
deactivate
```

## Troubleshooting

**If you get import errors:**
- Make sure the virtual environment is activated
- Check that all dependencies are installed: `pip list`

**If you get configuration errors:**
- Verify your `.env` file has all required variables
- Check that your Supabase and OpenRouter credentials are correct

**If the server doesn't start:**
- Check if port 8000 is available
- Try a different port: `uvicorn main:app --port 8001`
