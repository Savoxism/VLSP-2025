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
[HƯỚNG DẪN XÁC MINH]
Bạn được cung cấp một object JSON sau:
{JSON}
Hãy kiểm tra xem kết_luận có thể được suy ra hợp lệ từ câu_hỏi, tiền_đề_lớn, tiền_đề_nhỏ và giải_thích hay không.
Nếu phù hợp, trường verification_status = "valid", ngược lại = "invalid".
Các trường khác phải giữ nguyên.
"""



