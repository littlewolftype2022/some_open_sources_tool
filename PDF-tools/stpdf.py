# # 保存为 pdf_page_extractor.py
# import streamlit as st
# from PyPDF2 import PdfReader, PdfWriter
# import io
# import re
#
# st.set_page_config(page_title="PDF页面提取工具", page_icon="📄", layout="centered")
#
# st.title("📄 PDF 页面提取工具")
# st.markdown("上传 PDF，输入要提取的页码（如 `1,3,5-8`），下载提取后的新文件。")
#
# uploaded_file = st.file_uploader("选择一个 PDF 文件", type="pdf")
#
# def parse_pages(pages_str, total_pages):
#     """解析用户输入的页码字符串为整数列表"""
#     pages = set()
#     for part in re.split(r"[,\s]+", pages_str.strip()):
#         if "-" in part:
#             start, end = part.split("-")
#             try:
#                 start, end = int(start), int(end)
#                 pages.update(range(start, end + 1))
#             except ValueError:
#                 pass
#         else:
#             try:
#                 pages.add(int(part))
#             except ValueError:
#                 pass
#     # 过滤掉超出范围的页码
#     return [p for p in sorted(pages) if 1 <= p <= total_pages]
#
# if uploaded_file:
#     reader = PdfReader(uploaded_file)
#     total_pages = len(reader.pages)
#     st.info(f"文件共有 **{total_pages}** 页")
#
#     pages_str = st.text_input("输入要提取的页码", value="1")
#     if st.button("提取并下载"):
#         page_list = parse_pages(pages_str, total_pages)
#         if not page_list:
#             st.error("请输入有效的页码")
#         else:
#             writer = PdfWriter()
#             for page_num in page_list:
#                 writer.add_page(reader.pages[page_num - 1])
#             output_pdf = io.BytesIO()
#             writer.write(output_pdf)
#             output_pdf.seek(0)
#
#             st.success(f"已提取 {len(page_list)} 页")
#             st.download_button(
#                 label="下载提取后的 PDF",
#                 data=output_pdf,
#                 file_name="extracted_pages.pdf",
#                 mime="application/pdf"
#             )
# 保存为 pdf_page_extractor_with_preview.py
# 保存为 st_pdf_extract.py
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import pytesseract
from PIL import Image
import io, re

st.set_page_config(page_title="PDF提取工具", page_icon="📄", layout="centered")
st.title("📄 PDF 页面 & 文字提取工具")

def parse_pages(pages_str, total_pages):
    """解析用户输入的页码字符串为整数列表"""
    pages = set()
    for part in re.split(r"[,\s]+", pages_str.strip()):
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                pages.update(range(start, end + 1))
            except:
                pass
        else:
            try:
                pages.add(int(part))
            except:
                pass
    return [p for p in sorted(pages) if 1 <= p <= total_pages]

uploaded_file = st.file_uploader("选择一个 PDF 文件", type="pdf")

if uploaded_file:
    # 读取 PDF
    reader = PdfReader(uploaded_file)
    total_pages = len(reader.pages)
    st.info(f"文件共有 **{total_pages}** 页")

    pages_str = st.text_input("输入要提取的页码/区间（如 1,3,5-7,10-12）", value="")

    # 提取 PDF 按钮
    if st.button("提取 PDF"):
        page_list = parse_pages(pages_str, total_pages)
        if not page_list:
            st.error("请输入有效的页码")
        else:
            writer = PdfWriter()
            for p in page_list:
                writer.add_page(reader.pages[p - 1])
            output_pdf = io.BytesIO()
            writer.write(output_pdf)
            output_pdf.seek(0)

            st.success(f"已提取 {len(page_list)} 页")
            st.download_button(
                label="下载提取后的 PDF",
                data=output_pdf,
                file_name="../extracted_pages.pdf",
                mime="application/pdf"
            )

    # 提取文字按钮
    if st.button("提取文字（OCR）"):
        page_list = parse_pages(pages_str, total_pages)
        if not page_list:
            st.error("请输入有效的页码")
        else:
            text_result = []
            for p in page_list:
                # 将 PDF 页面转为图片（PyPDF2 无法直接 OCR，需要渲染）
                # 这里用 Pillow 从 PDF 渲染，支持中文 OCR
                page_obj = reader.pages[p - 1]
                text_from_pdf = page_obj.extract_text()  # 尝试直接提取
                if not text_from_pdf.strip():
                    # 如果 PDF 不是文本型，则用 OCR
                    from pdf2image import convert_from_bytes
                    images = convert_from_bytes(uploaded_file.read(), dpi=200, first_page=p, last_page=p)
                    text_from_pdf = pytesseract.image_to_string(images[0], lang="chi_sim")
                text_result.append(f"--- 第 {p} 页 ---\n{text_from_pdf}\n")

            text_data = "\n".join(text_result)
            st.success("文字提取完成")
            st.download_button(
                label="下载文字 TXT",
                data=text_data.encode("utf-8"),
                file_name="../extracted_text.txt",
                mime="text/plain"
            )
