# CSV Data Cleaner for Finances

**DS4300 Final Project**
**Team Members:** Lily, Heidi, Mihalis, and Maya

This project allows users to upload raw financial CSV files (e.g., containing `Name`, `Age`, `Checking Account Balance`, etc.). It detects and removes faulty or missing entries, stores the cleaned version, and provides interactive graphs to visualize relationships within the data.


## Core Features

- **CSV Upload**: Users upload CSVs with financial data
- **Data Cleaning**: Automatically removes rows with missing or erroneous values
- **Graphical Insights**: Visualizations using `pandas`, `NumPy`, `matplotlib`
- **User Data Display**: Showcases cleaned user data attributes



## AWS Architecture

- **S3 (Simple Storage Service)**  
  - One bucket for raw CSV uploads  
  - One bucket for cleaned CSV files  

- **Lambda**  
  - Triggered on CSV upload  
  - Cleans data and stores results in the cleaned S3 bucket  

- **RDS (Relational Database Service)**  
  - Stores parsed and cleaned attributes (e.g., `Name`, `Age`, `Balance`)  

- **EC2 (Elastic Compute Cloud)**  
  - Hosts a Streamlit web app  
  - Displays cleaned user data and generates visual insights  


## Project Goals

- Build a robust pipeline for financial CSV processing  
- Automatically clean and validate user-uploaded data  
- Prevent faulty data from crashing the system  
- Provide clean UI and insightful visualizations of user balances and trends  


## Requirements

- Python 3.11
- AWS account with S3 and RDS access
- Required Python packages (see requirements.txt)

---

## AWS Setup Instructions

Idk how in depth we should be here.
1. Create S3 Bucket
2. Create IAM User and Policy

## Project Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your AWS credentials:
   ```bash
   cp .env.example .env
   ```
4. Edit the `.env` file with your AWS credentials:
   ```
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_REGION=your_aws_region
   S3_BUCKET_NAME=your_bucket_name
   ```
5. Update the configuration variables

## Usage

Run the script:

```bash
python streamlit run src/app/Home.py --server.port 8501 --server.enableCORS false --server.enableXsrfProtection false --server.address 0.0.0.0
```


## Security Notes

- Never commit your `.env` file to version control
- Keep your AWS credentials secure
- Use appropriate IAM roles and permissions for S3 access