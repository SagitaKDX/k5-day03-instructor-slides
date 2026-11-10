# Submission: Day 03

> README lab Day 03 chưa có `SUBMISSION.md`. Tên repo, nộp LMS và deadline dưới đây áp dụng quy ước chung của khóa, giống `SUBMISSION.md` và `RULES.md` của Day 02. Hậu tố bài cần key coach chốt.

## Loại bài

Bài nhóm. Cả nhóm làm chung một repo do nhóm trưởng fork. Mỗi thành viên nộp link repo đó lên LMS bằng tài khoản của mình.

## Tên repo

```text
K5-<L3A hoặc L3B>-DAY03-HoVaTen-MSSV-PromptEngineeringToolCalling
```

Ví dụ nhóm trưởng Nguyễn Văn An, MSSV 20241234, lớp L3A: `K5-L3A-DAY03-NguyenVanAn-20241234-PromptEngineeringToolCalling`.

Không dấu, không khoảng trắng, nối bằng `-`, ngày học hai chữ số (`DAY03`). `HoVaTen-MSSV` là của nhóm trưởng.

## File phải nộp (trong `starter_v0/`, theo README lab)

- `artifacts/system_prompt.md`
- `artifacts/tools.yaml`
- `artifacts/version_log.csv`, ít nhất `v0`, `v1`, `v2`, `v3`
- `artifacts/REPORT.md`: Phần A xong trước 16:30, Phần B nộp sau
- `artifacts/poster.html` hoặc `poster.svg` (tùy chọn)
- `data/eval_group.json`
- `tests/`: unit test cho tool mới
- `runs/*.json`
- `transcripts/*.transcript.json`
- `analysis/*.csv` nếu có parse log
- Code tool và UI nhóm đã thêm hoặc sửa
- Nếu làm Small Local Model Challenge: run JSON của model local, prompt và tools riêng cho local (nếu có)

Không nộp `.env` hay API key.

## Deadline (GMT+7)

- Lab sáng: trước 23h59 ngày học.
- Lab chiều hoặc tối: trước 11h59 ngày hôm sau.
- Chấm theo commit cuối cùng trước deadline. Key coach có thể gia hạn tối đa 48 giờ, thông báo trên LMS.
