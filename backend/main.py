from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import json
import os
from pathlib import Path
from datetime import datetime
from models import get_db, Report, Satellite, Language

app = FastAPI(title="Team Persia Reports API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportRequest(BaseModel):
    satellite: str
    language: str

class ReportResponse(BaseModel):
    satellite: str
    language: str
    status: str
    file_count: int
    timestamp: str
    content: str

class SatelliteInfo(BaseModel):
    name: str
    languages: List[str]
    enabled: bool

@app.get("/")
async def root():
    return {"message": "Team Persia Reports API", "version": "1.0.0"}

@app.get("/satellites", response_model=List[SatelliteInfo])
async def get_satellites():
    """Get list of available satellites and their languages."""
    try:
        config_path = Path(__file__).parent.parent / "config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        satellites = []
        for satellite_name, languages in config["satellites"].items():
            enabled_languages = [
                lang for lang, settings in languages.items()
                if settings.get("enabled", False)
            ]
            satellites.append(SatelliteInfo(
                name=satellite_name,
                languages=enabled_languages,
                enabled=len(enabled_languages) > 0
            ))

        return satellites
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading satellites: {str(e)}")

@app.post("/reports/generate", response_model=ReportResponse)
async def generate_report(request: ReportRequest, db: Session = Depends(get_db)):
    """Generate a report for specific satellite and language."""
    try:
        # Import the report generator
        import sys
        sys.path.append(str(Path(__file__).parent.parent))

        from generate_report import ReportGenerator

        generator = ReportGenerator()
        content = generator.generate_report(request.satellite, request.language)

        # Get analysis info
        analysis = generator.analyze_codebase(request.satellite, request.language)

        # Save to database
        db_report = Report(
            satellite=request.satellite,
            language=request.language,
            status=analysis["status"],
            file_count=analysis["file_count"],
            content=content
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)

        return ReportResponse(
            satellite=request.satellite,
            language=request.language,
            status=analysis["status"],
            file_count=analysis["file_count"],
            timestamp=datetime.now().isoformat(),
            content=content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.get("/reports/{satellite}/{language}")
async def get_report(satellite: str, language: str, db: Session = Depends(get_db)):
    """Get existing report for satellite and language."""
    try:
        # Try to get from database first
        db_report = db.query(Report).filter(
            Report.satellite == satellite,
            Report.language == language
        ).order_by(Report.created_at.desc()).first()

        if db_report:
            return {
                "satellite": satellite,
                "language": language,
                "content": db_report.content,
                "status": db_report.status,
                "file_count": db_report.file_count,
                "timestamp": db_report.created_at.isoformat(),
                "exists": True,
                "source": "database"
            }

        # Fallback to file system
        report_path = Path(__file__).parent.parent / satellite / language / "Report.md"
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")

        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "satellite": satellite,
            "language": language,
            "content": content,
            "exists": True,
            "source": "filesystem"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading report: {str(e)}")

@app.get("/reports/history/{satellite}/{language}")
async def get_report_history(satellite: str, language: str, db: Session = Depends(get_db)):
    """Get report history for satellite and language."""
    try:
        reports = db.query(Report).filter(
            Report.satellite == satellite,
            Report.language == language
        ).order_by(Report.created_at.desc()).all()

        return [
            {
                "id": report.id,
                "satellite": report.satellite,
                "language": report.language,
                "status": report.status,
                "file_count": report.file_count,
                "timestamp": report.created_at.isoformat(),
                "updated_at": report.updated_at.isoformat()
            }
            for report in reports
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching report history: {str(e)}")

@app.post("/reports/generate-all")
async def generate_all_reports():
    """Generate reports for all enabled satellites and languages."""
    try:
        import sys
        sys.path.append(str(Path(__file__).parent.parent))

        from generate_report import ReportGenerator

        generator = ReportGenerator()
        generator.run_analysis()

        return {"message": "All reports generated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating reports: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)