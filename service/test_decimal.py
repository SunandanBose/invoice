"""
Test decimal amounts in CGST/SGST and round-off
"""

from invoice_generator import InvoiceGenerator

# Test with decimal CGST/SGST amounts
invoice_data = {
    "invoice_no": "TEST-DECIMAL-001",
    "invoice_date": "09-Dec-2025",
    "to": "The Director, CSIR - National Metallurgical Laboratory",
    "job_description": "Test Invoice with Decimals",
    "items": [
        {
            "name": "Test Service Item",
            "hsn": "997329",
            "qty": 1,
            "rate": "25401",
            "amount": "25401"
        }
    ],
    "taxable_amount": "25401",
    "cgst": "2286.09",
    "sgst": "2286.09",
    "total": "29973.18"
}

generator = InvoiceGenerator()
generator.generate_invoice(invoice_data, output_path="test_decimal.pdf")

print("✅ Decimal test completed - test_decimal.pdf created")
print("\nTest data:")
print(f"  Taxable Amount: 25401")
print(f"  CGST: 2286.09 (should show with decimals)")
print(f"  SGST: 2286.09 (should show with decimals)")
print(f"  Subtotal: 29973.18")
print(f"  Round off: 0.82 (to make total 29974)")
print(f"  Invoice Total: 29974")

