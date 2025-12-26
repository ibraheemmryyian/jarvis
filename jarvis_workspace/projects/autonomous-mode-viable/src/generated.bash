mkdir admin-dashboard
cd admin-dashboard
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn python-multipart pydantic