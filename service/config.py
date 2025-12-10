"""
Configuration file for invoice generator
Edit these values to customize your company details
"""

# Company Information
COMPANY_CONFIG = {
    "name": "GOPAL TENT HOUSE",
    "address": "26, TINASHED, GOLMURI MARKET, JAMSHEDPUR, JHARKHAND",
    "mobile": "7004829773, 9431330019",
    "state": "Jharkhand",
    "gstin": "20ABKPB5821F2ZA",
    "state_code": "20",
    "bank_details": {
        "ifsc": "CBI0282406",
        "account_number": "1843803988",
        "bank_name": "Central Bank of India Golmuri, Jamshedpur"
    }
}

# Default Customer GST (if not provided in input)
DEFAULT_CUSTOMER_GSTIN = "20AAATC2716R2ZS"

# Tax Rates (in percentage)
DEFAULT_CGST_RATE = 9
DEFAULT_SGST_RATE = 9
DEFAULT_IGST_RATE = 18

# Invoice Settings
INVOICE_SETTINGS = {
    "page_size": "A4",
    "show_qty_rate": True,  # Show quantity and rate columns
    "max_items_rows": 27,   # Maximum rows in items table
    "currency": "Rs.",
    "round_off_enabled": True
}

