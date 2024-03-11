##########
# Base Image
##########
# Use the official Python image as the base image
FROM python:3.9-slim
# FROM ubuntu:16.04


##########
# Dir
##########
# Set working directory in the container
WORKDIR /app

# Copy the Python script, Jupyter Notebook, and requirements.txt into the container
# COPY requirements.txt .
COPY . .
# COPY ./src src
# COPY ./data data


##########
# Install
##########
# Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt


##########
# Jupyter
##########
# Install Jupyter Notebook
# RUN pip install jupyterlab

# Expose port for Jupyter Notebook
# EXPOSE 8888


##########
# StartUp Commands
##########
# Command to run Jupyter Notebook
# CMD ["python3", "-m", " ~/.local/bin/jupyter-notebook", "--ip='*'", "--port=8888", "--no-browser", "--allow-root"]        ## if want to explore the JN
CMD ["python", "main.py"]
