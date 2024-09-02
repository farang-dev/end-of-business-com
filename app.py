import streamlit as st
from openai import OpenAI
import traceback
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import logging

# Add this at the beginning of the file, after imports
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client at the top level
client = None

def initialize_openai_client():
    global client
    if 'openai_api_key' in st.session_state and st.session_state.openai_api_key:
        client = OpenAI(api_key=st.session_state.openai_api_key)

# Define translations
translations = {
    'en': {
        'title': "MailSlayer",
        'api_key_prompt': "Enter your OpenAI API Key:",
        'api_key_warning': "Please enter your OpenAI API Key to continue.",
        'choose_option': "Choose an option:",
        'create': "Create",
        'reply': "Reply",
        'recipient': "Who are you sending the message to?",
        'platform': "Platform:",
        'tone': "Tone:",
        'length': "Length:",
        'receiver_name': "Receiver's name:",
        'message_input': "I want to say:",
        'generate_message': "Generate Message",
        'paste_message': "Paste the message you want to reply to:",
        'generate_reply': "Generate Reply",
        'generated_message': "Generated Message:",
        'copy_to_clipboard': "Copy to Clipboard",
        'copied_message': "Message copied to clipboard!",
        'edit_request': "Edit request (e.g., 'make it shorter'):",
        'edited_message': "Edited Message:",
        'copy_edited_message': "Copy Edited Message",
        'copied_edited_message': "Edited message copied to clipboard!",
    },
    'ja': {
        'title': "メールスレイヤー",
        'api_key_prompt': "OpenAI APIキーを入力してください：",
        'api_key_warning': "続行するにはOpenAI APIキーを入力しください。",
        'choose_option': "オションを選択してください：",
        'create': "新規作成",
        'reply': "返信",
        'recipient': "誰にメッセージを送信しますか？",
        'platform': "プラットフォーム：",
        'tone': "トーン：",
        'length': "長さ：",
        'receiver_name': "受信者の名：",
        'message_input': "伝えたいこと：",
        'generate_message': "メッセージを生成",
        'paste_message': "返信したいメッセージを貼り付けてください：",
        'generate_reply': "返信を生成",
        'generated_message': "生成されたメッセージ：",
        'copy_to_clipboard': "クリップボードにコピー",
        'copied_message': "メッセージがクリップボードにコピーされました！",
        'edit_request': "編集リクエスト（例：「短くする」）：",
        'edited_message': "編集されたメッセージ：",
        'copy_edited_message': "編集されたメッセージをコピー",
        'copied_edited_message': "編集されたメッセージがクリップボードにコピーされました！",
        'colleague': "同僚",
        'manager': "上司",
        'friend': "友人",
        'family': "家族",
        'email': "メール",
        'linkedin': "LinkedIn",
        'instagram': "Instagram",
        'whatsapp': "WhatsApp",
        'professional': "ビジネス",
        'neutral': "中立(ナチュラル)",
        'casual': "カジュアル",
        'very_short': "とても短い",
        'short': "短い",
        'medium': "普通",
        'detailed': "詳細（長い）",
    }
}

def main():
    try:
        clear_old_cache()
        st.set_page_config(page_title="MailSlayer")

        # Language selection
        lang = st.sidebar.selectbox("Language / 言語", ["English", "日本語"], index=0)
        lang_code = 'en' if lang == "English" else 'ja'
        t = translations[lang_code]

        st.title(t['title'])

        # API Key input
        api_key = st.text_input(t['api_key_prompt'], type="password", key="api_key_input")
        if 'openai_api_key' not in st.session_state and api_key:
            st.session_state.openai_api_key = api_key
        elif 'openai_api_key' in st.session_state:
            api_key = st.session_state.openai_api_key

        if not api_key:
            st.warning(t['api_key_warning'])
            return

        initialize_openai_client()

        # Main option selection
        option = st.radio(t['choose_option'], [t['create'], t['reply']])

        try:
            with st.spinner("Processing your request..."):
                if option == t['create']:
                    create_message(t)
                else:
                    reply_to_message(t)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            logging.error(traceback.format_exc())
            st.error("An error occurred. Please try again or contact support if the issue persists.")
            st.error("If you're on a mobile device, try refreshing the page or using a desktop browser.")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        logging.error(traceback.format_exc())
        st.error("An error occurred. Please try again or contact support if the issue persists.")
        st.error("If you're on a mobile device, try refreshing the page or using a desktop browser.")

def create_message(t):
    recipient_options = ["Colleague", "Manager", "Friend", "Family"] if t == translations['en'] else ["同僚", "上司", "友人", "家族"]
    platform_options = ["Email", "LinkedIn", "Instagram", "WhatsApp"] if t == translations['en'] else ["メール", "LinkedIn", "Instagram", "WhatsApp"]
    tone_options = ["Professional", "Neutral", "Casual"] if t == translations['en'] else ["ビジネス", "中立", "カジュアル"]
    length_options = ["Very Short", "Short", "Medium", "Detailed (Long)"] if t == translations['en'] else ["とても短い", "短い", "普通", "詳細（長い）"]

    recipient = st.selectbox(t['recipient'], recipient_options)
    platform = st.selectbox(t['platform'], platform_options)
    tone = st.selectbox(t['tone'], tone_options)
    length = st.selectbox(t['length'], length_options)
    receiver_name = st.text_input(t['receiver_name'])
    message = st.text_area(t['message_input'])

    if st.button(t['generate_message']):
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Preparing request...")
        progress_bar.progress(10)

        status_text.text("Generating message...")
        generated_message = generate_ai_message(recipient, platform, tone, length, receiver_name, message, t == translations['ja'])
        progress_bar.progress(90)

        if generated_message:
            status_text.text("Finalizing...")
            progress_bar.progress(100)
            display_and_edit_message(generated_message, t)
        else:
            status_text.text("Failed to generate message. Please try again.")

        progress_bar.empty()
        status_text.empty()

def reply_to_message(t):
    original_message = st.text_area(t['paste_message'])
    recipient_options = ["Colleague", "Manager", "Friend", "Family"] if t == translations['en'] else ["同僚", "上司", "友人", "家族"]
    platform_options = ["Email", "LinkedIn", "Instagram", "WhatsApp"] if t == translations['en'] else ["メール", "LinkedIn", "Instagram", "WhatsApp"]
    tone_options = ["Professional", "Neutral", "Casual"] if t == translations['en'] else ["ビジネス", "中立(n)", "カジュアル"]
    length_options = ["Very Short", "Short", "Medium", "Detailed (Long)"] if t == translations['en'] else ["とて短い", "短い", "普通", "詳細（長い）"]

    recipient = st.selectbox(t['recipient'], recipient_options)
    platform = st.selectbox(t['platform'], platform_options)
    tone = st.selectbox(t['tone'], tone_options)
    length = st.selectbox(t['length'], length_options)
    receiver_name = st.text_input(t['receiver_name'])

    if st.button(t['generate_reply']):
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Preparing request...")
        progress_bar.progress(10)

        status_text.text("Generating reply...")
        generated_reply = generate_ai_reply(original_message, recipient, platform, tone, length, receiver_name, t == translations['ja'])
        progress_bar.progress(90)

        if generated_reply:
            status_text.text("Finalizing...")
            progress_bar.progress(100)
            display_and_edit_message(generated_reply, t)
        else:
            status_text.text("Failed to generate reply. Please try again.")

        progress_bar.empty()
        status_text.empty()

@st.cache_data(ttl=3600, show_spinner=False)
def generate_ai_message(recipient, platform, tone, length, receiver_name, message, is_japanese):
    global client
    language = "日本語" if is_japanese else "English"
    prompt = f"Generate a {tone} {length} message in {language} for {recipient} named {receiver_name} on {platform}. The message should convey: {message}"

    def api_call():
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    try:
        return retry_api_call(api_call)
    except Exception as e:
        st.error(f"API request failed after multiple attempts: {str(e)}")
        return "Failed to generate message. Please try again."

@st.cache_data(ttl=3600, show_spinner=False)
def generate_ai_reply(original_message, recipient, platform, tone, length, receiver_name, is_japanese):
    global client
    language = "日本語" if is_japanese else "English"
    prompt = f"Generate a {tone} {length} reply in {language} for {recipient} named {receiver_name} on {platform} to the following message: {original_message}"

    def api_call():
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    try:
        return retry_api_call(api_call)
    except Exception as e:
        st.error(f"API request failed after multiple attempts: {str(e)}")
        return "Failed to generate reply. Please try again."

@st.cache_data(ttl=3600, show_spinner=False)
def edit_ai_message(original_message, edit_request):
    global client
    prompt = f"Edit the following message according to this request: {edit_request}\n\nOriginal message: {original_message}"

    def api_call():
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    try:
        return retry_api_call(api_call)
    except Exception as e:
        st.error(f"API request failed after multiple attempts: {str(e)}")
        return "Failed to edit message. Please try again."

def display_and_edit_message(message, t):
    st.text_area(t['generated_message'], value=message, height=300)
    st.button(t['copy_to_clipboard'], on_click=lambda: st.write(t['copied_message']))

    edit_request = st.text_input(t['edit_request'])
    if edit_request:
        edited_message = edit_ai_message(message, edit_request)
        st.text_area(t['edited_message'], value=edited_message, height=300)
        st.button(t['copy_edited_message'], on_click=lambda: st.write(t['copied_edited_message']))

def timeout_wrapper(func, timeout_duration):
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            try:
                result = await asyncio.wait_for(
                    loop.run_in_executor(pool, func, *args, **kwargs),
                    timeout=timeout_duration
                )
                return result
            except asyncio.TimeoutError:
                st.error(f"The request timed out after {timeout_duration} seconds. Please try again.")
                return None

    return wrapper

def retry_api_call(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(1)  # Wait for 1 second before retrying

def clear_old_cache():
    if 'cache_counter' not in st.session_state:
        st.session_state.cache_counter = 0

    st.session_state.cache_counter += 1
    if st.session_state.cache_counter > 10:  # Clear cache every 10 operations
        st.cache_data.clear()
        st.session_state.cache_counter = 0

if __name__ == "__main__":
    main()
