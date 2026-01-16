import streamlit as st
import pandas as pd
import numpy as np

st.title('🎈 내 첫 Streamlit 앱')
st.write('## 안녕하세요!')
st.write('Windows에서 Streamlit이 실행되고 있어요!')

df = pd.DataFrame({
    '이름': ['철수', '영희', '민수'],
    '나이': [25, 30, 35],
    '점수': [85, 92, 78]
})
st.dataframe(df)

chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['A', 'B', 'C']
)
st.line_chart(chart_data)

if st.button('클릭하세요!'):
    st.success('버튼이 클릭되었습니다! 🎉')
