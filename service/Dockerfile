FROM public.ecr.aws/lambda/python:3.12

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt -t /asset

# Copy source files
COPY invoice_generator.py /asset/
COPY lambda_function.py /asset/
COPY config.py /asset/

