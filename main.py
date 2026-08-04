import os
import json
import sqlite3
from datetime import datetime
from fastapi import FastAPI, UploadFile, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fpdf import FPDF
import uvicorn

# ---------------------------
# Setup
# ---------------------------
app = FastAPI()
UPLOAD_DIR = "uploads"
DB_FILE = "evidence.db"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static uploads folder to serve files directly
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Set up templates
templates = Jinja2Templates(directory="templates")

# ---------------------------
# Database setup & Migration
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT,
                    description TEXT,
                    filename TEXT,
                    staff_name TEXT,
                    uploaded_at TEXT,
                    category TEXT,
                    severity TEXT,
                    status TEXT
                )''')
    
    # Run migration to add new columns if they do not exist
    c.execute("PRAGMA table_info(evidence)")
    columns = [col[1] for col in c.fetchall()]
    if "category" not in columns:
        c.execute("ALTER TABLE evidence ADD COLUMN category TEXT DEFAULT 'General'")
    if "severity" not in columns:
        c.execute("ALTER TABLE evidence ADD COLUMN severity TEXT DEFAULT 'Medium'")
    if "status" not in columns:
        c.execute("ALTER TABLE evidence ADD COLUMN status TEXT DEFAULT 'Under Investigation'")
    
    conn.commit()
    conn.close()

init_db()

# ---------------------------
# Save uploaded evidence
# ---------------------------
@app.post("/upload")
async def upload(
    file: UploadFile,
    case_id: str = Form(...),
    description: str = Form(...),
    staff_name: str = Form(...),
    category: str = Form("General"),
    severity: str = Form("Medium"),
    status: str = Form("Under Investigation")
):
    # Ensure filename is valid (not None)
    filename = file.filename or f"unnamed_{datetime.now().timestamp()}"
    # Sanitizing filename slightly
    filename = os.path.basename(filename)
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Write file content
    with open(filepath, "wb") as f:
        f.write(await file.read())

    # Insert metadata into SQLite
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO evidence (case_id, description, filename, staff_name, uploaded_at, category, severity, status) VALUES (?,?,?,?,?,?,?,?)",
        (case_id, description, filename, staff_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), category, severity, status)
    )
    conn.commit()
    conn.close()
    
    # Redirect to home page after success
    return HTMLResponse("<script>window.location.href = '/';</script>")

# ---------------------------
# Delete evidence
# ---------------------------
@app.delete("/evidence/{evidence_id}")
async def delete_evidence(evidence_id: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT filename FROM evidence WHERE id = ?", (evidence_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    filename = row[0]
    c.execute("DELETE FROM evidence WHERE id = ?", (evidence_id,))
    conn.commit()
    conn.close()

    # Attempt to delete file from disk
    if filename:
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error removing file {filepath}: {e}")
                
    return {"status": "ok"}

# ---------------------------
# Generate PDF
# ---------------------------
@app.get("/report")
async def report():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT case_id, description, filename, staff_name, uploaded_at, category, severity, status FROM evidence ORDER BY uploaded_at DESC")
    rows = c.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(10, 25, 47)  # Primary dark theme color
    pdf.cell(0, 15, "Digital Evidence Custody Report", ln=True, align="C")
    
    # Subtitle
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, f"Report Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.ln(10)
    
    # Body
    for idx, row in enumerate(rows, 1):
        case_id, desc, filename, staff, uploaded_at, category, severity, status = row
        
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(0, 102, 204)  # Accent blue
        pdf.cell(0, 8, f"Item #{idx}: Case ID - {case_id}", ln=True)
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        
        metadata = (
            f"Category: {category}  |  Severity: {severity}  |  Status: {status}\n"
            f"File Name: {filename}\n"
            f"Custodian: {staff}  |  Uploaded: {uploaded_at}\n"
            f"Description: {desc}"
        )
        pdf.multi_cell(0, 6, metadata)
        
        # Divider line
        pdf.set_draw_color(220, 220, 220)
        pdf.line(10, pdf.get_y() + 4, 200, pdf.get_y() + 4)
        pdf.ln(8)

    report_file = "Evidence_Report.pdf"
    pdf.output(report_file)
    return FileResponse(report_file, media_type="application/pdf", filename=report_file)

# ---------------------------
# HTML Interface (Rendered via Jinja2)
# ---------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Fetch all evidence
    c.execute("SELECT id, case_id, description, filename, staff_name, uploaded_at, category, severity, status FROM evidence ORDER BY uploaded_at DESC")
    evidence_rows = c.fetchall()
    
    # Parse items to dicts
    evidence_list = []
    for row in evidence_rows:
        evidence_list.append({
            "id": row[0],
            "case_id": row[1],
            "description": row[2],
            "filename": row[3],
            "staff_name": row[4],
            "uploaded_at": row[5],
            "category": row[6],
            "severity": row[7],
            "status": row[8]
        })
        
    # Calculate stats
    c.execute("SELECT COUNT(*) FROM evidence")
    total_evidence = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM evidence WHERE severity IN ('Critical', 'High')")
    critical_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM evidence WHERE status = 'Secured'")
    secured_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT case_id) FROM evidence")
    unique_cases = c.fetchone()[0]
    
    conn.close()
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "evidence": evidence_list,
            "stats": {
                "total_evidence": total_evidence,
                "critical_count": critical_count,
                "secured_count": secured_count,
                "unique_cases": unique_cases
            }
        }
    )

# ---------------------------
# Run server
# ---------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
