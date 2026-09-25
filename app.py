import streamlit as st
import yfinance as yf
import google.generativeai as genai
from urllib.parse import urlparse

# ตั้งค่าหน้าตาเว็บ (รองรับมือถือ & Dark Mode)
st.set_page_config(
    page_title="AI Stock Analyzer 10D",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# แถบเมนูด้านข้าง (Sidebar)
with st.sidebar:
    st.title("⚙️ ตั้งค่าระบบ")
    api_key = st.text_input("กรอก Gemini API Key:", type="password")
    st.markdown("---")
    ticker_input = st.text_input("พิมพ์ชื่อหุ้นที่ต้องการดู:", value="MU").upper()
    btn_analyze = st.button("🚀 เริ่มวิเคราะห์หุ้น", use_container_width=True)

st.title("📊 AI Stock Analyzer (10-Dimension Dashboard)")

if btn_analyze:
    if not api_key:
        st.error("⚠️ กรุณากรอก Gemini API Key ที่แถบเมนูด้านข้างก่อนครับ")
    else:
        try:
            genai.configure(api_key=api_key)
            stock = yf.Ticker(ticker_input)
            info = stock.info

            # ดึงข้อมูลการเงินสด
            price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
            pe = info.get('trailingPE', 'N/A')
            f_pe = info.get('forwardPE', 'N/A')
            target = info.get('targetMeanPrice', 'N/A')
            rec = str(info.get('recommendationKey', 'N/A')).upper()
            summary = info.get('longBusinessSummary', '')

            website = info.get('website', '')
            domain = urlparse(website).netloc.replace('www.', '') if website else f"{ticker_input.lower()}.com"

            # แสดงตัวเลขการเงินเป็น Metric Cards
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("ราคาปัจจุบัน", f"${price}")
            col2.metric("Trailing P/E", f"{pe}")
            col3.metric("Forward P/E", f"{f_pe}")
            col4.metric("ราคาเป้าหมายเฉลี่ย", f"${target}")

            st.markdown("---")

            # ปุ่มทางด่วนเปิด 7 แหล่งข้อมูล
            st.subheader("🌐 ลิงก์เจาะลึก 7 มิติข้อมูล")
            urls = {
                "AltIndex (AI Score)": f"https://altindex.com/ticker/{ticker_input.lower()}/ai-stock-analysis",
                "Google Trends": f"https://trends.google.com/explore?q={ticker_input}",
                "TradingView": f"https://www.tradingview.com/symbols/NASDAQ-{ticker_input}/",
                "Similarweb": f"https://www.similarweb.com/website/{domain}/",
                "Unusual Whales": f"https://unusualwhales.com/stock/{ticker_input}/overview?chart=options-volume",
                "Quiver Quant": f"https://www.quiverquant.com/stock/{ticker_input}/",
                "Bloomberg Deals": "https://www.bloomberg.com/deals"
            }

            c1, c2, c3, c4 = st.columns(4)
            btn_cols = [c1, c2, c3, c4]
            idx = 0
            for name, url in urls.items():
                btn_cols[idx % 4].link_button(name, url, use_container_width=True)
                idx += 1

            st.markdown("---")

            # สั่ง AI ประมวลผล 10 มิติ + 7 เว็บไซต์
            st.subheader(f"🤖 รายงานวิเคราะห์เจาะลึก 10 มิติ: [{ticker_input}]")
            
            prompt = f"""
คุณคือนักวิเคราะห์การลงทุนระดับสถาบัน จงวิเคราะห์หุ้น [{ticker_input}] โดยใช้ข้อมูลประกอบดังนี้:

[ข้อมูลราคาและงบการเงินล่าสุด]
- ราคาปัจจุบัน: ${price} | Trailing P/E: {pe} | Forward P/E: {f_pe}
- ราคาเป้าหมายเฉลี่ย: ${target} | คำแนะนำนักวิเคราะห์: {rec}
- สรุปข้อมูลบริษัท: {summary[:1000]}

[กรอบข้อมูลประกอบจาก 7 แหล่งที่คุณต้องนำมาร่วมประเมินวิเคราะห์]
1. AltIndex: คะแนน AI Score รวมข้อมูลทุกแหล่ง และ Sentiment (Buy/Hold/Sell)
2. Google Trends: ความสนใจค้นหาชื่อหุ้น/สินค้าบน Google
3. Similarweb: ยอดทราฟฟิกคนเข้าชมเว็บไซต์บริษัท ({domain})
4. Unusual Whales: สัญญาณ Options Flow (การซื้อ Call/Put ก้อนใหญ่ผิดปกติ)
5. Quiver Quant: การซื้อขายของ ส.ส./ส.ว. สหรัฐฯ และสถาบันใหญ่ (Whale)
6. TradingView: สัญญาณทางเทคนิคัลและราคา
7. Bloomberg Deals: ข่าวการควบรวมกิจการ (M&A) และการลงทุนใหญ่

คำสั่ง: จงเขียนบทวิเคราะห์จัดหมวดหมู่ให้ชัดเจน อ่านง่าย เป็นข้อๆ ตาม 10 หัวข้อนี้:
1. โมเดลธุรกิจและการสร้างรายได้ (Business Model & Monetization)
2. คูเมืองความได้เปรียบที่คู่แข่งเลียนแบบไม่ได้ (Economic Moat)
3. ความแข็งแกร่งของงบการเงิน กระแสเงินสด และภาระหนี้สิน (Financial Health, Cash Flow & Debt Structure)
4. ความเสี่ยงเรื่องเทรนด์อนาคตและการถูก Disruption (Disruption Risk & Future Trends)
5. ความโปร่งใสของผู้บริหารและประสิทธิภาพการจัดสรรเงินทุน (Capital Allocation, ROE/ROIC & Corporate Governance)
6. ปัจจัยเร่ง (Catalysts)
7. ความคุ้มค่าของราคาปัจจุบันเทียบกับมูลค่าที่แท้จริง และ Margin of Safety (Valuation & MOS)
8. สัญญาณอันตรายที่เป็นเงื่อนไขในการขายหุ้นทิ้ง (Red Flags & Exit Criteria)
9. โครงสร้างอำนาจการต่อรอง และความเสี่ยงการพึ่งพาลูกค้า/ซัพพลายเออร์รายใหญ่ (Bargaining Power & Concentration Risk)
10. ความเป็นวัฏจักรของธุรกิจ และอำนาจในการปรับขึ้นราคา (Cyclicality & Pricing Power)

[สรุปปิดท้าย]
- สรุปกระแสข่าวและสถานะปัจจุบันของหุ้นตัวนี้ไปทาง "ดี" หรือ "แย่"?
- เหมาะกับการลงทุน "ระยะสั้น (เก็งกำไร)" หรือ "ระยะยาว (ลงทุน)" ดีกว่ากัน พร้อมเหตุผลชัดเจน?
- สรุปประเมินภาพรวมจากการเชื่อมโยง 7 แหล่งข้อมูลทางเลือก (AltIndex, Google Trends, Similarweb, Unusual Whales, Quiver Quant, TradingView, Bloomberg Deals)
"""

            with st.spinner("กำลังให้ AI วิเคราะห์ข้อมูล... กรุณารอแปปเดียวนะครับ"):
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                st.markdown(response.text)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
else:
    st.info(" พิมพ์ชื่อหุ้น API Key mrc test 1' ")
