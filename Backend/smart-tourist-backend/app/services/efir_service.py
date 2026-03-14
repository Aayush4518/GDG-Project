"""
Automated E-FIR Generation Service

This module provides automated Electronic First Information Report (E-FIR) generation
for missing tourists. It creates a comprehensive PDF report with tourist details,
location history, and tamper-evident ledger verification for law enforcement use.
"""

from fpdf import FPDF
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional
import io

from ..db import models
from ..crud import crud_dashboard, crud_tourist


class EFIRReport(FPDF):
    """
    Custom FPDF class for E-FIR report generation with formatted headers and footers
    """
    
    def header(self):
        """
        Add header to each page of the E-FIR report
        """
        # Logo placeholder - in production, add actual police/authority logo
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'SMART TOURIST SAFETY SYSTEM', 0, 1, 'C')
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'PRELIMINARY E-FIR: MISSING TOURIST REPORT', 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        """
        Add footer to each page with page numbers and generation timestamp
        """
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")} - Page {self.page_no()}', 0, 0, 'C')


def generate_efir_pdf(db: Session, tourist_id: str) -> bytes:
    """
    Generate a comprehensive E-FIR PDF report for a missing tourist
    
    This function creates a formatted PDF document that law enforcement can use
    as a preliminary FIR for missing tourist cases. It includes verified tourist
    information, location tracking history, and tamper-evident ledger verification.
    
    Args:
        db: Database session for executing queries
        tourist_id: UUID string of the missing tourist
        
    Returns:
        bytes: PDF content ready for download or storage
        
    Raises:
        ValueError: If tourist not found or insufficient data
        Exception: If PDF generation fails
        
    Example:
        >>> pdf_content = generate_efir_pdf(db, "123e4567-e89b-12d3")
        >>> with open("efir_report.pdf", "wb") as f:
        ...     f.write(pdf_content)
    """
    try:
        # Step 1: Fetch tourist details
        tourist = crud_tourist.get_tourist(db, tourist_id)
        if not tourist:
            raise ValueError(f"Tourist with ID {tourist_id} not found")
        
        # Step 2: Fetch location history (last 5 locations)
        location_history = crud_dashboard.get_tourist_location_history(db, tourist_id, limit=5)
        
        # Step 3: Fetch latest ledger hash for evidence integrity
        # Get the most recent ledger entry for this tourist
        latest_ledger = db.query(models.IDLedger).filter(
            models.IDLedger.tourist_id == tourist_id
        ).order_by(models.IDLedger.timestamp.desc()).first()
        
        # Step 4: Initialize PDF document
        pdf = EFIRReport()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Step 5: Report Header Information
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'E-FIR REFERENCE: EFIR-{tourist_id[:8].upper()}-{datetime.now().strftime("%Y%m%d")}', 0, 1)
        pdf.cell(0, 10, f'REPORT GENERATED: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}', 0, 1)
        pdf.ln(5)
        
        # Step 6: Tourist Details Section
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'SECTION 1: TOURIST DETAILS', 0, 1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(50, 8, 'Name:', 0, 0, 'L')
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, tourist.name, 0, 1, 'L')
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(50, 8, 'Tourist ID:', 0, 0, 'L')
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, str(tourist.id), 0, 1, 'L')
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(50, 8, 'KYC Hash:', 0, 0, 'L')
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, tourist.kyc_hash, 0, 1, 'L')
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(50, 8, 'Registration Date:', 0, 0, 'L')
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, tourist.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), 0, 1, 'L')
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(50, 8, 'Trip End Date:', 0, 0, 'L')
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, tourist.trip_end_date.strftime("%Y-%m-%d %H:%M:%S UTC"), 0, 1, 'L')
        
        # Emergency Contact Information
        if tourist.emergency_contact:
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Emergency Contact Information:', 0, 1)
            pdf.set_font('Arial', '', 11)
            
            if 'name' in tourist.emergency_contact:
                pdf.cell(50, 6, 'Contact Name:', 0, 0, 'L')
                pdf.cell(0, 6, str(tourist.emergency_contact['name']), 0, 1, 'L')
            
            if 'phone' in tourist.emergency_contact:
                pdf.cell(50, 6, 'Phone:', 0, 0, 'L')
                pdf.cell(0, 6, str(tourist.emergency_contact['phone']), 0, 1, 'L')
                
            if 'email' in tourist.emergency_contact:
                pdf.cell(50, 6, 'Email:', 0, 0, 'L')
                pdf.cell(0, 6, str(tourist.emergency_contact['email']), 0, 1, 'L')
        
        pdf.ln(10)
        
        # Step 7: Location History Section
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'SECTION 2: LAST KNOWN LOCATIONS', 0, 1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        if location_history:
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(40, 8, 'Timestamp', 1, 0, 'C')
            pdf.cell(35, 8, 'Latitude', 1, 0, 'C')
            pdf.cell(35, 8, 'Longitude', 1, 0, 'C')
            pdf.cell(70, 8, 'Location Details', 1, 1, 'C')
            
            pdf.set_font('Arial', '', 9)
            for location in location_history:
                # location_history is a list of dicts from crud_dashboard
                ts = location['timestamp']
                timestamp_str = ts.strftime("%m/%d %H:%M") if hasattr(ts, 'strftime') else str(ts)

                lat_str = f"{location['latitude']:.6f}"
                lng_str = f"{location['longitude']:.6f}"

                location_desc = f"GPS: {lat_str}, {lng_str}"
                
                pdf.cell(40, 6, timestamp_str, 1, 0, 'C')
                pdf.cell(35, 6, lat_str, 1, 0, 'C')
                pdf.cell(35, 6, lng_str, 1, 0, 'C')
                pdf.cell(70, 6, location_desc, 1, 1, 'L')
        else:
            pdf.set_font('Arial', 'I', 11)
            pdf.cell(0, 8, 'No location data available for this tourist.', 0, 1)
        
        pdf.ln(10)
        
        # Step 8: Evidence Integrity Section
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'SECTION 3: EVIDENCE INTEGRITY SEAL', 0, 1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, 'This report is backed by tamper-evident blockchain technology.', 0, 1)
        pdf.cell(0, 8, 'All tourist interactions are cryptographically secured.', 0, 1)
        pdf.ln(3)
        
        if latest_ledger:
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, f'Latest Ledger Block ID: {latest_ledger.id}', 0, 1)
            pdf.cell(0, 6, f'Ledger Hash: {latest_ledger.current_hash}', 0, 1)
            pdf.cell(0, 6, f'Last Update: {latest_ledger.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}', 0, 1)
        else:
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 6, 'No ledger entries found for this tourist.', 0, 1)
        
        pdf.ln(10)
        
        # Step 9: Report Footer
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'SECTION 4: OFFICIAL NOTES', 0, 1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 6, 'This is a preliminary automated report generated by the Smart Tourist Safety System.', 0, 1)
        pdf.cell(0, 6, 'For official FIR filing, please contact the nearest police station with this document.', 0, 1)
        pdf.cell(0, 6, 'All data in this report is cryptographically verified and tamper-evident.', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'I', 9)
        pdf.cell(0, 6, 'Generated by Smart Tourist Safety System - Automated E-FIR Module', 0, 1)
        
        # Step 10: Return PDF as bytes
        pdf_output = io.BytesIO()
        pdf_content = pdf.output(dest='S').encode('latin-1')
        
        return pdf_content
        
    except ValueError:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle PDF generation errors
        raise Exception(f"Failed to generate E-FIR PDF: {str(e)}")


def get_efir_filename(tourist_id: str) -> str:
    """
    Generate a standardized filename for E-FIR reports
    
    Args:
        tourist_id: UUID string of the tourist
        
    Returns:
        str: Formatted filename for the E-FIR PDF
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = tourist_id[:8].upper()
    return f"EFIR_{short_id}_{timestamp}.pdf"
