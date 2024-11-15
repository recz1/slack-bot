import google.generativeai as genai


# only for test

def make_request(message):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(message)
    res = response.candidates[0].content.parts[0].text
    return res