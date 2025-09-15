@echo off
echo Installing required packages...
pip install --user streamlit python-dotenv openai pymupdf

echo.
echo Starting the SOP Agent...
echo Open your browser to: http://localhost:8501
echo.

python -m streamlit run streamlit_app.py

pause