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
