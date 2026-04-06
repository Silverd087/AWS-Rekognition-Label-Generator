# 🚀 Serverless AI Image Labeling Pipeline

A production-ready, event-driven cloud pipeline that automatically detects objects in images, annotates them with high-contrast bounding boxes, and indexes metadata for search. Built with **Python 3.14** and **AWS**.

---

## 📌 Project Overview
This project automates image metadata extraction and visual annotation. When a user uploads a raw image to an S3 bucket, a Lambda function is triggered to:
1. Analyze the image using **Amazon Rekognition**.
2. Draw pixel-perfect bounding boxes using **Pillow**.
3. Store sanitized metadata in **Amazon DynamoDB**.
4. Notify the developer via **Amazon SNS** if any processing errors occur.

### 🏗️ Architecture


1. **Trigger:** S3 Bucket (`s3:ObjectCreated:*` event).
2. **Compute:** AWS Lambda (Python 3.14).
3. **AI Service:** Amazon Rekognition (Object & Instance Detection).
4. **Processing:** Pillow (PIL) for dynamic image annotation.
5. **Database:** Amazon DynamoDB (NoSQL) for metadata persistence.
6. **Monitoring:** Amazon SNS for real-time error alerting.

---

## 🛠️ Tech Stack
* **Language:** Python 3.14
* **Cloud Provider:** Amazon Web Services (AWS)
* **SDK:** Boto3
* **Libraries:** Pillow (PIL), Decimal, IO, JSON.

---

## 🚀 Key Features
* **Event-Driven & Scalable:** Zero server management; scales instantly with upload volume.
* **Smart Annotation:** Dynamically scales font sizes and bounding boxes based on image resolution (4K vs. 720p).
* **Data Integrity:** Implements a recursive `float_to_decimal` helper to handle AWS Rekognition's float outputs for DynamoDB compatibility.
* **Observability:** Integrated `try-except` blocks with SNS publishing for instant "Pipeline Failure" alerts.

---

## 🔧 Setup & Infrastructure

### 1. Lambda Layer
This project utilizes the **Pillow** library as a Lambda Layer. 
* To build the layer compatible with the AWS Linux environment:
  ```bash
  pip install --platform manylinux2014_x86_64 --target=python pillow