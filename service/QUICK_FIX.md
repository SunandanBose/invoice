# 🚨 Quick Fix for Pillow Import Error

## Error You're Seeing

```
"errorMessage": "Unable to import module 'lambda_function': cannot import name '_imaging' from 'PIL'"
```

## ⚡ Fastest Solution (5 minutes)

### Option A: Use Lambda Layer (EASIEST) ✅

**Step 1: Create Small Package (Code Only)**

```bash
cd service
mkdir package
cp invoice_generator.py lambda_function.py config.py package/
cd package
zip -r ../lambda_deployment.zip .
cd ..
```

**Step 2: Upload to Lambda**

Upload the small `lambda_deployment.zip` (< 1MB)

**Step 3: Add Pillow Layer**

1. Go to Lambda Console → Your Function
2. Scroll to "Layers" section
3. Click "Add a layer"
4. Choose "Specify an ARN"
5. **Change Runtime to Python 3.9 first!**
6. Use this ARN (for us-east-1):
   ```
   arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p39-Pillow:1
   ```
7. Click "Add"

**Step 4: Test**

Your function should now work!

---

## 🌍 Layer ARNs by Region

Find the correct ARN for your region:

| Region | Python 3.9 Pillow Layer ARN |
|--------|----------------------------|
| us-east-1 | `arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p39-Pillow:1` |
| us-west-2 | `arn:aws:lambda:us-west-2:770693421928:layer:Klayers-p39-Pillow:1` |
| eu-west-1 | `arn:aws:lambda:eu-west-1:770693421928:layer:Klayers-p39-Pillow:1` |
| ap-south-1 | `arn:aws:lambda:ap-south-1:770693421928:layer:Klayers-p39-Pillow:1` |

**Full list**: https://github.com/keithrozario/Klayers

---

## 🐳 Alternative: Use Docker (If Layer Doesn't Work)

**Step 1: Create Dockerfile**

```dockerfile
FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt -t /asset

COPY invoice_generator.py /asset/
COPY lambda_function.py /asset/
COPY config.py /asset/
```

**Step 2: Build**

```bash
cd service
docker build -t invoice-lambda .
docker create --name temp invoice-lambda
docker cp temp:/asset ./package
docker rm temp
cd package
zip -r ../lambda_deployment.zip .
```

**Step 3: Upload**

Upload the larger `lambda_deployment.zip` (~15-20MB)

---

## ⚙️ Lambda Configuration

Make sure these settings are correct:

| Setting | Value |
|---------|-------|
| Runtime | **Python 3.9** (not 3.14!) |
| Handler | `lambda_function.lambda_handler` |
| Memory | 512 MB |
| Timeout | 30 seconds |

---

## ✅ Verification

Test with this payload:

```json
{
  "invoice_no": "TEST-001",
  "invoice_date": "10-Dec-2025",
  "to": "Test Customer, Test Address",
  "job_description": "Test Invoice",
  "items": [
    {
      "name": "Test Item",
      "hsn": "997329",
      "qty": 1,
      "rate": "1000",
      "amount": "1000"
    }
  ],
  "taxable_amount": "1000",
  "cgst": "90",
  "sgst": "90",
  "total": "1180"
}
```

Expected result: PDF file `invoice_TEST-001.pdf`

---

## 🎯 Summary

**Problem**: Pillow needs to be compiled for Amazon Linux  
**Solution**: Use Lambda Layer (easiest) or Docker (most reliable)  
**Key**: Change runtime to Python 3.9 for better layer support

**Recommended**: Option A with Lambda Layer - 5 minutes setup! ✅

