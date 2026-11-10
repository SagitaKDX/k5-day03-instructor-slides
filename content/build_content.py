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

S = []


def slide(title, html, notes, cp=None, minutes=None, label=None, done=None):
    S.append({
        "index": len(S),
        "title": title,
        "html": html.strip(),
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
    li = "".join(f"<li>{x}</li>" for x in items)
    return f'<section class="coach"><h3>Coach nói gì</h3><ul>{li}</ul></section>'


def anti(*items):
    li = "".join(f"<li>{x}</li>" for x in items)
    return f'<section class="anti"><h3>Anti-pattern thường gặp</h3><ul>{li}</ul></section>'


def check(text):
    return f'<section class="selfcheck"><h3>Tự kiểm tra</h3><p>{text}</p></section>'


# 0 ── Title ─────────────────────────────────────────────────────────────
slide(
    "Day 03: Prompt Engineering và Tool Calling",
    """
<div class="title-slide">
  <div class="title-copy">
    <p class="course">VinUni AI20k, K5 Level 3 (L3A và L3B), {{SESSION}}, {{SESSION_RANGE}}</p>
    <h1 class="hero">Agent gọi đúng tool nhờ bằng chứng, không nhờ cảm giác</h1>
    <p class="lede">Hôm nay nhóm dựng một research agent nhỏ chạy thực tế: nhận request, chọn tool, truyền args, gọi API thật và lưu log JSON. Dùng chính log đó để cải thiện prompt và tool declaration qua từng phiên bản.</p>
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
  <section><h2>Hình thức</h2><p>Làm việc theo nhóm trên repo <code>starter_v0/</code>.</p></section>
  <section><h2>Đầu ra</h2><p>Agent kèm UI, 4 phiên bản <code>v0</code> đến <code>v3</code> có log, eval và test riêng, cùng report.</p></section>
  <section><h2>Tiêu chí chấm</h2><p>Đánh giá vòng lặp có bằng chứng, không chấm điểm câu trả lời cảm tính.</p></section>
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
<p class="lede">Mỗi phiên bản <code>v0</code>, <code>v1</code>, <code>v2</code>, <code>v3</code> đều qua trọn sáu bước. Mỗi vòng chỉ kiểm chứng một giả thuyết.</p>
<ol class="loop">
  <li><b>Chạy baseline</b><span>Gọi provider thật, không dùng mock. Output nằm trong <code>runs/*.json</code>.</span></li>
  <li><b>Đọc run JSON</b><span>Sai tool, sai args, không hỏi lại, hay gọi tool thừa?</span></li>
  <li><b>Sửa một điểm</b><span>Một dòng trong <code>system_prompt.md</code> hoặc một description trong <code>tools.yaml</code>.</span></li>
  <li><b>Chạy lại, ghi log</b><span>Một dòng trong <code>version_log.csv</code>, có metric trước và sau.</span></li>
  <li><b>Tự viết eval</b><span>Case trong <code>eval_group.json</code> đo đúng lỗi nhóm quan tâm.</span></li>
  <li><b>Viết report</b><span>Dựa trên log thật, không suy đoán theo cảm tính.</span></li>
</ol>
<div class="grid grid-3 roles">
  <section class="panel"><h3>Người đọc log</h3><p>Mở file run JSON, gán loại lỗi cho từng case FAIL và đề xuất giả thuyết.</p></section>
  <section class="panel"><h3>Người viết tool và test</h3><p>Viết tool mới, tạo <code>TOOL.md</code>, đăng ký hàm và giữ <code>pytest</code> luôn xanh.</p></section>
  <section class="panel"><h3>Người dựng UI và report</h3><p>Dựng UI qua Streamlit hoặc Vercel, lấy link dùng thử, hoàn thành <code>REPORT.md</code> Phần A.</p></section>
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
    <p>Mở file run JSON, đọc <code>failures</code> và <code>observed_mismatch</code>, gán mỗi case FAIL vào một trong sáu loại lỗi: <code>wrong_tool</code>, <code>wrong_arg_value</code>, <code>missing_info</code>, <code>wrong_boundary</code>, <code>unnecessary_tool</code>, <code>out_of_scope</code>.</p>
    <p class="cp-ref">Dùng ở CP1, CP2</p>
  </section>
  <section class="panel">
    <h3>Viết prompt và tool declaration có ranh giới rõ</h3>
    <p>Mỗi tool nói rõ công dụng, khi nào dùng, khi nào không dùng và quy ước args. Agent hỏi lại bằng <code>clarify</code> khi thiếu thông tin, chỉ <code>send</code> khi user đã xác nhận.</p>
    <p class="cp-ref">Dùng ở CP2, CP3, CP5</p>
  </section>
  <section class="panel">
    <h3>Tách hai loại kiểm thử: eval và unit test</h3>
    <p>Eval đo model có chọn đúng tool và args không. Unit test đo code của tool nhận args đó có chạy đúng không. Hai loại lỗi này khác nhau và cần hai bộ test riêng biệt.</p>
    <p class="cp-ref">Dùng ở CP2, CP3</p>
  </section>
  <section class="panel">
    <h3>Ra quyết định bằng số đo có thể kiểm lại</h3>
    <p>Mỗi phiên bản có một giả thuyết, metric trước và sau, <code>prompt_hash</code>, <code>tools_hash</code> và đường dẫn file run. Không có file run thì không có kết luận.</p>
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
    <tr><td class="num">15:00 đến 15:30</td><td><b>CP1</b> Baseline và UI</td><td>Đo</td><td>Chạy <code>v0</code>, gán loại lỗi cho từng case FAIL, dựng UI</td></tr>
    <tr><td class="num">15:30 đến 16:00</td><td><b>CP2</b> v1 và tool mới</td><td>Sửa</td><td>Một giả thuyết, chạy <code>v1</code>; ít nhất 1 tool mới có <code>TOOL.md</code> và 3 unit test</td></tr>
    <tr><td class="num">16:00 đến 16:30</td><td><b>CP3</b> Eval nhóm và v2</td><td>Đo lại</td><td>Tạo case trong <code>eval_group.json</code>, chạy <code>v2</code>, <code>REPORT.md</code> Phần A</td></tr>
    <tr class="row-key"><td class="num">16:30 đến 17:30</td><td><b>CP4</b> Team showdown</td><td>Demo</td><td>Nhóm khác dùng thử agent qua link public; chat live có transcript</td></tr>
    <tr><td class="num">Từ 17:30</td><td><b>CP5</b> v3 và report</td><td>Đóng gói</td><td>Chạy <code>v3</code>, <code>version_log.csv</code> đủ 4 dòng, <code>REPORT.md</code> Phần B</td></tr>
  </tbody>
</table>
<p class="note">Mốc cứng duy nhất: <code>REPORT.md</code> Phần A phải xong trước 16:30, vì nhóm khác cần đọc để hiểu agent khi thử.</p>
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
    <p>Họ tên trước, MSSV sau, nối bằng dấu <code>-</code>, không dấu tiếng Việt, ngày học hai chữ số (<code>DAY03</code>).</p>
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
      <h3>Lỗi đặt tên thường gặp</h3>
      <ul>
        <li>Đặt tên nhóm tùy tiện (<code>Nhom1-AIAgent</code>) thay cho họ tên và MSSV nhóm trưởng.</li>
        <li>Quên mã lớp <code>L3A</code> hoặc <code>L3B</code>, ghi <code>DAY3</code> thay cho <code>DAY03</code>.</li>
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
    <tr><td class="num">Prompt và tool</td><td>Chỉ sửa <code>artifacts/system_prompt.md</code> và <code>artifacts/tools.yaml</code>. Mỗi phiên bản một giả thuyết.</td><td>Sửa nhiều chỗ cùng lúc rồi gọi đó là một phiên bản.</td></tr>
    <tr><td class="num">Eval base</td><td>Đọc case để hiểu agent sai ở đâu.</td><td>Sửa nội dung case trong <code>data/eval_base.json</code> khiến run không hợp lệ.</td></tr>
    <tr><td class="num">Đổi tên tool</td><td>Đổi đồng bộ cả ba nơi: <code>tools.yaml</code>, <code>tools/__init__.py</code>, hai file eval. Chạy lại <code>test_tool_contract.py</code>.</td><td>Chỉ đổi một nơi, để eval báo <em>not declared in tools.yaml</em>.</td></tr>
    <tr><td class="num">Unit test</td><td>Mock HTTP bằng fixture <code>fake_http</code>. Test chạy offline, không tốn credit.</td><td>Gọi API thật trong test.</td></tr>
    <tr><td class="num">Report</td><td>Mọi số liệu trỏ về file trong <code>runs/</code> hoặc <code>transcripts/</code>.</td><td>Viết kết quả từ trí nhớ hay nhận định cảm tính.</td></tr>
    <tr><td class="num">Bảo mật</td><td><code>.env</code> nằm trong <code>.gitignore</code>, kiểm tra <code>git status</code> trước mỗi lần push.</td><td>Commit <code>.env</code> hay API key, kể cả trong lịch sử commit.</td></tr>
  </tbody>
</table>
<p class="note">Nguyên tắc cốt lõi: điểm nằm ở chất lượng lập luận và tính thật của bằng chứng. Một phiên bản có giả thuyết rõ mà không cải thiện vẫn quý hơn ba phiên bản tăng điểm mà không ai giải thích được.</p>
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
        <tr><td><code>OPENROUTER_API_KEY</code></td><td>model (hoặc OpenAI, Anthropic, Gemini)</td></tr>
        <tr><td><code>TAVILY_API_KEY</code></td><td><code>lookup</code></td></tr>
        <tr><td><code>FIRECRAWL_API_KEY</code></td><td><code>fetch</code></td></tr>
        <tr><td><code>RAPIDAPI_KEY</code></td><td><code>timeline</code>, <code>social_search</code></td></tr>
        <tr><td><code>TELEGRAM_BOT_TOKEN</code>, <code>TELEGRAM_CHAT_ID</code></td><td>bonus <code>send</code></td></tr>
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
        "Chạy eval khi preflight còn lỗi, dẫn đến việc đọc FAIL do hạ tầng thành FAIL do prompt.",
        "Dán key thẳng vào mã nguồn hoặc gửi vào chat nhóm.",
        "Dùng hết credit gói miễn phí (khoảng 1.000 lượt mỗi tháng cho Tavily, Firecrawl, RapidAPI) vì chạy eval lặp vô ích.",
    )}
    {check("Nhóm bạn chạy <code>pytest</code> và đọc được dòng tổng kết (bao nhiêu passed, bao nhiêu skipped) chưa?")}
  </div>
</div>
""",
    """
<strong>Gợi ý hướng dẫn CP0</strong>
<ul>
  <li>Quan sát xem nhóm nào chưa có key Tavily, Firecrawl hoặc RapidAPI. Thiếu key thì tool tương ứng trả error dict, eval FAIL vì hạ tầng chứ không vì prompt.</li>
  <li>Nhóm dùng provider khác OpenRouter đổi cờ <code>--provider</code> tương ứng.</li>
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
<pre class="code">python run_eval.py \\
  --provider openrouter \\
  --version v0 \\
  --suite base \\
  --eval-cases data/eval_base.json

python scripts/parse_runs.py runs/ \\
  --output analysis/base_runs.csv</pre>
    <section class="panel">
      <h3>Đọc trong run JSON</h3>
      <ol class="plain">
        <li>Bốn chỉ số trong <code>summary</code>.</li>
        <li>Với mỗi case FAIL: xem <code>failures</code>, <code>observed_mismatch</code> và tool call thực tế.</li>
        <li>Ghi <code>prompt_hash</code>, <code>tools_hash</code> vào dòng <code>v0</code>.</li>
      </ol>
    </section>
    <section class="panel">
      <h3>Song song: dựng UI</h3>
      <p>Bắt buộc có UI chạy được trên Streamlit hoặc Vercel để dùng lại ở showdown lúc 16:30.</p>
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
        "Chạy lại baseline nhiều lần rồi chọn lần điểm cao nhất.",
        "Để dành việc dựng UI tới 16:20 mới làm.",
    )}
    {check("Nhóm bạn kể được tên 3 case FAIL của <code>v0</code> và loại lỗi của từng case không?")}
  </div>
</div>
""",
    """
<strong>Hành động của giảng viên trong CP1</strong>
<ul>
  <li>Quan sát màn hình các nhóm: ai đang mở run JSON, ai chỉ nhìn điểm tổng. Yêu cầu nhóm chỉ ra <code>observed_mismatch</code> của một case cụ thể.</li>
  <li>Nhắc ghi ngay dòng <code>v0</code> vào <code>version_log.csv</code> kèm hash và đường dẫn file run.</li>
  <li>Script <code>parse_runs.py</code> là tùy chọn, nhưng giúp nhóm so sánh nhiều run trong một bảng.</li>
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
<h2 class="title">Sáu loại lỗi, mỗi loại một case mẫu từ base eval</h2>
<table class="data">
  <thead><tr><th>Loại lỗi</th><th>Case mẫu</th><th>User nói</th><th>Kỳ vọng</th></tr></thead>
  <tbody>
    <tr><td><code>wrong_tool</code></td><td>R01</td><td>Tweet mới nhất của Sam Altman là gì?</td><td><code>timeline(screenname="sama")</code></td></tr>
    <tr><td><code>wrong_arg_value</code></td><td>R06</td><td>Tin công nghệ trong tuần này</td><td><code>lookup(topic="news", timeframe="week")</code></td></tr>
    <tr><td><code>missing_info</code></td><td>R11</td><td>Tóm tắt bài viết này hộ mình</td><td>Gọi <code>clarify</code>, không tự đoán URL</td></tr>
    <tr class="row-key"><td><code>wrong_boundary</code></td><td>R12</td><td>Đăng bản tin này lên Telegram giúp mình</td><td>Gọi <code>clarify(response_type="yes_no")</code> trước khi gửi</td></tr>
    <tr><td><code>unnecessary_tool</code></td><td>R09</td><td>Bạn là gì và làm được những gì?</td><td>Trả lời thẳng, không gọi tool</td></tr>
    <tr><td><code>out_of_scope</code></td><td>R08</td><td>Nguyên hàm của x^2 là gì?</td><td>Từ chối lịch sự, không gọi tool</td></tr>
  </tbody>
</table>
<p class="caption">Base eval có 20 case: 6 <code>wrong_tool</code>, 6 <code>wrong_arg_value</code>, 4 <code>missing_info</code>, 2 <code>out_of_scope</code>, 1 <code>unnecessary_tool</code>, 1 <code>wrong_boundary</code>. Sáu case multi turn kiểm tra agent có nhớ và sửa args theo lượt sau không.</p>
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
        <li>Đoán thay vì gọi <code>clarify</code>, kể cả tự chọn tài khoản hay URL.</li>
        <li>Gửi hoặc đăng ngay mà không chờ xác nhận.</li>
        <li>Ép mọi việc vào một bước, một tool.</li>
      </ul>
    </figure>
    <section class="panel">
      <h3>Viết lại mỗi tool trong <code>tools.yaml</code></h3>
      <p>Làm gì, khi nào dùng, khi nào không. Ghi rõ quy ước args: handle không có <code>@</code>, <code>topic=news</code> cho tin tức, <code>timeframe</code>, <code>search_type=Top|Latest</code>. Mô tả <code>send</code> chỉ chạy khi <code>confirmed=true</code>.</p>
    </section>
  </div>
  <div class="stack">
    {coach(
        "<b>Một giả thuyết mỗi phiên bản:</b> ví dụ “Agent gọi <code>lookup</code> thay vì <code>timeline</code> vì description không nói khi nào dùng <code>timeline</code>.”",
        "<b>Sửa một thứ, chạy lại, so số:</b> không cải thiện thì đổi giả thuyết, không chồng thêm sửa đổi.",
        "<b>Prompt hay tool declaration?</b> Rule routing chung đặt trong prompt; quy ước args của một tool đặt trong description của tool đó.",
    )}
    {anti(
        "Viết lại toàn bộ prompt trong một lần rồi gọi là <code>v1</code>.",
        "Hard-code đáp án của từng case vào prompt (chẳng hạn “nếu user hỏi Sam Altman thì…”).",
        "Ghi <code>metric_after</code> mà không có <code>run_file</code> tương ứng.",
    )}
    {check("Giả thuyết của <code>v1</code> có viết được thành câu “Agent sai X vì Y, nên sửa Z” không?")}
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
      <li>File <code>tools/&lt;tên&gt;/tool.py</code> tự chứa, trả error dict thay vì raise.</li>
      <li>Tạo file <code>TOOL.md</code> với frontmatter như trên.</li>
      <li>Đăng ký trong <code>TOOL_FUNCTIONS</code> của <code>tools/__init__.py</code>.</li>
      <li>Khai báo trong <code>artifacts/tools.yaml</code>, kèm ít nhất 1 eval case route tới tool mới.</li>
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
      <p>Mẫu có sẵn để tham khảo: <code>test_send_without_confirmation_does_not_call_network</code>, <code>test_lookup_http_error_returns_error_dict</code>.</p>
    </section>
    {coach(
        "<b>Tên test mô tả hành vi:</b> một test kiểm tra một hành vi; assert cả request gửi đi lẫn kết quả trả về.",
        "<b>Chạy <code>pytest tests/test_tool_contract.py</code> sau mỗi lần thêm tool:</b> test này giữ <code>tools.yaml</code>, code và eval luôn đồng bộ.",
    )}
    {anti(
        "Tool mới có code nhưng quên <code>TOOL.md</code> hoặc quên đăng ký, khiến contract test đỏ.",
        "Test chỉ gọi hàm rồi <code>assert result</code>, không kiểm tra dữ liệu cụ thể.",
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
      <section class="panel"><h3>Eval đo model</h3><p>Chọn đúng tool, đúng args, biết hỏi lại và biết từ chối.</p></section>
      <section class="panel"><h3>Unit test đo code</h3><p>Nhận args đó, tool có gọi đúng API và trả đúng kết quả không.</p></section>
    </div>
  </div>
  <div class="stack">
    {coach(
        "<b>Viết case từ lỗi thật:</b> mỗi case nhắm vào một lỗi nhóm đã thấy trong run <code>v0</code> hoặc <code>v1</code>.",
        "<b>Có cả single turn và multi turn:</b> multi turn kiểm tra agent có nhớ thông tin và sửa args theo lượt sau.",
        "<b>Challenge+:</b> thử input biên như <code>limit=0</code>, <code>max_results=\"5\"</code>, <code>items</code> thiếu <code>url</code>. Tìm được bug thì sửa, giữ test làm regression test, ghi vào B5.",
    )}
    {anti(
        "Viết case dễ để agent PASS cho đẹp.",
        "Chép lại case của <code>eval_base.json</code> và đổi vài chữ.",
        "Quên <code>metadata.what_it_tests</code>, khiến người chấm không biết case đo điều gì.",
    )}
    {check("Nhóm có chỉ ra được một lỗi mà unit test bắt được nhưng eval không bắt được không?")}
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
    <p>Baseline <code>v0</code>, ít nhất hai vòng tối ưu, một tool mới có test và case eval của nhóm. Agent đã đủ hoàn thiện để người ngoài dùng thử.</p>
  </section>
  <section class="panel">
    <h3>Điểm mới ở CP4</h3>
    <p>Người thử là nhóm khác, không biết prompt của nhóm. Họ sẽ hỏi theo cách nhóm chưa lường trước; đó là bài eval thật nhất của buổi.</p>
  </section>
</div>
<h3 class="sub">Ba việc phải xong trước 16:30</h3>
<ol class="loop loop--three">
  <li><b>Chạy UI và mở tunnel</b><span><code>cloudflared tunnel --url http://localhost:8501</code>, copy link <code>trycloudflare.com</code>.</span></li>
  <li><b>Viết Phần A của report</b><span>Agent làm gì, có tool nào, 3 đến 5 câu hỏi mẫu kèm link dùng thử.</span></li>
  <li><b>Chọn người trực demo</b><span>Một người giữ máy chạy UI và tunnel suốt CP4; những người còn lại đi thử agent của nhóm khác.</span></li>
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
<pre class="code">streamlit run app.py   <span class="c"># http://localhost:8501</span>
cloudflared tunnel --url http://localhost:8501

<span class="c"># cài cloudflared</span>
brew install cloudflared                      <span class="c"># macOS</span>
winget install --id Cloudflare.cloudflared    <span class="c"># Windows</span></pre>
    <section class="panel">
      <h3>Phần A của report, gói gọn một trang</h3>
      <ol class="plain">
        <li>A1. Agent làm được gì, kèm link dùng thử.</li>
        <li>A2. Bảng tool: tên, công dụng, đánh dấu tool nhóm tự thêm.</li>
        <li>A3. 3 đến 5 câu hỏi mẫu để nhóm khác tự thử.</li>
      </ol>
      <p>Khuyến khích làm thêm poster <code>artifacts/poster.html</code> hoặc <code>poster.svg</code>. Bản markdown vẫn bắt buộc.</p>
    </section>
  </div>
  <div class="stack">
    {coach(
        "<b>Thử ba kiểu request:</b> một request bình thường, một request thiếu thông tin, một request “gửi bản tin lên Telegram”.",
        "<b>Quan sát ranh giới:</b> agent hỏi lại trước khi gửi, hay hành động ngay?",
        "<b>Ghi lại lỗi nhóm khác tìm ra:</b> đó là nguyên liệu cho giả thuyết của <code>v3</code>.",
    )}
    {anti(
        "Chỉ demo những câu đã biết chắc agent trả lời được.",
        "Tắt tunnel giữa chừng khiến nhóm khác mở link thấy lỗi.",
        "Phần A viết như quảng cáo, không nói rõ tool nào làm gì.",
    )}
    {check("Một người ngoài nhóm đọc Phần A trong 1 phút có tự đặt được câu hỏi để thử agent không?")}
  </div>
</div>
""",
    """
<strong>Điều phối showdown</strong>
<ul>
  <li>Cho các nhóm trong cùng zone thử chéo agent của nhau. Mỗi nhóm vừa trực demo vừa đi thử.</li>
  <li>Quan sát agent có hỏi lại trước khi gửi không. Đây là phép thử ranh giới quan trọng nhất của buổi.</li>
  <li>Nếu nhóm deploy hẳn lên Vercel hoặc Streamlit Cloud thì dùng link đó thay cho tunnel.</li>
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
    <p>Một câu hỏi research rõ ràng. Agent nên chọn đúng tool ngay lượt đầu.</p>
  </section>
  <section class="panel">
    <h3>Request thiếu thông tin</h3>
    <p>Không nói rõ account hay URL, lượt sau mới bổ sung. Agent nên gọi <code>clarify</code>, không tự đoán.</p>
  </section>
  <section class="panel">
    <h3>Request gửi bản tin</h3>
    <p>“Đăng lên Telegram.” Agent hành động ngay hay hỏi lại? Nhóm tự quyết định hành vi đúng rồi sửa prompt cho khớp.</p>
  </section>
</div>
<pre class="code">python chat.py --provider openrouter --version v3</pre>
<p class="caption">Mỗi lượt được ghi vào <code>transcripts/*.transcript.json</code> làm bằng chứng cho mục B4 của report. Mẫu định dạng có trong <code>samples/transcripts/</code>.</p>
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
        <tr><td>B2</td><td>Phân tích lỗi</td><td><code>failures</code>, loại lỗi, cách sửa</td></tr>
        <tr><td>B3</td><td>Eval case của nhóm</td><td><code>eval_group.json</code></td></tr>
        <tr><td>B4</td><td>Chat live</td><td><code>transcripts/</code></td></tr>
        <tr><td>B5</td><td>Bonus và bug tìm được</td><td>output <code>pytest</code>, regression test</td></tr>
        <tr><td>B6</td><td>Reflection</td><td>bốn câu hỏi trong template</td></tr>
        <tr><td>B7</td><td>Small local model</td><td>run của model local</td></tr>
      </tbody>
    </table>
  </div>
  <div class="stack">
    {coach(
        "<b>Lỗi nhóm khác tìm ra ở CP4 là giả thuyết tốt nhất cho <code>v3</code>.</b>",
        "<b>B6 hỏi bốn câu:</b> lỗi nào thuộc về <code>system_prompt.md</code>, lỗi nào thuộc về <code>tools.yaml</code>, lỗi nào cần review tay thay vì chấm tự động, nhóm sẽ cải thiện gì tiếp.",
        "<b>Phần B có thể hoàn thiện sau buổi,</b> nhưng <code>v3</code> nên chạy xong trong buổi để còn đọc log.",
    )}
    {anti(
        "Dòng trong B1 không có <code>run_file</code>, hoặc trỏ tới file không có trong <code>runs/</code>.",
        "B2 chỉ ghi “sai tool”, không ghi tool call thực tế và cách sửa.",
        "Reflection viết chung chung, có thể dán vào report của bất kỳ nhóm nào.",
    )}
    {check("Mỗi con số trong report có mở ngược lại được tới một file trong <code>runs/</code> hoặc <code>transcripts/</code> không?")}
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
python scripts/preflight_provider.py \\
  --provider ollama --model qwen2.5:7b

python run_eval.py --provider ollama \\
  --model qwen2.5:7b --version v3-qwen7b \\
  --suite base --eval-cases data/eval_base.json</pre>
    <section class="panel">
      <h3>Tiêu chí đạt</h3>
      <ol class="plain">
        <li>Ít nhất 2 model local chạy base eval với prompt <code>v3</code>, không sửa gì.</li>
        <li>Ít nhất 2 vòng tối ưu riêng (<code>v4-local</code>, <code>v5-local</code>), mỗi vòng một giả thuyết.</li>
        <li>Bảng so sánh cloud và local trong B7.</li>
        <li>Một kết luận có bằng chứng: điều gì giúp model nhỏ gọi tool đúng hơn.</li>
      </ol>
    </section>
  </div>
  <div class="stack">
    <section class="panel">
      <h3>Lỗi đặc thù của model nhỏ cần đếm</h3>
      <ul>
        <li>Chọn sai tool hoặc bịa tên tool không có trong <code>tools.yaml</code>.</li>
        <li>Args JSON lỗi, giữ lại trong <code>args._invalid_json_arguments</code>.</li>
        <li>Không gọi tool, trả lời luôn; hoặc gọi tool khi lẽ ra phải <code>clarify</code>.</li>
        <li>Gọi thừa hoặc lặp cùng một tool.</li>
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
    <h3>Bắt buộc, và bằng chứng người chấm mở ra xem</h3>
    <table class="data data--compact">
      <tbody>
        <tr><td>Chạy bằng provider thật, agent có ít nhất 5 tool</td><td><code>tools.yaml</code>, <code>runs/</code></td></tr>
        <tr><td>Baseline <code>v0</code> và 3 vòng <code>v1</code>, <code>v2</code>, <code>v3</code></td><td><code>version_log.csv</code></td></tr>
        <tr><td>Ít nhất 1 tool mới, mỗi tool ít nhất 3 unit test</td><td><code>tools/</code>, <code>tests/</code></td></tr>
        <tr><td>Eval case của nhóm</td><td><code>eval_group.json</code></td></tr>
        <tr><td>UI chạy được và link dùng thử</td><td>REPORT Phần A</td></tr>
        <tr><td>Chat live ít nhất 3 lượt</td><td><code>transcripts/</code></td></tr>
        <tr><td>Report Phần A và Phần B</td><td><code>REPORT.md</code></td></tr>
      </tbody>
    </table>
  </section>
  <div class="stack">
    <section class="panel">
      <h3>Bonus</h3>
      <ul>
        <li><code>send</code> có bước xác nhận, có transcript chứng minh.</li>
        <li>Tool mở rộng: <code>policy</code>, <code>papers</code>, <code>paper_text</code>.</li>
        <li>Small Local Model Challenge.</li>
        <li>Điểm thưởng: có UI và tự viết hơn 3 tool mới.</li>
      </ul>
    </section>
    <section class="anti">
      <h3>Lỗi nặng</h3>
      <ul>
        <li>Lộ API key hoặc commit <code>.env</code>.</li>
        <li>Sửa nội dung case trong <code>eval_base.json</code>.</li>
        <li>Số liệu trong report không có file run tương ứng.</li>
        <li>Đổi tên tool không đồng bộ, eval chấm sai cả loạt.</li>
      </ul>
    </section>
  </div>
</div>
<p class="note">Repo lab chưa có <code>RUBRIC.md</code> nên slide này chưa ghi điểm số. Key coach công bố thang điểm; theo quy ước chung của khóa, bonus tối đa 10 điểm và là điểm lab, không phải điểm phát biểu.</p>
""",
    """
<strong>Về chấm điểm</strong>
<ul>
  <li>Audit repo lab cho thấy thiếu <code>RUBRIC.md</code>, <code>SUBMISSION.md</code>, <code>CHECKPOINTS.md</code>, <code>RULES.md</code>. Nếu ban chuyên môn đã có rubric, điền điểm vào slide này trước giờ học.</li>
  <li>Mục “lỗi nặng” suy ra từ các quy định trong README lab; mức trừ điểm cụ thể do key coach quyết định.</li>
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
      <li><code>version_log.csv</code> đủ <code>v0</code> đến <code>v3</code>, mỗi dòng có <code>run_file</code></li>
      <li><code>REPORT.md</code> Phần A và Phần B; poster nếu có</li>
      <li><code>eval_group.json</code>, <code>tests/</code>, <code>runs/</code>, <code>transcripts/</code></li>
      <li>Không có <code>.env</code>, không có key trong lịch sử commit</li>
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
      <p>Chấm theo commit cuối cùng trước deadline. Commit sau mốc đó không được chấm.</p>
    </section>
    <div class="cta-row">
      <button class="btn-primary" type="button" onclick="window.kickoffLab && window.kickoffLab()">Bắt đầu CP0: Setup</button>
      <p class="caption">Nhảy thẳng tới slide CP0.</p>
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
