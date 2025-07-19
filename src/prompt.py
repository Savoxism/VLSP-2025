GENERATE_PROMPT = """
[BỐI CẢNH]
{CONTEXT}

[HƯỚNG DẪN]
Bạn là chuyên gia pháp luật. Thực hiện hai nhiệm vụ:

Bước 1 – Tạo câu hỏi  
• Viết một câu hỏi tình huống thực tiễn xoay quanh bối cảnh trên, yêu cầu người trả lời phải phân tích và kết luận theo quy định pháp luật.

Bước 2 – Trả lời theo cấu trúc pháp lý. Dựa vào Câu hỏi cùng với bối cảnh, hãy xây dựng bài trả lời gồm bốn phần bắt buộc:
  1. Tiền đề lớn: Trích dẫn chính xác điều, khoản, điểm, tên văn bản (luật/nghị định/thông tư) điều chỉnh tình huống.
  2. Tiền đề nhỏ: Tóm tắt ngắn gọn các chi tiết then chốt của tình huống liên quan tới Tiền đề lớn.
  3. Kết luận: Khẳng định cuối cùng về quyền/nghĩa vụ hoặc hậu quả pháp lý.
  4. Giải thích: Phân tích vì sao điều kiện của tình huống đủ hoặc chưa đủ để phát sinh quyền lợi/hậu quả theo luật. Nêu rõ mọi yếu tố bổ sung có thể làm thay đổi kết quả.

[ĐỊNH DẠNG ĐẦU RA]
Xuất ra một JSON với 7 trường sau:
  id: -1

  verification_status: "unchecked"

  câu_hỏi: <Câu hỏi bạn vừa tạo>  

  tiền_đề_lớn: <Điều … khoản …, Luật/ Nghị định …>  

  tiền_đề_nhỏ: <Tóm tắt tình huống>  

  kết_luận: <Kết luận hợp pháp>  

  giải_thích: <Phân tích chi tiết theo luật và tình huống>  


Bạn chỉ trả về CHÍNH XÁC một object JSON, KHÔNG kèm text nào khác.

[MẪU]
Dưới đây là một mẫu để tham khảo:
{JSON}
"""

VERIFICATION_PROMPT = """
[HƯỚNG DẪN]
Bạn là chuyên gia pháp luật. Kiểm tra tính nhất quán logic giữa kết luận và các thành phần khác trong câu hỏi pháp lý được cung cấp.

[DỮ LIỆU ĐẦU VÀO]
{JSON}

[HƯỚNG DẪN]
Hãy phân tích câu hỏi pháp lý và kiểm tra xem "kết_luận" có thể được suy ra một cách hợp lý từ các thành phần sau hay không:
1. câu_hỏi (nêu vấn đề pháp lý)
2. tiền_đề_lớn (căn cứ pháp lý, điều luật)
3. tiền_đề_nhỏ (tóm tắt tình huống)
4. giải_thích (phân tích chi tiết)

Tiêu chí đánh giá:
- Kết luận phải phù hợp với nội dung của câu hỏi
- Kết luận phải dựa trên các căn cứ pháp lý được nêu trong tiền đề lớn
- Kết luận phải áp dụng đúng pháp luật vào tình huống cụ thể trong tiền đề nhỏ
- Kết luận phải được hỗ trợ bởi phần giải thích

[ĐỊNH DẠNG ĐẦU RA]
Trả về JSON với cấu trúc đầy đủ như dữ liệu đầu vào, trong đó:

1. Nếu kết luận hợp lý và nhất quán:
   {{
     "verification_status": "pass",
     ... (giữ nguyên tất cả các trường từ dữ liệu đầu vào)
   }}

2. Nếu kết luận cần sửa:
   {{
     "id": -1,
     "verification_status": "fixed",
     "câu_hỏi": "...",
     "tiền_đề_lớn": "...",
     "tiền_đề_nhỏ": "...",
     "kết_luận": "... (kết luận đã được sửa) ...",
     "giải_thích": "... (giải thích đã được điều chỉnh nếu cần) ..."
   }}

3. Nếu có vấn đề nghiêm trọng về logic hoặc nội dung:
   {{
     "verification_status": "error",
     "error_message": "... (mô tả vấn đề) ...",
     ... (giữ nguyên các trường gốc)
   }}

Hãy trả về CHÍNH XÁC một JSON object duy nhất.
"""



