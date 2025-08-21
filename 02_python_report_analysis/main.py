from typing import Dict, List, TypedDict, Annotated, Any
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("...")

# Load environment variables
load_dotenv()

# Define state type
class AnalysisState(TypedDict):
    hr_data: List[Dict]
    financial_data: List[Dict]
    analysis: str
    summary: str
    html: str

# Node 1 prompt - Data Analysis
NODE1_PROMPT = """Phân tích dữ liệu tài chính và nhân sự được cung cấp của Công ty cổ phần MISA trong năm 2025.
Ngày phân tích: {current_date}

Dữ liệu nhân sự:
{hr_data}

Dữ liệu tài chính:
{financial_data}

Yêu cầu:
1. Phân tích xu hướng hàng tháng về số lượng nhân viên và doanh thu
2. Xác định những thay đổi hoặc mô hình đáng chú ý
3. Tính toán các chỉ số quan trọng như tỷ lệ tăng trưởng
4. Đưa ra các nhận định chuyên môn về hiệu suất công ty
5. Sử dụng các con số và tỷ lệ phần trăm cụ thể trong phân tích
6. Cấu trúc phản hồi rõ ràng với các phần và điểm chính

Vui lòng cung cấp một bài phân tích chi tiết, chuyên nghiệp kết nối dữ liệu nhân sự và tài chính để đưa ra những hiểu biết có ý nghĩa về hiệu suất của công ty."""

# Node 2 prompt - Summary and Recommendations
NODE2_PROMPT = """Dựa trên phân tích trước đó, hãy cung cấp bản tóm tắt ngắn gọn tập trung vào ba lĩnh vực chính:

Phân tích trước đó:
{previous_analysis}

Vui lòng cung cấp:
1. Điểm tích cực:
   - Liệt kê 3-5 điểm mạnh và xu hướng tích cực chính được xác định từ dữ liệu
   - Hỗ trợ mỗi điểm bằng dữ liệu cụ thể

2. Điểm cần cải thiện:
   - Xác định 3-5 thách thức chính hoặc xu hướng đáng lo ngại
   - Chứng minh mỗi điểm bằng dữ liệu liên quan

3. Khuyến nghị chiến lược:
   - Đưa ra 3-5 khuyến nghị khả thi cho doanh nghiệp
   - Mỗi khuyến nghị phải giải quyết các thách thức cụ thể đã được xác định
   - Bao gồm cả đề xuất ngắn hạn và dài hạn

Định dạng phản hồi của bạn thành các phần rõ ràng với các điểm chính."""

# Node 3 prompt - HTML Formatting
NODE3_PROMPT = """Chuyển đổi bài phân tích kinh doanh sau đây thành tài liệu HTML.
Sử dụng định dạng HTML phù hợp để tạo báo cáo rõ ràng, dễ đọc.

Tiêu đề: Công ty cổ phần MISA - Báo cáo phân tích Tài chính và Nhân sự năm 2025
Ngày phân tích: {current_date}

Nội dung cần định dạng:
{content}

Yêu cầu:
1. Sử dụng phông chữ và kiểu dáng chuyên nghiệp
2. Bao gồm hệ thống tiêu đề phù hợp
3. Định dạng danh sách và điểm dữ liệu rõ ràng
4. Thêm khoảng cách và lề phù hợp
5. Sử dụng bảng màu chuyên nghiệp
6. Đảm bảo nội dung được tổ chức tốt và dễ đọc

Tạo tài liệu HTML hoàn chỉnh với cấu trúc và kiểu dáng phù hợp."""

# Function to load data
def load_data() -> tuple[List[Dict], List[Dict]]:
    hr_path = Path("hr_data.json")
    financial_path = Path("financial_data.json")
    
    with open(hr_path) as f:
        hr_data = json.load(f)
    with open(financial_path) as f:
        financial_data = json.load(f)
        
    return hr_data, financial_data

# Node functions
def analyze_data(state: AnalysisState) -> AnalysisState:
    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
    )
    prompt = ChatPromptTemplate.from_template(NODE1_PROMPT)
    chain = prompt | llm
    
    from datetime import datetime
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    response = chain.invoke({
        "hr_data": json.dumps(state["hr_data"], indent=2),
        "financial_data": json.dumps(state["financial_data"], indent=2),
        "current_date": current_date
    })
    
    state["analysis"] = str(response.content)
    return state

def generate_summary(state: AnalysisState) -> AnalysisState:
    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
    )
    prompt = ChatPromptTemplate.from_template(NODE2_PROMPT)
    chain = prompt | llm
    
    response = chain.invoke({
        "previous_analysis": str(state["analysis"])
    })
    
    state["summary"] = str(response.content)
    return state

def generate_html(state: AnalysisState) -> AnalysisState:
    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
    )
    prompt = ChatPromptTemplate.from_template(NODE3_PROMPT)
    chain = prompt | llm
    
    from datetime import datetime
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    # Combine analysis and summary
    content = f"""Công ty cổ phần MISA - Báo cáo phân tích Tài chính và Nhân sự năm 2025
Ngày phân tích: {current_date}

BÁO CÁO PHÂN TÍCH:
{str(state['analysis'])}

TÓM TẮT VÀ KHUYẾN NGHỊ:
{str(state['summary'])}
"""
    
    # Save content to text file
    with open("MISA_Analysis_Report_2025.txt", "w", encoding="utf-8") as f:
        f.write(content)
        print("Text content has been saved to MISA_Analysis_Report_2025.txt")
    
    response = chain.invoke({
        "content": str(content),
        "current_date": current_date
    })
    
    html_content = str(response.content)
    # Remove ```html marks if present
    if html_content.startswith("```html"):
        html_content = html_content[8:]  # Remove ```html prefix
    if html_content.endswith("```"):
        html_content = html_content[:-3]  # Remove ``` suffix
    
    state["html"] = html_content.strip()
    return state

def generate_pdf(state: AnalysisState) -> AnalysisState:
    # Save HTML file
    html_file = "MISA_Analysis_Report_2025.html"
    pdf_file = "MISA_Analysis_Report_2025.pdf"
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(state["html"])
    
    # Convert HTML to PDF using xhtml2pdf
    from xhtml2pdf import pisa
    
    try:
        # Ensure HTML content has proper structure
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 40px;
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #444;
            margin-top: 30px;
        }}
        p {{
            margin-bottom: 15px;
        }}
        ul, ol {{
            margin-bottom: 20px;
        }}
        .content {{
            max-width: 1000px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="content">
        {state["html"]}
    </div>
</body>
</html>"""
        
        with open(pdf_file, "wb") as output_pdf:
            success = pisa.CreatePDF(
                html_content,
                dest=output_pdf,
                encoding='utf-8'
            )
        
        if success:
            print(f"PDF file generated successfully: {pdf_file}")
        else:
            print("Warning: Some errors occurred during PDF conversion")
            print("HTML file has been saved as an alternative.")
    except Exception as e:
        print(f"Warning: Could not generate PDF file. Error: {str(e)}")
        print("HTML file has been saved as an alternative.")
    
    return state

# Build the graph
def build_graph():
    # Create the graph
    workflow = StateGraph(AnalysisState)
    
    # Add nodes
    workflow.add_node("analyze", analyze_data)
    workflow.add_node("summarize", generate_summary)
    workflow.add_node("html", generate_html)
    workflow.add_node("pdf", generate_pdf)
    
    # Define edges
    workflow.add_edge("analyze", "summarize")
    workflow.add_edge("summarize", "html")
    workflow.add_edge("html", "pdf")
    workflow.add_edge("pdf", END)
    
    # Set entry point
    workflow.set_entry_point("analyze")
    
    return workflow.compile()

def main():
    # Load data
    hr_data, financial_data = load_data()
    
    # Create workflow
    workflow = build_graph()
    
    # Create initial state
    initial_state: AnalysisState = {
        "hr_data": hr_data,
        "financial_data": financial_data,
        "analysis": "",
        "summary": "",
        "html": ""
    }
    
    # Run workflow
    result = workflow.invoke(initial_state)
    
    print("Analysis complete! Results have been saved as TEXT, HTML, and PDF files.")

if __name__ == "__main__":
    main()
