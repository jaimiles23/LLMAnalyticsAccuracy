# Use the official Python image as the base image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Copy the Python script, Jupyter Notebook, and requirements.txt into the container
COPY requirements.txt .
COPY your_script.py .
COPY notebook.ipynb .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Jupyter Notebook
RUN pip install jupyterlab

# Expose port for Jupyter Notebook
EXPOSE 8888

# Command to run Jupyter Notebook
CMD ["jupyter", "notebook", "--ip='*'", "--port=8888", "--no-browser", "--allow-root"]