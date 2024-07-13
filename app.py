import pandas as pd
import streamlit as st
from openai import OpenAI
import hmac
import os
import json

# Configure the Streamlit page
st.set_page_config(page_title="CIIS 新聞稿產生器", page_icon="💡", layout="wide")
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Function to check the password
def check_password():
    """Returns `True` if the user has the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.title("請登入")
    st.text_input(
        "密碼",
        type="password",
        on_change=password_entered,
        key="password",
    )
    if "password_correct" in st.session_state:
        st.error("😕 密碼不正確")
    return False


# Stop execution if password is not correct
if not check_password():
    st.stop()

# System prompt for the OpenAI model
SYSTEM_PROMPT = """
你是一位專業記者，請撰寫一篇1000字以上的新聞稿，介紹中華創新發明學會(CIIS)在某發明展中的表現。請確保不創造虛構的採訪或引用，並包含以下要點：

1. 展覽基本資訊：時間、地點及主辦方。
2. 參展範圍：展覽的國際範圍與展品數量。
3. 代表團成就：CIIS代表團獲得的獎項與榮譽。
4. 創新技術介紹：幾項關鍵發明與技術，包括功能、使用方式及潛在影響。
5. 未來展望：這些技術對行業或全球的長遠影響。

文章應專業且資訊充實，吸引科技愛好者、行業專家及公眾的關注。
文章格式為一篇完整的內文，無需分段標題或聯絡方式。
"""

# Initialize session state variables
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "press" not in st.session_state:
    st.session_state.press = ""


# Function to interact with the OpenAI API
def llm(exhibition_details, invention_details):
    client = OpenAI(api_key=os.getenv("OPENAI_CIIS_API_KEY"))

    st.session_state.messages.append(
        {
            "role": "user",
            "content": f"展覽的資訊:{exhibition_details}\n\n得獎作品的資訊:{invention_details}",
        }
    )
    stream = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        temperature=0.7,
        max_tokens=2000,
        stream=True,
    )
    return stream


# Function to calculate monthly total cost
def monthly_total_cost():
    current_year_month = pd.Timestamp.now().strftime("%Y%m")
    filename = f"api_usage/{current_year_month}.csv"
    df = pd.read_csv(filename)
    total_cost = int(df["Total Cost"].sum() * 10)
    return total_cost


# Function to get event description from a JSON file
def get_event_description(event_name):
    try:
        with open("exhibitions/exhibition_desc.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        for event in data["events"]:
            if event["Event Name"] == event_name:
                return event["Description"]
        return "Event name not found."
    except FileNotFoundError:
        return "The file 'exhibition_desc.json' was not found."
    except json.JSONDecodeError:
        return "Error decoding JSON from the file."
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Title of the Streamlit app
st.title("💡CIIS 新聞稿產生器")

# Create two columns for layout
col1, col2 = st.columns(2)

with col1:
    # Load exhibition data
    exhibition_data = pd.read_csv("exhibitions/exhibition_data.csv")
    exhibition_data["Date_simplified"] = pd.to_datetime(
        exhibition_data["Date"].str.extract(r"(\d{4}/\d{2}/\d{2})")[0]
    ) + pd.DateOffset(months=1)

    # Filter upcoming exhibitions
    upcoming_exhibitions = exhibition_data.query(
        "Date_simplified >= @pd.Timestamp.now()"
    )["Event Name"].unique()

    # Dropdown to select an exhibition
    exhibition_choice = st.selectbox("請選擇發明展:", upcoming_exhibitions)
    st.session_state["selected_exhibition"] = exhibition_choice

    with st.form(key="news_generation_form"):
        # Get selected exhibition information
        exhibition_info = exhibition_data.query("`Event Name` == @exhibition_choice")
        exhibition_desc = get_event_description(exhibition_choice)
        if not exhibition_info.empty:
            exhibition_desc = (
                f"時間: {exhibition_info.iloc[0]['Date']}\n{exhibition_desc}"
            )

        # Text areas to input exhibition and invention details
        exhibition_details = st.text_area(
            label="發明展的相關資訊:", height=100, value=exhibition_desc
        )
        invention_details = st.text_area(label="請提供得獎作品的相關資訊:", height=250)

        # Button to generate news
        generate_news_button = st.form_submit_button(label="請點擊以生成新聞稿")

with col2:
    if generate_news_button:
        # Contact information
        contact_info = (
            "新聞聯絡：<br>"
            "中華創新發明學會執行長吳智堯<br>"
            "手機：0978-123567<br>"
            "LINE：0932-388855"
        )

        # Generate news using OpenAI API
        st.session_state.press = llm(exhibition_details, invention_details)
        with st.spinner("*請等待生成結果...*"):
            content = st.write_stream(st.session_state.press)
            st.markdown(contact_info, unsafe_allow_html=True)

        # Prepare content for download
        full_content = content + "\r\n\r\n" + contact_info.replace("<br>", "\r\n")
        st.download_button(
            label="下載新聞稿",
            data=full_content.encode("utf-8"),
            file_name=f"新聞稿_{pd.Timestamp.now().strftime('%Y%m%d%H%M')}.txt",
            mime="text/plain",
        )
