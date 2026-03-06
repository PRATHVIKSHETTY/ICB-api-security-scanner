API Security Scanner with Chatbot Assistant
Project Overview

Modern applications rely heavily on Application Programming Interfaces (APIs) to exchange data between systems. However, poorly secured APIs can expose sensitive information and create vulnerabilities that attackers can exploit.

This project develops a web-based API Security Scanner integrated with a chatbot assistant that helps identify potential security vulnerabilities in APIs and provides guidance on how to fix them.

The system allows users to enter an API endpoint URL, after which the scanner analyzes the endpoint for common security issues such as missing authentication, insecure headers, exposed data, and improper HTTP methods. The tool then generates a security report highlighting detected vulnerabilities.

Additionally, a chatbot interface explains the detected vulnerabilities and provides recommendations for improving API security.

Features

Scan API endpoints for basic security vulnerabilities
Detect issues such as:
  Missing authentication
  Missing security headers
  Exposed data
  Improper HTTP methods  
Generate a vulnerability report
Interactive chatbot assistant for explaining vulnerabilities
Simple web-based dashboard

Tech Stack:

Backend
Python
Flask
Requests Library

Frontend
HTML
CSS
JavaScript

Other Tools
Git
GitHub
VS Code

Project Structure
api-security-scanner/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── scanner/
│   ├── __init__.py
│   ├── api_scanner.py
│   └── checks.py
│
├── chatbot/
│   ├── __init__.py
│   └── chatbot.py
│
├── templates/
│   ├── index.html
│   ├── result.html
│   └── chatbot.html
│
├── static/
│   ├── css/style.css
│   ├── js/chatbot.js
│   └── images/
│
├── reports/
│   └── sample_report.json
│
└── docs/
    └── architecture.md
