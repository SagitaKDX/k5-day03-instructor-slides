"""Builds app/src/slides/content.json for the Day 03 instructor deck.

Structure mirrors the Day 02 deck (SagitaKDX/k5-day02-instructor-slides): opening, format, goals,
schedule, naming, AI boundaries, one slide per checkpoint (meta bar, task, coach, anti-pattern,
self-check), a phase transition, rubric, and the submission checklist.

Facts come from the Day03 lab repo (VinUni-AI20k/Day03-Prompt-Engineering-Tool-Calling-Labs-student):
README.md, TOOL-SETUP.md, starter_v0/tools/README.md, starter_v0/artifacts/REPORT.md,
starter_v0/data/eval_base.json, starter_v0/tests/*. Course-wide conventions (repo naming, LMS,
deadlines) come from the Day 02 SUBMISSION.md and RULES.md and are marked as such in the notes.

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
    "Day 03: Prompt Engineering và Tool Calling",
    """
<div class="title-slide">
  <div class="title-copy">
    <p class="course">VinUni AI20k, K5 Level 3 (L3A và L3B), {{SESSION}}, {{SESSION_RANGE}}</p>
    <h1 class="hero">Agent gọi đúng tool nhờ bằng chứng, không nhờ cảm giác</h1>
    <p class="lede">Dựng research agent chạy API thật, rồi dùng chính log JSON để sửa prompt và tool.</p>
  </div>
  <figure class="title-proof">
    <figcaption>Mỗi lần chạy eval đều lưu lại một file run JSON:</figcaption>
<pre class="code code--big"><span class="c">// runs/*.json</span>
"summary": {
  "case_accuracy": …,
  "tool_routing_accuracy": …,
  "argument_accuracy": …,
  "multiturn_accuracy": …
},
"artifact_version", "prompt_hash", "tools_hash"
"results[*].result.failures"
"results[*].result.observed_mismatch"</pre>
  </figure>
</div>
<div class="facts">
  <section><h2>Hình thức</h2><p>Nhóm, repo <code>starter_v0/</code>.</p></section>
  <section><h2>Đầu ra</h2><p>Agent có UI, <code>v0</code> đến <code>v3</code>, report.</p></section>
  <section><h2>Tiêu chí chấm</h2><p>Vòng lặp có bằng chứng.</p></section>
  <section><h2>Điều khiển</h2><p><kbd>←</kbd> <kbd>→</kbd> chuyển slide, <kbd>P</kbd> timer, <kbd>N</kbd> ghi chú.</p></section>
</div>
""",
    """
<strong>Chào lớp và neo tư duy</strong>
<ul>
  <li>Nhấn mạnh ngay từ đầu: buổi học không chấm agent trả lời hay hay dở, mà chấm vòng lặp cải tiến có bằng chứng: chạy thật, đọc log, sửa từng điểm, chạy lại và ghi nhận kết quả.</li>
  <li>Khung code bên phải mô tả cấu trúc file run JSON. Mọi kết luận trong report đều phải đối chiếu với các trường này.</li>
  <li>Prompt starter được cố tình viết chưa tối ưu. Baseline thấp là bình thường; điều quan trọng là nhóm giải thích được nguyên nhân.</li>
  <li>Nhắc lớp mở sẵn repo starter và file <code>TOOL-SETUP.md</code>.</li>
</ul>
""",
)

# 1 ── Format ────────────────────────────────────────────────────────────
slide(
    "Hình thức: làm nhóm, theo vòng lặp có bằng chứng",
    """
<h2 class="title">Một vòng lặp sáu bước, chạy ít nhất bốn lần</h2>
<p class="lede">Mỗi phiên bản <code>v0</code> đến <code>v3</code> đi trọn sáu bước, một giả thuyết mỗi vòng.</p>
<ol class="loop">
  <li><b>Chạy baseline</b><span>Provider thật, output trong <code>runs/</code>.</span></li>
  <li><b>Đọc run JSON</b><span>Sai tool, sai args, không hỏi lại, hay gọi tool thừa?</span></li>
  <li><b>Sửa một điểm</b><span>Trong <code>system_prompt.md</code> hoặc <code>tools.yaml</code>.</span></li>
  <li><b>Chạy lại, ghi log</b><span>Metric trước và sau trong <code>version_log.csv</code>.</span></li>
  <li><b>Tự viết eval</b><span>Case trong <code>eval_group.json</code>.</span></li>
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
  <li>Ba vai ở hàng dưới là gợi ý phân công, không phải quy định bắt buộc. README lab không giới hạn số người hay vai trò.</li>
  <li>Cảnh báo tình trạng chia nhỏ việc rồi ghép cơ học: ở bước 2 và 3 (đọc log, chọn giả thuyết), cả nhóm phải cùng ngồi thảo luận.</li>
  <li>Bước 2 dễ bị bỏ qua nhất: sinh viên thường nhìn điểm tổng rồi sửa prompt theo cảm tính. Yêu cầu mở <code>observed_mismatch</code> của từng case FAIL.</li>
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
    <h3>Đọc lỗi của agent từ log, không từ cảm giác</h3>
    <p>Đọc <code>observed_mismatch</code>, gán mỗi case FAIL vào một trong sáu loại lỗi.</p>
    <p class="cp-ref">Dùng ở CP1, CP2</p>
  </section>
  <section class="panel">
    <h3>Viết prompt và tool declaration có ranh giới rõ</h3>
    <p>Tool nói rõ khi nào dùng, khi nào không. Thiếu thông tin thì <code>clarify</code>.</p>
    <p class="cp-ref">Dùng ở CP2, CP3, CP5</p>
  </section>
  <section class="panel">
    <h3>Tách hai loại kiểm thử: eval và unit test</h3>
    <p>Eval đo model chọn tool. Unit test đo code của tool.</p>
    <p class="cp-ref">Dùng ở CP2, CP3</p>
  </section>
  <section class="panel">
    <h3>Ra quyết định bằng số đo có thể kiểm lại</h3>
    <p>Mỗi phiên bản có giả thuyết, metric trước và sau, file run.</p>
    <p class="cp-ref">Dùng ở CP1 đến CP5</p>
  </section>
</div>
""",
    """
<strong>Trọng tâm đánh giá của bốn mục tiêu</strong>
<ul>
  <li>Mục tiêu 1: nhóm nào chỉ báo accuracy tăng mà không chỉ ra case nào đổi từ FAIL sang PASS thì chưa đạt.</li>
  <li>Mục tiêu 2: việc <code>send</code> gửi khi chưa xác nhận là lỗi ranh giới nghiêm trọng nhất của buổi (case <code>R12_confirm_before_send</code>).</li>
  <li>Mục tiêu 3: ví dụ trong README: model gọi đúng <code>lookup(topic="news")</code> nhưng tool quên gửi <code>topic</code> lên API. Eval vẫn PASS, user vẫn nhận kết quả sai.</li>
  <li>Mục tiêu 4: không chấp nhận nhận định prompt mới tốt hơn nếu không có hai con số trước sau và đường dẫn tới file run.</li>
</ul>
""",
)

# 3 ── Schedule ──────────────────────────────────────────────────────────
slide(
    "Lịch trình 240 phút (CP0 đến CP5)",
    """
<h2 class="title">Lịch trình 240 phút gồm sáu checkpoint</h2>
<table class="data">
  <thead><tr><th>Khung giờ</th><th>Checkpoint</th><th>Giai đoạn</th><th>Nhiệm vụ trọng tâm và sản phẩm</th></tr></thead>
  <tbody>
    <tr><td class="num">Trước 15:00</td><td><b>CP0</b> Setup</td><td>Chuẩn bị</td><td><code>.env</code> đủ key, preflight pass, <code>pytest</code> chạy được</td></tr>
    <tr><td class="num">15:00 đến 15:30</td><td><b>CP1</b> Baseline và UI</td><td>Đo</td><td>Chạy <code>v0</code>, gán loại lỗi, dựng UI</td></tr>
    <tr><td class="num">15:30 đến 16:00</td><td><b>CP2</b> v1 và tool mới</td><td>Sửa</td><td>Chạy <code>v1</code>, 1 tool mới có 3 test</td></tr>
    <tr><td class="num">16:00 đến 16:30</td><td><b>CP3</b> Eval nhóm và v2</td><td>Đo lại</td><td>Eval nhóm, chạy <code>v2</code>, Phần A</td></tr>
    <tr class="row-key"><td class="num">16:30 đến 17:30</td><td><b>CP4</b> Team showdown</td><td>Demo</td><td>Nhóm khác thử agent qua link public</td></tr>
    <tr><td class="num">Từ 17:30</td><td><b>CP5</b> v3 và report</td><td>Đóng gói</td><td>Chạy <code>v3</code>, report Phần B</td></tr>
  </tbody>
</table>
<p class="note">Mốc cứng: <code>REPORT.md</code> Phần A xong trước 16:30.</p>
""",
    """
<strong>Chiến lược điều phối thời gian</strong>
<ul>
  <li>Khung giờ lớp chiều lấy từ mục Checkpoint 4h trong README lab, tính theo giờ bắt đầu mỗi chặng. Lớp sáng dùng cùng lịch, dời sớm 5 tiếng; deck tự đổi theo giờ máy khi mở (trước 13:00 là lớp sáng) và có nút đổi tay trên header.</li>
  <li>Timer trên header tự chạy khi mở slide CP1 đến CP4. Nhắc lớp khi còn 2 phút.</li>
  <li>CP1 thường nghẽn vì thiếu key hoặc quota. Nhóm nào chưa chạy được baseline lúc 15:15 thì cho dùng tạm provider khác.</li>
  <li>CP4 dài nhất (60 phút) vì vừa demo vừa thử chéo. Không cắt bớt CP4 để bù giờ cho các CP trước.</li>
</ul>
""",
)

# 4 ── Naming ────────────────────────────────────────────────────────────
slide(
    "Fork và đặt tên repo",
    """
<h2 class="title">Quy ước fork và đặt tên repo của nhóm</h2>
<div class="grid grid-2">
  <section class="panel">
    <h3>Tên repo nhóm, do nhóm trưởng fork</h3>
<pre class="code code--wrap">K5-&lt;L3A hoặc L3B&gt;-DAY03-HoVaTen-MSSV-PromptEngineeringToolCalling</pre>
    <p>Ví dụ nhóm trưởng Nguyễn Văn An, MSSV 20241234, lớp L3A:</p>
<pre class="code code--wrap">K5-L3A-DAY03-NguyenVanAn-20241234-PromptEngineeringToolCalling</pre>
    <p>Họ tên trước, MSSV sau, không dấu, <code>DAY03</code>.</p>
  </section>
  <div class="stack">
    <section class="panel">
      <h3>Những gì nằm trong repo nộp</h3>
<pre class="code">starter_v0/
  artifacts/   system_prompt.md, tools.yaml,
               version_log.csv, REPORT.md
  data/        eval_group.json
  tests/       unit test cho tool mới
  runs/        *.json
  transcripts/ *.transcript.json
  analysis/    *.csv (nếu có)</pre>
    </section>
    <section class="anti">
      <h3>{ICONS_ANTI}Lỗi đặt tên thường gặp</h3>
      <ul>
        <li>Tên tự đặt như <code>Nhom1-AIAgent</code>.</li>
        <li>Thiếu <code>L3A</code>/<code>L3B</code>, ghi <code>DAY3</code>.</li>
        <li>Commit <code>.env</code> cùng lần push đầu tiên.</li>
      </ul>
    </section>
  </div>
</div>
""",
    """
<strong>Hành động của giảng viên trong 10 phút đầu</strong>
<ul>
  <li>README lab Day 03 chưa ghi quy ước tên repo. Cú pháp trên áp dụng quy ước chung của khóa, giống <code>SUBMISSION.md</code> của Day 02. Hậu tố bài (<code>PromptEngineeringToolCalling</code>) cần chốt với key coach trước giờ học.</li>
  <li>Quan sát trực tiếp xem các nhóm trưởng đã fork và đổi tên đúng cú pháp chưa.</li>
  <li>Nhắc nhóm trưởng vào Settings, Collaborators để mời thành viên ngay, tránh việc thành viên không push được.</li>
  <li>Mỗi thành viên nộp link repo nhóm lên LMS bằng tài khoản riêng của mình.</li>
</ul>
""",
)

# 5 ── Rules and AI boundaries ───────────────────────────────────────────
slide(
    "Luật vàng và ranh giới khi làm lab",
    """
<h2 class="title">Quy tắc vàng: phạm vi được sửa và hành vi bị cấm</h2>
<table class="data">
  <thead><tr><th>Phần</th><th>Cách làm đúng</th><th>Hành vi bị cấm</th></tr></thead>
  <tbody>
    <tr><td class="num">Prompt và tool</td><td>Sửa <code>system_prompt.md</code>, <code>tools.yaml</code>; một giả thuyết mỗi bản</td><td>Sửa nhiều chỗ trong một bản</td></tr>
    <tr><td class="num">Eval base</td><td>Chỉ đọc case</td><td>Sửa case trong <code>eval_base.json</code></td></tr>
    <tr><td class="num">Đổi tên tool</td><td>Đổi đủ 3 nơi, chạy <code>test_tool_contract.py</code></td><td>Chỉ đổi một nơi</td></tr>
    <tr><td class="num">Unit test</td><td>Mock bằng <code>fake_http</code>, chạy offline</td><td>Gọi API thật</td></tr>
    <tr><td class="num">Report</td><td>Số liệu trỏ về <code>runs/</code>, <code>transcripts/</code></td><td>Viết từ trí nhớ</td></tr>
    <tr><td class="num">Bảo mật</td><td>Kiểm tra <code>git status</code> trước khi push</td><td>Commit <code>.env</code> hay key</td></tr>
  </tbody>
</table>
<p class="note">Giả thuyết rõ mà không cải thiện vẫn hơn điểm tăng không giải thích được.</p>
""",
    """
<strong>Nhấn mạnh với lớp</strong>
<ul>
  <li>Eval chấm theo đúng tên tool. Đổi <code>send</code> thành <code>send_telegram</code> mà quên một trong ba nơi thì eval chấm sai mọi case liên quan.</li>
  <li>Được dùng trợ lý AI để viết code tool và test. Theo quy ước chung của khóa (RULES Day 02): phần reflection trong report phải tự viết; mỗi lần dùng AI nên ghi lại dùng để làm gì, AI sai ở đâu, nhóm sửa gì.</li>
  <li>README lab Day 03 chưa có <code>RULES.md</code> riêng; hai ý trên lấy từ quy ước chung, cần key coach xác nhận.</li>
</ul>
""",
)

# 6 ── CP0 ───────────────────────────────────────────────────────────────
slide(
    "CP0: Setup, key và preflight",
    f"""
<h2 class="title">CP0: thiết lập môi trường và kiểm tra preflight</h2>
{meta(when="Trước 15:00", who="Cả nhóm", write="<code>.env</code> (không commit)", out="Preflight pass, <code>pytest</code> chạy được")}
<div class="cp-layout">
  <div class="stack">
<pre class="code">cd starter_v0
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/preflight_provider.py --provider openrouter
pytest</pre>
    <table class="data data--compact">
      <thead><tr><th>Key</th><th>Dùng cho</th></tr></thead>
      <tbody>
        <tr><td><code>OPENROUTER_API_KEY</code></td><td>model</td></tr>
        <tr><td><code>TAVILY_API_KEY</code></td><td><code>lookup</code></td></tr>
        <tr><td><code>FIRECRAWL_API_KEY</code></td><td><code>fetch</code></td></tr>
        <tr><td><code>RAPIDAPI_KEY</code></td><td><code>timeline</code>, <code>social_search</code></td></tr>
      </tbody>
    </table>
  </div>
  <div class="stack">
    {coach(
        "<b>Một người có đủ key là có thể bắt đầu:</b> theo <code>TOOL-SETUP.md</code>, mỗi nhóm cần ít nhất một người chuẩn bị đủ key trước giờ học.",
        "<b>Preflight chưa pass thì chưa chạy eval:</b> sửa đúng ba chỗ: key trong <code>.env</code>, dependency trong venv và kết nối mạng.",
        "<b>Kỳ vọng của <code>pytest</code> lúc này:</b> contract test và example test xanh, các test TODO đang <code>skipped</code>.",
    )}
    {anti(
        "Chạy eval khi preflight còn lỗi.",
        "Dán key vào code hoặc chat nhóm.",
        "Đốt hết credit miễn phí vì chạy eval lặp.",
    )}
    {check("Đọc được dòng tổng kết của <code>pytest</code> chưa?")}
  </div>
</div>
""",
    """
<strong>Gợi ý hướng dẫn CP0</strong>
<ul>
  <li>Quan sát xem nhóm nào chưa có key Tavily, Firecrawl hoặc RapidAPI. Thiếu key thì tool tương ứng trả error dict, eval FAIL vì hạ tầng chứ không vì prompt.</li>
  <li>Nhóm dùng provider khác OpenRouter đổi cờ <code>--provider</code> tương ứng.</li>
  <li>Bonus <code>send</code> cần thêm <code>TELEGRAM_BOT_TOKEN</code> và <code>TELEGRAM_CHAT_ID</code>.</li>
  <li>Nếu <code>pytest</code> fail vì network: test đó đang gọi mạng thật. File <code>conftest.py</code> chặn mọi HTTP thật và xóa env key trước mỗi test.</li>
</ul>
""",
    cp="0",
)

# 7 ── CP1 ───────────────────────────────────────────────────────────────
slide(
    "CP1: Baseline v0 và dựng UI",
    f"""
<h2 class="title">CP1: chạy baseline v0, đọc từng case như bệnh án</h2>
{meta(time="30 phút", when="15:00 đến 15:30", who="Nhóm", write="<code>runs/*.json</code>, <code>version_log.csv</code>", out="Run <code>v0</code> và danh sách case FAIL có loại lỗi")}
<div class="cp-layout">
  <div class="stack">
<pre class="code">python run_eval.py --provider openrouter \\
  --version v0 --suite base \\
  --eval-cases data/eval_base.json</pre>
    <section class="panel">
      <h3>Đọc trong run JSON</h3>
      <ol class="plain">
        <li>Bốn chỉ số trong <code>summary</code>.</li>
        <li>Mỗi case FAIL: <code>observed_mismatch</code>.</li>
        <li>Ghi <code>prompt_hash</code>, <code>tools_hash</code> vào dòng <code>v0</code>.</li>
      </ol>
    </section>
    <section class="panel">
      <h3>Song song: dựng UI</h3>
      <p>Streamlit hoặc Vercel, dùng lại lúc 16:30.</p>
    </section>
  </div>
  <div class="stack">
    {coach(
        "<b>Baseline thấp là đúng kịch bản:</b> prompt starter dạy agent đoán thay vì hỏi, gửi không cần xác nhận, ép mọi việc vào một bước.",
        "<b>Đọc từng case, không đọc điểm tổng:</b> base eval có 20 case (14 single turn, 6 multi turn). Mỗi case FAIL phải gán một loại lỗi.",
        "<b>Chia việc ngay:</b> hai người đọc log, một người dựng UI. Tránh để cả nhóm ngồi nhìn một màn hình.",
    )}
    {anti(
        "Sửa prompt ngay khi chưa ghi lại số đo <code>v0</code>.",
        "Chạy baseline nhiều lần, chọn lần cao nhất.",
        "Để UI tới 16:20 mới làm.",
    )}
    {check("Kể được 3 case FAIL của <code>v0</code> và loại lỗi?")}
  </div>
</div>
""",
    """
<strong>Hành động của giảng viên trong CP1</strong>
<ul>
  <li>Quan sát màn hình các nhóm: ai đang mở run JSON, ai chỉ nhìn điểm tổng. Yêu cầu nhóm chỉ ra <code>observed_mismatch</code> của một case cụ thể.</li>
  <li>Nhắc ghi ngay dòng <code>v0</code> vào <code>version_log.csv</code> kèm hash và đường dẫn file run.</li>
  <li>Script <code>parse_runs.py</code> là tùy chọn, nhưng giúp nhóm so sánh nhiều run trong một bảng: <code>python scripts/parse_runs.py runs/ --output analysis/base_runs.csv</code>.</li>
</ul>
""",
    cp="1",
    minutes=30,
    label="CP1: Baseline và UI",
)

# 8 ── Failure taxonomy ──────────────────────────────────────────────────
slide(
    "Sáu loại lỗi trong base eval",
    """
<h2 class="title">Sáu loại lỗi trong 20 case của base eval</h2>
<table class="data">
  <thead><tr><th>Loại lỗi</th><th>Số case</th><th>Case mẫu</th><th>Kỳ vọng</th></tr></thead>
  <tbody>
    <tr><td><code>wrong_tool</code></td><td class="bar-cell" title="6 case wrong_tool"><span class="bar" style="--v: 1.000"></span><span class="bar-val">6</span></td><td>R01: Tweet mới nhất của Sam Altman?</td><td><code>timeline(screenname="sama")</code></td></tr>
    <tr><td><code>wrong_arg_value</code></td><td class="bar-cell" title="6 case wrong_arg_value"><span class="bar" style="--v: 1.000"></span><span class="bar-val">6</span></td><td>R06: Tin công nghệ trong tuần này</td><td><code>lookup(topic="news", timeframe="week")</code></td></tr>
    <tr><td><code>missing_info</code></td><td class="bar-cell" title="4 case missing_info"><span class="bar" style="--v: 0.667"></span><span class="bar-val">4</span></td><td>R11: Tóm tắt bài viết này hộ mình</td><td><code>clarify</code>, không đoán URL</td></tr>
    <tr><td><code>out_of_scope</code></td><td class="bar-cell" title="2 case out_of_scope"><span class="bar" style="--v: 0.333"></span><span class="bar-val">2</span></td><td>R08: Nguyên hàm của x^2 là gì?</td><td>Từ chối, không gọi tool</td></tr>
    <tr class="row-key"><td><code>wrong_boundary</code></td><td class="bar-cell" title="1 case wrong_boundary"><span class="bar" style="--v: 0.167"></span><span class="bar-val">1</span></td><td>R12: Đăng bản tin lên Telegram</td><td><code>clarify(response_type="yes_no")</code></td></tr>
    <tr><td><code>unnecessary_tool</code></td><td class="bar-cell" title="1 case unnecessary_tool"><span class="bar" style="--v: 0.167"></span><span class="bar-val">1</span></td><td>R09: Bạn làm được những gì?</td><td>Trả lời, không gọi tool</td></tr>
  </tbody>
</table>
<p class="caption">6 case multi turn kiểm tra agent có nhớ và sửa args theo lượt sau.</p>
""",
    """
<strong>Dùng slide này khi các nhóm bắt đầu gán loại lỗi</strong>
<ul>
  <li>Hỏi lớp: R01 sai vì agent không biết “Sam Altman” ứng với handle <code>sama</code>. Nên sửa ở prompt hay ở description của <code>timeline</code>?</li>
  <li>R12 là case ranh giới quan trọng nhất: agent phải hỏi xác nhận yes/no trước khi gửi.</li>
  <li>Case multi turn như <code>M03_correction_handle</code>: user đổi ý ở lượt sau, agent phải dùng handle mới.</li>
</ul>
""",
    cp="1",
)

# 9 ── CP2 prompt ────────────────────────────────────────────────────────
slide(
    "CP2: v1, sửa đúng một giả thuyết",
    f"""
<h2 class="title">CP2: sửa đúng một giả thuyết cho v1</h2>
{meta(time="30 phút", when="15:30 đến 16:00", who="Nhóm", write="<code>system_prompt.md</code>, <code>tools.yaml</code>", out="Run <code>v1</code> và một dòng mới trong <code>version_log.csv</code>")}
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
        "<b>Sửa một thứ, chạy lại, so số:</b> không cải thiện thì đổi giả thuyết, không chồng thêm sửa đổi.",
        "<b>Prompt hay tool declaration?</b> Rule routing chung đặt trong prompt; quy ước args của một tool đặt trong description của tool đó.",
    )}
    {anti(
        "Viết lại cả prompt rồi gọi là <code>v1</code>.",
        "Hard-code đáp án từng case vào prompt.",
        "Ghi metric mà không có <code>run_file</code>.",
    )}
    {check("Viết được: “Agent sai X vì Y, nên sửa Z”?")}
  </div>
</div>
""",
    """
<strong>Phương pháp, không phải đáp án</strong>
<ul>
  <li>Không đưa sẵn prompt tốt. Hỏi nhóm: case FAIL này sai vì thiếu rule routing, thiếu quy ước args, hay vì prompt đang khuyến khích đoán?</li>
  <li>Câu trích dẫn là nguyên văn trong <code>artifacts/system_prompt.md</code> của starter. Ba thói xấu là ba điểm README yêu cầu bỏ.</li>
  <li>Hard-code đáp án làm eval đẹp nhưng agent không khá lên; hỏi nhóm: case mới trong <code>eval_group.json</code> có còn PASS không?</li>
</ul>
""",
    cp="2",
    minutes=30,
    label="CP2: v1 và tool mới",
)

# 10 ── CP2 tool contract ────────────────────────────────────────────────
slide(
    "CP2: tool mới và hợp đồng thư mục tool",
    f"""
<h2 class="title">CP2: tool mới phải đủ bốn thứ và ba test</h2>
{meta(who="Nhóm", write="<code>tools/&lt;tên&gt;/</code>, <code>tests/test_tools_todo.py</code>", out="Ít nhất 1 tool mới, mỗi tool ít nhất 3 unit test", bonus="UI cộng hơn 3 tool mới")}
<div class="cp-layout">
  <div class="stack">
<pre class="code"><span class="c"># tools/&lt;tên&gt;/TOOL.md</span>
---
name: tool_name
track: core | bonus
kind: live_api | local_formatter | local_knowledge | action | control
provider: ...
requires_env: [ENV_VAR]
inputs: [arg_name]
outputs: [field_name]
side_effect: false | true | local_file_write
requires_confirmation: true  <span class="c"># chỉ cho tool hành động</span>
---</pre>
    <ol class="steps">
      <li><code>tool.py</code> trả error dict, không raise.</li>
      <li><code>TOOL.md</code> với frontmatter trên.</li>
      <li>Đăng ký trong <code>TOOL_FUNCTIONS</code>.</li>
      <li>Khai báo trong <code>tools.yaml</code> và 1 eval case.</li>
    </ol>
  </div>
  <div class="stack">
    <section class="panel">
      <h3>Ba test bắt buộc cho mỗi tool mới</h3>
      <ul>
        <li><b>Happy path:</b> args đúng, kết quả đúng.</li>
        <li><b>Input xấu từ model:</b> chuỗi rỗng, sai kiểu, ngoài enum.</li>
        <li><b>Nhánh lỗi:</b> thiếu key, HTTP 429, trả error dict.</li>
      </ul>
      
    </section>
    {coach(
        "<b>Tên test mô tả hành vi:</b> một test kiểm tra một hành vi; assert cả request gửi đi lẫn kết quả trả về.",
        "<b>Chạy <code>pytest tests/test_tool_contract.py</code> sau mỗi lần thêm tool:</b> test này giữ <code>tools.yaml</code>, code và eval luôn đồng bộ.",
    )}
    {anti(
        "Quên <code>TOOL.md</code> hoặc đăng ký.",
        "Chỉ <code>assert result</code>.",
    )}
  </div>
</div>
""",
    """
<strong>Lưu ý giảng viên về tool mới</strong>
<ul>
  <li>Tool có sẵn trong starter: <code>clarify</code>, <code>timeline</code>, <code>social_search</code>, <code>lookup</code>, <code>fetch</code>, <code>format</code>, và bonus <code>send</code>, <code>policy</code>, <code>papers</code>, <code>paper_text</code>. Tool mới phải khác các tool này.</li>
  <li>Điểm thưởng theo README: nhóm làm cả hai, có UI và tự viết hơn 3 tool mới (đủ <code>TOOL.md</code>, đăng ký, khai báo).</li>
  <li>Ba stub <code>test_my_new_tool_*</code> trong <code>test_tools_todo.py</code> là chỗ viết ba test bắt buộc.</li>
</ul>
""",
    cp="2",
)

# 11 ── CP3 ──────────────────────────────────────────────────────────────
slide(
    "CP3: eval nhóm, v2 và unit test challenge",
    f"""
<h2 class="title">CP3: tự viết bài kiểm tra cho agent của mình</h2>
{meta(time="30 phút", when="16:00 đến 16:30", who="Nhóm", write="<code>data/eval_group.json</code>", out="Case của nhóm và run <code>v2</code>", bonus="<code>pytest</code> 0 failed, 0 skipped")}
<div class="cp-layout">
  <div class="stack">
<pre class="code">{{
  "id": "G01_...",
  "phase": "B",
  "query": "...",               <span class="c">// hoặc "turns"</span>
  "failure_type": "missing_info",
  "expect": {{ "tool_calls": [ ... ] }},  <span class="c">// hoặc "no_tool"</span>
  "metadata": {{ "what_it_tests": "..." }}
}}</pre>
<pre class="code">python run_eval.py --provider openrouter \\
  --version v2 --suite group \\
  --eval-cases data/eval_group.json</pre>
    <div class="grid grid-2">
      <section class="panel"><h3>Eval đo model</h3><p>Đúng tool, đúng args.</p></section>
      <section class="panel"><h3>Unit test đo code</h3><p>Gọi đúng API, trả đúng.</p></section>
    </div>
  </div>
  <div class="stack">
    {coach(
        "<b>Viết case từ lỗi thật:</b> mỗi case nhắm vào một lỗi nhóm đã thấy trong run <code>v0</code> hoặc <code>v1</code>.",
        "<b>Có cả single turn và multi turn:</b> multi turn kiểm tra agent có nhớ thông tin và sửa args theo lượt sau.",
        "<b>Challenge+:</b> thử input biên như <code>limit=0</code>, <code>max_results=\"5\"</code>, <code>items</code> thiếu <code>url</code>. Tìm được bug thì sửa, giữ test làm regression test, ghi vào B5.",
    )}
    {anti(
        "Viết case dễ cho đẹp điểm.",
        "Chép case của <code>eval_base.json</code>.",
        "Thiếu <code>what_it_tests</code>.",
    )}
    {check("Chỉ ra một lỗi unit test bắt được mà eval bỏ sót?")}
  </div>
</div>
""",
    """
<strong>Lưu ý CP3</strong>
<ul>
  <li>Số case cần chốt với lớp ngay đầu checkpoint: phần Scope trong README và mục B3 của report ghi 10 case (5 single turn, 5 multi turn); Step 4 và phần Submit ghi ít nhất 5.</li>
  <li>Ví dụ từ README: model gọi đúng <code>lookup(topic="news")</code> nhưng tool quên gửi <code>topic</code> lên API. Eval vẫn PASS, user vẫn nhận kết quả sai. Đó là lỗi unit test bắt được.</li>
  <li>Challenge: điền hết các stub <code>pytest.skip(TODO)</code> cho <code>clarify</code>, <code>format</code>, <code>send</code>, <code>lookup</code>, <code>fetch</code>, <code>timeline</code>, <code>social_search</code>, <code>policy</code>.</li>
</ul>
""",
    cp="3",
    minutes=30,
    label="CP3: Eval nhóm và v2",
)

# 12 ── Transition ───────────────────────────────────────────────────────
slide(
    "Chuyển sang showdown: chuẩn bị trong 10 phút cuối CP3",
    """
<h2 class="title">Trước 16:30: từ tự kiểm tra sang cho nhóm khác thử</h2>
<div class="grid grid-2">
  <section class="panel">
    <h3>Nhóm đã có gì đến lúc này</h3>
    <p><code>v0</code>, hai vòng tối ưu, tool mới, eval nhóm.</p>
  </section>
  <section class="panel">
    <h3>Điểm mới ở CP4</h3>
    <p>Nhóm khác hỏi theo cách bạn chưa lường trước.</p>
  </section>
</div>
<h3 class="sub">Ba việc phải xong trước 16:30</h3>
<ol class="loop loop--three">
  <li><b>Chạy UI và mở tunnel</b><span>Copy link <code>trycloudflare.com</code>.</span></li>
  <li><b>Viết Phần A của report</b><span>Agent làm gì, tool nào, câu hỏi mẫu.</span></li>
  <li><b>Chọn người trực demo</b><span>Một người giữ máy, cả nhóm đi thử chéo.</span></li>
</ol>
""",
    """
<strong>Chuyển pha</strong>
<ul>
  <li>Báo lớp còn 10 phút trước showdown. Nhóm nào chưa có link public thì ưu tiên mở tunnel trước, viết report Phần A sau.</li>
  <li>Link <code>trycloudflare.com</code> chỉ sống theo phiên; tắt lệnh là mất. Máy giữ tunnel không được sleep.</li>
  <li>Nhắc các nhóm cùng zone ngồi gần nhau để thử chéo thuận tiện.</li>
</ul>
""",
    done=3,
)

# 13 ── CP4 ──────────────────────────────────────────────────────────────
slide(
    "CP4: Team showdown",
    f"""
<h2 class="title">CP4: nhóm khác trực tiếp dùng thử agent của bạn</h2>
{meta(time="60 phút", when="16:30 đến 17:30", who="Nhóm", write="<code>REPORT.md</code> Phần A, <code>transcripts/</code>", out="Link dùng thử và transcript các lượt chat")}
<div class="cp-layout">
  <div class="stack">
<pre class="code">streamlit run app.py
cloudflared tunnel --url http://localhost:8501</pre>
    <section class="panel">
      <h3>Phần A của report, gói gọn một trang</h3>
      <ol class="plain">
        <li>A1. Agent làm gì, link dùng thử.</li>
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
        "Tắt tunnel giữa chừng.",
        "Phần A như quảng cáo.",
    )}
    {check("Người ngoài đọc Phần A 1 phút có tự thử được?")}
  </div>
</div>
""",
    """
<strong>Điều phối showdown</strong>
<ul>
  <li>Cho các nhóm trong cùng zone thử chéo agent của nhau. Mỗi nhóm vừa trực demo vừa đi thử.</li>
  <li>Quan sát agent có hỏi lại trước khi gửi không. Đây là phép thử ranh giới quan trọng nhất của buổi.</li>
  <li>Nếu nhóm deploy hẳn lên Vercel hoặc Streamlit Cloud thì dùng link đó thay cho tunnel.</li>
  <li>Cài <code>cloudflared</code>: <code>brew install cloudflared</code> (macOS), <code>winget install --id Cloudflare.cloudflared</code> (Windows).</li>
  <li>Phần A có thể làm thêm poster <code>artifacts/poster.html</code> hoặc <code>poster.svg</code>; bản markdown vẫn bắt buộc.</li>
</ul>
""",
    cp="4",
    minutes=60,
    label="CP4: Team showdown",
)

# 14 ── Live chat ────────────────────────────────────────────────────────
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
    <h3>Request thiếu thông tin</h3>
    <p>Agent gọi <code>clarify</code>, không tự đoán.</p>
  </section>
  <section class="panel">
    <h3>Request gửi bản tin</h3>
    <p>Agent hỏi xác nhận trước khi gửi?</p>
  </section>
</div>
<pre class="code">python chat.py --provider openrouter --version v3</pre>
<p class="caption">Transcript lưu trong <code>transcripts/</code>, dùng cho mục B4.</p>
""",
    """
<strong>Gợi ý</strong>
<ul>
  <li>Không có câu trả lời mẫu cho lượt thứ ba. Mục đích là để nhóm tự lập luận về ranh giới hành động, rồi ghi lại trong reflection.</li>
  <li>Nhóm làm bonus <code>send</code> cần transcript chứng minh có bước xác nhận trước khi gửi.</li>
  <li>File trong <code>samples/</code> chỉ là mock để xem định dạng, không phải đáp án.</li>
</ul>
""",
    cp="4",
)

# 15 ── CP5 ──────────────────────────────────────────────────────────────
slide(
    "CP5: v3 và report Phần B",
    f"""
<h2 class="title">CP5: chốt v3 và viết report từ log thật</h2>
{meta(when="Từ 17:30", who="Nhóm", write="<code>artifacts/REPORT.md</code> Phần B, <code>version_log.csv</code>", out="Run <code>v3</code>, đủ 4 dòng <code>v0</code> đến <code>v3</code>")}
<div class="cp-layout">
  <div class="stack">
<pre class="code code--wrap">version, author, changed_artifact, artifact_version, prompt_hash, tools_hash, reason, hypothesis, metric_before, metric_after, run_file</pre>
    <table class="data data--compact">
      <thead><tr><th>Mục</th><th>Nội dung</th><th>Bằng chứng</th></tr></thead>
      <tbody>
        <tr><td>B1</td><td>Bảng v0 đến v3</td><td><code>version_log.csv</code>, <code>runs/</code></td></tr>
        <tr><td>B2</td><td>Phân tích lỗi</td><td><code>failures</code></td></tr>
        <tr><td>B3</td><td>Eval case của nhóm</td><td><code>eval_group.json</code></td></tr>
        <tr><td>B4</td><td>Chat live</td><td><code>transcripts/</code></td></tr>
        <tr><td>B5</td><td>Bonus, bug tìm được</td><td>output <code>pytest</code></td></tr>
        <tr><td>B6</td><td>Reflection</td><td>4 câu hỏi</td></tr>
        <tr><td>B7</td><td>Small local model</td><td>run của model local</td></tr>
      </tbody>
    </table>
  </div>
  <div class="stack">
    {coach(
        "<b>Giả thuyết <code>v3</code></b>: lấy từ lỗi nhóm khác tìm ra ở CP4.",
        "<b>B6 hỏi bốn câu:</b> lỗi nào thuộc về <code>system_prompt.md</code>, lỗi nào thuộc về <code>tools.yaml</code>, lỗi nào cần review tay thay vì chấm tự động, nhóm sẽ cải thiện gì tiếp.",
        "<b>Chạy <code>v3</code> trong buổi:</b> Phần B có thể hoàn thiện sau buổi, nhưng <code>v3</code> nên chạy xong trong buổi để còn đọc log.",
    )}
    {anti(
        "B1 thiếu <code>run_file</code>.",
        "B2 chỉ ghi “sai tool”.",
        "Reflection chung chung.",
    )}
    {check("Mỗi con số mở ngược được tới một file?")}
  </div>
</div>
""",
    """
<strong>Kiểm tra report</strong>
<ul>
  <li>Mỗi dòng trong B1 phải có <code>run_file</code> trỏ tới file có thật. Không có file thì dòng đó không được tính.</li>
  <li>B5 hỏi thêm: số test đã viết, số bug tìm được trong tool có sẵn, và một ví dụ lỗi unit test bắt được mà eval không bắt được.</li>
</ul>
""",
    cp="5",
)

# 16 ── Local model bonus ────────────────────────────────────────────────
slide(
    "Bonus: Small Local Model Challenge",
    f"""
<h2 class="title">Prompt tốt cho model cloud có còn tốt trên model 3B?</h2>
{meta(who="Nhóm, tùy chọn", write="<code>REPORT.md</code> mục B7", out="Run của ít nhất 2 model local", bonus="Small Local Model Challenge")}
<div class="cp-layout">
  <div class="stack">
<pre class="code">ollama pull qwen2.5:7b     <span class="c"># ~4.7 GB</span>
ollama pull llama3.2:3b    <span class="c"># ~2 GB</span>

python run_eval.py --provider ollama \\
  --model qwen2.5:7b --version v3-qwen7b \\
  --suite base --eval-cases data/eval_base.json</pre>
    <section class="panel">
      <h3>Tiêu chí đạt</h3>
      <ol class="plain">
        <li>2 model local chạy base eval với <code>v3</code>.</li>
        <li>2 vòng tối ưu: <code>v4-local</code>, <code>v5-local</code>.</li>
        <li>Bảng cloud và local trong B7.</li>
        <li>Kết luận: điều gì giúp model nhỏ.</li>
      </ol>
    </section>
  </div>
  <div class="stack">
    <section class="panel">
      <h3>Lỗi đặc thù của model nhỏ cần đếm</h3>
      <ul>
        <li>Sai tool hoặc bịa tên tool.</li>
        <li>Args JSON lỗi.</li>
        <li>Không gọi tool, hoặc bỏ qua <code>clarify</code>.</li>
        <li>Gọi lặp cùng một tool.</li>
      </ul>
    </section>
    {coach(
        "<b>Hướng gợi ý:</b> rút gọn system prompt, description ngắn có ví dụ args, 1 đến 2 ví dụ few-shot, bỏ tool không cần cho suite đang chạy.",
        "<b>Tách bản local:</b> dùng <code>--system-prompt</code> và <code>--tools</code> để không phá bản <code>v3</code> của cloud.",
    )}
  </div>
</div>
""",
    """
<strong>Lưu ý</strong>
<ul>
  <li>Máy RAM dưới 16 GB dùng model 3B. Model phải có tag “tools” trên Ollama.</li>
  <li>Model local chạy chậm; nên chạy thử 3 đến 5 case bằng một file eval nhỏ trước.</li>
  <li>Ollama có thể bỏ qua <code>tool_choice="required"</code>. Model không gọi tool là lỗi cần đo, không phải bug của harness.</li>
  <li>Kiểm tra ngược: chạy bản <code>v5-local</code> trên model cloud. Có tìm được một bản prompt dùng tốt cho cả hai không?</li>
  <li>Preflight local: <code>python scripts/preflight_provider.py --provider ollama --model qwen2.5:7b</code>. Args JSON lỗi được giữ trong <code>args._invalid_json_arguments</code>.</li>
</ul>
""",
)

# 17 ── Rubric ───────────────────────────────────────────────────────────
slide(
    "Tiêu chí chấm: bắt buộc, bonus và lỗi nặng",
    """
<h2 class="title">Tiêu chí chấm: bắt buộc, bonus và lỗi nặng</h2>
<div class="grid grid-2">
  <section class="panel">
    <h3>Bắt buộc và bằng chứng</h3>
    <table class="data data--compact">
      <tbody>
        <tr><td>Provider thật, ít nhất 5 tool</td><td><code>tools.yaml</code>, <code>runs/</code></td></tr>
        <tr><td><code>v0</code> và 3 vòng tối ưu</td><td><code>version_log.csv</code></td></tr>
        <tr><td>1 tool mới, 3 unit test</td><td><code>tools/</code>, <code>tests/</code></td></tr>
        <tr><td>Eval case của nhóm</td><td><code>eval_group.json</code></td></tr>
        <tr><td>UI và link dùng thử</td><td>REPORT Phần A</td></tr>
        <tr><td>Chat live ít nhất 3 lượt</td><td><code>transcripts/</code></td></tr>
        <tr><td>Report Phần A và Phần B</td><td><code>REPORT.md</code></td></tr>
      </tbody>
    </table>
  </section>
  <div class="stack">
    <section class="panel">
      <h3>Bonus</h3>
      <ul>
        <li><code>send</code> có xác nhận.</li>
        <li><code>policy</code>, <code>papers</code>, <code>paper_text</code>.</li>
        <li>Small Local Model Challenge.</li>
        <li>UI cộng hơn 3 tool mới.</li>
      </ul>
    </section>
    <section class="anti">
      <h3>{ICONS_ANTI}Lỗi nặng</h3>
      <ul>
        <li>Lộ API key hoặc commit <code>.env</code>.</li>
        <li>Sửa nội dung case trong <code>eval_base.json</code>.</li>
        <li>Số liệu không có file run.</li>
        <li>Đổi tên tool không đồng bộ.</li>
      </ul>
    </section>
  </div>
</div>
<p class="note">Chưa có <code>RUBRIC.md</code>: key coach công bố điểm. Bonus tối đa 10 điểm.</p>
""",
    """
<strong>Về chấm điểm</strong>
<ul>
  <li>Audit repo lab cho thấy thiếu <code>RUBRIC.md</code>, <code>SUBMISSION.md</code>, <code>CHECKPOINTS.md</code>, <code>RULES.md</code>. Nếu ban chuyên môn đã có rubric, điền điểm vào slide này trước giờ học.</li>
  <li>Mục “lỗi nặng” suy ra từ các quy định trong README lab; mức trừ điểm cụ thể do key coach quyết định.</li>
  <li>Theo quy ước chung của khóa, bonus tối đa 10 điểm và là điểm lab, không phải điểm phát biểu.</li>
</ul>
""",
    done=5,
)

# 18 ── Submit checklist ─────────────────────────────────────────────────
slide(
    "Checklist nộp bài và khởi động lab",
    """
<h2 class="title">Checklist nộp bài và khởi động lab</h2>
<div class="grid grid-2">
  <div>
    <h3 class="sub">Trước khi rời phòng lab</h3>
    <ul class="checklist">
      <li>Tên repo đúng cú pháp <code>K5-&lt;L3A/L3B&gt;-DAY03-HoVaTen-MSSV-…</code></li>
      <li><code>artifacts/system_prompt.md</code>, <code>tools.yaml</code> là bản <code>v3</code></li>
      <li><code>version_log.csv</code> đủ <code>v0</code> đến <code>v3</code></li>
      <li><code>REPORT.md</code> Phần A và Phần B; poster nếu có</li>
      <li><code>eval_group.json</code>, <code>tests/</code>, <code>runs/</code>, <code>transcripts/</code></li>
      <li>Không có <code>.env</code> hay key</li>
      <li>Mỗi thành viên tự nộp link repo nhóm lên LMS</li>
    </ul>
  </div>
  <div class="stack">
    <section class="panel">
      <h3>Hạn nộp (GMT+7)</h3>
      <ul>
        <li class="deadline-morning">Lab sáng: trước 23h59 ngày học.</li>
        <li class="deadline-afternoon">Lab chiều hoặc tối: trước 11h59 ngày hôm sau.</li>
      </ul>
      <p>Chấm theo commit cuối trước deadline.</p>
    </section>
    <div class="cta-row">
      <button class="btn-primary" type="button" onclick="window.kickoffLab && window.kickoffLab()">Bắt đầu CP0: Setup</button>
      
    </div>
  </div>
</div>
""",
    """
<strong>Lời dặn kết thúc</strong>
<ul>
  <li>Bấm nút để quay về CP0 và bắt đầu.</li>
  <li>Hạn nộp, quy định chấm theo commit cuối và việc mỗi thành viên tự nộp LMS lấy theo quy ước chung của khóa (RULES và SUBMISSION Day 02); README lab Day 03 chưa ghi. Xác nhận lại với lớp.</li>
  <li>Chúc các nhóm làm việc tập trung và đọc log thật kỹ.</li>
</ul>
""",
    done=5,
)

out = pathlib.Path(__file__).resolve().parent.parent / "app/src/slides/content.json"
out.write_text(json.dumps(S, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {len(S)} slides -> {out}")
