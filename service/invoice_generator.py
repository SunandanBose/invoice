"""
Invoice PDF Generator
Generates GST-compliant tax invoices in PDF format

This module provides functionality to generate professional PDF invoices
with automatic tax calculations, text wrapping, and Indian numbering system.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from typing import List, Dict, Optional, Union
import io
from config import COMPANY_CONFIG, DEFAULT_CUSTOMER_GSTIN, DEFAULT_CGST_RATE, DEFAULT_SGST_RATE


# ============================================================================
# CONSTANTS - Page Layout and Dimensions
# ============================================================================
PAGE_MARGIN = 30  # Page margins in points
SECTION_SPACING = 8  # Spacing between sections in points
MAX_ITEMS_ROWS = 12  # Maximum item rows to fit on one page (plus 1 header)

# Column widths for items table (total should equal page width minus margins)
ITEMS_TABLE_WIDTHS = [0.45, 2.85, 0.75, 0.45, 0.65, 1.15]  # in inches

# Column widths for other tables
INVOICE_INFO_WIDTHS = [3.15, 3.15]  # in inches
CUSTOMER_DETAILS_WIDTHS = [3.15, 3.15]  # in inches
FOOTER_WIDTHS = [3.2, 3.1]  # in inches (bank details, tax summary)
TAX_TABLE_WIDTHS = [1.5, 1.4]  # in inches (label, amount)
WORDS_TABLE_WIDTHS = [1.3, 5.0]  # in inches (label, text)

# Font sizes
FONT_SIZE_TITLE = 14
FONT_SIZE_COMPANY = 18
FONT_SIZE_NORMAL = 10
FONT_SIZE_TABLE = 9
FONT_SIZE_TABLE_SMALL = 8

# Padding values
PADDING_STANDARD = 8
PADDING_REDUCED = 6
PADDING_SMALL = 4
PADDING_MINIMAL = 2


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def number_to_words(num: int) -> str:
    """
    Convert a number to words using Indian numbering system.
    
    Args:
        num: Integer number to convert
        
    Returns:
        String representation in words (e.g., "Twenty Nine Thousand Nine Hundred Seventy Two")
        
    Examples:
        >>> number_to_words(29972)
        'Twenty Nine Thousand Nine Hundred Seventy Two'
        >>> number_to_words(1000000)
        'Ten Lakh'
    """
    # Number word mappings
    ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 
             'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    
    def convert_below_thousand(n: int) -> str:
        """Convert numbers below 1000 to words"""
        if n == 0:
            return ''
        elif n < 10:
            return ones[n]
        elif n < 20:
            return teens[n - 10]
        elif n < 100:
            return tens[n // 10] + (' ' + ones[n % 10] if n % 10 != 0 else '')
        else:
            hundreds = ones[n // 100] + ' Hundred'
            remainder = convert_below_thousand(n % 100)
            return hundreds + (' ' + remainder if remainder else '')
    
    # Handle zero
    if num == 0:
        return 'Zero'
    
    # Indian numbering system: crore (10,000,000), lakh (100,000), thousand (1,000)
    crore = num // 10000000
    num %= 10000000
    lakh = num // 100000
    num %= 100000
    thousand = num // 1000
    num %= 1000
    
    # Build result
    result = []
    if crore:
        result.append(convert_below_thousand(crore) + ' Crore')
    if lakh:
        result.append(convert_below_thousand(lakh) + ' Lakh')
    if thousand:
        result.append(convert_below_thousand(thousand) + ' Thousand')
    if num:
        result.append(convert_below_thousand(num))
    
    return ' '.join(result)


def safe_float(value: Union[str, int, float], default: float = 0.0) -> float:
    """
    Safely convert a value to float, handling empty strings and None.
    
    Args:
        value: Value to convert (can be string, int, float, or None)
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    if value is None or value == '':
        return default
    try:
        if isinstance(value, str):
            return float(value.replace(',', ''))
        return float(value)
    except (ValueError, AttributeError):
        return default


def format_amount(amount: float) -> str:
    """
    Format amount for display - show decimals only if present.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted string (e.g., "2286" or "2286.09")
    """
    if amount % 1 != 0:  # Has decimal places
        return f"{amount:.2f}"
    return str(int(amount))


# ============================================================================
# MAIN INVOICE GENERATOR CLASS
# ============================================================================

class InvoiceGenerator:
    """
    Generate GST-compliant tax invoices in PDF format.
    
    This class handles the complete invoice generation process including:
    - PDF layout and styling
    - Tax calculations (CGST, SGST, IGST)
    - Text wrapping for long descriptions
    - Number to words conversion
    - Automatic round-off calculations
    
    Attributes:
        page_width: Page width from A4 size
        page_height: Page height from A4 size
        styles: ReportLab paragraph styles
        company_config: Company configuration dictionary
    """
    
    def __init__(self, company_config: Optional[Dict] = None):
        """
        Initialize invoice generator with optional company configuration.
        
        Args:
            company_config: Optional company configuration dictionary.
                          If None, uses configuration from config.py
        """
        self.page_width, self.page_height = A4
        self.styles = getSampleStyleSheet()
        self.company_config = company_config or COMPANY_CONFIG
        self._setup_custom_styles()
    
    # ========================================================================
    # INITIALIZATION AND SETUP METHODS
    # ========================================================================
    
    def _setup_custom_styles(self):
        """
        Setup custom paragraph styles for the invoice.
        
        Creates the following styles:
        - CompanyName: Large bold text for company name
        - InvoiceTitle: Medium bold text for "Tax Invoice"
        - CompanyDetails: Normal text for company address/contact
        - TableCell: Standard table cell text
        - TableCellSmall: Smaller table cell text for items table
        """
        # Company name style (18pt, bold, centered)
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=FONT_SIZE_COMPANY,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=4,
            spaceBefore=0,
            fontName='Helvetica-Bold',
            leading=20
        ))
        
        # Invoice title style (14pt, bold, centered)
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=FONT_SIZE_TITLE,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=SECTION_SPACING,
            spaceBefore=0,
            fontName='Helvetica-Bold',
            leading=16
        ))
        
        # Company details style (10pt, centered)
        self.styles.add(ParagraphStyle(
            name='CompanyDetails',
            parent=self.styles['Normal'],
            fontSize=FONT_SIZE_NORMAL,
            alignment=TA_CENTER,
            spaceAfter=PADDING_MINIMAL,
            leading=12
        ))
        
        # Standard table cell style (9pt, left-aligned)
        self.styles.add(ParagraphStyle(
            name='TableCell',
            parent=self.styles['Normal'],
            fontSize=FONT_SIZE_TABLE,
            alignment=TA_LEFT,
            leading=11,
            leftIndent=0,
            rightIndent=0
        ))
        
        # Small table cell style for items table (8pt, left-aligned)
        self.styles.add(ParagraphStyle(
            name='TableCellSmall',
            parent=self.styles['Normal'],
            fontSize=FONT_SIZE_TABLE_SMALL,
            alignment=TA_LEFT,
            leading=10,
            leftIndent=0,
            rightIndent=0
        ))
    
    # ========================================================================
    # PUBLIC API METHODS
    # ========================================================================
    
    def generate_invoice(self, invoice_data: Dict, output_path: Optional[str] = None) -> Optional[bytes]:
        """
        Generate a GST-compliant invoice PDF from simplified input data.
        
        This is the main entry point for invoice generation. It handles:
        1. Data transformation and validation
        2. PDF document creation
        3. Building all invoice sections
        4. Saving to file or returning bytes
        
        Args:
            invoice_data: Dictionary with simplified invoice data:
                {
                    "invoice_no": "134",                    # Invoice number
                    "invoice_date": "05-Dec-2025",          # Invoice date
                    "to": "Customer Name, Address",         # Customer info
                    "job_description": "Event details",     # Job description
                    "items": [                              # List of items
                        {
                            "name": "Item description",
                            "hsn": "HSN code",
                            "qty": 1,
                            "rate": "1000",
                            "amount": "1000"
                        }
                    ],
                    "taxable_amount": "25400",              # Amount before tax
                    "cgst": "2286",                         # CGST amount (can be decimal)
                    "sgst": "2286",                         # SGST amount (can be decimal)
                    "total": "29972"                        # Final total
                }
            output_path: Optional file path to save PDF. If None, returns bytes
            
        Returns:
            PDF as bytes if output_path is None, otherwise None
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Transform simplified input to internal format
        transformed_data = self._transform_input(invoice_data)
        
        # Create PDF buffer
        if output_path:
            pdf_buffer = output_path
        else:
            pdf_buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        
        # Build content
        story = []
        
        # Header Section
        story.extend(self._build_header(transformed_data))
        story.append(Spacer(1, 8))
        
        # Invoice Info Section
        story.extend(self._build_invoice_info(transformed_data))
        story.append(Spacer(1, 8))
        
        # Customer Details Section
        story.extend(self._build_customer_details(transformed_data))
        story.append(Spacer(1, 8))
        
        # Items Table
        story.extend(self._build_items_table(transformed_data))
        story.append(Spacer(1, 8))
        
        # Footer Section (Bank Details + Tax Summary)
        story.extend(self._build_footer(transformed_data))
        story.append(Spacer(1, 8))
        
        # Amount in Words
        story.extend(self._build_amount_in_words(transformed_data))
        
        # Signature
        story.extend(self._build_signature(transformed_data))
        
        # Build PDF
        doc.build(story)
        
        # Return bytes if no output path
        if not output_path:
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()
            return pdf_bytes
        
        return None
    
    # ========================================================================
    # DATA TRANSFORMATION METHODS
    # ========================================================================
    
    def _transform_input(self, invoice_data: Dict) -> Dict:
        """
        Transform simplified input format to internal format.
        
        Converts user-friendly input format to internal structure with:
        - Parsed customer details
        - Calculated tax rates
        - Automatic round-off calculation
        - Validated amounts
        
        Args:
            invoice_data: Simplified input format from user
            
        Returns:
            Internal format dictionary with all required fields
        """
        # Parse customer details from 'to' field
        customer_name, customer_address = self._parse_customer_info(
            invoice_data.get('to', '')
        )
        
        # Transform items to internal format
        transformed_items = self._transform_items(invoice_data.get('items', []))
        
        # Extract and validate amounts
        taxable = safe_float(invoice_data.get('taxable_amount', '0'))
        cgst_amount = safe_float(invoice_data.get('cgst', '0'))
        sgst_amount = safe_float(invoice_data.get('sgst', '0'))
        total_input = safe_float(invoice_data.get('total', '0'))
        
        # Calculate tax rates from amounts
        cgst_rate = self._calculate_tax_rate(cgst_amount, taxable, DEFAULT_CGST_RATE)
        sgst_rate = self._calculate_tax_rate(sgst_amount, taxable, DEFAULT_SGST_RATE)
        
        # Calculate round-off (always positive)
        actual_total = taxable + cgst_amount + sgst_amount
        rounded_total = round(actual_total)
        round_off = abs(rounded_total - actual_total)
        
        # Use provided total or calculated rounded total
        final_total = total_input if total_input > 0 else rounded_total
        
        return {
            'company': self.company_config,
            'invoice_number': invoice_data.get('invoice_no', ''),
            'invoice_date': invoice_data.get('invoice_date', ''),
            'customer': {
                'name': customer_name,
                'address': customer_address,
                'gstin': invoice_data.get('customer_gstin', DEFAULT_CUSTOMER_GSTIN)
            },
            'job_description': invoice_data.get('job_description', ''),
            'event_name': invoice_data.get('event_name', ''),
            'items': transformed_items,
            'tax_summary': {
                'taxable_amount': taxable,
                'cgst_rate': cgst_rate,
                'cgst_amount': cgst_amount,
                'sgst_rate': sgst_rate,
                'sgst_amount': sgst_amount,
                'igst_rate': invoice_data.get('igst_rate', ''),
                'round_off': round(round_off, 2) if abs(round_off) > 0.01 else '',
                'invoice_total': final_total
            }
        }
    
    def _parse_customer_info(self, to_field: str) -> tuple:
        """
        Parse customer name and address from 'to' field.
        
        Args:
            to_field: Combined customer info string
            
        Returns:
            Tuple of (customer_name, customer_address)
        """
        to_parts = to_field.split(',', 1)
        customer_name = to_parts[0].strip() if to_parts else ''
        customer_address = to_parts[1].strip() if len(to_parts) > 1 else to_field
        return customer_name, customer_address
    
    def _transform_items(self, items: List[Dict]) -> List[Dict]:
        """
        Transform items from input format to internal format.
        
        Args:
            items: List of item dictionaries from input
            
        Returns:
            List of transformed item dictionaries
        """
        transformed = []
        for item in items:
            transformed.append({
                'description': item.get('name', ''),
                'hsn_code': item.get('hsn', ''),
                'quantity': str(item.get('qty', '')),
                'rate': str(item.get('rate', '')),
                'amount': safe_float(item.get('amount', 0))
            })
        return transformed
    
    def _calculate_tax_rate(self, tax_amount: float, taxable: float, default_rate: float) -> float:
        """
        Calculate tax rate from tax amount and taxable amount.
        
        Args:
            tax_amount: Tax amount
            taxable: Taxable amount
            default_rate: Default rate if calculation fails
            
        Returns:
            Calculated tax rate as percentage
        """
        if taxable > 0 and tax_amount > 0:
            return round((tax_amount / taxable * 100), 2)
        return default_rate
    
    # ========================================================================
    # PDF BUILDING METHODS - Each method builds a section of the invoice
    # ========================================================================
    
    def _build_header(self, data: Dict) -> List:
        """Build company header section"""
        elements = []
        
        company = data['company']
        
        # Title
        title = Paragraph("Tax Invoice", self.styles['InvoiceTitle'])
        elements.append(title)
        elements.append(Spacer(1, 4))
        
        # Company Name
        company_name = Paragraph(
            f"<b>{company['name']}</b>",
            self.styles['CompanyName']
        )
        elements.append(company_name)
        elements.append(Spacer(1, 2))
        
        # Company Address
        address = Paragraph(
            company['address'],
            self.styles['CompanyDetails']
        )
        elements.append(address)
        
        # Mobile Numbers
        mobile = Paragraph(
            f"Mobile No.: {company['mobile']}",
            self.styles['CompanyDetails']
        )
        elements.append(mobile)
        elements.append(Spacer(1, 6))
        
        # GST and State Info Table
        gst_table_data = [
            [company['state'], f"GSTIN NO: {company['gstin']}", f"State Code: {company['state_code']}"]
        ]
        
        gst_table = Table(gst_table_data, colWidths=[1.8*inch, 2.7*inch, 1.8*inch])
        gst_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(gst_table)
        
        return elements
    
    def _build_invoice_info(self, data: Dict) -> List:
        """Build invoice number and date section"""
        elements = []
        
        invoice_info_data = [
            [f"Invoice No.: {data['invoice_number']}", f"Invoice Date: {data['invoice_date']}"]
        ]
        
        invoice_table = Table(invoice_info_data, colWidths=[3.15*inch, 3.15*inch])
        invoice_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(invoice_table)
        
        return elements
    
    def _build_customer_details(self, data: Dict) -> List:
        """Build customer details section"""
        elements = []
        
        customer = data['customer']
        job_desc = data.get('job_description', '')
        event_name = data.get('event_name', '')
        
        # Format recipient details without internal lines
        recipient_text = f"<b>Details of Recipient:</b>\nName: {customer['name']}\nAddress: {customer['address']}\nGST No: {customer['gstin']}"
        recipient_para = Paragraph(recipient_text.replace('\n', '<br/>'), self.styles['TableCell'])
        
        # Format job description without internal lines
        job_text = f"<b>Job Description:</b> {job_desc}"
        if event_name:
            job_text += f"<br/>{event_name}"
        job_para = Paragraph(job_text, self.styles['TableCell'])
        
        customer_data = [[recipient_para, job_para]]
        
        customer_table = Table(customer_data, colWidths=[3.15*inch, 3.15*inch])
        customer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(customer_table)
        
        return elements
    
    def _build_items_table(self, data: Dict) -> List:
        """Build items/services table with text wrapping"""
        elements = []
        
        # Table headers
        table_data = [
            [
                Paragraph('<b>Sl. No.</b>', self.styles['TableCellSmall']),
                Paragraph('<b>Description of Goods / Services</b>', self.styles['TableCellSmall']),
                Paragraph('<b>HSN Code</b>', self.styles['TableCellSmall']),
                Paragraph('<b>Qty</b>', self.styles['TableCellSmall']),
                Paragraph('<b>Rate</b>', self.styles['TableCellSmall']),
                Paragraph('<b>Amount (Rs.)</b>', self.styles['TableCellSmall'])
            ]
        ]
        
        # Add items with text wrapping
        items = data.get('items', [])
        for idx, item in enumerate(items, 1):
            # Wrap description text
            description = item.get('description', '')
            desc_para = Paragraph(description, self.styles['TableCellSmall'])
            
            table_data.append([
                Paragraph(str(idx), self.styles['TableCellSmall']),
                desc_para,
                Paragraph(item.get('hsn_code', ''), self.styles['TableCellSmall']),
                Paragraph(str(item.get('quantity', '')), self.styles['TableCellSmall']),
                Paragraph(str(item.get('rate', '')), self.styles['TableCellSmall']),
                Paragraph(str(item.get('amount', '')), self.styles['TableCellSmall'])
            ])
        
        # Add empty rows to fill table (prevents page overflow)
        current_rows = len(table_data)
        max_rows = MAX_ITEMS_ROWS + 1  # +1 for header row
        
        for i in range(current_rows, max_rows):
            if i == max_rows - 1:  # Last row for "Extra Item Total Amount"
                table_data.append([
                    Paragraph(str(i), self.styles['TableCellSmall']),
                    Paragraph('Extra Item Total Amount', self.styles['TableCellSmall']),
                    Paragraph('', self.styles['TableCellSmall']),
                    Paragraph('', self.styles['TableCellSmall']),
                    Paragraph('', self.styles['TableCellSmall']),
                    Paragraph('', self.styles['TableCellSmall'])
                ])
            else:
                table_data.append([
                    Paragraph(str(i), self.styles['TableCellSmall']),
                    Paragraph('', self.styles['TableCellSmall']),
                    Paragraph('', self.styles['TableCellSmall']),
                    Paragraph('', self.styles['TableCellSmall']),
                    Paragraph('', self.styles['TableCellSmall']),
                    Paragraph('', self.styles['TableCellSmall'])
                ])
        
        # Create table with proper column widths
        items_table = Table(
            table_data,
            colWidths=[w*inch for w in ITEMS_TABLE_WIDTHS],
            repeatRows=1  # Repeat header on new pages if needed
        )
        
        # Style the table
        style_commands = [
            # Header row
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            
            # All cells
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Sl. No.
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Description
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # HSN
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Qty
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Rate
            ('ALIGN', (5, 1), (5, -1), 'RIGHT'),   # Amount
            
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        
        items_table.setStyle(TableStyle(style_commands))
        elements.append(items_table)
        
        return elements
    
    def _build_footer(self, data: Dict) -> List:
        """Build footer with bank details and tax summary"""
        elements = []
        
        bank = data['company']['bank_details']
        tax = data['tax_summary']
        
        # Format bank details without internal lines
        bank_text = f"Bank Details: {data['company']['name']}<br/>IFSC Code: {bank['ifsc']}<br/>Account No.: {bank['account_number']}<br/>Bank: {bank['bank_name']}"
        bank_para = Paragraph(bank_text, self.styles['TableCell'])
        
        # Calculate CGST and SGST amounts from rates and taxable amount
        taxable = float(tax['taxable_amount'])
        
        # Handle empty strings for rates
        cgst_rate = float(tax.get('cgst_rate', 0)) if tax.get('cgst_rate') else 0
        sgst_rate = float(tax.get('sgst_rate', 0)) if tax.get('sgst_rate') else 0
        igst_rate_val = tax.get('igst_rate', '')
        igst_rate = float(igst_rate_val) if igst_rate_val and igst_rate_val != '' else 0
        
        # Get actual amounts from tax summary (which come from input)
        cgst_amt = float(tax.get('cgst_amount', 0)) if tax.get('cgst_amount') else 0
        sgst_amt = float(tax.get('sgst_amount', 0)) if tax.get('sgst_amount') else 0
        igst_amt = float(tax.get('igst_amount', 0)) if tax.get('igst_amount') else 0
        
        # Format amounts - show decimals if present, otherwise show as integer
        cgst_amount = f"{cgst_amt:.2f}" if cgst_amt and cgst_amt % 1 != 0 else (str(int(cgst_amt)) if cgst_amt else "")
        sgst_amount = f"{sgst_amt:.2f}" if sgst_amt and sgst_amt % 1 != 0 else (str(int(sgst_amt)) if sgst_amt else "")
        igst_amount = f"{igst_amt:.2f}" if igst_amt and igst_amt % 1 != 0 else (str(int(igst_amt)) if igst_amt else "")
        
        # Format display with rate in parentheses and amount
        cgst_display = f"{cgst_rate:.0f}%" if cgst_rate else ""
        sgst_display = f"{sgst_rate:.0f}%" if sgst_rate else ""
        igst_display = f"{igst_rate:.0f}%" if igst_rate else ""
        
        # Format round off - always show as positive (addition)
        round_off_val = tax.get('round_off', '')
        if round_off_val and round_off_val != '':
            round_off_display = f"{abs(float(round_off_val)):.2f}"
        else:
            round_off_display = ''
        
        # Tax summary as separate rows
        tax_data = [
            ['TAXABLE AMOUNT', str(int(taxable))],
            [f'CGST ({cgst_display})' if cgst_display else 'CGST', cgst_amount if cgst_amount else ''],
            [f'SGST ({sgst_display})' if sgst_display else 'SGST', sgst_amount if sgst_amount else ''],
            [f'IGST ({igst_display})' if igst_display else 'IGST', igst_amount if igst_amount else ''],
            ['Round off', round_off_display],
            ['Invoice Total', str(int(tax['invoice_total']))]
        ]
        
        tax_table = Table(tax_data, colWidths=[1.5*inch, 1.4*inch])
        tax_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        # Combine bank details and tax summary
        footer_data = [[bank_para, tax_table]]
        
        footer_table = Table(footer_data, colWidths=[3.2*inch, 3.1*inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(footer_table)
        
        return elements
    
    def _build_amount_in_words(self, data: Dict) -> List:
        """Build amount in words section"""
        elements = []
        
        total = data['tax_summary']['invoice_total']
        words = number_to_words(int(total))
        
        words_data = [
            ['In Words', f"{words} only."]
        ]
        
        words_table = Table(words_data, colWidths=[1.3*inch, 5*inch])
        words_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('SPAN', (1, 0), (1, 0)),
        ]))
        elements.append(words_table)
        
        return elements
    
    def _build_signature(self, data: Dict) -> List:
        """Build signature section"""
        elements = []
        
        # Just add empty space, no signature text
        elements.append(Spacer(1, 40))
        
        return elements



# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

if __name__ == "__main__":
    # Sample invoice data - SIMPLIFIED FORMAT
    sample_data = {
  "invoice_no": "134",
  "invoice_date": "05-Dec-2025",
  "to": "The Director, CSIR - National Metallurgical Laboratory",
  "job_description": "Platinum Jubilee",
  "items": [
    {
      "name": "Stage Programme PA System with Stage light & codeless microphone (3nos)",
      "hsn": "997329",
      "qty": 1,
      "rate": "25400",
      "amount": "25400"
    },
    {
      "name": "Stage Programme PA System with Stage light & codeless microphone (3nos)",
      "hsn": "997329",
      "qty": 1,
      "rate": "25400",
      "amount": "25400"
    },
    {
      "name": "Stage Programme PA System with Stage light & codeless microphone (3nos)",
      "hsn": "997329",
      "qty": 1,
      "rate": "25400",
      "amount": "25400"
    },
    {
      "name": "Stage Programme PA System with Stage light & codeless microphone (3nos)",
      "hsn": "997329",
      "qty": 1,
      "rate": "25400",
      "amount": "25400"
    },
    {
      "name": "Stage Programme PA System with Stage light & codeless microphone (3nos)",
      "hsn": "997329",
      "qty": 1,
      "rate": "25400",
      "amount": "25400"
    },
    {
      "name": "Stage Programme PA System with Stage light & codeless microphone (3nos)",
      "hsn": "997329",
      "qty": 1,
      "rate": "25400",
      "amount": "25400"
    },
    {
      "name": "Stage Programme PA System with Stage light & codeless microphone (3nos)",
      "hsn": "997329",
      "qty": 1,
      "rate": "25400",
      "amount": "25400"
    },
    {
      "name": "Stage Programme PA System with Stage light & codeless microphone (3nos)",
      "hsn": "997329",
      "qty": 1,
      "rate": "25400",
      "amount": "25400"
    },
    {
      "name": "Stage Programme PA System with Stage light & codeless microphone (3nos)",
      "hsn": "997329",
      "qty": 1,
      "rate": "25400",
      "amount": "25400"
    }
  ],
  "taxable_amount": "25401",
  "cgst": "2286.09",
  "sgst": "2286.09",
  "total": "29973.18"
}


    
    # Generate invoice
    generator = InvoiceGenerator()
    pdf_bytes = generator.generate_invoice(sample_data, output_path="test_invoice.pdf")
    print("Invoice generated successfully: test_invoice.pdf")
    print("\nUsing company config from config.py")
    print(f"Company: {COMPANY_CONFIG['name']}")

