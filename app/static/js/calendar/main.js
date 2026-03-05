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
            showIssueDetailModal(issue);
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

/**
 * 달력 이슈 버튼 클릭 시 상세 모달에 title, createdBy, createdAt, status, dueDate, comment 표시
 */
function showIssueDetailModal(issue) {
  $("#modal-detailInfo-title").text(issue.title || "-");
  $("#modal-detailInfo-description").text(issue.description || "-");
  $("#modal-detailInfo-createdAt").text(formatDateTime(issue.created_at));
  $("#modal-detailInfo-status").text(issue.status || "-");
  $("#modal-detailInfo-dueDate").text(issue.due_date ? issue.due_date.slice(0, 10) : "-");
  $("#modal-detailInfo-comment").text(issue.commnets || "(없음)");
  new bootstrap.Modal($("#modal-detailInfo")).show();
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
