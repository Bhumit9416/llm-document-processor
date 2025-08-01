import os
import email.message
import email.policy
import email.utils
import datetime

def create_sample_email():
    """Create a sample email document with insurance policy information"""
    # Create email message
    msg = email.message.EmailMessage(policy=email.policy.default)
    
    # Set email headers
    msg['Subject'] = 'National Parivar Mediclaim Plus Policy - Important Information'
    msg['From'] = 'insurance@example.com'
    msg['To'] = 'policyholder@example.com'
    msg['Date'] = email.utils.formatdate(localtime=True)
    msg['Message-ID'] = email.utils.make_msgid(domain='example.com')
    
    # Email content
    content = """\
Dear Policyholder,

Thank you for choosing our National Parivar Mediclaim Plus Policy. This email contains important information about your policy coverage and benefits.

**POLICY DETAILS**

**Policy Number:** NPM-12345678
**Policy Period:** 01-Jan-2023 to 31-Dec-2023
**Sum Insured:** ₹500,000
**Plan:** Plan A

**KEY POLICY FEATURES**

1. **Hospitalization Coverage:**
   Your policy covers medical expenses incurred for hospitalization during the policy year, up to the Sum Insured and Cumulative Bonus specified in your policy schedule.

2. **AYUSH Treatment:**
   Your policy covers medical expenses for inpatient care treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems of medicines up to the limit of sum insured as specified in your policy schedule in any AYUSH Hospital.

3. **Maternity Expenses:**
   Your policy covers maternity expenses incurred for the delivery of a child and/or expenses related to medically necessary and lawful termination of pregnancy, subject to the following conditions:
   - The female insured person must have been continuously covered for at least 24 months.
   - This benefit is limited to two deliveries or terminations during the lifetime of the female insured person.

4. **Organ Donor Expenses:**
   Your policy covers medical expenses incurred towards in-patient hospitalization of an organ donor for harvesting the organ, provided that:
   - The organ donor is any person whose organ has been made available in accordance with the Transplantation of Human Organs Act 1994.
   - The Company has accepted an inpatient Hospitalization claim for the insured member under the policy.

**IMPORTANT WAITING PERIODS**

1. **Pre-Existing Diseases:**
   All Pre-Existing Diseases and their direct complications shall not be covered until 36 months of continuous coverage have elapsed since inception of the first policy with the Company.

2. **Specific Waiting Periods:**
   - 24 months: For specified conditions including benign ENT disorders, hysterectomy, hernia, etc.
   - 24 months: For joint replacement treatments unless arising from accident.
   - 24 months: For cataract surgery.

**GENERAL CONDITIONS**

1. **Grace Period:**
   A grace period of thirty days is allowed following the expiry of the policy period to maintain continuity of coverage. No coverage is available during the grace period.

2. **No Claim Discount:**
   You are entitled to a No Claim Discount of 5% on the base premium, on renewal of a claim-free policy, for a one-year policy term. The aggregate discount shall not exceed 5% of the total base premium.

3. **Preventive Health Check-up:**
   Expenses incurred for preventive health check-up will be reimbursed at the end of a block of two continuous policy years, subject to a maximum of the amount specified in the Table of Benefits.

4. **Room Rent Capping:**
   For Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN).

Please review your policy document for complete terms, conditions, and exclusions. If you have any questions or need assistance, please contact our customer service at 1800-XXX-XXXX or email us at support@example.com.

Thank you for your trust in our services.

Best regards,
Customer Service Team
National Insurance Company

This is an automated email. Please do not reply to this message.

DISCLAIMER: This email and any files transmitted with it are confidential and intended solely for the use of the individual or entity to whom they are addressed.
"""
    
    # Set email content
    msg.set_content(content)
    
    # Save the email
    output_dir = "data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, "sample_policy_email.eml")
    
    with open(output_path, 'w') as f:
        f.write(msg.as_string())
    
    print(f"Sample email created at: {output_path}")
    return output_path

def main():
    """Main function to create sample email document"""
    print("=== Generating Sample Email Document ===")
    
    # Create sample email
    email_path = create_sample_email()
    
    print("\nSample email document generated successfully!")
    print(f"Email: {email_path}")

if __name__ == "__main__":
    main()