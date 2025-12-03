
const etaMinutes = parseInt(document.getElementById("eta_minutes").value);
const createdAtString = document.getElementById("order_created").value;


const createdAt = new Date(createdAtString.replace(" ", "T"));


const deadline = new Date(createdAt.getTime() + etaMinutes * 60000);


const timerEl = document.getElementById("timer");

function updateTimer() {
  const now = new Date();
  const diff = deadline - now;

  if (diff <= 0) {
    timerEl.innerHTML = `<b style="color:#00b894">Tu pedido debería estar listo ahora 🎉</b>`;
    return;
  }

  const min = Math.floor(diff / 60000);
  const sec = Math.floor((diff % 60000) / 1000);

  timerEl.innerHTML = `Pedido listo en <b>${String(min).padStart(2, "0")}:${String(sec).padStart(2, "0")}</b>`;
}


updateTimer();


setInterval(updateTimer, 1000);
