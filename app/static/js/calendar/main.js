function pad2(n) {
  return String(n).padStart(2, "0");
}

function fmtYMD(d) {
  return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`;
}

const calendar = (y, m, d) => {
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

    let cell = $("<button>");
    cell.addClass("calendar-day");

    let ymd = fmtYMD(d);
    cell.attr("data-date", ymd);

    cell.append($("<div>").addClass("date-num").text(d.getDate()));
    cell.append($("<div>").addClass("items"));

    // 다른 달이면 다름
    if (d.getMonth() !== month - 1) cell.addClass("other-month");

    // 오늘이면 강조
    let today = new Date();
    if (fmtYMD(d) === fmtYMD(today)) cell.addClass("today");

    cell.on("click", () => {
      alert("clicked");
    });

    dayList.append(cell);
  }
};

// 이전달로 이동
const btnPrev = () => {
  let btnPrev = $("#btnPrev");
  btnPrev.on("click", (num) => {
    let dayList = $("#calendar-days");
    dayList.find(".calendar-day").remove();

    curMonth -= 1;
    let curDate = new Date(curYear, curMonth - 1);
    let tmpY = curDate.getFullYear();
    let tmpM = curDate.getMonth() + 1;

    calendar(tmpY, tmpM, 1);
  });
};

// 다음 달로 이동
const btnNext = () => {
  let btnNext = $("#btnNext");
  btnNext.on("click", () => {
    let dayList = $("#calendar-days");
    dayList.find(".calendar-day").remove();

    curMonth += 1;
    let curDate = new Date(curYear, curMonth - 1);
    let tmpY = curDate.getFullYear();
    let tmpM = curDate.getMonth() + 1;

    calendar(tmpY, tmpM, 1);
  });
};

// All 버튼 클릭
const btnAll = () => {
  let btnAll = $("#all");

  btnAll.on("click", () => {
    let days = $("[data-date='2026-03-05']");

    let btn = $("<button>");
    btn.addClass("Status");
    btn.text("TODO");

    let item = days.find(".items");

    item.append(btn);
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
