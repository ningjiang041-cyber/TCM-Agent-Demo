import streamlit as st
from neo4j import GraphDatabase
import pandas as pd

st.set_page_config(page_title="中医智能辅助诊疗系统", layout="wide")
st.title("🧑‍⚕️ 中医“病-证-方-效”智能辅助诊疗系统")

# 连接Neo4j（这里先用默认配置，后续可以改）
@st.cache_resource
def get_driver():
    # 如果你没有云端数据库，这部分代码在公网演示时可能会报错。
    # 为了先跑通界面，我们先用一个模拟的数据展示。
    return None

user_input = st.text_area("请输入患者症状（如：咳嗽，痰黄，咽喉痛）", height=100)

if st.button("开始辨证", type="primary"):
    if user_input:
        with st.spinner("正在检索知识图谱..."):
            # 模拟检索结果（防报错演示版）
            mock_data = [
                {"证型": "风热犯肺证", "治法": "疏风清热，宣肺止咳", "方剂": "桑菊饮", "出处": "《温病条辨》"},
                {"证型": "痰热壅肺证", "治法": "清热化痰，肃肺止咳", "方剂": "清金化痰汤", "出处": "《医学统旨》"}
            ]
            st.success("检索到以下相关证型与方剂：")
            st.dataframe(pd.DataFrame(mock_data))
            
            st.info("💡 系统提示：由于当前展示为轻量化前端，完整辨证思维链与溯源功能已在后端Agent中实现。")
    else:
        st.warning("请输入症状描述。")
