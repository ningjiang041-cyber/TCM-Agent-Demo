import streamlit as st
import pandas as pd
from openai import OpenAI
import base64

st.set_page_config(page_title="中医智能辅助诊疗系统", layout="wide")
st.title("🧑‍⚕️ 中医“病-证-法-方-效”智能辅助诊疗系统")

try:
    api_key = st.secrets["DASHSCOPE_API_KEY"]
except Exception:
    st.error("⚠️ 请在 Streamlit 控制台的 Secrets 中配置 DASHSCOPE_API_KEY")
    st.stop()

client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

# === 界面布局：左边输入，右边展示 ===
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("患者信息录入")
    user_input = st.text_area("请输入患者症状（如：咳嗽，痰黄，咽喉痛）", height=100)
    uploaded_file = st.file_uploader("📸 上传舌象照片（多模态输入）", type=["jpg", "jpeg", "png"])
    submit = st.button("开始智能辨证", type="primary", use_container_width=True)

with col2:
    st.subheader("智能推演结果")
    if submit:
        if not user_input and not uploaded_file:
            st.warning("请输入症状或上传舌象。")
        else:
            with st.spinner("系统正在解析四诊信息并推演..."):
                tongue_desc = ""
                # 1. 多模态：如果上传了图片，先看图
                if uploaded_file is not None:
                    image_bytes = uploaded_file.read()
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                    vl_response = client.chat.completions.create(
                        model="qwen-vl-plus",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "请用中医术语描述这张舌象的舌质、舌苔、厚薄、润燥，只输出一句话。"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }]
                    )
                    tongue_desc = vl_response.choices[0].message.content
                    st.info(f"👁️ 多模态视觉分析：{tongue_desc}")

                # 2. 整合文本和图像，发给大模型
                final_query = f"文字症状：{user_input}。舌象特征：{tongue_desc}"
                
                system_prompt = """
                你是“中医病-证-法-方-效”智能辅助诊疗Agent，基于多模态知识图谱与GraphRAG技术。
                1. 必须严格按“病→证→法→方→效”推演。
                2. 严禁编造，推荐方剂必须标注经典出处（如《伤寒论》）。
                3. 四诊信息不足时，主动追问。
                """
                
                response = client.chat.completions.create(
                    model="qwen-plus",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": final_query}
                    ],
                    temperature=0.2 # 严控幻觉
                )
                
                result = response.choices[0].message.content
                st.success("推演完成！")
                st.markdown(result)
