"""
AWS Lambda Handler for Invoice Generation

This module provides the Lambda function handler for generating invoices.
It accepts JSON input, generates a PDF invoice, and returns it as base64-encoded data.
"""

import json
import base64
from invoice_generator import InvoiceGenerator
from config import COMPANY_CONFIG


def lambda_handler(event, context):
    """
    AWS Lambda handler function for invoice generation.
    
    This function:
    1. Parses the incoming JSON request
    2. Validates required fields
    3. Generates a PDF invoice
    4. Returns the PDF as base64-encoded data with proper filename
    
    Expected input format (SIMPLIFIED):
    {
        "body": {
            "invoice_no": "134",
            "invoice_date": "05-Dec-2025",
            "to": "The Director, CSIR - National Metallurgical Laboratory",
            "job_description": "Platinum Jubilee",
            "items": [
                {"name": "...", "hsn": "...", "qty": 1, "rate": "...", "amount": "..."}
            ],
            "taxable_amount": "25400",
            "cgst": "2286",
            "sgst": "2286",
            "total": "29972"
        }
    }
    
    Returns:
    {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/pdf",
            "Content-Disposition": "attachment; filename=invoice_<invoice_no>.pdf"
        },
        "body": "<base64-encoded-pdf>",
        "isBase64Encoded": true
    }
    
    The returned PDF filename will be: invoice_<invoice_no>.pdf
    Example: invoice_134.pdf
    """
    
    try:
        # Debug: Log the incoming event
        print(f"DEBUG - Event type: {type(event)}")
        print(f"DEBUG - Event keys: {event.keys() if isinstance(event, dict) else 'not a dict'}")
        print(f"DEBUG - Event: {json.dumps(event)[:500]}")  # First 500 chars
        
        # Parse input - handle API Gateway event structure
        if 'body' in event:
            body = event['body']
            print(f"DEBUG - Body type: {type(body)}")
            print(f"DEBUG - isBase64Encoded: {event.get('isBase64Encoded', False)}")
            
            # Check if body is base64 encoded
            if event.get('isBase64Encoded', False) and isinstance(body, str):
                # Decode base64
                import base64
                body = base64.b64decode(body).decode('utf-8')
                print(f"DEBUG - Decoded body: {body[:200]}")
            
            # Parse JSON
            if isinstance(body, str) and body:
                invoice_data = json.loads(body)
            else:
                invoice_data = body
        else:
            # Direct invocation (testing)
            invoice_data = event
        
        print(f"DEBUG - Parsed invoice_data keys: {invoice_data.keys() if isinstance(invoice_data, dict) else 'not a dict'}")
        
        # Validate required fields (simplified format)
        required_fields = ['invoice_no', 'invoice_date', 'to', 'items', 'taxable_amount', 'total']
        missing_fields = [field for field in required_fields if field not in invoice_data]
        
        if missing_fields:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                })
            }
        
        # Generate invoice (uses company config from config.py)
        generator = InvoiceGenerator()
        pdf_bytes = generator.generate_invoice(invoice_data)
        
        # Encode to base64 for API Gateway
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Create filename: invoice_<Invoice number>.pdf
        invoice_number = invoice_data.get('invoice_no', 'unknown')
        filename = f'invoice_{invoice_number}.pdf'
        
        # Return response with proper filename
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/pdf',
                'Content-Disposition': f'attachment; filename={filename}'
            },
            'body': pdf_base64,
            'isBase64Encoded': True
        }
        
    except json.JSONDecodeError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Invalid JSON format',
                'details': str(e)
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }


# For local testing
if __name__ == "__main__":
    # Sample test event - SIMPLIFIED FORMAT
    test_event = {
        "body": {
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
    }
    
    print(f"Using company config: {COMPANY_CONFIG['name']}")
    
    response = lambda_handler(test_event, None)
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        # Decode and save PDF for testing
        pdf_data = base64.b64decode(response['body'])
        with open('lambda_test_invoice.pdf', 'wb') as f:
            f.write(pdf_data)
        print("PDF saved as lambda_test_invoice.pdf")
    else:
        print(f"Error: {response['body']}")

