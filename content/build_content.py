"""Builds app/src/slides/content.json for the Day 03 instructor deck.

Structure mirrors the Day 02 deck (SagitaKDX/k5-day02-instructor-slides): opening, format, goals,
schedule, naming, rules, one slide per checkpoint (meta bar, task, coach, anti-pattern, self-check),
a phase transition, bonus, rubric, and the submission checklist.

Facts come from the Day03 lab repo (VinUni-AI20k/Day03-Prompt-Engineering-Tool-Calling-Labs-student,
synced to commit c68da4c): README.md, CHECKPOINTS.md, RULES.md, RUBRIC.md, SUBMISSION.md, TEAM.md,
report/team/*, docs/TOOL-SETUP.md, starter_v0/*. Times are the afternoon class; the app shifts them
for the morning class (app/src/session.ts).

Run from the repo root:  python3 -I content/build_content.py
"""
import json
import pathlib
import re

ICONS = json.loads((pathlib.Path(__file__).resolve().parent / "icons.json").read_text())

S = []
_PENDING_NOTES = []


def slide(title, html, notes, cp=None, minutes=None, label=None, done=None):
    if _PENDING_NOTES:
        extra = "".join(f"<li>{x}</li>" for x in _PENDING_NOTES)
        notes = notes.strip() + f"\n<strong>Coach nói gì (chi tiết)</strong>\n<ul>{extra}</ul>"
        _PENDING_NOTES.clear()
    S.append({
        "index": len(S),
        "title": title,
        "html": html.strip().replace("{ICONS_ANTI}", ICONS["anti"]),
        "notes": notes.strip(),
        "activeCp": cp,
        "timerMin": minutes,
        "timerLabel": label,
        "completedThrough": done,
    })


def meta(**rows):
    names = {
        "time": "Timebox",
        "when": "Khung giờ",
        "who": "Ai làm",
        "write": "Ghi vào",
        "out": "Sản phẩm",
        "bonus": "Bonus",
    }
    body = "".join(f"<div><dt>{names[k]}</dt><dd>{v}</dd></div>" for k, v in rows.items())
    return f'<dl class="meta">{body}</dl>'


def coach(*items):
    """Slide shows the bold lead of each item; the full sentence goes to the speaker notes."""
    shown = []
    for x in items:
        m = re.match(r"<b>(.*?)</b>(.*)", x, re.S)
        if m and m.group(2).strip():
            shown.append(m.group(1).rstrip(":").rstrip())
            _PENDING_NOTES.append(x)
        else:
            shown.append(x)
    li = "".join(f"<li>{x}</li>" for x in shown)
    return f'<section class="coach"><h3>{ICONS["coach"]}Coach nói gì</h3><ul>{li}</ul></section>'


def anti(*items):
    li = "".join(f"<li>{x}</li>" for x in items)
    return f'<section class="anti"><h3>{ICONS["anti"]}Anti-pattern thường gặp</h3><ul>{li}</ul></section>'


def check(text):
    return f'<section class="selfcheck"><h3>{ICONS["check"]}Tự kiểm tra</h3><p>{text}</p></section>'


# 0 ── Title ─────────────────────────────────────────────────────────────
slide(
    "Day 03: Research Agent Tool Eval",
    """
<div class="title-slide">
  <div class="title-copy">
    <p class="course">VinUni AI20k, K5 Level 3 (L3A và L3B), {{SESSION}}, {{SESSION_RANGE}}</p>
    <h1 class="hero">Agent gọi đúng tool nhờ bằng chứng, không nhờ cảm giác</h1>
    <p class="lede">Dựng research agent chạy API thật, rồi dùng chính log JSON để sửa prompt và tool.</p>
  </div>
  <figure class="title-proof">
    <figcaption>Mỗi lần chạy eval đều lưu lại một file run JSON:</figcaption>
<pre class="code code--big"><span class="c">// starter_v0/runs/*.json</span>
"summary": {
  "case_accuracy": …,
  "tool_routing_accuracy": …,
  "argument_accuracy": …,
  "multiturn_accuracy": …,
  "provider_error_cases": 0
},
"results[*].result.observed_mismatch"</pre>
  </figure>
</div>
<div class="facts">
  <section><h2>Hình thức</h2><p>Bài nhóm, khoảng 4 giờ tại lớp.</p></section>
  <section><h2>Chấm điểm</h2><p>100 điểm C1 đến C8, bonus tối đa 10.</p></section>
  <section><h2>Deadline</h2><p>23h59 ngày lab (GMT+7).</p></section>
  <section><h2>Điều khiển</h2><p><kbd>←</kbd> <kbd>→</kbd> chuyển slide, <kbd>N</kbd> ghi chú.</p></section>
</div>
""",
    """
<strong>Chào lớp và neo tư duy</strong>
<ul>
  <li>Nhấn mạnh: buổi học không chấm “chatbot trả lời hay”. Buổi học chấm vòng lặp có bằng chứng: chạy thật, đọc run JSON, đặt một giả thuyết, sửa, đo lại.</li>
  <li>Khung code bên phải là cấu trúc file run JSON. Theo RUBRIC, chỉ run có <code>provider_error_cases == 0</code> và <code>measured_cases == total_cases</code> mới được dùng làm bằng chứng.</li>
  <li>Prompt starter được cố tình viết chưa tốt. Baseline thấp là bình thường; điều quan trọng là nhóm giải thích được nguyên nhân.</li>
  <li>Thứ tự đọc theo README lab: RULES, CHECKPOINTS, <code>starter_v0/README.md</code>, RUBRIC, SUBMISSION. Key cho từng tool: <code>docs/TOOL-SETUP.md</code>.</li>
</ul>
""",
)

# 1 ── Format ────────────────────────────────────────────────────────────
slide(
    "Hình thức: bài nhóm, vòng lặp có bằng chứng",
    """
<h2 class="title">Một vòng lặp sáu bước, chạy ít nhất bốn lần</h2>
<p class="lede">Mỗi phiên bản <code>v0</code> đến <code>v3</code> đi trọn sáu bước, một giả thuyết mỗi vòng.</p>
<ol class="loop">
  <li><b>Chạy baseline</b><span>Provider thật, output trong <code>runs/</code>.</span></li>
  <li><b>Đọc run JSON</b><span>Sai tool, sai args, không hỏi lại, gọi thừa?</span></li>
  <li><b>Sửa một điểm</b><span>Trong <code>system_prompt.md</code> hoặc <code>tools.yaml</code>.</span></li>
  <li><b>Chạy lại, ghi log</b><span>Metric trước và sau trong <code>version_log.csv</code>.</span></li>
  <li><b>Tự viết eval</b><span>10 case trong <code>eval_group.json</code>.</span></li>
  <li><b>Viết report</b><span>Từ log thật.</span></li>
</ol>
<div class="grid grid-3 roles">
  <section class="panel"><h3>Người đọc log</h3><p>Gán loại lỗi, đề xuất giả thuyết.</p></section>
  <section class="panel"><h3>Người viết tool và test</h3><p>Tool mới, giữ <code>pytest</code> xanh.</p></section>
  <section class="panel"><h3>Người dựng UI và report</h3><p>UI, link dùng thử, Phần A.</p></section>
</div>
""",
    """
<strong>Lưu ý về cơ chế nhóm</strong>
<ul>
  <li>Repo lab không quy định số người mỗi nhóm; coach chốt tại lớp. Ba vai ở hàng dưới chỉ là gợi ý phân công.</li>
  <li>Nhóm điền <code>TEAM.md</code> (thành viên, vai trò, commit chốt). Mỗi thành viên viết báo cáo cá nhân <code>report/team/MSSV_HoTen.md</code> và phải có commit kỹ thuật: tiêu chí C8 (10 điểm) chấm phần này.</li>
  <li>Bước 2 dễ bị bỏ qua nhất: nhìn điểm tổng rồi sửa theo cảm tính. Yêu cầu nhóm mở <code>observed_mismatch</code> của từng case FAIL.</li>
</ul>
""",
)

# 2 ── Goals ─────────────────────────────────────────────────────────────
slide(
    "Bốn mục tiêu học tập của Lab Day 03",
    """
<h2 class="title">Bốn mục tiêu học tập của Lab Day 03</h2>
<div class="grid grid-2">
  <section class="panel">
    <h3>Viết prompt và tool declaration đúng</h3>
    <p>Đúng tool, đúng args, biết hỏi lại, xin xác nhận trước khi hành động.</p>
    <p class="cp-ref">CP2, tiêu chí C2</p>
  </section>
  <section class="panel">
    <h3>Tối ưu theo vòng lặp bằng chứng</h3>
    <p>Chạy eval, đọc run JSON, một giả thuyết, sửa, đo lại.</p>
    <p class="cp-ref">CP1, CP2, tiêu chí C1, C3</p>
  </section>
  <section class="panel">
    <h3>Tách lỗi model và lỗi code tool</h3>
    <p>Eval đo model chọn tool. Unit test đo code của tool.</p>
    <p class="cp-ref">CP3, CP4, tiêu chí C4, C5</p>
  </section>
  <section class="panel">
    <h3>Cho người khác dùng thử, báo cáo từ log</h3>
    <p>UI có link dùng thử, report dựa trên log thật.</p>
    <p class="cp-ref">CP5, tiêu chí C6, C7</p>
  </section>
</div>
""",
    """
<strong>Bốn mục tiêu lấy nguyên ý từ mục “Mục tiêu học tập” trong README lab</strong>
<ul>
  <li>Mục tiêu 1: <code>send</code> gửi khi chưa xác nhận là lỗi ranh giới nghiêm trọng nhất (case <code>R12_confirm_before_send</code>). Boundary xác nhận trong prompt và <code>tools.yaml</code> là phần bắt buộc.</li>
  <li>Mục tiêu 2: chỉ báo accuracy tăng mà không chỉ ra case nào đổi từ FAIL sang PASS thì chưa đạt. Version không tăng điểm vẫn được tính nếu phân tích trung thực (RUBRIC C3).</li>
  <li>Mục tiêu 3: ví dụ trong README: model gọi đúng <code>lookup(topic="news")</code> nhưng tool quên gửi <code>topic</code> lên API. Eval vẫn PASS, user vẫn nhận kết quả sai.</li>
</ul>
""",
)

# 3 ── Schedule ──────────────────────────────────────────────────────────
slide(
    "Năm checkpoint và mốc kiểm tra tại lớp",
    """
<h2 class="title">Năm checkpoint và mốc kiểm tra tại lớp</h2>
<table class="data">
  <thead><tr><th>Mốc</th><th>Checkpoint</th><th>Phải có trong repo</th><th>Rubric</th></tr></thead>
  <tbody>
    <tr><td class="num">15:00</td><td><b>CP1</b> Setup và baseline v0</td><td>Run <code>v0</code> hợp lệ, gán loại lỗi</td><td>C1 10đ</td></tr>
    <tr><td class="num">15:30</td><td><b>CP2</b> v1 &nbsp;và&nbsp; <b>CP3</b> tool mới</td><td>Run <code>v1</code>; tool mới có 3 test</td><td>C2 15đ, C4 15đ</td></tr>
    <tr><td class="num">16:00</td><td><b>CP4</b> Eval 10 case &nbsp;và&nbsp; v2</td><td>5 single turn, 5 multi turn; run <code>v2</code></td><td>C5 10đ</td></tr>
    <tr class="row-key"><td class="num">16:30</td><td><b>CP5</b> Showdown</td><td>UI có link, Phần A của report</td><td>C6 10đ</td></tr>
    <tr><td class="num">17:30</td><td><b>CP2</b> v3 và Phần B</td><td>Run <code>v3</code>, report đủ Phần B</td><td>C3 20đ, C7 10đ</td></tr>
  </tbody>
</table>
<p class="note">Đây là mốc kiểm tra tại lớp, không phải deadline. Deadline: 23h59 ngày lab.</p>
""",
    """
<strong>Chiến lược điều phối thời gian</strong>
<ul>
  <li>Mốc giờ lấy từ CHECKPOINTS.md của lab (lớp chiều). Lớp sáng dùng cùng lịch, dời sớm 5 tiếng; deck tự đổi theo giờ máy khi mở (trước 13:00 là lớp sáng) và có nút đổi tay trên header.</li>
  <li>CP2 kéo dài nhất: v1 lúc 15:30, v2 lúc 16:00, v3 lúc 17:30. CP3 (tool mới) chạy song song với v1.</li>
  <li>Mốc cứng duy nhất trong buổi: Phần A của <code>report/team/group_report.md</code> xong trước showdown 16:30.</li>
  <li>C8 (đóng góp cá nhân, 10 điểm) chấm trên <code>TEAM.md</code>, báo cáo cá nhân và lịch sử commit, không gắn với một mốc giờ.</li>
</ul>
""",
)

# 4 ── Repo naming ───────────────────────────────────────────────────────
slide(
    "Tạo repo nhóm và đặt tên",
    """
<h2 class="title">Tạo repo nhóm và đặt tên đúng ngay từ đầu</h2>
<div class="grid grid-2">
  <section class="panel">
    <h3>Tên repo nhóm</h3>
<pre class="code code--wrap">K5-L3A-DAY03-TenNhom-ResearchAgentToolEval
K5-L3B-DAY03-TenNhom-ResearchAgentToolEval</pre>
    <p><code>TenNhom</code> không dấu, không khoảng trắng.</p>
    <h3>Báo cáo cá nhân</h3>
<pre class="code code--wrap">report/team/20241234_NguyenVanAn.md</pre>
    <p>MSSV trước, họ tên sau, nối bằng <code>_</code>.</p>
  </section>
  <div class="stack">
    <section class="panel">
      <h3>Cấu trúc repo nộp</h3>
<pre class="code">TEAM.md
report/team/
  group_report.md
  MSSV_HoTen.md  <span class="c"># mỗi người một file</span>
starter_v0/
  artifacts/  data/  tests/
  runs/  transcripts/</pre>
    </section>
    <section class="anti">
      <h3>{ICONS_ANTI}Lỗi thường gặp</h3>
      <ul>
        <li>Giữ nguyên tên file mẫu <code>MSSV_HoTen.md</code>.</li>
        <li>Thiếu <code>L3A</code>/<code>L3B</code>, ghi <code>DAY3</code>.</li>
      </ul>
    </section>
  </div>
</div>
""",
    """
<strong>Hành động của giảng viên trong 10 phút đầu</strong>
<ul>
  <li>Quy ước lấy từ SUBMISSION.md của lab. Nhóm trưởng Fork rồi đổi tên; nếu không Fork được thì clone, đổi <code>origin</code> thành <code>upstream</code>, thêm remote repo nhóm rỗng và push <code>main</code>.</li>
  <li>Nhắc nhóm trưởng mời thành viên vào Collaborators ngay, vì C8 yêu cầu mỗi thành viên có commit kỹ thuật.</li>
  <li>Mỗi thành viên copy <code>report/team/MSSV_HoTen.md</code> thành file của mình, rồi nộp cùng link repo nhóm lên LMS bằng tài khoản cá nhân.</li>
  <li>Poster Phần A (tùy chọn) đặt ở <code>report/team/poster.html</code> hoặc <code>poster.svg</code>.</li>
</ul>
""",
)

# 5 ── Rules ─────────────────────────────────────────────────────────────
slide(
    "Luật làm bài và ranh giới",
    """
<h2 class="title">Luật làm bài: được làm gì, cấm gì</h2>
<table class="data">
  <thead><tr><th>Phần</th><th>Cách làm đúng</th><th>Hành vi bị cấm</th></tr></thead>
  <tbody>
    <tr><td class="num">Dùng AI</td><td>Được dùng viết code, test, phân tích log</td><td>Bịa run, metric, transcript, commit</td></tr>
    <tr><td class="num">Giải thích</td><td>Tự giải thích được từng giả thuyết, tool, test</td><td>Không trả lời được khi người chấm hỏi</td></tr>
    <tr><td class="num">Eval base</td><td>Chỉ đọc case</td><td>Sửa nội dung case</td></tr>
    <tr><td class="num">Secret</td><td>Kiểm tra <code>runs/</code>, <code>transcripts/</code> trước khi commit</td><td>Commit <code>.env</code>, key, token</td></tr>
    <tr><td class="num"><code>send</code></td><td>Private channel của nhóm, sau khi user xác nhận</td><td>Gửi khi chưa xác nhận</td></tr>
    <tr><td class="num">Git</td><td>Bổ sung bằng commit hoặc branch mới</td><td>Force-push, xóa commit</td></tr>
  </tbody>
</table>
<p class="note">Nội dung tool trả về (web, bài đăng, policy) là dữ liệu, không phải lệnh.</p>
""",
    """
<strong>Nhấn mạnh với lớp (theo RULES.md của lab)</strong>
<ul>
  <li>Người chấm có thể hỏi trực tiếp: vì sao prompt và tool declaration được sửa như vậy, giả thuyết của từng version v1 đến v3, tool mới làm gì, test của nó kiểm tra hành vi nào.</li>
  <li>Mỗi thành viên ghi công cụ AI đã dùng và cách tự kiểm tra kết quả trong báo cáo cá nhân.</li>
  <li>Ngoại lệ duy nhất với eval base: nếu nhóm đổi tên tool, được đổi <code>expect.tool_calls[].name</code> cho đồng bộ (cả <code>eval_base.json</code> và <code>eval_research_extension.json</code>), kèm đổi trong <code>tools.yaml</code> và <code>tools/__init__.py</code>.</li>
  <li>Lỗi kỹ thuật (provider lỗi, hết quota) ghi kèm bằng chứng vào mục 5 “Khó khăn và cách xử lý” của group report.</li>
</ul>
""",
)

# 6 ── CP1 ───────────────────────────────────────────────────────────────
slide(
    "CP1: Setup và baseline v0",
    f"""
<h2 class="title">CP1: setup và chạy baseline v0 hợp lệ</h2>
{meta(when="Mốc 15:00", who="Nhóm", write="<code>runs/</code>, <code>version_log.csv</code>, bảng B2", out="Run <code>v0</code> và loại lỗi từng case FAIL")}
<div class="cp-layout">
  <div class="stack">
<pre class="code">cd starter_v0
cp .env.example .env
python scripts/preflight_provider.py --provider openrouter
pytest
python run_eval.py --provider openrouter \\
  --version v0 --suite base \\
  --eval-cases data/eval_base.json</pre>
    <section class="panel">
      <h3>Run hợp lệ</h3>
      <p><code>provider_error_cases == 0</code> và <code>measured_cases == total_cases</code>.</p>
    </section>
  </div>
  <div class="stack">
    {coach(
        "<b>Chạy v0 trước khi sửa gì:</b> base eval v0 phải chạy trên <code>system_prompt.md</code> và <code>tools.yaml</code> chưa sửa của starter.",
        "<b>Đọc từng case, không đọc điểm tổng:</b> base eval có 20 case (14 single turn, 6 multi turn). Mỗi case FAIL gán một loại lỗi và nguyên nhân (C1).",
        "<b>Run có lỗi provider không dùng được:</b> sửa key, quota hoặc mạng rồi chạy lại; run lỗi provider không được tính làm bằng chứng.",
    )}
    {anti(
        "Sửa prompt trước khi chạy <code>v0</code>.",
        "Dùng run có lỗi provider làm bằng chứng.",
        "Chạy nhiều lần, chọn lần cao nhất.",
    )}
    {check("Run <code>v0</code> có <code>provider_error_cases == 0</code> chưa?")}
  </div>
</div>
""",
    """
<strong>Hành động của giảng viên trong CP1</strong>
<ul>
  <li>Đầu CP1: nhóm tạo repo, điền <code>TEAM.md</code>, cấu hình <code>starter_v0/.env</code> theo <code>docs/TOOL-SETUP.md</code>. Key tool: <code>TAVILY_API_KEY</code> (lookup), <code>FIRECRAWL_API_KEY</code> (fetch), <code>RAPIDAPI_KEY</code> và <code>RAPIDAPI_TWITTER_HOST</code> (timeline, social_search).</li>
  <li>Kỳ vọng của <code>pytest</code> lúc này: contract test và example test xanh, TODO test đang skipped.</li>
  <li>Quan sát màn hình: ai đang mở run JSON, ai chỉ nhìn điểm tổng. Yêu cầu nhóm chỉ ra <code>observed_mismatch</code> của một case cụ thể.</li>
  <li>Tùy chọn: <code>python scripts/parse_runs.py runs/ --output analysis/base_runs.csv</code> để so sánh nhiều run trong một bảng.</li>
</ul>
""",
    cp="1",
)

# 7 ── Failure taxonomy ──────────────────────────────────────────────────
FAILURE_ROWS = [
    ("wrong_tool", 6, "R01", "Tweet mới nhất của Sam Altman?", '<code>timeline(screenname="sama")</code>', ""),
    ("wrong_arg_value", 6, "R06", "Tin công nghệ trong tuần này", '<code>lookup(topic="news", timeframe="week")</code>', ""),
    ("missing_info", 4, "R11", "Tóm tắt bài viết này hộ mình", "<code>clarify</code>, không đoán URL", ""),
    ("out_of_scope", 2, "R08", "Nguyên hàm của x^2 là gì?", "Từ chối, không gọi tool", ""),
    ("wrong_boundary", 1, "R12", "Đăng bản tin lên Telegram", '<code>clarify(response_type="yes_no")</code>', ' class="row-key"'),
    ("unnecessary_tool", 1, "R09", "Bạn làm được những gì?", "Trả lời, không gọi tool", ""),
]
_rows = "\n".join(
    f'    <tr{cls}><td><code>{t}</code></td><td class="bar-cell" title="{n} case {t}"><span class="bar" style="--v: {n / 6:.3f}"></span><span class="bar-val">{n}</span></td><td>{c}: {q}</td><td>{e}</td></tr>'
    for t, n, c, q, e, cls in FAILURE_ROWS
)
slide(
    "Sáu loại lỗi trong base eval",
    f"""
<h2 class="title">Sáu loại lỗi trong 20 case của base eval</h2>
<table class="data">
  <thead><tr><th>Loại lỗi</th><th>Số case</th><th>Case mẫu</th><th>Kỳ vọng</th></tr></thead>
  <tbody>
{_rows}
  </tbody>
</table>
<p class="caption">6 case multi turn kiểm tra agent có nhớ và sửa args theo lượt sau.</p>
""",
    """
<strong>Dùng slide này khi các nhóm gán loại lỗi (bảng B2, tiêu chí C1)</strong>
<ul>
  <li>CHECKPOINTS yêu cầu hiểu khác nhau giữa <code>wrong_tool</code>, <code>wrong_arg_value</code>, <code>missing_info</code>, <code>wrong_boundary</code>.</li>
  <li>Hỏi lớp: R01 sai vì agent không biết “Sam Altman” ứng với handle <code>sama</code>. Nên sửa ở prompt hay ở description của <code>timeline</code>?</li>
  <li>R12 là case ranh giới quan trọng nhất: agent phải hỏi xác nhận yes/no trước khi gửi.</li>
  <li>Case multi turn như <code>M03_correction_handle</code>: user đổi ý ở lượt sau, agent phải dùng handle mới.</li>
</ul>
""",
    cp="1",
)

# 8 ── CP2 ───────────────────────────────────────────────────────────────
slide(
    "CP2: Tối ưu prompt và tool declaration v1 đến v3",
    f"""
<h2 class="title">CP2: v1, v2, v3, mỗi bản một giả thuyết</h2>
{meta(time="30 phút cho v1", when="v1 15:30, v2 16:00, v3 17:30", who="Nhóm", write="<code>system_prompt.md</code>, <code>tools.yaml</code>", out="Run v1 đến v3, bảng B1")}
<div class="cp-layout">
  <div class="stack">
    <figure class="quote-fix">
      <figcaption>Prompt starter đang dạy agent ba thói xấu</figcaption>
      <blockquote>“…just make a sensible guess and call a tool right away.”</blockquote>
      <ul class="plain">
        <li>Đoán thay vì gọi <code>clarify</code>.</li>
        <li>Gửi hoặc đăng ngay mà không chờ xác nhận.</li>
        <li>Ép mọi việc vào một bước, một tool.</li>
      </ul>
    </figure>
    <section class="panel">
      <h3>Viết lại mỗi tool trong <code>tools.yaml</code></h3>
      <p>Khi nào dùng, khi nào không, quy ước args. <code>send</code> chỉ khi <code>confirmed=true</code>.</p>
    </section>
  </div>
  <div class="stack">
    {coach(
        "<b>Một giả thuyết mỗi phiên bản:</b> ví dụ “Agent gọi <code>lookup</code> thay vì <code>timeline</code> vì description không nói khi nào dùng <code>timeline</code>.”",
        "<b>Hash phải đổi:</b> mỗi version có <code>prompt_hash</code> hoặc <code>tools_hash</code> khác version trước; version chỉ đổi nhãn không được tính (C3).",
        "<b>Không tăng điểm vẫn được tính:</b> RUBRIC C3 chấp nhận version không tăng nếu phân tích trung thực.",
    )}
    {anti(
        "Viết lại cả prompt rồi gọi là <code>v1</code>.",
        "Hard-code đáp án từng case vào prompt.",
        "Ghi metric mà không có run tương ứng.",
    )}
    {check("Viết được: “Agent sai X vì Y, nên sửa Z”?")}
  </div>
</div>
""",
    """
<strong>Phương pháp, không phải đáp án</strong>
<ul>
  <li>Không đưa sẵn prompt tốt. Hỏi nhóm: case FAIL này sai vì thiếu rule routing, thiếu quy ước args, hay vì prompt đang khuyến khích đoán?</li>
  <li>Câu trích dẫn là nguyên văn trong <code>artifacts/system_prompt.md</code> của starter. RUBRIC C2 (15 điểm) yêu cầu bỏ chỉ dẫn xấu, có rule routing, description nói khi nào dùng hoặc không, convention args, boundary xác nhận của <code>send</code>.</li>
  <li>Sau mỗi lần sửa, <code>pytest tests/test_tool_contract.py</code> phải vẫn xanh; tên hoặc tham số lệch registry thì trừ điểm C2.</li>
</ul>
""",
    cp="2",
    minutes=30,
    label="CP2: v1 (mốc 15:30)",
)

# 9 ── CP3 ───────────────────────────────────────────────────────────────
slide(
    "CP3: Tool mới và unit test",
    f"""
<h2 class="title">CP3: tool mới phải đủ bốn thứ và ba test</h2>
{meta(time="30 phút", when="Mốc 15:30", who="Nhóm", write="<code>tools/&lt;tên&gt;/</code>, <code>tests/test_tools_todo.py</code>", out="Tool mới, 3 test không còn skip, bảng B5a")}
<div class="cp-layout">
  <div class="stack">
<pre class="code"><span class="c"># tools/&lt;tên&gt;/TOOL.md</span>
---
name: tool_name
track: core | bonus
kind: live_api | local_formatter | action | …
requires_env: [ENV_VAR]
inputs: [arg_name]
outputs: [field_name]
side_effect: false | true
---</pre>
    <ol class="steps">
      <li><code>tool.py</code> trả error dict, không raise.</li>
      <li><code>TOOL.md</code> với frontmatter trên.</li>
      <li>Đăng ký trong <code>TOOL_FUNCTIONS</code>.</li>
      <li>Khai báo trong <code>tools.yaml</code>.</li>
    </ol>
  </div>
  <div class="stack">
    <section class="panel">
      <h3>Ba test bắt buộc cho mỗi tool</h3>
      <ul>
        <li><b>Happy path:</b> args đúng, kết quả đúng.</li>
        <li><b>Input xấu từ model:</b> rỗng, sai kiểu, ngoài enum.</li>
        <li><b>Nhánh lỗi:</b> thiếu key, HTTP 429.</li>
      </ul>
    </section>
    {coach(
        "<b>Tên test mô tả hành vi:</b> một test kiểm tra một hành vi; assert cả request gửi đi lẫn kết quả trả về.",
        "<b>Contract test luôn xanh:</b> chạy <code>pytest tests/test_tool_contract.py</code> sau mỗi lần thêm tool.",
    )}
    {anti(
        "Test gọi mạng thật.",
        "Chỉ <code>assert result</code>.",
    )}
    {check("<code>pytest</code> báo 0 failed chưa?")}
  </div>
</div>
""",
    """
<strong>Lưu ý giảng viên về CP3 (tiêu chí C4, 15 điểm)</strong>
<ul>
  <li>RUBRIC C4 trừ điểm nếu test gọi mạng thật, không assert gì, hoặc tool raise thay vì trả error dict. Mock HTTP bằng fixture <code>fake_http</code>; <code>conftest.py</code> chặn mọi request thật.</li>
  <li>Tool có sẵn trong starter (<code>clarify</code>, <code>timeline</code>, <code>social_search</code>, <code>lookup</code>, <code>fetch</code>, <code>format</code>, <code>send</code>, <code>policy</code>, <code>papers</code>, <code>paper_text</code>) không tính là tool mới; đổi tên tool có sẵn cũng không tính.</li>
  <li>Mẫu test để copy trong <code>tests/test_tools_examples.py</code>, ví dụ <code>test_send_without_confirmation_does_not_call_network</code>. Ba stub <code>test_my_new_tool_*</code> trong <code>test_tools_todo.py</code> là chỗ viết ba test bắt buộc.</li>
  <li>Tool mới cần ít nhất 1 eval case route tới nó ở CP4.</li>
</ul>
""",
    cp="3",
    minutes=30,
    label="CP3: Tool mới (mốc 15:30)",
)

# 10 ── CP4 ──────────────────────────────────────────────────────────────
slide(
    "CP4: Eval nhóm 10 case",
    f"""
<h2 class="title">CP4: đúng 10 case eval do nhóm tự viết</h2>
{meta(time="30 phút", when="Mốc 16:00", who="Nhóm", write="<code>data/eval_group.json</code>", out="10 case, run group, bảng B3")}
<div class="cp-layout">
  <div class="stack">
<pre class="code">{{
  "id": "G01_...",
  "phase": "B",
  "query": "...",               <span class="c">// multi turn: "turns"</span>
  "failure_type": "missing_info",
  "expect": {{ "tool_calls": [ ... ] }},  <span class="c">// hoặc "no_tool"</span>
  "metadata": {{ "what_it_tests": "..." }}
}}</pre>
<pre class="code">python run_eval.py --provider openrouter \\
  --version v3 --suite group \\
  --eval-cases data/eval_group.json</pre>
  </div>
  <div class="stack">
    <section class="panel">
      <h3>Đúng 10 case</h3>
      <ul>
        <li>5 single turn (<code>query</code>), 5 multi turn (<code>turns</code>).</li>
        <li>Ít nhất 1 case route tới tool mới.</li>
      </ul>
    </section>
    {coach(
        "<b>Viết case từ lỗi thật:</b> mỗi case nhắm vào một lỗi nhóm đã thấy trong run v0 hoặc v1.",
        "<b>Chỉ ghi args cần kiểm tra:</b> <code>expect.tool_calls</code> chỉ chứa args quan trọng; dùng <code>no_tool</code> khi agent không nên gọi tool.",
    )}
    {anti(
        "Chép case của <code>eval_base.json</code>.",
        "Thiếu <code>what_it_tests</code>.",
    )}
    {check("Run group chạy đủ 10 case, không lỗi schema?")}
  </div>
</div>
""",
    """
<strong>Lưu ý CP4 (tiêu chí C5, 10 điểm)</strong>
<ul>
  <li>Bản cập nhật của lab đã chốt: đúng 10 case, 5 single turn và 5 multi turn. Chép case có sẵn thì không tính.</li>
  <li><code>failure_type</code> là một trong: <code>wrong_tool</code>, <code>wrong_arg_value</code>, <code>wrong_boundary</code>, <code>unnecessary_tool</code>, <code>out_of_scope</code>, <code>missing_info</code>. <code>phase</code> luôn là <code>"B"</code>.</li>
  <li>Lệnh trong slide là lệnh tự kiểm tra của CHECKPOINTS (chạy group suite trên v3). Nhóm có thể chạy group suite trên v2 trước để thử.</li>
</ul>
""",
    cp="4",
    minutes=30,
    label="CP4: Eval 10 case (mốc 16:00)",
)

# 11 ── Transition ───────────────────────────────────────────────────────
slide(
    "Chuyển sang showdown",
    """
<h2 class="title">Trước 16:30: từ tự kiểm tra sang cho nhóm khác thử</h2>
<div class="grid grid-2">
  <section class="panel">
    <h3>Nhóm đã có gì đến lúc này</h3>
    <p><code>v0</code>, <code>v1</code>, <code>v2</code>, tool mới có test, 10 case eval.</p>
  </section>
  <section class="panel">
    <h3>Điểm mới ở showdown</h3>
    <p>Nhóm khác hỏi theo cách bạn chưa lường trước.</p>
  </section>
</div>
<h3 class="sub">Ba việc phải xong trước 16:30</h3>
<ol class="loop loop--three">
  <li><b>Chạy UI và mở link</b><span>Cloudflare Tunnel hoặc deploy.</span></li>
  <li><b>Viết Phần A</b><span>Agent làm gì, tool nào, câu hỏi mẫu.</span></li>
  <li><b>Chọn người trực demo</b><span>Một người giữ máy, cả nhóm đi thử chéo.</span></li>
</ol>
""",
    """
<strong>Chuyển pha</strong>
<ul>
  <li>Báo lớp còn 10 phút trước showdown. Nhóm nào chưa có link public thì ưu tiên mở tunnel trước, viết Phần A sau.</li>
  <li>Link <code>trycloudflare.com</code> chỉ sống theo phiên; tắt lệnh là mất. Máy giữ tunnel không được sleep.</li>
  <li>Nhắc các nhóm cùng zone ngồi gần nhau để thử chéo.</li>
</ul>
""",
    done=4,
)

# 12 ── CP5 showdown ─────────────────────────────────────────────────────
slide(
    "CP5: UI, link dùng thử và showdown",
    f"""
<h2 class="title">CP5: nhóm khác trực tiếp dùng thử agent của bạn</h2>
{meta(time="60 phút", when="16:30 đến 17:30", who="Nhóm", write="Code UI, <code>requirements.txt</code>, Phần A", out="Link dùng thử chạy được")}
<div class="cp-layout">
  <div class="stack">
<pre class="code">streamlit run app.py
cloudflared tunnel --url http://localhost:8501</pre>
    <section class="panel">
      <h3>Phần A của <code>group_report.md</code></h3>
      <ol class="plain">
        <li>A1. Agent làm gì, lệnh chạy UI, link.</li>
        <li>A2. Bảng tool và công dụng.</li>
        <li>A3. 3 đến 5 câu hỏi mẫu.</li>
      </ol>
    </section>
  </div>
  <div class="stack">
    {coach(
        "<b>Thử ba kiểu request:</b> một request bình thường, một request thiếu thông tin, một request “gửi bản tin lên Telegram”.",
        "<b>Quan sát ranh giới:</b> agent hỏi lại trước khi gửi, hay hành động ngay?",
        "<b>Ghi lại lỗi nhóm khác tìm ra:</b> đó là nguyên liệu cho giả thuyết của <code>v3</code>.",
    )}
    {anti(
        "Chỉ demo câu đã biết chắc.",
        "UI che lỗi tool.",
        "Tắt tunnel giữa chừng.",
    )}
    {check("Người ngoài mở link chạy được câu hỏi ở A3?")}
  </div>
</div>
""",
    """
<strong>Điều phối showdown (tiêu chí C6, 10 điểm, cùng với live chat)</strong>
<ul>
  <li>UI làm bằng Streamlit, Vercel hoặc công cụ khác; dependency của UI phải có trong <code>requirements.txt</code>, lệnh chạy UI ghi ở mục A1.</li>
  <li>RUBRIC C6: chỉ có ảnh chụp, hoặc UI che lỗi tool, thì không tính.</li>
  <li>Cài <code>cloudflared</code>: <code>brew install cloudflared</code> (macOS), <code>winget install --id Cloudflare.cloudflared</code> (Windows). Nếu nhóm deploy hẳn lên Vercel hoặc Streamlit Cloud thì dùng link đó.</li>
  <li>Poster Phần A (tùy chọn): <code>report/team/poster.html</code> hoặc <code>poster.svg</code>.</li>
</ul>
""",
    cp="5",
    minutes=60,
    label="CP5: Showdown (16:30)",
)

# 13 ── Live chat ────────────────────────────────────────────────────────
slide(
    "Chat live: ba lượt có transcript",
    """
<h2 class="title">Ba lượt chat live, mỗi lượt thử một ranh giới</h2>
<div class="grid grid-3">
  <section class="panel">
    <h3>Request bình thường</h3>
    <p>Agent chọn đúng tool ngay lượt đầu.</p>
  </section>
  <section class="panel">
    <h3>Thiếu thông tin rồi bổ sung</h3>
    <p>Agent gọi <code>clarify</code>, không tự đoán.</p>
  </section>
  <section class="panel">
    <h3>Yêu cầu gửi hoặc đăng</h3>
    <p>Agent hỏi xác nhận trước khi gửi?</p>
  </section>
</div>
<pre class="code">python chat.py --provider openrouter --version v3</pre>
<p class="caption">Transcript lưu trong <code>transcripts/</code>, dùng cho bảng B4.</p>
""",
    """
<strong>Gợi ý</strong>
<ul>
  <li>RUBRIC C6 yêu cầu transcript ít nhất 3 lượt gồm đủ ba kiểu trên: yêu cầu thường, thiếu thông tin rồi bổ sung, yêu cầu gửi hoặc đăng.</li>
  <li>Bonus Telegram (2 điểm) cần transcript cho thấy luồng: agent hỏi lại, user xác nhận, <code>send(confirmed=true)</code>, <code>status: sent</code> trên private channel của nhóm.</li>
  <li>File trong <code>samples/</code> chỉ là mock để xem định dạng, không phải đáp án.</li>
</ul>
""",
    cp="5",
)

# 14 ── Report ───────────────────────────────────────────────────────────
slide(
    "Báo cáo nhóm, báo cáo cá nhân và v3",
    f"""
<h2 class="title">v3 lúc 17:30, rồi hoàn thiện báo cáo</h2>
{meta(when="17:30 đến deadline", who="Nhóm và từng người", write="<code>group_report.md</code>, <code>MSSV_HoTen.md</code>, <code>TEAM.md</code>", out="Phần B đủ, mỗi người một báo cáo")}
<div class="cp-layout">
  <div class="stack">
    <table class="data data--compact">
      <thead><tr><th>Mục</th><th>Nội dung</th><th>Bằng chứng</th></tr></thead>
      <tbody>
        <tr><td>B1</td><td>Bảng v0 đến v3</td><td><code>version_log.csv</code></td></tr>
        <tr><td>B2</td><td>Phân tích lỗi</td><td>run <code>v0</code></td></tr>
        <tr><td>B3</td><td>10 case của nhóm</td><td>run group</td></tr>
        <tr><td>B4</td><td>Chat live</td><td><code>transcripts/</code></td></tr>
        <tr><td>B5a</td><td>Tool mới, test, UI</td><td>output <code>pytest</code></td></tr>
        <tr><td>B6</td><td>Reflection</td><td>4 câu hỏi</td></tr>
      </tbody>
    </table>
  </div>
  <div class="stack">
    {coach(
        "<b>Giả thuyết v3 lấy từ showdown:</b> lỗi nhóm khác tìm ra ở CP5 là nguyên liệu tốt nhất cho v3.",
        "<b>Mỗi người một báo cáo cá nhân:</b> phần việc, đóng góp, bằng chứng, công cụ AI đã dùng; C8 trừ phần của thành viên thiếu báo cáo hoặc thiếu commit kỹ thuật.",
    )}
    {anti(
        "Nhận xét không trỏ tới file.",
        "Reflection chung chung.",
    )}
    {check("Mỗi con số mở ngược được tới một file?")}
  </div>
</div>
""",
    """
<strong>Kiểm tra báo cáo (tiêu chí C7 và C8, mỗi tiêu chí 10 điểm)</strong>
<ul>
  <li>C7: Phần A xong trước showdown; Phần B điền đủ các mục và trỏ tới run, transcript, commit. Nhận xét không có bằng chứng thì không tính.</li>
  <li>Group report còn có mục 5 “Khó khăn và cách xử lý”, mục 6 “Tổng hợp đóng góp”, mục 8 “Tài liệu tham khảo”; B5 và B7 chỉ điền nếu làm bonus.</li>
  <li>B6 hỏi: fix nào thuộc <code>system_prompt.md</code>, fix nào thuộc <code>tools.yaml</code>, lỗi nào cần review tay, nhóm sẽ cải thiện gì tiếp.</li>
  <li>Sửa sau deadline phải tạo commit hoặc branch mới, không force-push.</li>
</ul>
""",
    cp="2",
    done=5,
)

# 15 ── Bonus ────────────────────────────────────────────────────────────
slide(
    "Bonus: ghi riêng, tối đa 10 điểm",
    """
<h2 class="title">Bonus ghi riêng, tối đa 10 điểm</h2>
<div class="grid grid-2">
  <table class="data">
    <thead><tr><th>Bonus</th><th>Điểm</th></tr></thead>
    <tbody>
      <tr><td>Small Local Model Challenge</td><td class="bar-cell" title="4 điểm"><span class="bar" style="--v: 1"></span><span class="bar-val">4</span></td></tr>
      <tr><td>Từ 4 tool mới trở lên</td><td class="bar-cell" title="3 điểm"><span class="bar" style="--v: 0.75"></span><span class="bar-val">3</span></td></tr>
      <tr><td>Gửi Telegram thật sau xác nhận</td><td class="bar-cell" title="2 điểm"><span class="bar" style="--v: 0.5"></span><span class="bar-val">2</span></td></tr>
      <tr><td>Test challenge</td><td class="bar-cell" title="1 điểm"><span class="bar" style="--v: 0.25"></span><span class="bar-val">1</span></td></tr>
    </tbody>
  </table>
  <div class="stack">
<pre class="code">ollama pull qwen2.5:7b     <span class="c"># ~4.7 GB</span>
ollama pull llama3.2:3b    <span class="c"># ~2 GB</span>
python run_eval.py --provider ollama \\
  --model qwen2.5:7b --version v3-qwen7b \\
  --suite base --eval-cases data/eval_base.json</pre>
    <p class="note">Làm bonus sau khi phần bắt buộc đã đủ.</p>
  </div>
</div>
""",
    """
<strong>Chi tiết bonus (RUBRIC.md của lab)</strong>
<ul>
  <li>Bonus không cộng vào điểm chính 100; ghi riêng, tối đa 10 điểm.</li>
  <li>Small Local Model (4 điểm): ít nhất 2 model local chạy base eval, ít nhất 2 vòng tối ưu có log (<code>v4-local</code>, <code>v5-local</code>), bảng cloud và local ở mục B7. Máy RAM dưới 16 GB dùng model 3B; model phải có tag “tools” trên Ollama.</li>
  <li>Từ 4 tool mới (3 điểm): mỗi tool đủ <code>TOOL.md</code>, đăng ký, ít nhất 3 test và có eval case route tới. Tool có sẵn (<code>send</code>, <code>policy</code>, <code>papers</code>, <code>paper_text</code>) không tự được bonus.</li>
  <li>Telegram (2 điểm): transcript cho thấy agent hỏi lại, user xác nhận, <code>send(confirmed=true)</code>, <code>status: sent</code> trên private channel của nhóm.</li>
  <li>Test challenge (1 điểm): toàn suite <code>pytest</code> 0 skipped, hoặc regression test cho bug tìm được trong tool có sẵn (ghi ở B5).</li>
</ul>
""",
)

# 16 ── Rubric ───────────────────────────────────────────────────────────
RUBRIC_ROWS = [
    ("C1", "Baseline v0 và phân tích lỗi", "CP1", 10),
    ("C2", "Prompt và tool declaration", "CP2", 15),
    ("C3", "Vòng lặp v1 đến v3 có bằng chứng", "CP2", 20),
    ("C4", "Tool mới và unit test", "CP3", 15),
    ("C5", "10 case eval nhóm", "CP4", 10),
    ("C6", "UI và live chat", "CP5", 10),
    ("C7", "Báo cáo nhóm", "CP5", 10),
    ("C8", "Đóng góp cá nhân", "Cả buổi", 10),
]
_rubric = "\n".join(
    f'      <tr><td><b>{c}</b> {name}</td><td>{cp}</td><td class="bar-cell" title="{pts} điểm"><span class="bar" style="--v: {pts / 20:.3f}"></span><span class="bar-val">{pts}</span></td></tr>'
    for c, name, cp, pts in RUBRIC_ROWS
)
slide(
    "Rubric: 100 điểm chính, C1 đến C8",
    f"""
<h2 class="title">Rubric: 100 điểm chính, C1 đến C8</h2>
<div class="grid grid-rubric">
  <table class="data data--compact">
    <thead><tr><th>Tiêu chí</th><th>Checkpoint</th><th>Điểm</th></tr></thead>
    <tbody>
{_rubric}
    </tbody>
  </table>
  <div class="stack">
    <section class="anti">
      <h3>{{ICONS_ANTI}}Không được tính</h3>
      <ul>
        <li>Run có lỗi provider.</li>
        <li>Version chỉ đổi nhãn.</li>
        <li>Nhận xét không trỏ tới file.</li>
        <li>Chép case eval có sẵn.</li>
      </ul>
    </section>
    <p class="note">Bằng chứng phải nằm trong repo nộp bài.</p>
  </div>
</div>
""",
    """
<strong>Quy tắc chấm (RUBRIC.md của lab)</strong>
<ul>
  <li>Run hợp lệ: <code>summary.provider_error_cases == 0</code> và <code>summary.measured_cases == summary.total_cases</code>. Run v0 không hợp lệ thì C1 bằng 0.</li>
  <li>C3 nặng nhất (20 điểm): mỗi version một giả thuyết, có hash, metric trước và sau; version không tăng điểm vẫn được tính nếu phân tích trung thực.</li>
  <li>C8: mỗi thành viên có báo cáo đúng tên file và có commit kỹ thuật; thiếu thành viên nào thì trừ phần của thành viên đó.</li>
  <li>Nhận xét không trỏ được tới file, run hoặc commit thì không tính điểm.</li>
</ul>
""",
    done=5,
)

# 17 ── Submit checklist ─────────────────────────────────────────────────
slide(
    "Checklist nộp bài và khởi động lab",
    """
<h2 class="title">Checklist nộp bài và khởi động lab</h2>
<div class="grid grid-2">
  <div>
    <h3 class="sub">Trước khi nộp</h3>
    <ul class="checklist">
      <li>Tên repo <code>K5-L3A-…</code> hoặc <code>K5-L3B-…</code></li>
      <li><code>TEAM.md</code> đủ thông tin, có commit chốt</li>
      <li>Mỗi người có <code>report/team/MSSV_HoTen.md</code></li>
      <li><code>group_report.md</code> đủ Phần A và B</li>
      <li><code>pytest</code> báo 0 failed</li>
      <li>Run v0 đến v3, run group, transcript, UI</li>
      <li>Không có <code>.env</code> hay key</li>
      <li>Mọi thành viên nộp link trên LMS</li>
    </ul>
  </div>
  <div class="stack">
    <section class="panel">
      <h3>Deadline (GMT+7)</h3>
      <p class="deadline">23h59 ngày lab</p>
      <p>Coach có thể gia hạn tối đa 48h.</p>
    </section>
    <div class="cta-row">
      <button class="btn-primary" type="button" onclick="window.kickoffLab && window.kickoffLab()">Bắt đầu CP1: Setup</button>
    </div>
  </div>
</div>
""",
    """
<strong>Lời dặn kết thúc</strong>
<ul>
  <li>Bấm nút để quay về CP1 và bắt đầu.</li>
  <li>Deadline theo SUBMISSION.md của lab: 23h59 ngày lab (GMT+7), áp dụng cho cả lớp sáng và lớp chiều. Coach có thể gia hạn tối đa 48h; nếu gia hạn thì theo thông báo của coach.</li>
  <li>Các mốc 15:00, 15:30, 16:00, 16:30, 17:30 chỉ là checkpoint tại lớp, không phải deadline.</li>
  <li>Không commit <code>.env</code>, API key, token Telegram, <code>.venv</code>, cache hay <code>arxiv_papers/</code>.</li>
</ul>
""",
    done=5,
)

out = pathlib.Path(__file__).resolve().parent.parent / "app/src/slides/content.json"
out.write_text(json.dumps(S, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {len(S)} slides -> {out}")
