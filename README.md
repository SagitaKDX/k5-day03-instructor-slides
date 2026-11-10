# K5 Day 03: Instructor Slides (React)

Deck giảng viên **Prompt Engineering và Tool Calling: Research Agent Tool Eval**, cùng khung với deck Day 02 (Vite + React, timer theo checkpoint, ghi chú giảng viên).

Nội dung lấy từ repo lab `VinUni-AI20k/Day03-Prompt-Engineering-Tool-Calling-Labs-student`. Logo Vingroup và VinUniversity cắt từ trang https://vinuni.edu.vn/aithucchien/.

## Sửa nội dung

Nội dung slide nằm trong `content/build_content.py` (HTML của từng slide và speaker notes). Sửa file này rồi sinh lại JSON:

```bash
python3 -I content/build_content.py
```

## Dev

```bash
cd app
npm install
npm run dev
```

## Build (GitHub Pages subpath)

```bash
cd app
npm run build
# output: app/dist, base path /k5-day03-instructor-slides/
```

## Lớp sáng và lớp chiều

Deck tự chọn ca theo giờ máy lúc mở trang, và không tự đổi giữa buổi:

- Mở trước 13:00: **lớp sáng**, 08:30 đến 12:30.
- Mở từ 13:00: **lớp chiều**, 13:30 đến 17:30 (giờ gốc trong README lab).

Lớp sáng dùng cùng lịch, dời sớm 5 tiếng: mọi mốc giờ trên slide và trong ghi chú tự đổi, hạn nộp của ca hiện tại được tô đậm. Nút ca trên header đổi tay và ghi vào link (`?ca=sang` hoặc `?ca=chieu`) để reload hay chia sẻ vẫn giữ đúng ca.

Lớp sáng bắt đầu giờ khác thì sửa `MORNING_SHIFT_HOURS` trong `app/src/session.ts`.

## Phím tắt

| Phím | Việc |
|------|------|
| ← → / Space | Đổi slide |
| P / R | Dừng hoặc chạy timer / đặt lại |
| M | Âm báo |
| B | Nhạc nền |
| N | Ghi chú giảng viên |
| F | Toàn màn hình |

Timer tự chạy khi mở slide CP1 (30 phút), CP2 (30 phút), CP3 (30 phút), CP4 (60 phút). Âm báo và nhạc nền mặc định tắt. `prefers-reduced-motion` tắt chuyển động và nhạc.

## Kiểm tra thiết kế

- Hallmark `sloplint`: 0 FAIL, 0 REFLEX.
- Impeccable `detect` trên dev server, cả `?ca=sang` và `?ca=chieu`: không có finding.
- Tiếng Việt được AGY (Gemini 3.8 Flash) biên tập; đã kiểm tra tự động rằng code, lệnh, đường dẫn, giờ, số liệu và mã case không đổi.
