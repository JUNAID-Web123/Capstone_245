**AI Tool for Preliminary Diagnosis of Dermatological Manifestations**


**📋 Project Overview**

This project is a web-based application designed to assist in the preliminary triage of skin conditions using Artificial Intelligence. Built with Flask and powered by Google's Gemini 2.5 Flash model, the tool analyzes user-uploaded images or live camera captures to provide a potential condition identification, along with causes, precautions, and awareness-level treatment options.

⚠️ Medical Disclaimer: > This tool is for educational and preliminary triage purposes only. It provides non-diagnostic insights and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a licensed dermatologist for clinical care.

**✨ Key Features**

AI-Powered Analysis: Utilizes the gemini-2.5-flash model to analyze skin lesions with high speed and accuracy.

Structured Output: Delivers clear results including:

Potential Disease Name

Primary Causes

Precautions

Suggested Treatments (Tablets/Creams - for awareness only)

Dual Input Modes: * Upload existing images (PNG, JPEG).

Real-time camera capture via the browser.

User Management: Secure Login and Registration system using persistent JSON storage (users.json).

History Tracking: Automatically saves previous analyses for users to review later.

Responsive UI: A modern, medical-themed interface compatible with mobile and desktop devices.

**🛠️ Tech Stack**

Backend: Python, Flask

AI Model: Google GenAI (Gemini 2.5 Flash)

Image Processing: Pillow (PIL)

Frontend: HTML5, CSS3, JavaScript (Vanilla)

Data Storage: Local JSON file (users.json)

⚙️ Prerequisites
Before running the application, ensure you have the following:

Python 3.8+ installed.

A valid Google Gemini API Key (Get one at Google AI Studio).

🚀 Installation & Setup
Clone or Download the Code Save the provided Python code into a file named app.py.

Install Dependencies Open your terminal/command prompt and run:

Bash

pip install flask pillow google-genai
Set Up Environment Variables You need to configure your API key. You can do this in your terminal before running the app:

Windows (Command Prompt):

DOS

set GEMINI_API_KEY=your_actual_api_key_here
Mac/Linux:

Bash

export GEMINI_API_KEY="your_actual_api_key_here"
(Alternatively, for testing, you can paste the key directly into the GEMINI_API_KEY variable in app.py, though this is not recommended for security).

Run the Application

Bash

python app.py
Access the Application Open your web browser and go to: http://127.0.0.1:5000

📖 Usage Guide
Register: Click "Sign Up" on the login screen to create a new account.

Login: Use your new credentials to access the dashboard.

Upload/Capture: * Click "Choose File" to upload an image from your device.

Click "Open Camera" to take a live photo.

Analyze: Click the "Analyze" button. The AI will process the image and display the results below.

View History: Click the "History" button in the top navigation bar to see your past scans.

📂 Project Structure
Main_Folder/ app.py
Templates Folder under main Folder/ login.html , signup.html , app.html 
🛡️ Security & Privacy
Data Storage: User credentials and history are stored locally in users.json.

Session Security: The app uses a session secret key. For production environments, ensure you set a persistent FLASK_SECRET_KEY environment variable.

<img width="553" height="557" alt="Screenshot 2025-11-17 192952" src="https://github.com/user-attachments/assets/a3ef1c58-a10d-448d-a8a2-32a09cf0fe1d" />
<img width="589" height="595" alt="Screenshot 2025-11-17 193012" src="https://github.com/user-attachments/assets/7c680bfc-9fda-4235-a4db-7624f67367bf" />
<img width="1910" height="920" alt="Screenshot 2025-11-17 193153" src="https://github.com/user-attachments/assets/a7be5b85-5f6a-478e-8473-c872cfaa3b1c" />
<img width="1918" height="1018" alt="Screenshot 2025-11-17 193212" src="https://github.com/user-attachments/assets/daeccbdd-e46a-4c90-bbe1-8305d64c6fa6" />
<img width="1909" height="920" alt="Screenshot 2025-11-17 193244" src="https://github.com/user-attachments/assets/0b1cb395-6907-4089-8533-d69ce6221b2a" />
<img width="1893" height="912" alt="Screenshot 2025-11-17 224547" src="https://github.com/user-attachments/assets/238ef461-ffe9-48df-ad30-dd0102fbb134" />
<img width="1900" height="914" alt="Screenshot 2025-11-17 224713" src="https://github.com/user-attachments/assets/71402417-a48e-4d21-b186-c4dab9109742" />
<img width="1900" height="916" alt="Screenshot 2025-11-17 224810" src="https://github.com/user-attachments/assets/dc1b2659-cd80-41b6-b9d0-f88713ab2562" />
<img width="1919" height="910" alt="Screenshot 2025-11-17 224844" src="https://github.com/user-attachments/assets/428d0a0a-06b3-4c22-945b-74386fce611e" />








