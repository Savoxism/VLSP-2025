
RAW_PROMPT = """
Bạn là chuyên gia pháp luật. Tôi sẽ đưa cho bạn:  
1) Một ví dụ vấn đề mẫu ở định dạng JSON, gồm các trường:  
   - id  
   - instruction (str): dạng câu hỏi  
   - question (str): nội dung câu hỏi  
   - answer (str): đáp án  
   - references (dict): các điều luật liên quan và nội dung của chúng  
   - reasoning_path (str): chuỗi mô tả quá trình suy luận  
{JSON}

2) Một văn bản pháp luật để trích dẫn. Bạn có nhiệm vụ tạo ra MỘT câu hỏi mới dưới dạng JSON, bao gồm toàn bộ các trường như mẫu. Đảm bảo rằng:  
- id luôn để -1
- `instruction` giữ nguyên  
- Loại câu hỏi **trắc nghiệm 4 phương án** (A, B, C hoặc D):  
  + Trong trường `question`, phải liệt kê rõ 4 lựa chọn A, B, C và D.  
  + Trường `answer` chỉ chứa **một** trong các giá trị `"A"`, `"B"`, `"C"` hoặc `"D"`.  
- Nội dung `question` & `answer` phải đa dạng và khác biệt so với mẫu.  
- Trường `references` BẮT BUỘC trích đúng các điều luật từ văn bản pháp luật đính kèm, đảm bảo chính xác tên điều và nội dung điều.  

Chỉ xuất ra một JSON object hợp lệ, không thêm bất kỳ chú thích hay văn bản nào khác. Nhắc lại vô cùng quan trọng là câu hỏi phải dựa vào các điều luật trong văn bản đính kèm. Chỉ tạo ra 1 câu hỏi mới.
{DOCUMENT}
"""

REFINEMENT_PROMPT = """Bạn là chuyên gia pháp luật có nhiệm vụ chuẩn hóa câu hỏi trắc nghiệm. Tôi sẽ cung cấp một câu hỏi pháp luật ở định dạng JSON. Câu hỏi này chưa đúng format - cụ thể là chưa liệt kê rõ 4 phương án trả lời A, B, C, D.

Hãy giúp tôi:
1) Dựa vào phần references (điều luật) đã được cung cấp trong JSON để tạo ra 4 phương án trả lời rõ ràng (A, B, C, D)
2) Chỉ định MỘT đáp án đúng duy nhất
3) Đảm bảo các đáp án sai phải hợp lý và có tính phân biệt
4) Trả về cấu trúc JSON đầy đủ, giữ nguyên tất cả các trường khác

Các quy tắc:
- Phần question phải bắt đầu với câu hỏi gốc và sau đó liệt kê 4 lựa chọn A, B, C, D được đánh dấu rõ ràng
- Trường answer chỉ chứa một trong các giá trị: "A", "B", "C" hoặc "D"
- Các đáp án phải liên quan trực tiếp đến nội dung trong phần references
- Đáp án đúng phải phù hợp với nội dung của references
- Thay đổi trường `reasoning_path` để phản ánh quá trình suy luận mới

Dưới đây là câu hỏi cần chuẩn hóa:
{JSON}

Chỉ trả về một JSON object hợp lệ đã được chuẩn hóa, không thêm bất kỳ chú thích hay văn bản nào khác.
"""