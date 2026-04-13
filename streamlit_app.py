import streamlit as st
import requests
import uuid

API_BASE = "http://127.0.0.1:8100/api/v1"

st.set_page_config(
    page_title="电商内容生成 Agent",
    page_icon="🛒",
    layout="wide",
)

st.title("🛒 电商内容生成 Agent")

# 会话管理
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# 侧边栏
with st.sidebar:
    st.header("设置")
    if st.button("新建会话"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    st.caption(f"Session: `{st.session_state.session_id[:8]}...`")

    st.divider()
    st.header("快捷指令")
    for prompt in [
        "帮我写一个保温杯的文案",
        "帮我生成一个保温杯的产品图",
        "帮我写一个口红的种草文案",
        "帮我生成一个运动鞋的产品图",
    ]:
        if st.button(prompt, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Agent 正在处理..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/chat",
                        json={
                            "message": prompt,
                            "session_id": st.session_state.session_id,
                        },
                        timeout=120,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    st.session_state.messages.append(
                        {"role": "assistant", "content": data["reply"]}
                    )
                except Exception as e:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"请求失败: {e}"}
                    )
            st.rerun()

# 聊天历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入框
if prompt := st.chat_input("请输入您的需求，如：帮我写一个保温杯的文案"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("多 Agent 协作中（协调器 → 专家 → 审校）..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/chat",
                    json={
                        "message": prompt,
                        "session_id": st.session_state.session_id,
                    },
                    timeout=120,
                )
                resp.raise_for_status()
                data = resp.json()
                st.markdown(data["reply"])

                # 显示协调信息
                with st.expander("Agent 工作流详情"):
                    st.write(f"**执行计划**: {data['plan']}")
                    st.write(f"**审校通过**: {'✅' if data['review_passed'] else '❌'}")
                    st.write(f"**审校轮次**: {data['review_cycle']}")
                    st.write(f"**会话ID**: {data['session_id']}")

                st.session_state.messages.append(
                    {"role": "assistant", "content": data["reply"]}
                )
            except Exception as e:
                st.error(f"请求失败: {e}")
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"请求失败: {e}"}
                )
