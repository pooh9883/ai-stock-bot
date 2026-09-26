import streamlit as st
import yfinance as yf
import google.generativeai as genai
from urllib.parse import urlparse
import time

# 1. ตั้งค่าหน้าตา Streamlit
st.set_page_config(
    page_title="AI Stock Analyzer (10D)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ฟังก์ชันวิเคราะห์หุ้นด้วยโมเดลมาตรฐาน gemini-1.5-flash (ฟรี)
@st.cache_data(ttl=3600, show_spinner=False)
def analyze_stock_with_gemini(api_key, ticker_input, price, pe, f_pe, target, rec, summary, domain):
    genai.configure(api_key=api_key)
    
    # ใช้ gemini-1.5-flash ซึ่งเป็นโมเดลมาตรฐานบน Free Tier
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
คุณคือนักวิเคราะห์การลงทุนระดับสถาบัน จงวิเคราะห์หุ้น [{ticker_input}] จากข้อมูลดังนี้:
- ราคาปัจจุบัน: ${price} | Trailing P/E: {pe} | Forward P/E: {f_pe}
- ราคาเป้าหมายเฉลี่ย: ${target} | คำแนะนำ: {rec}
- สรุปบริษัท: {summary[:800]}

จงเขียนบทวิเคราะห์จัดหมวดหมู่ให้กระชับ อ่านง่าย เป็นข้อๆ ตาม 10 หัวข้อนี้:
1. โมเดลธุรกิจและการสร้างรายได้
2. คูเมืองความได้เปรียบ (Economic Moat)
3. งบการเงิน กระแสเงินสด และหนี้สิน
4. ความเสี่ยงการถูก Disruption
5. ประสิทธิภาพผู้บริหารและการจัดสรรทุน (ROE/ROIC)
6. ปัจจัยเร่ง (Catalysts)
7. ความคุ้มค่าของราคา (Valuation & MOS)
8. สัญญาณอันตราย (Red Flags)
9. โครงสร้างอำนาจการต่อรอง
10. ความเป็นวัฏจักรและอำนาจปรับขึ้นราคา

[สรุปปิดท้าย]
- สรุปสถานะหุ้นว่า "ดี" หรือ "แย่"?
- เหมาะกับการลงทุน "ระยะสั้น" หรือ "ระยะยาว" พร้อมเหตุผล?
"""

    response = model.generate_content(prompt)
    if response and response.text:
        return response.text
    return "ไม่สามารถดึงข้อมูลจาก AI ได้ กรุณาลองใหม่อีกครั้ง"

# 3. ตั้งค่าแถบด้านซ้าย
api_key = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.title("⚙️ ตั้งค่าระบบ")
    if not api_key:
        api_key = st.text_input("กรอก Gemini API Key:", type="password")
    else:
        st.success("✅ เชื่อมต่อ Gemini API แล้ว")
        
    st.markdown("---")
    st.markdown("💡 **ทริกค้นหาหุ้น:** หุ้นไทยใส่ `.BK` (เช่น `PTT.BK`) หุ้นสหรัฐพิมพ์ชื่อย่อได้เลย (เช่น `AAPL`, `MU`)")
    ticker_input = st.text_input("พิมพ์ชื่อหุ้นที่ต้องการดู:", value="MU").upper().strip()
    btn_analyze = st.button("🚀 เริ่มวิเคราะห์หุ้น", use_container_width=True)

# 4. ส่วนแสดงผลหลัก
st.title("📊 AI Stock Analyzer (10-Dimension Dashboard)")

if btn_analyze:
    if not api_key:
        st.error("⚠️ ไม่พบ API Key! กรุณากรอก Gemini API Key ที่แถบด้านซ้าย")
    elif not ticker_input:
        st.warning("⚠️ กรุณากรอกชื่อหุ้นก่อนกดวิเคราะห์")
    else:
        try:
            with st.spinner(f"กำลังค้นหาข้อมูลหุ้น {ticker_input}..."):
                stock = yf.Ticker(ticker_input)
                info = stock.info

                # ตรวจสอบความถูกต้องของข้อมูลหุ้น
                if not info or len(info) < 5 or 'regularMarketPrice' not in info and 'currentPrice' not in info:
                    hist = stock.history(period="1d")
                    if hist.empty:
                        st.error(f"❌ไม่พบข้อมูลหุ้น '{ticker_input}' ในระบบ Yahoo Finance กรุณาตรวจสอบชื่อย่ออีกครั้ง (เช่น หุ้นไทยต้องใส่ .BK)")
                        st.stop()
                    price = hist['Close'].iloc[-1]
                else:
                    price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))

                pe = info.get('trailingPE', 'N/A')
                f_pe = info.get('forwardPE', 'N/A')
                target = info.get('targetMeanPrice', 'N/A')
                rec = str(info.get('recommendationKey', 'N/A')).upper()
                summary = info.get('longBusinessSummary', 'ไม่มีข้อมูลสรุปธุรกิจ')

                website = info.get('website', '')
                domain = urlparse(website).netloc.replace('www.', '') if website else f"{ticker_input.lower()}.com"

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("ราคาปัจจุบัน", f"${price}" if price != 'N/A' else 'N/A')
            col2.metric("Trailing P/E", f"{pe:.2f}" if isinstance(pe, (int, float)) else str(pe))
            col3.metric("Forward P/E", f"{f_pe:.2f}" if isinstance(f_pe, (int, float)) else str(f_pe))
            col4.metric("ราคาเป้าหมายเฉลี่ย", f"${target}" if target != 'N/A' else 'N/A')

            st.markdown("---")

            st.subheader("🌐 ลิงก์เจาะลึก 7 มิติข้อมูล")
            clean_ticker = ticker_input.replace('.BK', '')
            urls = {
                "AltIndex (AI Score)": f"https://altindex.com/ticker/{clean_ticker.lower()}/ai-stock-analysis",
                "Google Trends": f"https://trends.google.com/explore?q={clean_ticker}",
                "TradingView": f"https://www.tradingview.com/symbols/{ticker_input}/",
                "Similarweb": f"https://www.similarweb.com/website/{domain}/",
                "Unusual Whales": f"https://unusualwhales.com/stock/{clean_ticker}/overview?chart=options-volume",
                "Quiver Quant": f"https://www.quiverquant.com/stock/{clean_ticker}/",
                "Bloomberg Deals": "https://www.bloomberg.com/deals"
            }

            c1, c2, c3, c4 = st.columns(4)
            btn_cols = [c1, c2, c3, c4]
            idx = 0
            for name, url in urls.items():
                btn_cols[idx % 4].link_button(name, url, use_container_width=True)
                idx += 1

            st.markdown("---")

            st.subheader(f"🤖 รายงานวิเคราะห์เจาะลึก 10 มิติ: [{ticker_input}]")
            
            with st.spinner("กำลังให้ AI ประมวลผลบทวิเคราะห์ 10 มิติ... (กรุณารอประมาณ 5-10 วินาที)"):
                report = analyze_stock_with_gemini(
                    api_key, ticker_input, price, pe, f_pe, target, rec, summary, domain
                )
                st.markdown(report)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {e}")
else:
    st.info("👈 พิมพ์ชื่อหุ้นที่เมนูด้านซ้าย แล้วกดปุ่ม '🚀 เริ่มวิเคราะห์หุ้น' ได้เลยครับ")
