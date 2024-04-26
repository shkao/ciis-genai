import streamlit as st
from openai import OpenAI
import hmac
import os

st.set_page_config(
    page_title="CIIS 新聞稿產生器",
    page_icon="💡",
)


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.title("Login")
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
你是一位公司專業發言人，你需要針對公司給你的內容，運用自己獨特風格發表專業的公司新聞稿，向社會大眾聲明你公司提出的內容。
你跟公司是一體的，如果沒有發言的恰當，可能會面臨牢獄之災。
禁止回覆與新聞稿無關的內容，你務必只回答新聞稿。請不用加上任何免責聲明。
"""

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "press" not in st.session_state:
    st.session_state.press = ""


def llm(input_text):
    st.session_state.messages.append(
        {"role": "user", "content": f"公司提供的內容是：{input_text}"}
    )
    stream = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        stream=True,
    )
    return stream


st.title("💡CIIS 新聞稿產生器")

# 使用 Streamlit 以更禮貌的方式創建表單
with st.form(key="my_form"):
    input_text = st.text_area(label="請輸入您希望生成的新聞稿內容", height=100)
    submit_button = st.form_submit_button(label="請點擊以生成新聞稿")

# 在按下按鈕後，以禮貌的方式處理輸入，並顯示結果
if submit_button:
    st.session_state.press = llm(input_text)
    st.info(f"*您的新聞稿已成功生成*")
    st.write_stream(st.session_state.press)
