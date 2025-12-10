"""
Test script for invoice generator - Using SIMPLIFIED input format
"""

from invoice_generator import InvoiceGenerator
from config import COMPANY_CONFIG
import json


def test_basic_invoice():
    """Test basic invoice generation with simplified format"""
    
    invoice_data = {
        "invoice_no": "134",
        "invoice_date": "05-Dec-2025",
        "to": "The Director, CSIR - National Metallurgical Laboratory, Jamshedpur - 831017",
        "job_description": "Platinum Jubilee",
        "items": [
            {
                "name": "Stage Programme PA System with Stage light & codeless microphone (3nos)",
                "hsn": "997329",
                "qty": 1,
                "rate": "25400",
                "amount": "25400"
            }
        ],
        "taxable_amount": "25400",
        "cgst": "2286",
        "sgst": "2286",
        "total": "29972"
    }
    
    generator = InvoiceGenerator()
    generator.generate_invoice(invoice_data, output_path="test_output.pdf")
    print("✅ Basic invoice test passed - test_output.pdf created")


def test_multiple_items():
    """Test invoice with multiple items - simplified format"""
    
    invoice_data = {
        "invoice_no": "INV-002",
        "invoice_date": "09-Dec-2025",
        "to": "XYZ Corporation, 456 Business Park, Mumbai - 400001",
        "job_description": "Annual Conference",
        "items": [
            {
                "name": "Audio System Rental",
                "hsn": "997329",
                "qty": 2,
                "rate": "5000",
                "amount": "10000"
            },
            {
                "name": "Stage Setup",
                "hsn": "997329",
                "qty": 1,
                "rate": "15000",
                "amount": "15000"
            },
            {
                "name": "Lighting Equipment",
                "hsn": "997329",
                "qty": 5,
                "rate": "2000",
                "amount": "10000"
            }
        ],
        "taxable_amount": "35000",
        "cgst": "3150",
        "sgst": "3150",
        "total": "41300"
    }
    
    generator = InvoiceGenerator()
    generator.generate_invoice(invoice_data, output_path="test_multiple_items.pdf")
    print("✅ Multiple items test passed - test_multiple_items.pdf created")


def test_with_custom_config():
    """Test invoice with custom company configuration"""
    
    # Custom company config
    custom_company = {
        "name": "MY CUSTOM BUSINESS",
        "address": "123 Custom Street, Custom City, Custom State",
        "mobile": "1234567890",
        "state": "Custom State",
        "gstin": "12ABCDE1234F1Z5",
        "state_code": "12",
        "bank_details": {
            "ifsc": "CUST0001234",
            "account_number": "11111111111111",
            "bank_name": "Custom Bank, Custom Branch"
        }
    }
    
    invoice_data = {
        "invoice_no": "CUSTOM-001",
        "invoice_date": "09-Dec-2025",
        "to": "Test Customer, Test Address, Test City - 123456",
        "job_description": "Custom Services",
        "items": [
            {
                "name": "Custom Service Item",
                "hsn": "998314",
                "qty": 5,
                "rate": "1000",
                "amount": "5000"
            }
        ],
        "taxable_amount": "5000",
        "cgst": "450",
        "sgst": "450",
        "total": "5900"
    }
    
    # Create generator with custom config
    generator = InvoiceGenerator(company_config=custom_company)
    generator.generate_invoice(invoice_data, output_path="test_custom_config.pdf")
    print("✅ Custom config test passed - test_custom_config.pdf created")


if __name__ == "__main__":
    print("Running invoice generator tests...\n")
    print(f"Using default company config: {COMPANY_CONFIG['name']}\n")
    
    test_basic_invoice()
    test_multiple_items()
    test_with_custom_config()
    
    print("\n✅ All tests completed successfully!")
    print("\nGenerated files:")
    print("  - test_output.pdf (basic invoice with config.py)")
    print("  - test_multiple_items.pdf (multiple items)")
    print("  - test_custom_config.pdf (custom company config)")
    print("\n💡 Tip: Edit config.py to change default company details!")

