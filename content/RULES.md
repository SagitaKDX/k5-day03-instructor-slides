# Rules: Day 03

Các luật 1 đến 6 lấy từ README lab Day 03. Mục "Dùng AI" và "Làm nhóm" áp dụng quy ước chung của khóa (RULES Day 02), cần key coach xác nhận.

## Luật của lab

1. **Một giả thuyết mỗi phiên bản.** Chỉ sửa `artifacts/system_prompt.md` hoặc `artifacts/tools.yaml`; sửa một thứ, chạy lại, so metric trước và sau.
2. **Không sửa case trong `data/eval_base.json`.** Run có eval base bị sửa coi như không hợp lệ.
3. **Đổi tên tool phải đồng bộ ba nơi:** `artifacts/tools.yaml`, `tools/__init__.py` (`TOOL_FUNCTIONS`), `data/eval_base.json` và `data/eval_research_extension.json`. Chạy `pytest tests/test_tool_contract.py` sau mỗi lần đổi.
4. **Unit test chạy offline.** Mock HTTP bằng fixture `fake_http`; `conftest.py` chặn mọi request thật.
5. **Report dựa trên log thật.** Mỗi số liệu trỏ về một file trong `runs/` hoặc `transcripts/`.
6. **Không commit `.env` hay API key.**

## Dùng AI

- Được dùng trợ lý AI để viết code tool, test, UI.
- Reflection (REPORT mục B6) phải tự viết từ trải nghiệm của nhóm.
- Ghi lại mỗi lần dùng AI: dùng làm gì, AI sai ở đâu, nhóm sửa gì.

## Làm nhóm

- Cả nhóm làm trên một repo do nhóm trưởng fork; mời thành viên vào Collaborators ngay từ đầu.
- Mỗi thành viên commit bằng tài khoản GitHub của mình và nộp link repo lên LMS bằng tài khoản LMS của mình.
