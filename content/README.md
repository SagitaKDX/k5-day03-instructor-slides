# Nội dung deck

- `build_content.py`: HTML và speaker notes của từng slide. Chạy `python3 -I content/build_content.py` từ thư mục gốc để sinh `app/src/slides/content.json`.
- `icons.json`: SVG Lucide dùng trong slide, sinh bằng `node scripts/build_icons.mjs` (chạy trong `app/`).

## Nguồn sự thật

Deck lấy nội dung từ repo lab [VinUni-AI20k/Day03-Prompt-Engineering-Tool-Calling-Labs-student](https://github.com/VinUni-AI20k/Day03-Prompt-Engineering-Tool-Calling-Labs-student), đồng bộ tới commit `c68da4c`. Quy định chính thức nằm trong repo lab:

- `CHECKPOINTS.md`: 5 checkpoint (CP1 đến CP5) và mốc kiểm tra tại lớp
- `RUBRIC.md`: 100 điểm C1 đến C8, bonus tối đa 10
- `RULES.md`: dùng AI, liêm chính, secret, nộp muộn
- `SUBMISSION.md`: tên repo `K5-L3A-DAY03-TenNhom-ResearchAgentToolEval`, deliverable, deadline 23h59 ngày lab

Khi repo lab thay đổi, cập nhật `build_content.py` theo các file trên rồi chạy lại.
