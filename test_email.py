"""
Email Testing Script for CTF Registration API
This script helps you test the email functionality without making API calls
"""

import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Import email functions from main.py
try:
    from main import (
        send_confirmation_email, 
        create_email_template_internal,
        create_email_template_external,
        SMTP_USERNAME,
        SMTP_PASSWORD
    )
except ImportError as e:
    print(f"❌ Error importing from main.py: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

def test_smtp_connection():
    """Test SMTP connection and credentials"""
    print("=" * 60)
    print("🔧 Testing SMTP Configuration")
    print("=" * 60)
    
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("❌ SMTP credentials not configured!")
        print("\nPlease add the following to your .env file:")
        print("SMTP_SERVER=smtp.gmail.com")
        print("SMTP_PORT=587")
        print("SMTP_USERNAME=your-email@gmail.com")
        print("SMTP_PASSWORD=your-app-password")
        print("SMTP_FROM_EMAIL=your-email@gmail.com")
        print("SMTP_FROM_NAME=CTF Registration Team")
        return False
    
    print(f"✓ SMTP Username: {SMTP_USERNAME}")
    print(f"✓ SMTP Password: {'*' * len(SMTP_PASSWORD)} (configured)")
    return True

def test_internal_email():
    """Test internal student email"""
    print("\n" + "=" * 60)
    print("📧 Testing Internal Student Email")
    print("=" * 60)
    
    # Get recipient email
    to_email = input("\nEnter recipient email address (or press Enter to use SMTP_USERNAME): ").strip()
    if not to_email:
        to_email = SMTP_USERNAME
    
    print(f"\n📬 Sending test email to: {to_email}")
    
    # Sample internal student data
    test_data = {
        'name': 'John Doe',
        'reg_no': '21ITR001',
        'division': 'A',
        'year_of_study': '3',
        'email': to_email,
        'phone_number': '+919876543210',
        'recipt_no': 'TXN_TEST_12345'
    }
    
    # Create email template
    html_content = create_email_template_internal(test_data)
    
    # Send email
    result = send_confirmation_email(
        to_email=to_email,
        subject="✅ CTF Registration Confirmed - Internal Participant [TEST]",
        html_content=html_content,
        student_name=test_data['name']
    )
    
    if result['success']:
        print("\n✅ Internal student email sent successfully!")
        print(f"📬 Check inbox: {to_email}")
        print("💡 Tip: Check spam folder if you don't see it")
    else:
        print(f"\n❌ Failed to send email: {result['message']}")
    
    return result['success']

def test_external_email():
    """Test external student email"""
    print("\n" + "=" * 60)
    print("📧 Testing External Student Email")
    print("=" * 60)
    
    # Get recipient email
    to_email = input("\nEnter recipient email address (or press Enter to use SMTP_USERNAME): ").strip()
    if not to_email:
        to_email = SMTP_USERNAME
    
    print(f"\n📬 Sending test email to: {to_email}")
    
    # Sample external student data
    test_data = {
        'name': 'Jane Smith',
        'reg_no': 'EXT001',
        'dept_name': 'Information Technology',
        'year_of_study': '2',
        'college_name': 'ABC Engineering College',
        'email': to_email,
        'phone_number': '+919123456789',
        'recipt_no': 'TXN_TEST_67890'
    }
    
    # Create email template
    html_content = create_email_template_external(test_data)
    
    # Send email
    result = send_confirmation_email(
        to_email=to_email,
        subject="✅ CTF Registration Confirmed - External Participant [TEST]",
        html_content=html_content,
        student_name=test_data['name']
    )
    
    if result['success']:
        print("\n✅ External student email sent successfully!")
        print(f"📬 Check inbox: {to_email}")
        print("💡 Tip: Check spam folder if you don't see it")
    else:
        print(f"\n❌ Failed to send email: {result['message']}")
    
    return result['success']

def save_template_preview():
    """Save HTML templates to files for preview"""
    print("\n" + "=" * 60)
    print("💾 Saving Email Template Previews")
    print("=" * 60)
    
    # Internal template
    internal_data = {
        'name': 'John Doe',
        'reg_no': '21ITR001',
        'division': 'A',
        'year_of_study': '3',
        'email': 'john.doe@example.com',
        'phone_number': '+919876543210',
        'recipt_no': 'TXN123456789'
    }
    
    internal_html = create_email_template_internal(internal_data)
    with open('email_template_internal_preview.html', 'w', encoding='utf-8') as f:
        f.write(internal_html)
    print("✓ Saved: email_template_internal_preview.html")
    
    # External template
    external_data = {
        'name': 'Jane Smith',
        'reg_no': 'EXT001',
        'dept_name': 'Information Technology',
        'year_of_study': '2',
        'college_name': 'ABC Engineering College',
        'email': 'jane.smith@example.com',
        'phone_number': '+919123456789',
        'recipt_no': 'TXN987654321'
    }
    
    external_html = create_email_template_external(external_data)
    with open('email_template_external_preview.html', 'w', encoding='utf-8') as f:
        f.write(external_html)
    print("✓ Saved: email_template_external_preview.html")
    
    print("\n💡 Open these HTML files in your browser to preview the email templates!")

def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("📧 CTF Registration Email Testing Tool")
    print("=" * 60)
    
    # Test SMTP configuration
    if not test_smtp_connection():
        print("\n⚠️  Please configure SMTP settings in .env file first.")
        print("See EMAIL_SETUP.md for detailed instructions.")
        return
    
    # Menu
    while True:
        print("\n" + "=" * 60)
        print("Choose an option:")
        print("=" * 60)
        print("1. Test Internal Student Email")
        print("2. Test External Student Email")
        print("3. Test Both Emails")
        print("4. Save Template Previews (HTML files)")
        print("5. Exit")
        print("=" * 60)
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            test_internal_email()
        elif choice == '2':
            test_external_email()
        elif choice == '3':
            test_internal_email()
            test_external_email()
        elif choice == '4':
            save_template_preview()
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1-5.")
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
