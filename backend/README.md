# Bahmni Copilot - AI-Powered Health Care Support

## Overview

**Bahmni Copilot** is an AI-powered system integrated with Bahmni, an open-source EMR (Electronic Medical Record) system. This project leverages speech-to-text technology and Open AI models to enhance the user experience by automating form filling based on the transcribed speech of the user. The goal is to make form data entry easier, faster, and more intuitive by utilizing the transcription as context for populating fields in forms.

This approach leverages the power of **AI transcription** (using OpenAI's Whisper API) and **natural language processing (NLP)** to parse the transcription and map it to relevant fields in forms. It helps to speed up the data entry process and minimize human error by automating the population of form fields based on the transcription.

## Features

- **Speech-to-Text**: Converts audio input (speech) into text using AI-powered transcription.
- **Form Auto-Filling**: Automatically extracts relevant details from the transcription and fills out the required fields in the form.
- **Contextual Understanding**: Uses advanced NLP techniques to understand and populate the form based on the spoken words.
- **S3 File Storage**: Audio files are uploaded to Amazon S3 for safe and scalable storage.
- **FastAPI-based API**: RESTful API to manage the transcription service and integrate with the Bahmni EMR system.

## Installation

To set up **Bahmni Copilot**, follow the steps below:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/bahmni-copilot.git
   cd bahmni-copilot
   ```

2. **Set up a Virtual Environment**:
   It's recommended to use a virtual environment to avoid conflicts with system packages.

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   Install the necessary Python dependencies.

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Set the following environment variables:
   - **`OPENAI_API_KEY`**: Your OpenAI API key for using transcription services.
   - **`S3_ENDPOINT_URL`**: The URL endpoint for connecting to the S3-compatible storage service. For local development, you can use services like MinIO (e.g., `http://localhost:9000`). In production, this would typically point to AWS S3 or another S3-compatible service.
   - **`S3_ACCESS_KEY_ID`**: The access key ID for authenticating with the S3 storage service. This is used in conjunction with the secret access key to securely access your S3 bucket.
   - **`S3_SECRET_ACCESS_KEY`**: The secret key associated with the access key ID, used for authenticating requests to the S3 storage service. This should be kept confidential.
   - **`S3_BUCKET_NAME`**: The name of the S3 bucket where audio files will be stored. Ensure the bucket exists and is properly configured to allow uploads and access from the application.
   - **`DATABASE_URL`**: The SQL Alchemy Database URL to connect to your preferred database.
   - **`JWT_SECRET_KEY`**: The secret key used to sign and verify JSON Web Tokens (JWTs) for authentication. 
   - **`JWT_REFRESH_SECRET_KEY`**: The secret key used to sign and verify refresh tokens for extending user sessions securely.

   You can either set these variables directly in your terminal or create a `.env` file for convenience.

5. **Database Setup**:
   Ensure your database is set up and migrate the models. Run the following commands to create the necessary tables:

   ```bash
   uvicorn app.main:app --reload
   ```

6. **Start the Application**:
   You can now start the FastAPI dev server:

   ```bash
   uvicorn app.main:app --reload
   ```

   The application will be available at `http://127.0.0.1:8000`.

## Project Structure

Here’s a quick overview of the project’s folder structure:

``` text
bahmni-copilot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   └── [routes].py  # Contains the endpoints for handling transcription-related tasks
│   │   ├── db/
│   │   │   └── database.py  # Database-related logic
│   │   ├── models/
│   │   │   └── [models].py  # SQLAlchemy models related to fields
│   │   ├── services/
│   │   │   └── [services].py  # Transcription service logic
│   │   ├── utils/
│   │   │   └── [utils].py  # Utility functions for file upload/download and OpenAI interaction
│   │   ├── schemas/
│   │   │   └── [schemas].py  # Pydantic schemas for data validation
│   │   ├── static/  # Static files directory
│   │   ├── main.py  # Entry point for the FastAPI app
│   │   ├── config.py  # Configuration for the app
│   ├── test/
│   │   ├── test_app.py  # Tests for app-level functionalities
│   │   ├── test_routes.py  # Tests for API routes
│   │   └── test_services.py  # Tests for service logic
│   └── requirements.txt  # Project dependencies
```

Here’s the updated structure with a section for APIs in the README:  

---

## APIs  

The Bahmni Copilot backend exposes a variety of endpoints to facilitate transcription and form management tasks. These APIs are well-documented and available via Swagger UI, which is automatically generated by FastAPI.  

You can access the **Swagger UI** at:  

```text
http://<host>:<port>/docs
```  

Alternatively, the **Redoc documentation** is available at:

```text
http://<host>:<port>/redoc
```  

## How it Works

1. **Audio Upload**: A user uploads an audio file to the system. The file is stored in an S3 bucket.
2. **Transcription**: The audio file is transcribed using OpenAI's Whisper API to generate a textual representation of the speech.
3. **Form Population**: The transcribed text is then parsed using NLP techniques, where relevant information is extracted and used to populate the fields of a form.
4. **Auto-Filled Form**: The user receives the fields mapped out based on their speech, significantly reducing the time spent on manual data entry.

## Future Enhancements

- **User Authentication**: Implement user authentication and authorization for secure access to forms and transcriptions.
