const mockDaily = {
  "2026-03-21": { 学业agent: 102, 活动agent: 63, 党团agent: 41, 就业agent: 88, 行政agent: 57 },
  "2026-03-20": { 学业agent: 95, 活动agent: 72, 党团agent: 39, 就业agent: 76, 行政agent: 52 },
  "2026-03-19": { 学业agent: 81, 活动agent: 60, 党团agent: 45, 就业agent: 69, 行政agent: 48 }
};

const datePicker = document.getElementById("datePicker");
const dailyTable = document.getElementById("dailyTable");

function renderDaily(date) {
  const data = mockDaily[date] || {
    学业agent: 0,
    活动agent: 0,
    党团agent: 0,
    就业agent: 0,
    行政agent: 0
  };

  dailyTable.innerHTML = "";
  Object.entries(data).forEach(([name, count]) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${name}</td><td>${count}</td>`;
    dailyTable.appendChild(tr);
  });
}

const today = new Date().toISOString().slice(0, 10);
datePicker.value = today;
renderDaily(today);

document.getElementById("loadData").addEventListener("click", () => {
  renderDaily(datePicker.value);
});
