function pad2(n) {
  return String(n).padStart(2, "0");
}

function fmtYMD(d) {
  return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`;
}

const calendar = (y, m, d, projectId) => {
  curYear = y;
  curMonth = m;
  let monthText = $("#monthText");

  let checkDay = new Date(y, m - 1, d);
  let year = checkDay.getFullYear();
  let month = checkDay.getMonth() + 1;
  let firstDay = new Date(year, month - 1, 1);
  let startOffset = firstDay.getDay();
  let daysInMonth = new Date(year, month, 0).getDate();

  let totalCells = startOffset + daysInMonth;
  let weekCount = Math.ceil(totalCells / 7);
  let cellCount = weekCount * 7;

  let gridStart = new Date(year, month - 1, 1 - startOffset);

  // 상단 월 텍스트
  monthText.text(`${year}-${pad2(month)}`);
  let dayList = $("#calendar-days");

  // 달에 따라 요일 입력
  for (let i = 0; i < cellCount; i++) {
    let d = new Date(gridStart);
    d.setDate(gridStart.getDate() + i);

    let cell = $("<div>");
    cell.addClass("calendar-day");

    let ymd = fmtYMD(d);
    cell.attr("data-date", ymd);

    cell.append($("<div>").addClass("date-num").text(d.getDate()));
    cell.append($("<div>").addClass("items"));

    $.ajax({
      url: "/api/projects/" + projectId + "/issues/range",
      type: "GET",
      data: {
        start: fmtYMD(d),
        end: fmtYMD(d),
      },
      success: function (issues) {
        let days = $("[data-date='" + ymd + "']");
        for (let i = 0; i < issues.length; i++) {
          let issue = issues[i];
          let title = issue.title;
          let btn = $("<button>");
          btn.addClass("Status");
          btn.text(title);

          btn.on("click", () => {
            showIssueDetailModal(issue, issues, i);
          });

          let item = days.find(".items");
          item.append(btn);
        }
      },
    });

    // 다른 달이면 다름
    if (d.getMonth() !== month - 1) cell.addClass("other-month");

    // 오늘이면 강조
    let today = new Date();
    if (fmtYMD(d) === fmtYMD(today)) cell.addClass("today");

    dayList.append(cell);
  }
};

var COMMENT_PAGE_SIZE = 5;

/**
 * 댓글 목록 렌더 + 페이징
 * comments: [{ id, author_id, author_name, content, created_at, deleted, ... }, ...]
 */
function renderCommentList(comments, page) {
  comments = Array.isArray(comments) ? comments : [];
  var total = comments.length;
  var totalPages = Math.max(1, Math.ceil(total / COMMENT_PAGE_SIZE));
  page = Math.max(1, Math.min(page, totalPages));
  window.currentCommentPage = page;

  var start = (page - 1) * COMMENT_PAGE_SIZE;
  var slice = comments.slice(start, start + COMMENT_PAGE_SIZE);

  var $list = $("#modal-detailInfo-comment-list");
  $list.empty();
  if (slice.length === 0) {
    $list.append($("<div>").addClass("text-muted").text("댓글이 없습니다."));
  } else {
    slice.forEach(function (c) {
      var authorName = c.author_name || "Unknown";
      var content = c.deleted ? "[삭제됨]" : (c.content || "");
      var createdAt = formatDateTime(c.created_at);
      var $item = $("<div>")
        .addClass("border-bottom pb-2 mb-2 comment-item")
        .append($("<div>").addClass("text-secondary small").text(authorName + " · " + createdAt))
        .append($("<div>").text(content));
      $list.append($item);
    });
  }

  $("#modal-detailInfo-comment-count").text("(" + total + "건)");

  var $paging = $("#commentPaging");
  $paging.empty();
  if (totalPages <= 1) {
    return;
  }
  var $prev = $("<button>").attr("type", "button").addClass("btn btn-outline-secondary btn-sm").text("이전");
  var $next = $("<button>").attr("type", "button").addClass("btn btn-outline-secondary btn-sm").text("다음");
  var $info = $("<span>").addClass("text-muted px-2").text(page + " / " + totalPages);
  $prev.on("click", function () {
    if (page > 1) renderCommentList(comments, page - 1);
  });
  $next.on("click", function () {
    if (page < totalPages) renderCommentList(comments, page + 1);
  });
  $paging.append($prev).append($info).append($next);
}

var STATUS_ORDER = { TODO: 0, IN_PROGRESS: 1, DONE: 2 };

/** 현재 상태에서 순차적으로만 이동 가능한 다음 상태 목록 (현재 + 인접 1칸) */
function getAllowedStatusOptions(currentStatus) {
  var n = STATUS_ORDER[currentStatus];
  if (n === undefined) return ["TODO", "IN_PROGRESS", "DONE"];
  var allowed = [currentStatus];
  if (n - 1 >= 0) {
    var prev = Object.keys(STATUS_ORDER).find(function (k) { return STATUS_ORDER[k] === n - 1; });
    if (prev && allowed.indexOf(prev) === -1) allowed.push(prev);
  }
  if (n + 1 <= 2) {
    var next = Object.keys(STATUS_ORDER).find(function (k) { return STATUS_ORDER[k] === n + 1; });
    if (next && allowed.indexOf(next) === -1) allowed.push(next);
  }
  return allowed;
}

/** 모달 내용만 이슈로 채움 */
function updateModalContent(issue) {
  window.currentIssueId = issue._id;
  window.currentIssueVersion = issue.version;
  window.currentIssue = issue;
  window.currentIssueComments = Array.isArray(issue.comments) ? issue.comments : [];
  window.currentIssueIsCreator = String(issue.created_by || "") === String(window.currentUserId || "");
  $("#modal-detailInfo-title").text(issue.title || "-");
  $("#modal-detailInfo-description").text(issue.description || "-");
  $("#modal-detailInfo-createdAt").text(formatDateTime(issue.created_at));
  $("#modal-detailInfo-creatorName").text(issue.creator_name || "-");
  $("#modal-detailInfo-updatedAt").text(formatDateTime(issue.updated_at));
  $("#modal-detailInfo-status").text(issue.status || "-");
  $("#modal-detailInfo-startDate").text(formatDateTime(issue.start_date));
  $("#modal-detailInfo-dueDate").text(formatDateTime(issue.due_date));
  renderCommentList(window.currentIssueComments, 1);
  $("#formComment").attr("action", "/issues/" + issue._id + "/comments");
  $("#commentContent").val("");
  $("#issueEditForm").hide();
  if (window.currentIssueIsCreator) {
    $("#modalDelBtn").show();
  } else {
    $("#modalDelBtn").hide();
  }
}

/** 이전/다음 버튼 표시 상태 갱신 */
function updateModalNavButtons() {
  var issues = window.currentModalIssues || [];
  var idx = window.currentModalIndex ?? 0;
  if (issues.length <= 1) {
    $("#modalPrevIssue").hide();
    $("#modalNextIssue").hide();
  } else {
    $("#modalPrevIssue").show().prop("disabled", idx <= 0);
    $("#modalNextIssue").show().prop("disabled", idx >= issues.length - 1);
  }
}

/**
 * 달력 이슈 클릭 시: 이슈 목록·인덱스 저장 후 모달 표시
 */
function showIssueDetailModal(issue, issues, currentIndex) {
  issues = issues || [issue];
  currentIndex = currentIndex >= 0 ? currentIndex : issues.findIndex(function (i) { return i._id === issue._id; });
  if (currentIndex < 0) currentIndex = 0;

  window.currentModalIssues = issues;
  window.currentModalIndex = currentIndex;

  updateModalContent(issues[currentIndex]);
  updateModalNavButtons();
  $("#modalCommentBtn").show();
  new bootstrap.Modal($("#modal-detailInfo")).show();
}

/** 모달 안에서 이전 이슈로 이동 */
function modalPrevIssue() {
  var issues = window.currentModalIssues || [];
  var idx = window.currentModalIndex ?? 0;
  idx--;
  if (idx >= 0 && idx < issues.length) {
    window.currentModalIndex = idx;
    updateModalContent(issues[idx]);
    updateModalNavButtons();
  }
}

/** 모달 안에서 다음 이슈로 이동 */
function modalNextIssue() {
  var issues = window.currentModalIssues || [];
  var idx = window.currentModalIndex ?? 0;
  idx++;
  if (idx >= 0 && idx < issues.length) {
    window.currentModalIndex = idx;
    updateModalContent(issues[idx]);
    updateModalNavButtons();
  }
}

function formatDateTime(isoStr) {
  if (!isoStr) return "-";
  try {
    let d = new Date(isoStr);
    return isNaN(d.getTime()) ? isoStr : d.toLocaleString("ko-KR");
  } catch (_) {
    return isoStr;
  }
}

// 이전달로 이동
const btnPrev = (projectId) => {
  let btnPrev = $("#btnPrev");
  btnPrev.on("click", (num) => {
    let dayList = $("#calendar-days");
    dayList.find(".calendar-day").remove();

    curMonth -= 1;
    let curDate = new Date(curYear, curMonth - 1);
    let tmpY = curDate.getFullYear();
    let tmpM = curDate.getMonth() + 1;

    calendar(tmpY, tmpM, 1, projectId);
  });
};

// 다음 달로 이동
const btnNext = (projectId) => {
  let btnNext = $("#btnNext");
  btnNext.on("click", () => {
    let dayList = $("#calendar-days");
    dayList.find(".calendar-day").remove();

    curMonth += 1;
    let curDate = new Date(curYear, curMonth - 1);
    let tmpY = curDate.getFullYear();
    let tmpM = curDate.getMonth() + 1;

    calendar(tmpY, tmpM, 1, projectId);
  });
};

const btnTodo = () => {
  let btnTodo = $("#Todo");

  btnTodo.on("click", () => {});
};

const dateMin = () => {
  let dateMin = $("#dueDate");
  dateMin.attr("min", fmtYMD(new Date()));
};

/** 수정 폼 열기: 생성자만 제목/상태 수정 가능, 상태는 순차만 허용 */
function openIssueEditForm() {
  var issue = window.currentIssue;
  if (!issue) return;
  $("#editTitle").val(issue.title || "").prop("readonly", !window.currentIssueIsCreator);
  $("#editDescription").val(issue.description || "");
  $("#editStartDate").val(issue.start_date ? issue.start_date.slice(0, 10) : "");
  $("#editDueDate").val(issue.due_date ? issue.due_date.slice(0, 10) : "").attr("min", fmtYMD(new Date()));
  $("#editTitleHint").text(window.currentIssueIsCreator ? "" : "(생성자만 수정 가능)");
  var statusOpts = getAllowedStatusOptions(issue.status || "TODO");
  var $sel = $("#editStatus").empty();
  statusOpts.forEach(function (s) {
    $sel.append($("<option>").val(s).text(s).prop("selected", s === (issue.status || "TODO")));
  });
  $("#editStatus").prop("disabled", !window.currentIssueIsCreator);
  $("#editStatusHint").text(window.currentIssueIsCreator ? "" : "(생성자만 수정 가능)");
  $("#issueEditForm").show();
  setTimeout(function () {
    var el = document.getElementById("issueEditForm");
    if (el) el.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, 50);
}

/** 수정 저장: PATCH /api/issues/<id>/fields (생성자만 title/status 포함) */
function saveIssueEdit() {
  var issueId = window.currentIssueId;
  var version = window.currentIssueVersion;
  if (!issueId || version === undefined) return;
  var payload = { expected_version: version };
  if (window.currentIssueIsCreator) {
    payload.title = $("#editTitle").val();
    payload.status = $("#editStatus").val();
  }
  payload.description = $("#editDescription").val();
  var start = $("#editStartDate").val();
  var due = $("#editDueDate").val();
  if (start !== undefined) payload.start_date = start || null;
  if (due !== undefined) payload.due_date = due || null;
  $.ajax({
    url: "/api/issues/" + issueId + "/fields",
    type: "PATCH",
    contentType: "application/json",
    data: JSON.stringify(payload),
    success: function (updated) {
      var issues = window.currentModalIssues || [];
      var idx = window.currentModalIndex ?? 0;
      if (issues.length && updated && updated._id) {
        issues[idx] = updated;
        updateModalContent(updated);
      }
      $("#issueEditForm").hide();
      $("#alert").removeClass("alert-danger").addClass("alert-success").text("수정되었습니다.");
      new bootstrap.Modal($("#modal1")).show();
    },
    error: function (err) {
      var msg = (err.responseJSON && err.responseJSON.message) ? err.responseJSON.message : "수정에 실패했습니다.";
      $("#alert").removeClass("alert-success").addClass("alert-danger").text(msg);
      new bootstrap.Modal($("#modal1")).show();
    },
  });
}

/** 이슈 삭제: POST /issues/<id>/delete 후 캘린더로 리다이렉트 */
function delIssue() {
  var issueId = window.currentIssueId;
  if (!issueId) return;
  var modalEl = document.getElementById("modal-detailInfo");
  if (modalEl) {
    var modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
  }
  var form = document.createElement("form");
  form.method = "POST";
  form.action = "/issues/" + issueId + "/delete";
  document.body.appendChild(form);
  form.submit();
}

$(function () {
  $("#modalPrevIssue").on("click", modalPrevIssue);
  $("#modalNextIssue").on("click", modalNextIssue);
  $("#issueEditSave").on("click", saveIssueEdit);
  $("#issueEditCancel").on("click", function () { $("#issueEditForm").hide(); });
});
