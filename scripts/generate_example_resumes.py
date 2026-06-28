#!/usr/bin/env python3
"""Generate fictional example resume PDFs for portfolio mocks."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "app" / "static" / "examples" / "resumes"


class ResumePDF(FPDF):
    def header(self) -> None:
        return

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "Career Systems - sample delivery", align="C")


def _section(pdf: ResumePDF, title: str) -> None:
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(180, 80, 60)
    pdf.cell(0, 6, title.upper())
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)


def build_alex() -> Path:
    pdf = ResumePDF()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(20, 20, 22)
    pdf.cell(0, 10, "Alex Rivera")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(90, 90, 95)
    pdf.multi_cell(
        0,
        5,
        "Data Analyst Intern | alexrivera.me | alex.rivera@example.com | linkedin.com/in/alexrivera",
    )
    _section(pdf, "Summary")
    pdf.multi_cell(
        0,
        5,
        "Information Systems student seeking a data analyst internship. Ships Python/SQL projects with "
        "measurable outcomes - portfolio, resume, and LinkedIn aligned for technical recruiting.",
    )
    _section(pdf, "Projects")
    pdf.multi_cell(
        0,
        5,
        "- Campus Dining Insights: ETL on 40k+ meal-swipe records; peak-hour analysis adopted for pilot scheduling.\n"
        "- Healthcare Wait-Time Dashboard: SQL + Tableau capstone; identified drivers for 18% of ER wait delays.",
    )
    _section(pdf, "Skills")
    pdf.multi_cell(0, 5, "Python, SQL, Pandas, Tableau, Excel, statistics, technical writing.")
    _section(pdf, "Education")
    pdf.multi_cell(0, 5, "B.S. Information Systems (expected 2027) - GPA 3.7")
    path = OUT_DIR / "alex-rivera.pdf"
    pdf.output(str(path))
    return path


def build_jordan() -> Path:
    pdf = ResumePDF()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(20, 20, 22)
    pdf.cell(0, 10, "Jordan Kim")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(90, 90, 95)
    pdf.multi_cell(
        0,
        5,
        "Junior Software Engineer | jordankim.me | jordan.kim@example.com",
    )
    _section(pdf, "Summary")
    pdf.multi_cell(
        0,
        5,
        "Operations background + full-stack bootcamp. Targeting junior SWE with deployed projects, tests, "
        "and a pivot narrative consistent across GitHub, resume, and LinkedIn.",
    )
    _section(pdf, "Technical Projects")
    pdf.multi_cell(
        0,
        5,
        "- ShiftSync API: FastAPI + React shift-swap tool piloted at a local retailer.\n"
        "- Inventory Anomaly Detector: Python ML pipeline on shrink data from prior ops role.",
    )
    _section(pdf, "Experience")
    pdf.multi_cell(
        0,
        5,
        "Floor Lead, national retail (4 years) - inventory audits, training, Excel reporting adopted district-wide.",
    )
    _section(pdf, "Education")
    pdf.multi_cell(0, 5, "Full-stack engineering certificate - 2025")
    path = OUT_DIR / "jordan-kim.pdf"
    pdf.output(str(path))
    return path


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = [build_alex(), build_jordan()]
    for path in paths:
        print(f"Wrote {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
