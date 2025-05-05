import streamlit as st
import re
import phonenumbers
import requests
from googlesearch import search
from bs4 import BeautifulSoup

st.set_page_config(page_title="Free Contact Finder", page_icon="🔍")
st.title("🔍 Free Contact Finder")

st.markdown("""
This tool helps you find **phone numbers associated with an email**, **emails linked to a phone number**, and **social media profiles** using public web sources and advanced Google dorking.
""")

def extract_phones(text):
    phone_pattern = r"(\+?\d{1,3}[\s\-\.]?)?\(?\d{2,4}\)?[\s\-\.]?\d{3,5}[\s\-\.]?\d{3,5}"
    raw_phones = re.findall(phone_pattern, text)
    phones = set()
    for match in raw_phones:
        try:
            for p in phonenumbers.PhoneNumberMatcher(match, None):
                phones.add(phonenumbers.format_number(p.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
        except:
            continue
    return phones

def extract_emails(text):
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    return set(re.findall(email_pattern, text))

def extract_social_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = [a['href'] for a in soup.find_all('a', href=True)]
    social_patterns = {
        'Facebook': r'facebook\.com/[^/]+',
        'Twitter': r'twitter\.com/[^/]+',
        'Instagram': r'instagram\.com/[^/]+',
        'LinkedIn': r'linkedin\.com/in/[^/]+',
        'GitHub': r'github\.com/[^/]+'
    }
    social_links = {platform: set() for platform in social_patterns}
    for link in links:
        for platform, pattern in social_patterns.items():
            if re.search(pattern, link, re.IGNORECASE):
                social_links[platform].add(link)
    return {k: v for k, v in social_links.items() if v}

def validate_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None

def validate_phone(phone):
    try:
        parsed = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(parsed)
    except:
        return False

def get_visible_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator=" ", strip=True)

def build_search_queries(mode, value):
    # Google dorks for more accurate and targeted search
    queries = []
    if mode == "email":
        queries = [
            f'intext:"{value}"',
            f'"{value}" filetype:pdf',
            f'"{value}" site:linkedin.com',
            f'"{value}" site:facebook.com',
            f'inurl:contact intext:"{value}"',
            f'intext:"{value}" AND ("phone" OR "contact" OR "mobile")'
        ]
    else:  # phone
        queries = [
            f'intext:"{value}"',
            f'"{value}" filetype:pdf',
            f'"{value}" site:linkedin.com',
            f'"{value}" site:facebook.com',
            f'inurl:contact intext:"{value}"',
            f'intext:"{value}" AND ("email" OR "contact" OR "mail")'
        ]
    return queries

task = st.radio("Choose task:", ["📧 Email to Phone", "📱 Phone to Email"])

with st.form("contact_form"):
    num_results = st.slider("Number of web results to search per query", min_value=2, max_value=10, value=3)
    if task == "📧 Email to Phone":
        email = st.text_input("Enter email:", placeholder="e.g. john.doe@example.com")
        submitted = st.form_submit_button("Find")
        if submitted:
            if not validate_email(email):
                st.error("Please enter a valid email address (e.g. john.doe@example.com).")
            else:
                st.info("Searching for phone numbers and social profiles linked to this email using advanced Google dorks...")
                found_phones = set()
                found_socials = {}
                queries = build_search_queries("email", email)
                with st.spinner("Searching the web with multiple techniques..."):
                    try:
                        for q in queries:
                            for url in search(q, num=num_results, stop=num_results, pause=2):
                                try:
                                    response = requests.get(url, timeout=8)
                                    visible_text = get_visible_text(response.text)
                                    phones = extract_phones(visible_text)
                                    socials = extract_social_links(response.text)
                                    if phones:
                                        found_phones.update(phones)
                                        st.write(f"**Found on {url}:** {', '.join(phones)}")
                                    if socials:
                                        st.write(f"**Social profiles on {url}:**")
                                        for platform, links in socials.items():
                                            for link in links:
                                                st.markdown(f"- [{platform}]({link})")
                                        for platform, links in socials.items():
                                            if platform not in found_socials:
                                                found_socials[platform] = set()
                                            found_socials[platform].update(links)
                                except Exception:
                                    st.warning(f"Could not access {url}")
                        if found_phones:
                            st.success(f"Total unique phone numbers found: {len(found_phones)}")
                            st.write(", ".join(found_phones))
                        else:
                            st.info("No phone numbers found for this email in public sources.")
                        if found_socials:
                            st.success("Summary of unique social profiles found:")
                            for platform, links in found_socials.items():
                                for link in links:
                                    st.markdown(f"- [{platform}]({link})")
                        else:
                            st.info("No social profiles found for this email in public sources.")
                    except Exception:
                        st.warning("Google search limit reached or an error occurred.")
    else:
        phone = st.text_input("Enter phone number:", placeholder="e.g. +1 555-123-4567 or 5551234567")
        submitted = st.form_submit_button("Find")
        if submitted:
            if not validate_phone(phone):
                st.error("Please enter a valid phone number (e.g. +1 555-123-4567).")
            else:
                st.info("Searching for emails and social profiles linked to this phone number using advanced Google dorks...")
                found_emails = set()
                found_socials = {}
                queries = build_search_queries("phone", phone)
                with st.spinner("Searching the web with multiple techniques..."):
                    try:
                        for q in queries:
                            for url in search(q, num=num_results, stop=num_results, pause=2):
                                try:
                                    response = requests.get(url, timeout=8)
                                    visible_text = get_visible_text(response.text)
                                    emails = extract_emails(visible_text)
                                    socials = extract_social_links(response.text)
                                    if emails:
                                        found_emails.update(emails)
                                        st.write(f"**Found on {url}:** {', '.join(emails)}")
                                    if socials:
                                        st.write(f"**Social profiles on {url}:**")
                                        for platform, links in socials.items():
                                            for link in links:
                                                st.markdown(f"- [{platform}]({link})")
                                        for platform, links in socials.items():
                                            if platform not in found_socials:
                                                found_socials[platform] = set()
                                            found_socials[platform].update(links)
                                except Exception:
                                    st.warning(f"Could not access {url}")
                        if found_emails:
                            st.success(f"Total unique emails found: {len(found_emails)}")
                            st.write(", ".join(found_emails))
                        else:
                            st.info("No emails found for this phone number in public sources.")
                        if found_socials:
                            st.success("Summary of unique social profiles found:")
                            for platform, links in found_socials.items():
                                for link in links:
                                    st.markdown(f"- [{platform}]({link})")
                        else:
                            st.info("No social profiles found for this phone number in public sources.")
                    except Exception:
                        st.warning("Google search limit reached or an error occurred.")

st.caption("Note: Uses public data sources only. Rate limits may apply. For best results, use well-known emails or phone numbers.")
