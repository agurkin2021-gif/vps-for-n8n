#!/usr/bin/env python3
"""Conservative native-Vietnamese editorial polish; preserves HTML structure and technical values."""
from pathlib import Path
import sys
from _vi_translate_full import PAGES,ROOT,validate

GLOBAL=[
 ("n8n Đám mây","n8n Cloud"),
 ("n8n đám mây","n8n Cloud"),
 ("Tự lưu trữ","Self-Hosted"),
 ("tự lưu trữ","tự host"),
 ("Chế độ xếp hàng","Queue Mode"),
 ("Chế độ hàng đợi","Queue Mode"),
 ("chế độ xếp hàng","Queue Mode"),
 ("chế độ hàng đợi","Queue Mode"),
 ("Proxy ngược","Reverse proxy"),
 ("proxy ngược","reverse proxy"),
]

PER_PAGE={
"vi/index.html":[
 ("VPS cho n8n từ $0.07/Day - Hướng dẫn về Kế hoạch &amp; Định cỡ","VPS cho n8n từ $0.07/Day — Hướng dẫn chọn cấu hình và quy mô"),
 ("Biến cấu hình của bạn thành thứ tự VPS","Biến cấu hình của bạn thành một đơn hàng VPS"),
 ("Khi VPS là lựa chọn phù hợp cho n8n","Khi nào VPS là lựa chọn phù hợp cho n8n?"),
 ("Bắt đầu với một trường hợp. Thêm công nhân khi cần thiết.","Bắt đầu với một instance. Thêm worker khi cần."),
 ("Bạn phải trả bao nhiêu khi tự tổ chức n8n","Bạn thực sự phải trả những gì khi tự host n8n?"),
 ("Thêm RAM, thêm CPU hoặc thay đổi quy trình làm việc?","Cần thêm RAM, thêm CPU hay thay đổi workflow?"),
],
"vi/vps-n8n-tot-nhat.html":[
 ("VPS tốt nhất cho n8n trong 2026: 6 Các nhà cung cấp được so sánh","VPS tốt nhất cho n8n năm 2026: So sánh 6 nhà cung cấp"),
 ("VPS tốt nhất cho n8n: tùy chọn nhà cung cấp 6","VPS tốt nhất cho n8n: 6 lựa chọn nhà cung cấp"),
 ("Tiêu chí phân biệt n8n VPS tốt với không phù hợp","Tiêu chí phân biệt VPS phù hợp với n8n và một lựa chọn không phù hợp"),
 ("Các đề xuất ngắn gọn mà không cần giả vờ rằng một nhà cung cấp sẽ thắng mọi thứ","Gợi ý ngắn theo từng nhu cầu, không giả định một nhà cung cấp phù hợp với mọi trường hợp"),
 ("Lựa chọn nhà cung cấp không phải là kích thước máy chủ","Chọn nhà cung cấp và chọn cấu hình máy chủ là hai quyết định khác nhau"),
],
"vi/about.html":[
 ("phạm vi biên tập","Phạm vi biên tập"),
],
"vi/sao-luu-khoi-phuc-n8n.html":[
 ("n8n Sao lưu và khôi phục","Sao lưu và khôi phục n8n"),
 ("Xuất hợp lý và khắc phục thảm họa hoàn toàn","Export logic và khôi phục sau thảm họa toàn diện"),
 ("Sao lưu cơ sở dữ liệu một cách nhất quán","Sao lưu cơ sở dữ liệu nhất quán"),
 ("Bản sao lưu trên cùng VPS chỉ là bản sao cục bộ","Bản sao lưu trên cùng VPS vẫn chỉ là một bản sao cục bộ"),
 ("Bản sao lưu không được chứng minh cho đến khi khôi phục thành công","Bản sao lưu chỉ đáng tin cậy sau khi đã khôi phục thử thành công"),
],
"vi/contact.html":[
 ("Trạng thái liên hệ","Thông tin liên hệ"),
],
"vi/cai-n8n-tren-vps.html":[
 ("Chuẩn bị VPS trước khi bắt đầu n8n","Chuẩn bị VPS trước khi cài n8n"),
 ("Đặt bí mật và URL công khai có chủ ý","Cấu hình secret và URL công khai một cách có chủ đích"),
 ("Kiên trì n8n và PostgreSQL riêng biệt","Lưu dữ liệu n8n và PostgreSQL bền vững, tách biệt"),
 ("Xác minh tính bền vững trước khi sử dụng sản xuất","Xác minh dữ liệu persistent trước khi đưa vào production"),
],
"vi/n8n-cloud-vs-self-host.html":[
 ("n8n Đám mây so với Tự lưu trữ: Chi phí &amp; Kiểm soát","n8n Cloud vs Self-Hosted: Chi phí &amp; quyền kiểm soát"),
 ("n8n Đám mây và Tự lưu trữ","n8n Cloud vs Self-Hosted"),
 ("n8n Cloud so với VPS: sự khác biệt làm thay đổi quyết định","n8n Cloud vs VPS: những khác biệt ảnh hưởng trực tiếp đến quyết định"),
 ("n8n Đám mây so với tự lưu trữ VPS: bảng so sánh","n8n Cloud vs VPS tự host: bảng so sánh"),
 ("Cách một lịch trình đơn giản có thể sử dụng trợ cấp thực thi trên Đám mây","Một lịch chạy đơn giản có thể tiêu tốn hạn mức execution trên Cloud như thế nào?"),
 ("Một cú nhấp chuột n8n VPS không phải lúc nào cũng là dịch vụ được quản lý","VPS n8n one-click không phải lúc nào cũng là managed service"),
 ("Tự lưu trữ không chỉ là hóa đơn VPS","Tự host không chỉ là hóa đơn VPS"),
],
"vi/cau-hinh-vps-n8n.html":[
 ("n8n VPS Yêu cầu","Yêu cầu VPS cho n8n"),
 ("Sản xuất tối thiểu, thực tế và khối lượng công việc nặng hơn","Mức tối thiểu, production thực tế và workload nặng hơn"),
 ("Thông số kỹ thuật VPS thực để so sánh với khối lượng công việc n8n của bạn","Thông số VPS thực tế để đối chiếu với workload n8n của bạn"),
 ("Điều gì thực sự tiêu tốn tài nguyên máy chủ","Những gì thực sự tiêu tốn tài nguyên máy chủ"),
 ("Ước tính n8n lưu trữ lịch sử thực thi trước khi đặt hàng","Ước tính dung lượng cho lịch sử execution của n8n trước khi đặt VPS"),
 ("Docker và chi phí sản xuất","Docker và overhead production"),
],
"vi/privacy.html":[
 ("Chính sách bảo mật | n8nVPS","Chính sách quyền riêng tư | n8nVPS"),
 ("Phân tích và liên kết liên kết","Analytics và liên kết affiliate"),
],
"vi/bao-mat-n8n-vps.html":[
 ("Đường cơ sở bảo mật tối thiểu trước khi tiếp xúc với công chúng","Mức bảo mật nền tảng tối thiểu trước khi public ra Internet"),
 ("Giữ các dịch vụ phụ trợ ở chế độ riêng tư","Giữ các dịch vụ backend ở chế độ private"),
 ("Bảo vệ khóa mã hóa và ranh giới thông tin xác thực","Bảo vệ encryption key và phạm vi credential"),
 ("Các nút có thể mở rộng ranh giới bảo mật","Các node có thể mở rộng ranh giới bảo mật"),
 ("Bảo mật là một quá trình hoạt động","Bảo mật là một quy trình vận hành liên tục"),
 ("Bảo mật ngăn xếp trước khi kích hoạt quy trình sản xuất","Bảo mật toàn bộ stack trước khi bật workflow production"),
],
"vi/n8n-queue-mode.html":[
 ("n8n Chế độ xếp hàng","n8n Queue Mode"),
 ("Bạn có thực sự cần chế độ xếp hàng không?","Bạn có thực sự cần Queue Mode không?"),
 ("Mọi nhu cầu triển khai ở chế độ hàng đợi","Những thành phần mọi deployment Queue Mode đều cần"),
 ("Công nhân mở rộng quy mô cả theo số lượng và theo công việc trên mỗi công nhân","Khả năng xử lý được mở rộng theo số worker và concurrency trên mỗi worker"),
 ("Chế độ hàng đợi có thể thêm độ trễ chuyển giao thực thi","Queue Mode có thể làm tăng độ trễ khi bàn giao execution"),
 ("Đừng bỏ qua bộ nhớ dùng chung","Đừng bỏ qua shared storage"),
 ("Biết liệu hàng đợi có giúp ích được không","Đo lường xem Queue Mode có thực sự giúp ích hay không"),
 ("Quy mô một nút thắt tại một thời điểm","Scale từng bottleneck một"),
]
}

def polish(i):
    en,vi=PAGES[i]
    p=ROOT/vi
    text=p.read_text(encoding="utf-8")
    before=text;hits=0
    for old,new in PER_PAGE.get(vi,[]):
        n=text.count(old)
        if n:text=text.replace(old,new);hits+=n
    for old,new in GLOBAL:
        n=text.count(old)
        if n:text=text.replace(old,new);hits+=n
    validate((ROOT/en).read_text(encoding="utf-8"),text,en,vi)
    if text!=before:p.write_text(text,encoding="utf-8")
    print("VIETNAMESE_NATIVE_POLISH",i+1,"/11",vi,"replacements",hits,flush=True)

if __name__=="__main__":
    if len(sys.argv)!=2 or not sys.argv[1].isdigit():raise SystemExit("Usage: python _vi_native_polish.py PAGE_INDEX")
    i=int(sys.argv[1])
    if not 0<=i<len(PAGES):raise SystemExit("Page out of range")
    polish(i)
