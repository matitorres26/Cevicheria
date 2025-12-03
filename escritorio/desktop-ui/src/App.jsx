import { useEffect, useState, useRef } from "react";
import { sendNotification, requestPermission } from "@tauri-apps/plugin-notification";
import { writeTextFile, readTextFile, BaseDirectory } from "@tauri-apps/plugin-fs";

const API_URL = "https://cevicheria-production-1707.up.railway.app";
const WS_URL = "wss://cevicheria-production-1707.up.railway.app/ws/orders/";
async function apiPatch(url, body) {
  try {
    const r = await fetch(url, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return true;
  } catch {
    return false;
  }
}

const statusColors = {
  NEW: "#2ecc71",
  IN_PROGRESS: "#f1c40f",
  READY: "#3498db",
  DELIVERED: "#95a5a6",
};

function formatTimer(msLeft) {
  if (msLeft <= 0) return "Listo";
  const sec = Math.floor(msLeft / 1000);
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}m ${s.toString().padStart(2, "0")}s`;
}

async function saveOrders(orders) {
  try {
    await writeTextFile("pedidos.json", JSON.stringify(orders, null, 2), {
      baseDir: BaseDirectory.AppData,
    });
  // eslint-disable-next-line no-empty
  } catch {}
}

async function loadOrders() {
  try {
    const data = await readTextFile("pedidos.json", {
      baseDir: BaseDirectory.AppData,
    });
    return JSON.parse(data);
  } catch {
    return [];
  }
}

export default function App() {
  const [connected, setConnected] = useState(false);
  const [orders, setOrders] = useState([]);
  const [now, setNow] = useState(Date.now());
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    let delay = 2000;

    const connect = () => {
      if (wsRef.current) return;

      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        delay = 2000;
      };

      ws.onclose = () => {
        setConnected(false);
        wsRef.current = null;
        reconnectRef.current = setTimeout(connect, delay);
        delay = Math.min(delay * 1.5, 10000);
      };

      ws.onerror = () => ws.close();

      ws.onmessage = (msg) => {
        try {
          const data = JSON.parse(msg.data);
          if (data?.type !== "new_order") return;

          const order = { ...data.order, _receivedAt: Date.now() };

          setOrders((prev) => {
            if (prev.some((o) => o.id === order.id)) return prev;
            const updated = [order, ...prev];
            saveOrders(updated);
            return updated;
          });

          sendNotification({
            title: "🦞 Nuevo Pedido",
            body: `Pedido #${order.id} recibido`,
          });

          new Audio("/notification.mp3").play().catch(() => {});
        // eslint-disable-next-line no-empty
        } catch {}
      };
    };

    loadOrders().then(setOrders);
    requestPermission();
    connect();

    return () => {
      wsRef.current?.close();
      clearTimeout(reconnectRef.current);
    };
  }, []);

  async function setOrderStatus(id, status) {
    const ok = await apiPatch(`${API_URL}/orders/${id}/`, { status });
    if (!ok) return;

    setOrders((prev) => {
      const updated = prev.map((o) => (o.id === id ? { ...o, status } : o));
      saveOrders(updated);
      return updated;
    });
  }

  return (
    <div
      style={{
        padding: "40px",
        backgroundColor: "#1e1e1e",
        minHeight: "100vh",
        color: "#fff",
        fontFamily: "Poppins",
      }}
    >
      <h1>🦞 SOS Cevichería & Sushi</h1>

      <p>
        Estado:{" "}
        <strong style={{ color: connected ? "lightgreen" : "red" }}>
          {connected ? "Conectado 🟢" : "Desconectado 🔴"}
        </strong>
      </p>

      <h3>📦 Pedidos</h3>

      {orders.length === 0 && <p>Sin pedidos...</p>}

      {orders.map((o) => {
        const eta = (o.eta_minutes || 30) * 60000;
        const left = o._receivedAt ? o._receivedAt + eta - now : 0;

        return (
          <div
            key={o.id}
            style={{
              background: "#2c2c2c",
              padding: "15px",
              marginBottom: "12px",
              borderRadius: "10px",
              borderLeft: `6px solid ${statusColors[o.status] || "#2ecc71"}`,
            }}
          >
            <h4>Pedido #{o.id}</h4>

            <p>
              <strong>Cliente:</strong> {o.cliente || "—"} <br />
              <strong>Total:</strong> ${o.total || 0} <br />
              <strong>Estado:</strong> {o.status} <br />
              <strong>Tiempo restante:</strong> {formatTimer(left)}
            </p>

            <ul>
              {(o.items || []).map((i, idx) => (
                <li key={idx}>
                  {i.qty} × {i.product_name} — ${i.subtotal}
                </li>
              ))}
            </ul>

            <div style={{ marginTop: 10 }}>
              <button onClick={() => setOrderStatus(o.id, "IN_PROGRESS")} style={btn("#f1c40f")}>
                🧑‍🍳 Preparando
              </button>
              <button onClick={() => setOrderStatus(o.id, "READY")} style={btn("#3498db")}>
                ✅ Listo
              </button>
              <button onClick={() => setOrderStatus(o.id, "DELIVERED")} style={btn("#7f8c8d")}>
                🚚 Entregado
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}

const btn = (bg) => ({
  marginRight: "8px",
  background: bg,
  border: "none",
  padding: "6px 12px",
  borderRadius: "6px",
  fontWeight: "bold",
  cursor: "pointer",
});
