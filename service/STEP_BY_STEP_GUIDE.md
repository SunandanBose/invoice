# 📖 Step-by-Step Lambda Deployment Guide

## 🎯 Goal
Deploy your invoice generator to AWS Lambda without the Pillow import error.

---

## 📦 Part 1: Prepare Your Deployment Package

### Step 1: Create Code-Only Package

Open terminal and run:

```bash
cd /Users/subose/testWorkspace/invoice/service

# Create a clean package directory
rm -rf package
mkdir package

# Copy only your Python files (NOT dependencies)
cp invoice_generator.py package/
cp lambda_function.py package/
cp config.py package/

# Create zip file
cd package
zip -r ../lambda_deployment.zip .
cd ..

# Verify the zip
unzip -l lambda_deployment.zip
```

You should see:
```
Archive:  lambda_deployment.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    xxxxx  12-10-2024 10:00   invoice_generator.py
    xxxxx  12-10-2024 10:00   lambda_function.py
    xxxxx  12-10-2024 10:00   config.py
```

✅ **Result**: You now have `lambda_deployment.zip` (~50KB)

---

## 🚀 Part 2: Create Lambda Function (If New)

### Option A: If You Already Have a Lambda Function
Skip to Part 3.

### Option B: Create New Lambda Function

1. **Go to AWS Console**
   - Navigate to: https://console.aws.amazon.com/lambda
   - Make sure you're in the correct region (top-right corner)

2. **Click "Create function"**

3. **Choose "Author from scratch"**

4. **Fill in the details:**
   - **Function name**: `invoice-generator`
   - **Runtime**: Select **Python 3.9** (NOT 3.14!)
   - **Architecture**: x86_64
   - **Permissions**: Create a new role with basic Lambda permissions

5. **Click "Create function"**

✅ **Result**: Lambda function created

---

## 📤 Part 3: Upload Your Code

### Step 1: Upload ZIP File

1. **In Lambda Console** (you should see your function)

2. **Scroll down to "Code source" section**

3. **Click "Upload from"** dropdown button

4. **Select ".zip file"**

5. **Click "Upload"** button
   - Browse to: `/Users/subose/testWorkspace/invoice/service/lambda_deployment.zip`
   - Select the file
   - Click "Open"

6. **Click "Save"** button

7. **Wait for upload** (should be quick, ~50KB)

✅ **Result**: Your code is uploaded

---

## 🔧 Part 4: Configure Runtime Settings

### Step 1: Update Handler

1. **Scroll down to "Runtime settings" section**

2. **Click "Edit"** button

3. **Update these fields:**
   - **Runtime**: Python 3.9 (if not already)
   - **Handler**: `lambda_function.lambda_handler`
   - **Architecture**: x86_64

4. **Click "Save"**

✅ **Result**: Handler configured correctly

---

## 📚 Part 5: Add Pillow Layer (CRITICAL STEP)

This solves the Pillow import error!

### Step 1: Find Your Region

Look at the top-right corner of AWS Console to see your region.
Example: `us-east-1`, `us-west-2`, `ap-south-1`, etc.

### Step 2: Get the Correct Layer ARN

Based on your region, use the corresponding ARN:

| Region | Pillow Layer ARN |
|--------|------------------|
| **us-east-1** (N. Virginia) | `arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p39-Pillow:1` |
| **us-west-2** (Oregon) | `arn:aws:lambda:us-west-2:770693421928:layer:Klayers-p39-Pillow:1` |
| **eu-west-1** (Ireland) | `arn:aws:lambda:eu-west-1:770693421928:layer:Klayers-p39-Pillow:1` |
| **ap-south-1** (Mumbai) | `arn:aws:lambda:ap-south-1:770693421928:layer:Klayers-p39-Pillow:1` |
| **ap-southeast-1** (Singapore) | `arn:aws:lambda:ap-southeast-1:770693421928:layer:Klayers-p39-Pillow:1` |

**For other regions**: Visit https://github.com/keithrozario/Klayers

### Step 3: Add the Layer

1. **Scroll down to "Layers" section** (below Code source)

2. **Click "Add a layer"** button

3. **Select "Specify an ARN"** radio button

4. **Paste the ARN** for your region
   - Example for us-east-1:
   ```
   arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p39-Pillow:1
   ```

5. **Click "Verify"** (it should show "Verified")

6. **Click "Add"** button

7. **You should see the layer listed** under "Layers (1)"

✅ **Result**: Pillow layer added successfully

---

## ⚙️ Part 6: Configure Function Settings

### Step 1: Update Memory and Timeout

1. **Click "Configuration" tab** (top of page)

2. **Click "General configuration"** in left sidebar

3. **Click "Edit"** button

4. **Update settings:**
   - **Memory**: 512 MB
   - **Timeout**: 30 seconds

5. **Click "Save"**

✅ **Result**: Function configured for invoice generation

---

## 🧪 Part 7: Test Your Function

### Step 1: Create Test Event

1. **Click "Test" tab** (top of page)

2. **Click "Create new event"** button

3. **Fill in details:**
   - **Event name**: `test-invoice`
   - **Event sharing**: Private

4. **Paste this test JSON:**

```json
{
  "invoice_no": "TEST-001",
  "invoice_date": "10-Dec-2025",
  "to": "Test Customer, Test Address, Test City - 123456",
  "job_description": "Test Invoice",
  "items": [
    {
      "name": "Test Service Item",
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

5. **Click "Save"**

### Step 2: Run Test

1. **Click "Test"** button (orange button)

2. **Wait for execution** (should take 2-5 seconds)

3. **Check results:**

**✅ SUCCESS** - You should see:
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/pdf",
    "Content-Disposition": "attachment; filename=invoice_TEST-001.pdf"
  },
  "body": "JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PAovRjEgMi...",
  "isBase64Encoded": true
}
```

**❌ ERROR** - If you see errors, check:
- Is the layer added? (Check Layers section)
- Is runtime Python 3.9? (Check Runtime settings)
- Is handler correct? (Should be `lambda_function.lambda_handler`)

✅ **Result**: Function works! PDF generated successfully

---

## 🌐 Part 8: Create API Gateway (Optional)

If you want to call this via HTTP API:

### Step 1: Add Function URL (Easiest)

1. **Go to "Configuration" tab**

2. **Click "Function URL"** in left sidebar

3. **Click "Create function URL"**

4. **Configure:**
   - **Auth type**: NONE (or AWS_IAM for security)
   - **CORS**: Enable if calling from browser

5. **Click "Save"**

6. **Copy the Function URL**
   - Example: `https://abc123.lambda-url.us-east-1.on.aws/`

### Step 2: Test with cURL

```bash
curl -X POST https://your-function-url.lambda-url.us-east-1.on.aws/ \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_no": "TEST-002",
    "invoice_date": "10-Dec-2025",
    "to": "Customer Name, Address",
    "job_description": "Test",
    "items": [{"name": "Item", "hsn": "997329", "qty": 1, "rate": "1000", "amount": "1000"}],
    "taxable_amount": "1000",
    "cgst": "90",
    "sgst": "90",
    "total": "1180"
  }' \
  --output invoice_TEST-002.pdf
```

✅ **Result**: API is live and accessible

---

## ✅ Verification Checklist

Before going to production, verify:

- [ ] Lambda function created
- [ ] Code uploaded (lambda_deployment.zip)
- [ ] Runtime set to Python 3.9
- [ ] Handler set to `lambda_function.lambda_handler`
- [ ] Pillow layer added (check Layers section)
- [ ] Memory set to 512 MB
- [ ] Timeout set to 30 seconds
- [ ] Test event passes successfully
- [ ] Response contains base64 PDF data
- [ ] Filename format is correct: `invoice_<number>.pdf`

---

## 🆘 Troubleshooting

### Error: "Unable to import module 'lambda_function'"

**Solution**: 
- Check that handler is: `lambda_function.lambda_handler`
- Check that lambda_function.py is in the root of the zip

### Error: "cannot import name '_imaging' from 'PIL'"

**Solution**:
- Add the Pillow layer (Part 5)
- Make sure runtime is Python 3.9 (not 3.14)
- Verify layer ARN matches your region

### Error: "Task timed out after 3.00 seconds"

**Solution**:
- Increase timeout to 30 seconds (Part 6)

### Error: "Memory limit exceeded"

**Solution**:
- Increase memory to 512 MB (Part 6)

### PDF is corrupted or empty

**Solution**:
- Check that `isBase64Encoded: true` in response
- Verify Content-Type is `application/pdf`

---

## 📞 Need Help?

If you're stuck on any step:

1. **Check CloudWatch Logs**:
   - Go to "Monitor" tab
   - Click "View logs in CloudWatch"
   - Look for error messages

2. **Verify Layer**:
   - Scroll to "Layers" section
   - Should show: "Klayers-p39-Pillow:1"

3. **Re-read Part 5** (Adding Layer) - This is the most critical step!

---

## 🎉 Success!

Once your test passes, your invoice generator is live and ready to use!

**Returns**: PDF file with name `invoice_<invoice_no>.pdf`

**Next Steps**:
- Update `config.py` with your company details
- Set up API Gateway for HTTP access
- Add authentication (API key or IAM)
- Monitor with CloudWatch

