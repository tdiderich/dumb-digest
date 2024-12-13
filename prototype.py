import requests
from requests.auth import HTTPBasicAuth 
import os
import html2text
import markdown


def convert_to_plain_text_and_html(content):
    # Convert to HTML first (in case the input is Markdown)
    html_content = markdown.markdown(content)

    # Convert HTML to plain text
    h = html2text.HTML2Text()
    h.ignore_links = False
    plain_text = h.handle(html_content)

    return plain_text, html_content


def create_email(questions: list):
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    user_message = "\n- ".join(questions)
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant creating an email digest for your client. They are going to give you a list of questions to research and turn into an email newsletter. You should use smart brevity formatting, add emojis to make it fun, and have a fun tone. Today is 12/13/2025. Please only use search results that reference this date. Please only use plain text and emojis.",
        }, 
        {
            "role": "user",
            "content": user_message,
        }
    ]

    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers=headers,
        json={"model": "llama-3.1-sonar-huge-128k-online", "messages": messages},
    )

    if response.status_code == 200:
        completion = response.json()
        return completion
    else:
        raise Exception(
            f"Request failed with status code {response.status_code}: {response.text}"
        )


def send_email(content: str):
    # ForwardEmail API endpoint
    url = "https://api.forwardemail.net/v1/emails"

    plain_text, html_content = convert_to_plain_text_and_html(content)

    # Your email address and password
    email_address = "hello@dumb.company"
    password = os.environ.get("FORWARD_EMAIL_API_KEY")
    basic = HTTPBasicAuth(username=password, password="")

    # Email details
    data = {
        "from": email_address,
        "to": "tylerdiderich@gmail.com",
        "subject": "Your dumb digest",
        "text": plain_text,
        "html": html_content
    }

    # Make the POST request to send the email
    try:
        response = requests.post(url, auth=basic, json=data)

        # Check if the request was successful
        if response.status_code == 200:
            print("Email sent successfully!")
        else:
            print(f"Failed to send email: {response.status_code}")
            print(response.json())

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    email_content = create_email(["What's the weather like today in Madison, WI?", "Do the Wisconsin Badgers Basketball or Volleyball teams play today?", "Do the Milwaukee Bucks play today?", "What is an interesting fact about today?"])
    send_email(content=email_content["choices"][0]["message"]["content"])
