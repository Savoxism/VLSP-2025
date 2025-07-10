GENQA_PROMPT = """
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
- Nội dụng `question` & `answer` phải đa dạng và khác biệt so với mẫu
- Trường `references` BẮT BUỘC trích đúng các điều luật từ văn bản pháp luật đính kèm, đảm bảo chính xác tên điều và nội dung điều.

Chỉ xuất ra một JSON object, không thêm bất kỳ chú thích hay văn bản nào khác. Nhắc lại vô cùng quan trọng là câu hỏi phải dựa vào các điều luật trong văn bản đính kèm. Chỉ tạo ra 1 câu hỏi mới.
{DOCUMENT}
"""
