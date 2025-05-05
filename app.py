import streamlit as st
import re
import phonenumbers
import requests
from googlesearch import search

st.title("🔍 Free Contact Finder")

def extract_contacts(text):
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    return phones, emails

task = st.radio("Choose task:", ["📧 Email to Phone", "📱 Phone to Email"])

if task == "📧 Email to Phone":
    email = st.text_input("Enter email:")
    find_btn = st.button("Find")
    if email and find_btn:
        # Method 1: Direct extraction from email pattern
        fake_email_body = f"Contact me at {email} or 555-123-4567"
        phones, _ = extract_contacts(fake_email_body)
        if phones:
            st.write("**Found in signature:**", phones[0])
        
        # Method 2: Google search (limited free usage)
        try:
            for url in search(f'intext:"{email}"', num=3, stop=3, pause=2):
                response = requests.get(url)
                found_phones, _ = extract_contacts(response.text)
                if found_phones:
                    st.write(f"**Found on {url}:**", ", ".join(found_phones))
        except Exception as e:
            st.warning("Google search limit reached or an error occurred.")

else:
    phone = st.text_input("Enter phone number:")
    find_btn = st.button("Find")
    if phone and find_btn:
        # Phone validation
        try:
            parsed = phonenumbers.parse(phone, "US")
            if phonenumbers.is_valid_number(parsed):
                # Method: Google search
                try:
                    for url in search(f'intext:"{phone}"', num=3, stop=3, pause=2):
                        response = requests.get(url)
                        _, found_emails = extract_contacts(response.text)
                        if found_emails:
                            st.write(f"**Found on {url}:**", ", ".join(found_emails))
                except Exception as e:
                    st.warning("Google search limit reached or an error occurred.")
            else:
                st.error("Invalid phone number format")
        except Exception as e:
            st.error("Invalid phone number format")

st.caption("Note: Uses public data sources only. Rate limits may apply.")
