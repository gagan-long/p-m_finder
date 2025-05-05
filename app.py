import streamlit as st
import re
import phonenumbers
import requests
from googlesearch import search
from bs4 import BeautifulSoup

st.set_page_config(page_title="Free Contact Finder", page_icon="🔍")
st.title("🔍 Free Contact Finder")

def extract_contacts(text):
    phones = set(re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))
    emails = set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
    return phones, emails

def validate_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None

def validate_phone(phone):
    try:
        parsed = phonenumbers.parse(phone, "US")
        return phonenumbers.is_valid_number(parsed)
    except:
        return False

def get_visible_text(html):
    soup = BeautifulSoup(html, "html.parser")
    # Remove scripts and styles
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator=" ", strip=True)

task = st.radio("Choose task:", ["📧 Email to Phone", "📱 Phone to Email"])

with st.form("contact_form"):
    if task == "📧 Email to Phone":
        email = st.text_input("Enter email:", placeholder="e.g. john.doe@example.com")
        submitted = st.form_submit_button("Find")
        if submitted:
            if not validate_email(email):
                st.error("Please enter a valid email address.")
            else:
                # Simulate signature extraction
                fake_email_body = f"Contact me at {email} or 555-123-4567"
                phones, _ = extract_contacts(fake_email_body)
                if phones:
                    st.success(f"Found in signature: {', '.join(phones)}")
                # Google search
                found_phones = set()
                with st.spinner("Searching the web..."):
                    try:
                        for url in search(f'intext:"{email}"', num=3, stop=3, pause=2):
                            try:
                                response = requests.get(url, timeout=8)
                                visible_text = get_visible_text(response.text)
                                phones, _ = extract_contacts(visible_text)
                                if phones:
                                    found_phones.update(phones)
                                    st.info(f"Found on {url}: {', '.join(phones)}")
                            except Exception:
                                st.warning(f"Could not access {url}")
                        if not found_phones:
                            st.info("No phone numbers found for this email in public sources.")
                    except Exception:
                        st.warning("Google search limit reached or an error occurred.")
    else:
        phone = st.text_input("Enter phone number:", placeholder="e.g. +1 555-123-4567 or 5551234567")
        submitted = st.form_submit_button("Find")
        if submitted:
            if not validate_phone(phone):
                st.error("Please enter a valid US phone number.")
            else:
                found_emails = set()
                with st.spinner("Searching the web..."):
                    try:
                        for url in search(f'intext:"{phone}"', num=3, stop=3, pause=2):
                            try:
                                response = requests.get(url, timeout=8)
                                visible_text = get_visible_text(response.text)
                                _, emails = extract_contacts(visible_text)
                                if emails:
                                    found_emails.update(emails)
                                    st.info(f"Found on {url}: {', '.join(emails)}")
                            except Exception:
                                st.warning(f"Could not access {url}")
                        if not found_emails:
                            st.info("No emails found for this phone number in public sources.")
                    except Exception:
                        st.warning("Google search limit reached or an error occurred.")

st.caption("Note: Uses public data sources only. Rate limits may apply. For best results, use well-known emails or phone numbers.")
