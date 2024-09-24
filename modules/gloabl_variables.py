# Load environment variables from keys.env
key_env_path = '/Users/sahillakhe/repositories/secrets/keys.env'

schema = """
{
  "personalInformation": {
    "first_name": "string",
    "last_name": "string",
    "job_title": "string",
    "birth_date": "yyyy-mm-dd"
  },
  "contact": {
    "phone": "string",
    "email": "string",
    "github": "string",
    "linkedin": "string"
  },
  "about": {
    "summary": "string",
    "skill_tags": [
      string, string
    ]
  },
  "work_experience": [
    {
      "company": "string",
      "location": {"country": "string", "city": "string"},
      "position": "string",
      "start_date": "string",
      "end_date": "string",
      "achievements": ["string"],
      "role_description": "string",
      "tools": ["string"]
    }
  ],
  "education": [
    {
      "institution": "string",
      "end_date": "yyyy-mm-dd",
      "location": {"country": "string", "city": "string"},
      "program": "string"
    }
  ],
  "expertise": {
    "experience": [
      {
        "name": "string",
        "proficiency": "string"
      }
    ],
    "programming_language": [
      {
        "name": "string",
        "proficiency": "string"
      }
    ],
    "development_tools": [
      {
        "name": "string",
        "proficiency": "string"
      }
    ]
  },
  "courses": [{"institution": "string", "end_date": "yyyy-mm-dd", "title": "string"}],
  "languages": [{"name": "string", "proficiency": "string"}]
}
"""

# Craft the prompt
prompt = f"""
You are a professional resume parser. Your task is to extract information from the provided resume text and output a JSON object following the given schema.

First, clean and preprocess the text to ensure it is properly formatted and makes contextual sense.

Then, extract the relevant information and populate the JSON object accordingly. If certain fields are missing in the resume, you can leave them empty or as null.

Ensure that dates are in the format "yyyy-mm-dd" and all strings are properly escaped.

Schema:
{schema}

Resume Text:
\"\"\"
{text}
\"\"\"

Output:
"""