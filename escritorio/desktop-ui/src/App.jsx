import { useEffect, useState, useRef } from "react";
import { sendNotification, requestPermission } from "@tauri-apps/plugin-notification";
import { writeTextFile, readTextFile, BaseDirectory } from "@tauri-apps/plugin-fs";


async function updateStatus(id, status, orders, setOrders, saveOrders) {
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/orders/${id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });

    if (!response.ok) throw new Error(`Error ${response.status}`);
    console.log(`✅ Pedido #${id} actualizado a ${status}`);

    // 🔄 Actualizar el estado local y guardar
    const updatedOrders = orders.map((order) =>
      order.id === id ? { ...order, status } : order
    );
    setOrders(updatedOrders);
    saveOrders(updatedOrders);

    return true;
  } catch (err) {
    console.error(`❌ No se pudo actualizar pedido #${id}:`, err);
    return false;
  }
}

function App() {
  const [connected, setConnected] = useState(false);
  const [orders, setOrders] = useState([]);
  const [reconnecting, setReconnecting] = useState(false);
  const wsRef = useRef(null);

  async function saveOrders(orders) {
    try {
      const data = JSON.stringify(orders, null, 2);
      await writeTextFile("pedidos.json", data, { baseDir: BaseDirectory.AppData });
      console.log("💾 Pedidos guardados localmente.");
    } catch (err) {
      console.error("❌ Error guardando pedidos:", err);
    }
  }

  // --- Cargar pedidos guardados al iniciar ---
  async function loadOrders() {
    try {
      const data = await readTextFile("pedidos.json", { baseDir: BaseDirectory.AppData });
      console.log("📂 Pedidos cargados desde archivo local.");
      return JSON.parse(data);
    } catch {
      console.warn("⚠️ No hay pedidos guardados aún.");
      return [];
    }
  }

  useEffect(() => {
    // Cargar historial previo
    loadOrders().then((data) => setOrders(data));

    // Pedir permiso de notificaciones
    requestPermission();

    let reconnectInterval = 2000;
    let reconnectTimer;

    const connectWebSocket = () => {
      if (wsRef.current) return;

      console.log("🔌 Intentando conectar WebSocket...");
      const ws = new WebSocket("ws://127.0.0.1:8000/ws/orders/");
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("✅ Conectado al WebSocket");
        setConnected(true);
        setReconnecting(false);
      };

      ws.onclose = () => {
        console.warn("⚠️ WebSocket desconectado");
        setConnected(false);
        setReconnecting(true);
        wsRef.current = null;
        reconnectTimer = setTimeout(connectWebSocket, reconnectInterval);
        reconnectInterval = Math.min(reconnectInterval * 1.5, 10000);
      };

      ws.onerror = (err) => {
        console.error("❌ Error WS:", err);
        ws.close();
      };

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.type === "new_order" && data.order) {
            const order = data.order;
            console.log("📦 Pedido recibido:", order);

            setOrders((prev) => {
              if (prev.find((o) => o.id === order.id)) return prev;
              const updated = [order, ...prev];
              saveOrders(updated); // 💾 Guardar cada vez que llegue uno nuevo
              return updated;
            });

            sendNotification({
              title: "🦞 Nuevo Pedido",
              body: order.cliente
                ? `Pedido #${order.id} de ${order.cliente}`
                : `Nuevo pedido #${order.id}`,
            });

            const sound = new Audio("/notification.mp3");
            sound.volume = 0.3;
            sound.play().catch(() => {});
          }
        } catch (err) {
          console.error("Error procesando mensaje WS:", err);
        }
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      clearTimeout(reconnectTimer);
    };
  }, []);

  // --- Determinar color de borde según estado ---
  const getStatusColor = (status) => {
    switch (status) {
      case "NEW":
        return "#2ecc71"; // verde
      case "IN_PROGRESS":
        return "#f1c40f"; // amarillo
      case "READY":
        return "#3498db"; // azul
      case "DELIVERED":
        return "#95a5a6"; // gris
      default:
        return "#2ecc71";
    }
  };

  return (
    <div
      style={{
        padding: "40px",
        color: "#f1f1f1",
        backgroundColor: "#1e1e1e",
        fontFamily: "Poppins, sans-serif",
        minHeight: "100vh",
      }}
    >
      <h1>🦞 SOS Cevichería & Sushi</h1>
      <p>
        Estado:{" "}
        <span
          style={{
            color: connected ? "lightgreen" : reconnecting ? "orange" : "red",
            fontWeight: "bold",
          }}
        >
          {connected
            ? "Conectado 🟢"
            : reconnecting
            ? "Reconectando... 🟠"
            : "Desconectado 🔴"}
        </span>
      </p>

      <h3>📦 Pedidos recientes</h3>

      {orders.length === 0 ? (
        <p>Sin pedidos aún...</p>
      ) : (
        orders.map((order) => (
          <div
            key={order.id}
            style={{
              background: "#2c2c2c",
              padding: "15px",
              marginBottom: "12px",
              borderRadius: "10px",
              borderLeft: `5px solid ${getStatusColor(order.status || order.estado)}`,
            }}
          >
            <h4>Pedido #{order.id}</h4>
            <p>
              <strong>Cliente:</strong> {order.cliente || "Desconocido"} <br />
              <strong>Teléfono:</strong> {order.telefono || "—"} <br />
              <strong>Dirección:</strong> {order.direccion || "—"} <br />
              <strong>Pago:</strong> {order.pago || "—"} <br />
              <strong>Total:</strong> ${order.total?.toFixed(0) || 0} <br />
              <strong>Estado:</strong>{" "}
              <span style={{ color: getStatusColor(order.status || order.estado) }}>
                {order.status || order.estado || "Desconocido"}
              </span>{" "}
              <br />
              <small>{order.creado || "Fecha desconocida"}</small>
            </p>

            {order.items?.length > 0 ? (
              <ul style={{ listStyle: "none", padding: 0 }}>
                {order.items.map((item, idx) => (
                  <li key={idx}>
                    🐟 {item.cantidad} × {item.producto} — $
                    {item.subtotal?.toFixed(0) || 0}
                  </li>
                ))}
              </ul>
            ) : (
              <p style={{ fontSize: "0.9rem", color: "#aaa" }}>
                (Sin productos registrados)
              </p>
            )}

            {/* --- Botones de control de estado --- */}
            <div style={{ marginTop: "10px" }}>
              <button
                onClick={() =>
                  updateStatus(order.id, "IN_PROGRESS", orders, setOrders, saveOrders)
                }
                style={{
                  marginRight: "10px",
                  background: "#f1c40f",
                  color: "#000",
                  border: "none",
                  padding: "5px 10px",
                  borderRadius: "6px",
                  fontWeight: "bold",
                }}
              >
                🧑‍🍳 En preparación
              </button>
              <button
                onClick={() =>
                  updateStatus(order.id, "READY", orders, setOrders, saveOrders)
                }
                style={{
                  marginRight: "10px",
                  background: "#3498db",
                  color: "#fff",
                  border: "none",
                  padding: "5px 10px",
                  borderRadius: "6px",
                  fontWeight: "bold",
                }}
              >
                ✅ Listo
              </button>
              <button
                onClick={() =>
                  updateStatus(order.id, "DELIVERED", orders, setOrders, saveOrders)
                }
                style={{
                  background: "#95a5a6",
                  color: "#fff",
                  border: "none",
                  padding: "5px 10px",
                  borderRadius: "6px",
                  fontWeight: "bold",
                }}
              >
                🚚 Entregado
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default App;
