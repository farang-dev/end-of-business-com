import streamlit as st
from openai import OpenAI

def main():
    st.title("MailSlayer")

    # API Key input
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    if api_key:
        st.session_state.openai_api_key = api_key
    else:
        st.warning("Please enter your OpenAI API Key to continue.")
        return

    # Main option selection
    option = st.radio("Choose an option:", ["Create", "Reply"])

    if option == "Create":
        create_message()
    else:
        reply_to_message()

def create_message():
    # Input fields
    recipient = st.selectbox("Who are you sending the message to?", ["Colleague", "Manager", "Friend", "Family"])
    platform = st.selectbox("Platform:", ["Email", "LinkedIn", "Instagram", "WhatsApp"])
    tone = st.selectbox("Tone:", ["Professional", "Neutral", "Casual"])
    length = st.selectbox("Length:", ["Very Short", "Short", "Medium", "Detailed (Long)"])
    receiver_name = st.text_input("Receiver's name:")
    message = st.text_area("I want to say:")

    if st.button("Generate Message"):
        generated_message = generate_ai_message(recipient, platform, tone, length, receiver_name, message)
        display_and_edit_message(generated_message)

def reply_to_message():
    original_message = st.text_area("Paste the message you want to reply to:")

    # Input fields (similar to create_message)
    recipient = st.selectbox("Who are you replying to?", ["Colleague", "Manager", "Friend", "Family"])
    platform = st.selectbox("Platform:", ["Email", "LinkedIn", "Instagram", "WhatsApp"])
    tone = st.selectbox("Tone:", ["Professional", "Neutral", "Casual"])
    length = st.selectbox("Length:", ["Very Short", "Short", "Medium", "Detailed (Long)"])
    receiver_name = st.text_input("Receiver's name:")

    if st.button("Generate Reply"):
        generated_reply = generate_ai_reply(original_message, recipient, platform, tone, length, receiver_name)
        display_and_edit_message(generated_reply)

def generate_ai_message(recipient, platform, tone, length, receiver_name, message):
    client = OpenAI(api_key=st.session_state.openai_api_key)
    prompt = f"Generate a {tone} {length} message for {recipient} named {receiver_name} on {platform}. The message should convey: {message}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_ai_reply(original_message, recipient, platform, tone, length, receiver_name):
    client = OpenAI(api_key=st.session_state.openai_api_key)
    prompt = f"Generate a {tone} {length} reply for {recipient} named {receiver_name} on {platform} to the following message: {original_message}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def display_and_edit_message(message):
    st.text_area("Generated Message:", value=message, height=300)
    st.button("Copy to Clipboard", on_click=lambda: st.write("Message copied to clipboard!"))

    edit_request = st.text_input("Edit request (e.g., 'make it shorter'):")
    if edit_request:
        edited_message = edit_ai_message(message, edit_request)
        st.text_area("Edited Message:", value=edited_message, height=300)
        st.button("Copy Edited Message", on_click=lambda: st.write("Edited message copied to clipboard!"))

def edit_ai_message(original_message, edit_request):
    client = OpenAI(api_key=st.session_state.openai_api_key)
    prompt = f"Edit the following message according to this request: {edit_request}\n\nOriginal message: {original_message}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    main()
