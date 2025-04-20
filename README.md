#  AI-Powered Genomic Vulnerability Detection Pipeline 

GenoSense is a robust, AI-driven genomics platform designed to streamline the flow of genetic data between **hospitals**, **labs**, and **AI-powered analysis systems**. It enables early disease detection, prediction of genetic vulnerabilities, and geographic visualization of common disease trends — all while maintaining strict data privacy through **encryption**.

---

<a href="https://hack36.in"> 
  <img src="https://postimage.me/images/2025/04/19/built-at-hack36.png" height=24px> 
</a>


## Demo Video Link:
  <a href="#"></a>

  
## Presentation Link:
  <a href="https://www.canva.com/design/DAGlH2Ah5gU/YPzuAiYTL-rNtACJoFef6w/edit?utm_content=DAGlH2Ah5gU&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton"> PPT link here </a>

  
## 🚀 Project Overview

This platform facilitates a complete pipeline for genomics-based healthcare prediction and disease mapping:

1. **Hospital Data Submission**: Hospitals securely submit patient sample data to the system.
2. **Laboratory Processing**: Labs receive sample requests and perform DNA sequencing.
3. **Variant Generation**: Sequenced DNA is compared with the Human Genome Reference to extract genetic **variants (VCF format)**.
4. **AI Vulnerability Analysis**: The system uses a **Hugging Face LLaMA model** to analyze variants and predict possible **health vulnerabilities**.
5. **Human Insight Rendering**: Predictions are interpreted and displayed in an easy-to-understand human-readable format.
6. **Geographic Disease Mapping**: The system tracks **common genetic conditions** in **nearby regions** and displays them on an interactive map.
7. **End-to-End Encryption**: All sensitive information (patient identity, DNA data, medical history) is **encrypted** during transit and storage.

---

## 🏥 Hospital Dashboard

- Submit patient samples to certified labs.
- Track lab request status.
- View AI-generated health risk predictions.
- Explore local disease hotspots based on genomic data.

---

## 🧪 Lab Dashboard

- Accept or reject sequencing requests from hospitals.
- Upload DNA sequence data and generate VCF variant files.
- Monitor sample analytics and report predictions back to the hospital.
- Collaborate with AI models for high-accuracy genome analysis.

---

## 🌍 Disease Hotspot Mapping

- Aggregates anonymized predictions from various hospitals/labs.
- Displays regions with high frequency of certain genetic vulnerabilities.
- Helps in identifying and preparing for possible **public health concerns**.

---

## 🔒 Data Privacy & Encryption

- All sample and patient data is **encrypted end-to-end** using secure cryptographic protocols.
- No raw DNA or personal identity is exposed during AI processing.
- Role-based access control ensures **only authorized hospitals and labs** interact with relevant data.

---

## 🧠 AI Model

- Built using a fine-tuned **LLaMA model from Hugging Face**.
- Accepts VCF variant details and returns **interpretable medical insights**.
- Designed to aid genetic counselors, doctors, and patients in understanding potential **health risks**.

---

## 📁 Sample Workflow

```mermaid
graph LR
A[Hospital] -->|Sample Sent| B[Lab]
B -->|DNA Sequencing| C[Generate VCF]
C --> D[AI Model: Predict Vulnerabilities]
D --> E[Hospital Receives Report]
D --> F[Map Common Vulnerabilities on Human Body and also marking common disease of a particular region on map]
```

## Technology Stack:
  1) Frontend : Swelt
  2) Backend : Go
  3) Machine Learning : Flask , Python 
  

## Contributors:

Team Name: CodeNhiAta

- [Vaishnavi Tiwari](https://github.com/Vaishnavi1047)
- [Shourya Mishra](https://github.com/ShouryaMishra2006)
- [Anurag Mishra](https://github.com/theAnuragMishra)
- [Naman Agarwal](https://github.com/NamanAgarwal0905)


### Made at:
<a href="https://hack36.in"> <img src="https://postimage.me/images/2025/04/19/built-at-hack36.png" height=24px> </a>
