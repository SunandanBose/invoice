# Invoice PDF Generator Service

A Python service for generating GST-compliant tax invoices in PDF format. Designed to run on AWS Lambda or similar serverless platforms.

## Features

- ✅ GST-compliant invoice format
- ✅ Automatic tax calculations (CGST, SGST, IGST)
- ✅ Number to words conversion (Indian numbering system)
- ✅ Professional PDF layout with clean, readable design
- ✅ **Automatic text wrapping** for long item descriptions
- ✅ **Smart pagination** - limited to 20 rows per page to prevent overflow
- ✅ Improved typography and spacing for better readability
- ✅ AWS Lambda ready
- ✅ Base64 encoded output for API Gateway integration

## Installation

### Local Development

```bash
cd service
pip install -r requirements.txt
```

### AWS Lambda Deployment

1. Install dependencies in a deployment package:
```bash
pip install -r requirements.txt -t package/
cp invoice_generator.py lambda_handler.py package/
cd package
zip -r ../lambda_deployment.zip .
```

2. Upload `lambda_deployment.zip` to AWS Lambda

## Configuration

### Company Details (config.py)

Edit `config.py` to set your company details. These will be used for all invoices:

```python
COMPANY_CONFIG = {
    "name": "YOUR COMPANY NAME",
    "address": "Your complete address",
    "mobile": "Your contact numbers",
    "state": "Your State",
    "gstin": "Your GST Number",
    "state_code": "Your State Code",
    "bank_details": {
        "ifsc": "Your IFSC Code",
        "account_number": "Your Account Number",
        "bank_name": "Your Bank Name and Branch"
    }
}
```

## Usage

### Input Format (SIMPLIFIED)

The service expects a simple JSON input with the following structure:

```json
{
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
```

**Note:** Company details are automatically loaded from `config.py`. You only need to provide invoice-specific data!

### Local Testing

```bash
# Test the invoice generator directly
python invoice_generator.py

# Test the Lambda handler
python lambda_handler.py
```

### Lambda Integration

The Lambda handler returns a response compatible with API Gateway:

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/pdf",
    "Content-Disposition": "attachment; filename=invoice_134.pdf"
  },
  "body": "<base64-encoded-pdf>",
  "isBase64Encoded": true
}
```

**Filename Format**: `invoice_<invoice_no>.pdf`

Examples:
- Invoice #134 → `invoice_134.pdf`
- Invoice #INV-2025-001 → `invoice_INV-2025-001.pdf`
- Invoice #ABC123 → `invoice_ABC123.pdf`

## API Endpoints

### Generate Invoice

**POST** `/generate-invoice`

**Request Body:**
```json
{
  "invoice_no": "134",
  "invoice_date": "05-Dec-2025",
  "to": "Customer Name, Customer Address",
  "job_description": "Event/Job Description",
  "items": [
    {"name": "Item description", "hsn": "HSN code", "qty": 1, "rate": "1000", "amount": "1000"}
  ],
  "taxable_amount": "1000",
  "cgst": "90",
  "sgst": "90",
  "total": "1180"
}
```

**Response:**
- Success: PDF file (application/pdf)
- Error: JSON with error details

## Field Descriptions

### Required Fields

- `invoice_no`: Invoice number (string)
- `invoice_date`: Invoice date (string, format: DD-MMM-YYYY)
- `to`: Customer name and address (comma-separated string)
- `job_description`: Description of the job/event (optional)
- `items`: Array of items (see below)
- `taxable_amount`: Base amount before tax (string or number)
- `cgst`: CGST amount (string or number)
- `sgst`: SGST amount (string or number)
- `total`: Final total amount (string or number)

### Items Array
Each item contains:
- `name`: Service/product description
- `hsn`: HSN/SAC code
- `qty`: Quantity (number)
- `rate`: Rate per unit (string or number)
- `amount`: Total amount for the item (string or number)

### Optional Fields
- `customer_gstin`: Customer's GST number (defaults to value in config.py)
- `event_name`: Event name (optional)
- `igst`: IGST amount for inter-state transactions
- `round_off`: Rounding adjustment

## AWS Lambda Configuration

### Recommended Settings
- **Runtime**: Python 3.9 or higher
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Handler**: `lambda_handler.lambda_handler`

### Environment Variables
None required for basic operation.

## Dependencies

- `reportlab==4.0.7`: PDF generation library
- `Pillow==10.1.0`: Image processing (required by reportlab)

## Error Handling

The service returns appropriate HTTP status codes:

- `200`: Success - PDF generated
- `400`: Bad Request - Invalid input or missing required fields
- `500`: Internal Server Error - Processing error

## License

MIT License

## Support

For issues or questions, please open an issue in the repository.

