"""
Test text wrapping with long descriptions
"""

from invoice_generator import InvoiceGenerator

# Test with very long description
invoice_data = {
    "invoice_no": "TEST-WRAP-001",
    "invoice_date": "09-Dec-2025",
    "to": "The Director, CSIR - National Metallurgical Laboratory, Jamshedpur - 831017",
    "job_description": "Annual Event 2025",
    "items": [
        {
            "name": "Stage Programme PA System with Stage light & codeless microphone (3nos) including wireless speakers and complete audio setup with backup equipment",
            "hsn": "997329",
            "qty": 1,
            "rate": "25400",
            "amount": "25400"
        },
        {
            "name": "LED Display Screen 10x8 feet with high resolution for presentations",
            "hsn": "997329",
            "qty": 2,
            "rate": "5000",
            "amount": "10000"
        },
        {
            "name": "Decoration Services - Complete stage decoration with flowers, drapes, and lighting",
            "hsn": "997329",
            "qty": 1,
            "rate": "15000",
            "amount": "15000"
        }
    ],
    "taxable_amount": "50400",
    "cgst": "4536",
    "sgst": "4536",
    "total": "59472"
}

generator = InvoiceGenerator()
generator.generate_invoice(invoice_data, output_path="test_wrapping.pdf")
print("✅ Text wrapping test completed - test_wrapping.pdf created")
print("   This invoice has long descriptions to test text wrapping")

