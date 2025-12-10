# AWS Lambda Deployment Guide

## 📦 Deployment Options

### ⚠️ Important: Pillow Compatibility Issue

The error `cannot import name '_imaging' from 'PIL'` occurs because Pillow has C extensions that must be compiled for Amazon Linux (Lambda's runtime). 

**You have 3 options:**

---

## ✅ Option 1: Use Lambda Layer (RECOMMENDED - Easiest)

This is the simplest and most reliable method.

### Step 1: Create Code-Only Package

```bash
cd service
mkdir package
cp invoice_generator.py lambda_function.py config.py package/
cd package
zip -r ../lambda_deployment.zip .
cd ..
```

### Step 2: Upload Code to Lambda

Upload `lambda_deployment.zip` to your Lambda function (should be < 1MB).

### Step 3: Add Lambda Layer for Dependencies

Use Klayers (pre-built Lambda layers):

**For Python 3.14**: Use these ARNs based on your region:

```
# Pillow Layer
arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p314-Pillow:1

# ReportLab - you may need to create this yourself or use Python 3.9
```

**For Python 3.9** (RECOMMENDED - better layer support):

```
# Pillow Layer
arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p39-Pillow:1

# Or search for "Klayers" in Lambda Layers
```

### Step 4: Add Layer to Lambda Function

1. Go to Lambda Console → Your Function
2. Scroll down to "Layers"
3. Click "Add a layer"
4. Choose "Specify an ARN"
5. Paste the Pillow layer ARN for your region
6. Click "Add"

**Find layers for your region**: https://github.com/keithrozario/Klayers

---

## ✅ Option 2: Use Docker to Build (Most Reliable)

Build the package in an environment that matches Lambda's runtime.

### Step 1: Create Dockerfile

Create `Dockerfile` in the service directory:

```dockerfile
FROM public.ecr.aws/lambda/python:3.9

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt -t /asset

# Copy source files
COPY invoice_generator.py /asset/
COPY lambda_function.py /asset/
COPY config.py /asset/
```

### Step 2: Build and Extract

```bash
cd service

# Build Docker image
docker build -t invoice-lambda .

# Create container and copy files
docker create --name temp-container invoice-lambda
docker cp temp-container:/asset ./package
docker rm temp-container

# Create deployment package
cd package
zip -r ../lambda_deployment.zip .
cd ..
```

### Step 3: Upload to Lambda

Upload `lambda_deployment.zip` (will be ~15-20MB).

---

## ✅ Option 3: Use EC2 or Cloud9 (Amazon Linux)

Build the package on an Amazon Linux environment.

### Step 1: Launch EC2 (Amazon Linux 2023)

```bash
# SSH into EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Install Python and dependencies
sudo yum install python3.9 -y
python3.9 -m pip install --upgrade pip
```

### Step 2: Build Package

```bash
# Upload your files to EC2
# Then:
cd service
pip3.9 install -r requirements.txt -t package/
cp invoice_generator.py lambda_function.py config.py package/
cd package
zip -r ../lambda_deployment.zip .
```

### Step 3: Download and Upload

Download `lambda_deployment.zip` from EC2 and upload to Lambda.

---

## 🎯 Recommended Solution

**Use Option 1 (Lambda Layer)** - It's the easiest and cleanest approach:

1. ✅ Small deployment package (< 1MB)
2. ✅ No Docker required
3. ✅ Reusable across multiple functions
4. ✅ Easy to update dependencies

### Quick Setup (Option 1)

```bash
# 1. Create code package
cd service
mkdir package
cp invoice_generator.py lambda_function.py config.py package/
cd package
zip -r ../lambda_deployment.zip .

# 2. Upload to Lambda
# (Upload via AWS Console or CLI)

# 3. Add Pillow layer
# Use ARN: arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p39-Pillow:1
# (Change region as needed)
```

### Important Notes

- **Python 3.9 is recommended** (better layer support than 3.14)
- Change Lambda runtime to Python 3.9 if using Klayers
- Layers are region-specific - use the correct ARN for your region

---

## ⚙️ Lambda Configuration

### Function Settings

| Setting | Value |
|---------|-------|
| **Runtime** | Python 3.9 or higher |
| **Handler** | `lambda_handler.lambda_handler` |
| **Memory** | 512 MB |
| **Timeout** | 30 seconds |
| **Architecture** | x86_64 |

### Environment Variables

**Optional** - Only if you want to override config.py:
- `COMPANY_NAME` - Your company name
- `COMPANY_GSTIN` - Your GST number
- (Not recommended - better to edit config.py directly)

---

## 🔌 API Gateway Integration

### 1. Create REST API

1. Go to API Gateway console
2. Create new REST API
3. Create resource: `/generate-invoice`
4. Create method: `POST`
5. Integration type: Lambda Function
6. Select your Lambda function
7. Enable **Lambda Proxy Integration**

### 2. Binary Media Types

Add to API Gateway settings:
- `application/pdf`
- `*/*`

### 3. Deploy API

1. Create deployment stage (e.g., `prod`)
2. Deploy API
3. Note the Invoke URL

---

## 📤 Request Format

### Endpoint

```
POST https://your-api-id.execute-api.region.amazonaws.com/prod/generate-invoice
```

### Headers

```
Content-Type: application/json
```

### Body

```json
{
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
    }
  ],
  "taxable_amount": "25400",
  "cgst": "2286",
  "sgst": "2286",
  "total": "29972"
}
```

---

## 📥 Response Format

### Success Response (200)

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/pdf",
    "Content-Disposition": "attachment; filename=invoice_134.pdf"
  },
  "body": "<base64-encoded-pdf-data>",
  "isBase64Encoded": true
}
```

**Filename Format**: `invoice_<invoice_no>.pdf`

### Error Response (400)

```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Missing required fields: invoice_no, invoice_date\"}"
}
```

### Error Response (500)

```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Internal server error\", \"details\": \"...\"}"
}
```

---

## 🧪 Testing

### Using cURL

```bash
curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/generate-invoice \
  -H "Content-Type: application/json" \
  -d @example_input.json \
  --output invoice_134.pdf
```

### Using Python

```python
import requests
import json
import base64

# Read input data
with open('example_input.json', 'r') as f:
    invoice_data = json.load(f)

# Call API
response = requests.post(
    'https://your-api-id.execute-api.region.amazonaws.com/prod/generate-invoice',
    json=invoice_data
)

# Save PDF
if response.status_code == 200:
    # Decode base64 response
    pdf_data = base64.b64decode(response.json()['body'])
    
    # Save to file
    with open('invoice_134.pdf', 'wb') as f:
        f.write(pdf_data)
    print("Invoice saved!")
else:
    print(f"Error: {response.text}")
```

### Using Postman

1. **Method**: POST
2. **URL**: Your API Gateway endpoint
3. **Headers**: `Content-Type: application/json`
4. **Body**: Raw JSON (paste from example_input.json)
5. **Send**: Click Send
6. **Save Response**: Save response as binary file

---

## 🔒 Security Best Practices

### 1. API Key

Add API key requirement in API Gateway:
```bash
x-api-key: your-api-key-here
```

### 2. IAM Authentication

Use AWS IAM for authentication:
- Create IAM role
- Attach policy for API Gateway invoke
- Use AWS Signature V4

### 3. Rate Limiting

Configure in API Gateway:
- Throttling: 100 requests/second
- Burst: 200 requests
- Quota: 10,000 requests/day

### 4. CORS (if needed)

Enable CORS in API Gateway:
```json
{
  "Access-Control-Allow-Origin": "https://yourdomain.com",
  "Access-Control-Allow-Methods": "POST",
  "Access-Control-Allow-Headers": "Content-Type"
}
```

---

## 📊 Monitoring

### CloudWatch Metrics

Monitor these metrics:
- **Invocations**: Number of Lambda calls
- **Duration**: Execution time (should be < 5 seconds)
- **Errors**: Failed invocations
- **Throttles**: Rate limit hits

### CloudWatch Logs

Lambda automatically logs to CloudWatch:
```
/aws/lambda/your-function-name
```

### Alarms

Set up alarms for:
- Error rate > 5%
- Duration > 10 seconds
- Throttles > 0

---

## 💰 Cost Estimation

### Lambda Pricing (us-east-1)

- **Requests**: $0.20 per 1M requests
- **Duration**: $0.0000166667 per GB-second
- **Memory**: 512 MB
- **Avg Duration**: 2 seconds

**Example**: 10,000 invoices/month
- Requests: 10,000 × $0.20/1M = $0.002
- Duration: 10,000 × 2s × 0.5GB × $0.0000166667 = $0.17
- **Total**: ~$0.17/month

### API Gateway Pricing

- **Requests**: $3.50 per 1M requests
- **Data Transfer**: $0.09/GB (first 10TB)

**Example**: 10,000 invoices/month (avg 50KB each)
- Requests: 10,000 × $3.50/1M = $0.035
- Data: 0.5GB × $0.09 = $0.045
- **Total**: ~$0.08/month

**Grand Total**: ~$0.25/month for 10,000 invoices

---

## 🐛 Troubleshooting

### Issue: "Task timed out after 3.00 seconds"

**Solution**: Increase Lambda timeout to 30 seconds

### Issue: "Unable to import module 'lambda_handler'"

**Solution**: Check that all files are in the root of the zip:
```
lambda_deployment.zip
├── lambda_handler.py
├── invoice_generator.py
├── config.py
├── reportlab/
└── PIL/
```

### Issue: "No module named 'reportlab'"

**Solution**: Reinstall dependencies in package folder:
```bash
rm -rf package/
pip install -r requirements.txt -t package/
```

### Issue: PDF is corrupted

**Solution**: Ensure binary media types are configured in API Gateway

### Issue: "Internal server error"

**Solution**: Check CloudWatch Logs for detailed error message

---

## 📝 Checklist

Before deploying to production:

- [ ] Edit `config.py` with your company details
- [ ] Test locally: `python lambda_handler.py`
- [ ] Create deployment package
- [ ] Upload to Lambda
- [ ] Configure Lambda settings (512MB, 30s timeout)
- [ ] Create API Gateway endpoint
- [ ] Configure binary media types
- [ ] Test with cURL or Postman
- [ ] Set up CloudWatch alarms
- [ ] Configure API key (optional)
- [ ] Enable CORS (if needed)
- [ ] Document API endpoint for your team

---

## 🎉 You're Ready!

Your invoice generation API is now live and ready to use!

**Endpoint**: `https://your-api-id.execute-api.region.amazonaws.com/prod/generate-invoice`

**Returns**: `invoice_<invoice_no>.pdf`

