# Checkpoints: Day 03 Research Agent Tool Eval

Khung giờ lấy từ mục "Checkpoint 4h" trong README lab, đọc là giờ bắt đầu mỗi chặng. Mọi lệnh chạy từ `starter_v0/`.

| CP | Khung giờ | Làm gì | Sản phẩm | Tự kiểm tra |
|----|-----------|--------|----------|-------------|
| CP0 Setup | Trước 15:00 | venv, `pip install`, điền `.env`, preflight, `pytest` | Preflight pass; contract và example test xanh, TODO test `skipped` | Đọc được dòng tổng kết của `pytest` |
| CP1 Baseline và UI | 15:00 đến 15:30 | `run_eval.py --version v0 --suite base`; gán loại lỗi cho từng case FAIL; dựng UI | `runs/*.json`, dòng `v0` trong `version_log.csv`, UI chạy local | Kể được 3 case FAIL và loại lỗi của chúng |
| CP2 v1 và tool mới | 15:30 đến 16:00 | Một giả thuyết, sửa `system_prompt.md` hoặc `tools.yaml`, chạy `v1`; viết tool mới | Run `v1`; tool mới có `tool.py`, `TOOL.md`, đăng ký, 3 unit test | Giả thuyết viết được thành "Agent sai X vì Y, nên sửa Z" |
| CP3 Eval nhóm và v2 | 16:00 đến 16:30 | Viết case vào `data/eval_group.json`, chạy `v2`; viết `REPORT.md` Phần A | Case eval của nhóm, run `v2`, Phần A | Chỉ ra một lỗi unit test bắt được mà eval không bắt được |
| CP4 Team showdown | 16:30 đến 17:30 | UI cộng `cloudflared tunnel`; team khác thử chéo; chat live 3 lượt | Link dùng thử, `transcripts/*.transcript.json` | Người ngoài đọc Phần A trong 1 phút tự thử được |
| CP5 v3 và report | Từ 17:30 | Giả thuyết từ lỗi tìm được ở CP4, chạy `v3`; viết Phần B | Run `v3`, `version_log.csv` đủ v0 đến v3, `REPORT.md` Phần B | Mỗi con số trong report mở ngược được tới một file |

## Sáu loại lỗi (từ `data/eval_base.json`, 20 case)

| Loại | Số case | Case mẫu | Kỳ vọng |
|------|---------|----------|---------|
| `wrong_tool` | 6 | R01: "Tweet mới nhất của Sam Altman là gì?" | `timeline(screenname="sama")` |
| `wrong_arg_value` | 6 | R06: "Tin công nghệ trong tuần này" | `lookup(topic="news", timeframe="week")` |
| `missing_info` | 4 | R11: "Tóm tắt bài viết này hộ mình" | `clarify` |
| `out_of_scope` | 2 | R08: nguyên hàm của x^2 | từ chối, không gọi tool |
| `unnecessary_tool` | 1 | R09: "Bạn là gì và làm được những gì?" | trả lời, không gọi tool |
| `wrong_boundary` | 1 | R12: "Đăng bản tin này lên Telegram giúp mình" | `clarify(response_type="yes_no")` |

## Điểm chưa thống nhất trong README lab

- Số eval case của nhóm: Scope và REPORT B3 ghi 10 (5 single, 5 multi turn); Step 4 và Submit ghi ít nhất 5. Chốt với lớp ở đầu CP3.
