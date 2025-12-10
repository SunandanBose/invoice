# ✅ Lambda Deployment Checklist

## Quick Reference - Do These Steps in Order

### 📦 Step 1: Create Package (On Your Computer)
```bash
cd /Users/subose/testWorkspace/invoice/service
rm -rf package
mkdir package
cp invoice_generator.py lambda_function.py config.py package/
cd package
zip -r ../lambda_deployment.zip .
cd ..
```
- [ ] Package created
- [ ] File size ~50KB (not 15MB!)

---

### 🚀 Step 2: Go to AWS Lambda Console
- [ ] Logged into AWS Console
- [ ] Region selected (top-right corner)
- [ ] Navigated to Lambda service

---

### 🆕 Step 3: Create or Select Function
**If New Function:**
- [ ] Clicked "Create function"
- [ ] Selected "Author from scratch"
- [ ] Function name: `invoice-generator`
- [ ] Runtime: **Python 3.9** ⚠️ (NOT 3.14!)
- [ ] Clicked "Create function"

**If Existing Function:**
- [ ] Selected your function from list

---

### 📤 Step 4: Upload Code
- [ ] Found "Code source" section
- [ ] Clicked "Upload from" → ".zip file"
- [ ] Selected `lambda_deployment.zip`
- [ ] Clicked "Save"
- [ ] Upload completed (check for success message)

---

### 🔧 Step 5: Configure Handler
- [ ] Found "Runtime settings" section
- [ ] Clicked "Edit"
- [ ] Runtime: **Python 3.9**
- [ ] Handler: `lambda_function.lambda_handler`
- [ ] Clicked "Save"

---

### 📚 Step 6: Add Pillow Layer (MOST IMPORTANT!)

**Find Your Region First:**
- [ ] Checked region in top-right corner

**Get ARN for Your Region:**

| Your Region | Copy This ARN |
|-------------|---------------|
| us-east-1 | `arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p39-Pillow:1` |
| us-west-2 | `arn:aws:lambda:us-west-2:770693421928:layer:Klayers-p39-Pillow:1` |
| eu-west-1 | `arn:aws:lambda:eu-west-1:770693421928:layer:Klayers-p39-Pillow:1` |
| ap-south-1 | `arn:aws:lambda:ap-south-1:770693421928:layer:Klayers-p39-Pillow:1` |

**Add the Layer:**
- [ ] Scrolled to "Layers" section
- [ ] Clicked "Add a layer"
- [ ] Selected "Specify an ARN"
- [ ] Pasted ARN for your region
- [ ] Clicked "Verify" (should show "Verified")
- [ ] Clicked "Add"
- [ ] Layer appears in list (shows "Klayers-p39-Pillow:1")

---

### ⚙️ Step 7: Configure Memory & Timeout
- [ ] Clicked "Configuration" tab
- [ ] Clicked "General configuration"
- [ ] Clicked "Edit"
- [ ] Memory: **512 MB**
- [ ] Timeout: **30 seconds**
- [ ] Clicked "Save"

---

### 🧪 Step 8: Test Function
- [ ] Clicked "Test" tab
- [ ] Clicked "Create new event"
- [ ] Event name: `test-invoice`
- [ ] Pasted test JSON (see below)
- [ ] Clicked "Save"
- [ ] Clicked "Test" button
- [ ] Got success response (statusCode: 200)
- [ ] Response has base64 PDF data

**Test JSON:**
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

---

### ✅ Final Verification

**Check Response:**
```json
{
  "statusCode": 200,  ✅ Should be 200
  "headers": {
    "Content-Type": "application/pdf",  ✅ Should be PDF
    "Content-Disposition": "attachment; filename=invoice_TEST-001.pdf"  ✅ Correct filename
  },
  "body": "JVBERi0xLjQK...",  ✅ Base64 PDF data
  "isBase64Encoded": true  ✅ Should be true
}
```

- [ ] statusCode is 200
- [ ] Content-Type is application/pdf
- [ ] Filename is invoice_TEST-001.pdf
- [ ] body contains base64 data
- [ ] isBase64Encoded is true

---

## 🎉 Success Criteria

You're done when:
- ✅ Test returns statusCode 200
- ✅ Response contains PDF data
- ✅ Filename format is correct
- ✅ No import errors

---

## 🚨 Common Issues & Quick Fixes

### Issue: "Unable to import module 'lambda_function'"
**Fix:** Handler should be `lambda_function.lambda_handler`

### Issue: "cannot import name '_imaging' from 'PIL'"
**Fix:** Add Pillow layer (Step 6) - This is the most common issue!

### Issue: "Task timed out"
**Fix:** Set timeout to 30 seconds (Step 7)

### Issue: Layer not found
**Fix:** Make sure ARN matches your region

### Issue: Wrong runtime
**Fix:** Change to Python 3.9 (Step 5)

---

## 📱 Quick Command Reference

**Create package:**
```bash
cd service
mkdir package
cp invoice_generator.py lambda_function.py config.py package/
cd package && zip -r ../lambda_deployment.zip . && cd ..
```

**Test locally:**
```bash
python lambda_function.py
```

**Check file size:**
```bash
ls -lh lambda_deployment.zip
# Should be ~50KB, not 15MB
```

---

## 🆘 Still Stuck?

1. **Check CloudWatch Logs:**
   - Go to "Monitor" tab
   - Click "View logs in CloudWatch"

2. **Verify Layer:**
   - Layers section should show: "Klayers-p39-Pillow:1"

3. **Re-do Step 6:**
   - Remove layer and add again
   - Double-check ARN matches your region

4. **Start Fresh:**
   - Delete function
   - Follow all steps again from Step 3

---

## 📞 Support

If you're still getting errors after following all steps:
1. Check the error message in CloudWatch Logs
2. Verify all checkboxes above are ✅
3. Make sure Python 3.9 (not 3.14)
4. Make sure layer is added

**Most common fix:** Add the Pillow layer (Step 6)!

