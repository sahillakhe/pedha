# form_module.py

import streamlit as st
from datetime import datetime
import re

def create_form(data):
    with st.form("resume_form"):
        st.subheader("Personal Information")
        birth_date = datetime.strptime(data["personalInformation"]["birth_date"], "%Y-%m-%d").date()
        first_name = st.text_input("First Name", value=data["personalInformation"]["first_name"], key="first_name")
        last_name = st.text_input("Last Name", value=data["personalInformation"]["last_name"], key="last_name")
        job_title = st.text_input("Job Title", value=data["personalInformation"]["job_title"], key="job_title")
        birth_date = st.date_input("Birth Date", value=birth_date, key="birth_date")

        st.subheader("Contact")
        phone = st.text_input("Phone", value=data["contact"]["phone"], key="phone")
        email = st.text_input("Email", value=data["contact"]["email"], key="email")
        github = st.text_input("GitHub", value=data["contact"]["github"], key="github")
        linkedin = st.text_input("LinkedIn", value=data["contact"]["linkedin"], key="linkedin")

        st.subheader("About")
        summary = st.text_area("Summary", value=data["about"]["summary"], key="summary")
        skill_tags = st.multiselect("Skill Tags", options=data["about"]["skill_tags"], default=data["about"]["skill_tags"], key="skill_tags")

        st.subheader("Work Experience")
        work_experience = []
        for i, exp in enumerate(data["work_experience"]):
            st.write(f"Experience {i+1}")
            company = st.text_input(f"Company {i+1}", value=exp["company"], key=f"company_{i}")
            country = st.text_input(f"Country {i+1}", value=exp["location"]["country"], key=f"country_{i}")
            city = st.text_input(f"City {i+1}", value=exp["location"]["city"], key=f"city_{i}")
            position = st.text_input(f"Position {i+1}", value=exp["position"], key=f"position_{i}")
            start_date = st.text_input(f"Start Date {i+1}", value=exp["start_date"], key=f"start_date_{i}")
            end_date = st.text_input(f"End Date {i+1}", value=exp["end_date"], key=f"end_date_{i}")
            achievements = st.text_area(f"Achievements {i+1}", value="\n".join(exp["achievements"]), key=f"achievements_{i}")
            role_description = st.text_area(f"Role Description {i+1}", value=exp["role_description"], key=f"role_description_{i}")
            tools = st.multiselect(f"Tools {i+1}", options=exp["tools"], default=exp["tools"], key=f"tools_{i}")
            work_experience.append({
                "company": company,
                "location": {"country": country, "city": city},
                "position": position,
                "start_date": start_date,
                "end_date": end_date,
                "achievements": achievements.split("\n"),
                "role_description": role_description,
                "tools": tools
            })

        st.subheader("Education")
        education = []
        for i, edu in enumerate(data["education"]):
            st.write(f"Education {i+1}")
            end_date = datetime.strptime(edu["end_date"], "%Y-%m-%d").date()
            institution = st.text_input(f"Institution {i+1}", value=edu["institution"], key=f"institution_{i}")
            end_date = st.date_input(f"End Date {i+1}", value=end_date, key=f"edu_end_date_{i}")
            country = st.text_input(f"Country {i+1}", value=edu["location"]["country"], key=f"edu_country_{i}")
            city = st.text_input(f"City {i+1}", value=edu["location"]["city"], key=f"edu_city_{i}")
            program = st.text_input(f"Program {i+1}", value=edu["program"], key=f"program_{i}")
            education.append({
                "institution": institution,
                "end_date": end_date.strftime("%Y-%m-%d"),
                "location": {"country": country, "city": city},
                "program": program
            })

        st.subheader("Expertise")
        experience = []
        for i, exp in enumerate(data["expertise"]["experience"]):
            name = st.text_input(f"Experience {i+1}: {exp['name']}", key=f"exp_name_{i}")
            proficiency = st.text_input(f"Proficiency {i+1}: {exp['name']}", value=exp["proficiency"], key=f"exp_proficiency_{i}")
            experience.append({"name": name, "proficiency": proficiency})

        programming_language = []
        for i, lang in enumerate(data["expertise"]["programming_language"]):
            name = st.text_input(f"Programming Language {i+1}: {lang['name']}", key=f"prog_lang_name_{i}")
            proficiency = st.text_input(f"Proficiency {i+1}: {lang['name']}", value=lang["proficiency"], key=f"prog_lang_proficiency_{i}")
            programming_language.append({"name": name, "proficiency": proficiency})

        development_tools = []
        for i, tool in enumerate(data["expertise"]["development_tools"]):
            name = st.text_input(f"Development Tool {i+1}: {tool['name']}", key=f"dev_tool_name_{i}")
            proficiency = st.text_input(f"Proficiency {i+1}: {tool['name']}", value=tool["proficiency"], key=f"dev_tool_proficiency_{i}")
            development_tools.append({"name": name, "proficiency": proficiency})

        st.subheader("Courses")
        courses = []
        for i, course in enumerate(data["courses"]):
            st.write(f"Course {i+1}")
            end_date = datetime.strptime(course["end_date"], "%Y-%m-%d").date()
            institution = st.text_input(f"Institution {i+1}", value=course["institution"], key=f"course_institution_{i}")
            end_date = st.date_input(f"End Date {i+1}", value=end_date, key=f"course_end_date_{i}")
            title = st.text_input(f"Title {i+1}", value=course["title"], key=f"course_title_{i}")
            courses.append({
                "institution": institution,
                "end_date": end_date.strftime("%Y-%m-%d"),
                "title": title
            })

        st.subheader("Languages")
        languages = []
        for i, lang in enumerate(data["languages"]):
            st.write(f"Language {i+1}")
            name = st.text_input(f"Language {i+1}", value=lang["name"], key=f"lang_name_{i}")
            proficiency = st.text_input(f"Proficiency {i+1}", value=lang["proficiency"], key=f"lang_proficiency_{i}")
            languages.append({"name": name, "proficiency": proficiency})
        
        # Submit button inside the form
        submit_button = st.form_submit_button("Save Changes")
        
        # Validation
        errors = []

        if submit_button:
            # Basic validations
            if not first_name:
                errors.append("First Name is required.")
            if not last_name:
                errors.append("Last Name is required.")
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                errors.append("Invalid email format.")
            if len(phone) < 10:
                errors.append("Phone number should be at least 10 characters long.")
            if not skill_tags:
                errors.append("At least one skill tag is required.")
            
            # Check for errors
            if errors:
                for error in errors:
                    st.error(error)
            else:
                updated_data = {
                    "personalInformation": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "job_title": job_title,
                        "birth_date": birth_date.strftime("%Y-%m-%d")
                    },
                    "contact": {
                        "phone": phone,
                        "email": email,
                        "github": github,
                        "linkedin": linkedin
                    },
                    "about": {
                        "summary": summary,
                        "skill_tags": skill_tags
                    },
                    "work_experience": work_experience,
                    "education": education,
                    "expertise": {
                        "experience": experience,
                        "programming_language": programming_language,
                        "development_tools": development_tools
                    },
                    "courses": courses,
                    "languages": languages
                }
                st.json(updated_data)
                st.success("Changes saved successfully!")