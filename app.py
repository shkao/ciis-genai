import streamlit as st
from openai import OpenAI
import pandas as pd
import hmac
import os


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


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

SYSTEM_PROMPT = """
## 任務: 撰寫一篇關於中華創新發明學會在[年份][展覽名稱]中的成果的新聞稿。

## 關鍵要點：

1. 除非有提供，否則不要編造採訪、引用發明家的話語。
2. 活動基本信息：提及展覽的時間、地點以及主辦方。
3. 參展範圍：描述參展的國際範圍與展品數量。
4. 代表團成就：強調中華創新發明學會代表團所獲得的獎項與榮譽。
5. 創新技術介紹：具體介紹幾項重要的發明與創新技術及其潛在影響。
6. 專家觀點與引言：引用組織領導或專家的觀點和評論。
7. 未來展望與影響：討論這些創新技術對相關行業或全球發展目標的潛在影響。

* 風格和語調：確保語調專業、資訊全面，並適當使用引人入勝的敘述方式來吸引目標讀者——科技愛好者、行業專家及廣大公眾。
* 目標：通過詳盡的報導和深入的分析，使讀者能夠全面理解中華創新發明學會在推動科技創新和實現永續發展目標方面所做的貢獻。
* 格式：只要產生內文就好，不用分段標題，不用提供聯絡方式。
"""

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "press" not in st.session_state:
    st.session_state.press = ""


def llm(input_text):
    client = OpenAI(api_key=os.getenv("OPENAI_CIIS_API_KEY"))

    st.session_state.messages.append(
        {"role": "user", "content": f"展覽及作品的相關資訊為：{input_text}"}
    )
    stream = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        temperature=0.7,
        stream=True,
    )
    return stream


def monthly_total_cost():
    current_year_month = pd.Timestamp.now().strftime("%Y%m")
    filename = f"api_usage/{current_year_month}.csv"
    df = pd.read_csv(filename)
    total_cost = int(df["Total Cost"].sum() * 10)
    return total_cost


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
st.title("💡CIIS 新聞稿產生器")
col1, col2 = st.columns(2)

with col1:
    # exhibition_choice = st.selectbox(
    #     "請選擇發明展:",
    #     [
    #         "波蘭",
    #         "烏克蘭",
    #         "香港創新科技",
    #         "美國AII達文西",
    #         "馬來西亞MTE",
    #         "俄羅斯阿基米德",
    #         "日本東京創新天才",
    #         "韓國WiC世界創新發明大賽",
    #     ],
    # )
    # st.session_state["selected_exhibition"] = exhibition_choice
    with st.form(key="news_generation_form"):
        exhibition_details = st.text_area(
            label="請提供發明展及作品的相關資訊:", height=300
        )
        generate_news_button = st.form_submit_button(label="請點擊以生成新聞稿")
    st.info(f"本月使用量: {monthly_total_cost()}元。")

with col2:
    if generate_news_button:
        contact_info = (
            "新聞聯絡：<br>"
            "中華創新發明學會執行長吳智堯<br>"
            "手機：0978-123567<br>"
            "LINE：0932-388855"
        )
        st.session_state.press = llm(exhibition_details)
        with st.spinner("*請等待生成結果...*"):
            content = st.write_stream(st.session_state.press)
            st.markdown(contact_info, unsafe_allow_html=True)

        full_content = content + "\r\n\r\n" + contact_info.replace("<br>", "\r\n")
        st.download_button(
            label="下載新聞稿",
            data=full_content.encode("utf-8"),
            file_name=f"新聞稿_{pd.Timestamp.now().strftime('%Y%m%d%H%M')}.txt",
            mime="text/plain",
        )
