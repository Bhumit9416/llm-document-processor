import os
import sys
import subprocess

def check_and_install_dependencies():
    """Check and install required dependencies"""
    required_packages = [
        "fpdf",
        "python-docx",
        "pandas"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} is already installed")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")

def run_script(script_name):
    """Run a Python script and handle errors"""
    print(f"\nRunning {script_name}...")
    try:
        subprocess.run([sys.executable, script_name], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        return False

def create_csv_sample():
    """Create a sample CSV file with policy data"""
    import pandas as pd
    
    # Create data for the CSV
    data = {
        'Policy_ID': ['NPM001', 'NPM002', 'NPM003', 'NPM004', 'NPM005'],
        'Policyholder_Name': ['John Doe', 'Jane Smith', 'Robert Johnson', 'Emily Davis', 'Michael Brown'],
        'Age': [35, 42, 28, 50, 33],
        'Gender': ['Male', 'Female', 'Male', 'Female', 'Male'],
        'Sum_Insured': [500000, 1000000, 300000, 750000, 500000],
        'Plan_Type': ['Plan A', 'Plan B', 'Plan A', 'Plan C', 'Plan B'],
        'Start_Date': ['2023-01-01', '2023-02-15', '2023-03-10', '2023-01-20', '2023-04-05'],
        'End_Date': ['2024-01-01', '2024-02-15', '2024-03-10', '2024-01-20', '2024-04-05'],
        'Premium': [12500, 25000, 7500, 18750, 12500],
        'No_Claim_Bonus': ['5%', '0%', '5%', '0%', '5%'],
        'Waiting_Period_PED': ['36 months', '36 months', '36 months', '36 months', '36 months'],
        'Waiting_Period_Specific': ['24 months', '24 months', '24 months', '24 months', '24 months'],
        'Room_Rent_Cap': ['1% of SI', '2% of SI', '1% of SI', 'No Cap', '2% of SI'],
        'ICU_Cap': ['2% of SI', '4% of SI', '2% of SI', 'No Cap', '4% of SI']
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    output_dir = "data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, "sample_policies.csv")
    df.to_csv(output_path, index=False)
    
    print(f"Sample CSV created at: {output_path}")
    return output_path

def create_json_sample():
    """Create a sample JSON file with policy data"""
    import json
    
    # Create data for the JSON
    data = {
        "policies": [
            {
                "policy_id": "NPM001",
                "policyholder": {
                    "name": "John Doe",
                    "age": 35,
                    "gender": "Male",
                    "contact": {
                        "email": "john.doe@example.com",
                        "phone": "+91-9876543210"
                    }
                },
                "policy_details": {
                    "plan_type": "Plan A",
                    "sum_insured": 500000,
                    "premium": 12500,
                    "start_date": "2023-01-01",
                    "end_date": "2024-01-01",
                    "no_claim_bonus": "5%"
                },
                "coverage": {
                    "hospitalization": True,
                    "ayush_treatment": True,
                    "maternity": True,
                    "organ_donor": True,
                    "day_care": True,
                    "domiciliary": False
                },
                "waiting_periods": {
                    "pre_existing_diseases": "36 months",
                    "specific_conditions": "24 months",
                    "maternity": "24 months",
                    "cataract": "24 months"
                },
                "sub_limits": {
                    "room_rent": "1% of Sum Insured",
                    "icu": "2% of Sum Insured",
                    "cataract": "10% of Sum Insured",
                    "specified_diseases": "25% of Sum Insured"
                }
            },
            {
                "policy_id": "NPM002",
                "policyholder": {
                    "name": "Jane Smith",
                    "age": 42,
                    "gender": "Female",
                    "contact": {
                        "email": "jane.smith@example.com",
                        "phone": "+91-9876543211"
                    }
                },
                "policy_details": {
                    "plan_type": "Plan B",
                    "sum_insured": 1000000,
                    "premium": 25000,
                    "start_date": "2023-02-15",
                    "end_date": "2024-02-15",
                    "no_claim_bonus": "0%"
                },
                "coverage": {
                    "hospitalization": True,
                    "ayush_treatment": True,
                    "maternity": True,
                    "organ_donor": True,
                    "day_care": True,
                    "domiciliary": True
                },
                "waiting_periods": {
                    "pre_existing_diseases": "36 months",
                    "specific_conditions": "24 months",
                    "maternity": "24 months",
                    "cataract": "24 months"
                },
                "sub_limits": {
                    "room_rent": "2% of Sum Insured",
                    "icu": "4% of Sum Insured",
                    "cataract": "15% of Sum Insured",
                    "specified_diseases": "30% of Sum Insured"
                }
            }
        ],
        "definitions": {
            "hospital": "An institution established for in-patient care and day care treatment of illness and/or injuries and which has been registered as a hospital with the local authorities under Clinical Establishments (Registration and Regulation) Act 2010 or under enactments specified under the Schedule of Section 56(1) and the said act Or complies with all minimum criteria as under: has qualified nursing staff under its employment round the clock; has at least 10 in-patient beds in towns having a population of less than 10,00,000 and at least 15 in-patient beds in all other places; has qualified medical practitioner(s) in charge round the clock; has a fully equipped operation theatre of its own where surgical procedures are carried out; maintains daily records of patients and makes these accessible to the insurance company's authorized personnel.",
            "ayush_hospital": "A healthcare facility wherein medical/surgical/para-surgical treatment procedures and interventions are carried out by AYUSH Medical Practitioner(s) comprising of any of the following: Central or State Government AYUSH Hospital; or Teaching hospital attached to AYUSH College recognized by the Central Government/Central Council of Indian Medicine/Central Council for Homeopathy; or AYUSH Hospital, standalone or co-located with in-patient healthcare facility of any recognized system of medicine, registered with the local authorities, wherever applicable, and is under the supervision of a qualified registered AYUSH Medical Practitioner and must comply with the following criteria: Having at least 5 in-patient beds; Having qualified AYUSH Medical Practitioner in charge round the clock; Having dedicated AYUSH therapy sections as required and/or has equipped operation theatre where surgical procedures are to be carried out; Maintaining daily records of the patients and making them accessible to the insurance company's authorized representative.",
            "pre_existing_disease": "Any condition, ailment, injury or disease: a) That is/are diagnosed by a physician within 48 months prior to the effective date of the policy issued by the insurer or its reinstatement or b) For which medical advice or treatment was recommended by, or received from, a physician within 48 months prior to the effective date of the policy issued by the insurer or its reinstatement."
        },
        "general_conditions": {
            "grace_period": "A grace period of thirty days is allowed following the expiry of the policy period to maintain continuity of coverage. No coverage is available during the grace period. However, no coverage is available for expenses incurred during the break period.",
            "no_claim_discount": "The insured shall be entitled for a No Claim Discount of 5% on the base premium, on renewal of a claim free policy, for a one-year policy term. The aggregate of such discount shall not exceed 5% of the total base premium.",
            "preventive_health_checkup": "Expenses incurred for preventive health check-up will be reimbursed at the end of a block of two continuous policy years, subject to a maximum of the amount specified in the Table of Benefits, provided no claims have been made during this period and the policy has been renewed without a break."
        }
    }
    
    # Save to JSON
    output_dir = "data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, "sample_policies.json")
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Sample JSON created at: {output_path}")
    return output_path

def main():
    """Main function to generate all sample documents"""
    print("=== Generating All Sample Documents ===")
    
    # Check and install dependencies
    check_and_install_dependencies()
    
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
        print("Created data directory")
    
    # Run sample generation scripts
    scripts = [
        "generate_sample_pdf.py",
        "generate_sample_docx.py",
        "generate_sample_email.py"
    ]
    
    success_count = 0
    for script in scripts:
        if run_script(script):
            success_count += 1
    
    # Create CSV and JSON samples
    print("\nGenerating CSV sample...")
    csv_path = create_csv_sample()
    
    print("\nGenerating JSON sample...")
    json_path = create_json_sample()
    
    # Summary
    print("\n=== Sample Generation Summary ===")
    print(f"Successfully generated {success_count}/{len(scripts)} script-based samples")
    print(f"CSV sample: {csv_path}")
    print(f"JSON sample: {json_path}")
    print("\nAll sample documents have been generated in the 'data' directory.")

if __name__ == "__main__":
    main()