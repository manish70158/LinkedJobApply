'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''

from personals import *
import json

###################################################### CONFIGURE YOUR RESUME HERE ######################################################


# Give an relative path of your default resume to be uploaded. If file in not found, will continue using your previously uploaded resume in LinkedIn.
default_resume_path = "Manish2025Resume__Copy_.pdf"      # Using your resume from the main directory


# Resume Configuration
resume_headline = "Experienced Java Backend Developer with 5+ years in Spring Boot, Microservices and REST APIs"

# Experience Level in Years
years_of_experience = 5

# Education
education = {
    "degree": "Master's Degree",
    "field_of_study": "Computer Science",
    "school_name": "Your University",  # Replace with actual university name
    "start_date": "Aug 2015", 
    "end_date": "May 2018",
    "grade": "First Class"
}

# Skills (Based on what I found in your job applications)
skills = [
    "Java",
    "Spring Boot",
    "Microservices",
    "REST APIs",
    "AWS",
    "Docker",
    "Kubernetes",
    "CI/CD",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Git",
    "Jenkins",
    "Agile/Scrum",
    "Kafka",
    "JUnit",
    "Hibernate",
    "JPA",
    "JavaScript"
]

# Work Experience
work_experience = [
    {
        "title": "Senior Software Engineer",
        "company": "Current Company",  # Replace with actual company name
        "location": "India",
        "description": "Developed and maintained microservices architecture using Spring Boot and AWS. Implemented REST APIs, integrated messaging systems with Kafka, and optimized database performance.",
        "start_date": "June 2022",
        "end_date": "Present",
        "is_current": True
    },
    {
        "title": "Software Engineer",
        "company": "Previous Company",  # Replace with actual company name
        "location": "India",
        "description": "Worked on backend development using Java and Spring framework. Developed RESTful services, implemented CI/CD pipelines, and collaborated with cross-functional teams.",
        "start_date": "July 2020",
        "end_date": "May 2022",
        "is_current": False
    },
    {
        "title": "Junior Developer",
        "company": "First Company",  # Replace with actual company name
        "location": "India",
        "description": "Started career as a Java developer working on web applications. Gained experience in Spring MVC, Hibernate, and SQL databases.",
        "start_date": "June 2018",
        "end_date": "June 2020",
        "is_current": False
    }
]

# Projects
projects = [
    {
        "title": "Microservices Platform",
        "description": "Designed and implemented a scalable microservices architecture using Spring Boot, Docker and Kubernetes.",
        "skills_used": "Java, Spring Boot, Docker, Kubernetes, AWS, Kafka, REST APIs"
    },
    {
        "title": "Data Processing Pipeline",
        "description": "Developed a high-throughput data processing system using Spring Batch and Kafka streams.",
        "skills_used": "Java, Spring Batch, Kafka, AWS S3, MongoDB"
    }
]

# Certifications
certifications = [
    {
        "name": "AWS Certified Developer - Associate",
        "issuer": "Amazon Web Services",
        "issue_date": "2023"
    },
    {
        "name": "Spring Professional Certification",
        "issuer": "VMware",
        "issue_date": "2022"
    }
]


# # >>>>>>>>>>> RELATED SETTINGS <<<<<<<<<<<

# Allow Manual Inputs
# Should the tool pause before every submit application during easy apply to let you check the information?
pause_before_submit = True         # True or False, Note: True or False are case-sensitive
'''
Note: Will be treated as False if `run_in_background = True`
'''

# Should the tool pause if it needs help in answering questions during easy apply?
# Note: If set as False will answer randomly...
pause_at_failed_question = True    # True or False, Note: True or False are case-sensitive
'''
Note: Will be treated as False if `run_in_background = True`
'''
##

# Do you want to overwrite previous answers?
overwrite_previous_answers = False # True or False, Note: True or False are case-sensitive







############################################################################################################
'''
THANK YOU for using my tool 😊! Wishing you the best in your job hunt 🙌🏻!

Sharing is caring! If you found this tool helpful, please share it with your peers 🥺. Your support keeps this project alive.

Support my work on <PATREON_LINK>. Together, we can help more job seekers.

As an independent developer, I pour my heart and soul into creating tools like this, driven by the genuine desire to make a positive impact.

Your support, whether through donations big or small or simply spreading the word, means the world to me and helps keep this project alive and thriving.

Gratefully yours 🙏🏻,
Sai Vignesh Golla
'''
############################################################################################################