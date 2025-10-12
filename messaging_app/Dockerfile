FROM python:3.10

# Step 2: Set working directory
WORKDIR /app

# Step 3: Copy dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy app code
COPY . .

# Step 5: Expose port Django runs on
EXPOSE 8000
# -p 
# Step 6: Start Django server
CMD "python3 manage.py runserver 0.0.0.0:8000"
