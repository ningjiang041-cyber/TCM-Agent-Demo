import streamlit as st
import pandas as pd
from openai import OpenAI
import base64

st.set_page_config(page_title="中医智能辅助诊疗系统", layout="wide")
st.title("中医“病-证-法-方-效”智能辅助诊疗系统")

try:
    api_key = st.secrets["DASHSCOPE_API_KEY"]
except Exception:
    st.error("请在 Streamlit 控制台的 Secrets 中配置 DASHSCOPE_API_KEY")
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
                        model="qwen3-vl-plus",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "请用中医术语描述这张舌象的舌质、舌苔、厚薄、润燥，只输出一句话。"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }]
                    )
                    tongue_desc = vl_response.choices[0].message.content
                    st.info(f"多模态视觉分析：{tongue_desc}")

                # 2. 整合文本和图像，发给大模型
                final_query = f"文字症状：{user_input}。舌象特征：{tongue_desc}"
                
                system_prompt = """
你是一个严谨的中医临床辅助决策系统。严禁任何寒暄、情绪化表达或废话。输出推理过程。
若输入信息缺失（无舌象、无脉象），仅输出需追问的缺失项，你的输出必须经得起文献查证。

【推演路径】
1. 症状提取：[提取文字与图片中的核心症状、舌象、脉象]
2. 病机分析：[用一句话说明病机]
3. 辨证推演：[推导证型，需对应《中医内科学》或经典标准]
4. 治则治法：[给出治法]
5. 选方依据：[说明为何选此方，结合病机]

【最终结论】
病：[病名]
证：[证型]
治法：[治法]
方剂：[方名]（《出处·具体篇名/条文号》，如《伤寒论·辨太阳病脉证并治上》第35条）
经典佐证：[引用一句支持该辨证或方剂的经典原文原话]
药材与剂量：[列出主要药材及具体克数或原方比例，如：麻黄9g、桂枝6g]
煎服与禁忌：[具体的煎服法（如先煎、后下）及用药禁忌]
置信度：[高/中/低]
- 评判标准：高（四诊俱全且高度契合经典）；中（部分信息缺失，推断合理）；低（严重缺信息，仅为方向性猜测）。

补充规则：
1. 四诊信息不足时，必须在“推演路径”中指出，严禁编造舌脉。
2. 出处必须精确。若典籍版本无法确定具体条号，仅写书名及篇名，绝对禁止编造条文号。
3. 药材剂量必须参考原方比例或常规临床剂量，不得随意乱写。
4. 若文字与图片冲突，以文字为准。
5. 禁止输出模板之外的任何解释。
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
