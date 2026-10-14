document.addEventListener("DOMContentLoaded", () => {
  const data = window.dashboardData || {};
  if (typeof Chart !== "undefined") {
    const palette = ["#7162f4", "#31b8a3", "#f4a65d", "#4d8ef7", "#e67ea5", "#8b9aaa", "#b49af5"];
    const typeCanvas = document.getElementById("typeChart");
    if (typeCanvas) {
      new Chart(typeCanvas, {
        type: "doughnut",
        data: { labels: data.typeLabels || [], datasets: [{ data: data.typeValues || [], backgroundColor: palette, borderWidth: 0, hoverOffset: 7 }] },
        options: { maintainAspectRatio: false, cutout: "70%", plugins: { legend: { position: "bottom", labels: { usePointStyle: true, boxWidth: 7, padding: 16, font: { family: "DM Sans", size: 11 } } } } }
      });
    }
    const extensionCanvas = document.getElementById("extensionChart");
    if (extensionCanvas) {
      new Chart(extensionCanvas, {
        type: "bar",
        data: { labels: data.extensionLabels || [], datasets: [{ label: "Files", data: data.extensionValues || [], backgroundColor: "#7162f4", borderRadius: 6, maxBarThickness: 28 }] },
        options: { maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false }, ticks: { font: { family: "DM Sans", size: 10 } } }, y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: "#edf0f6" } } } }
      });
    }
  }
  const search = document.getElementById("fileSearch");
  const table = document.getElementById("filesTable");
  if (search && table) {
    search.addEventListener("input", () => {
      const query = search.value.toLowerCase();
      table.querySelectorAll("tbody tr").forEach(row => {
        row.hidden = !row.textContent.toLowerCase().includes(query);
      });
    });
  }
});
