from celery import shared_task
from django.utils import timezone
from pedidos.models import Order, DailyReport
from django.core.mail import EmailMessage
import csv
from pathlib import Path

@shared_task
def generate_daily_report():
    today = timezone.localdate()
    orders = Order.objects.filter(created_at__date=today)

    total_orders = orders.count()
    total_revenue = sum(o.total_price for o in orders)

    report, created = DailyReport.objects.get_or_create(
        date=today,
        defaults={"total_orders": total_orders, "total_revenue": total_revenue},
    )

    # Crear CSV
    reports_dir = Path("media/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    filename = reports_dir / f"reporte_{today}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID Pedido", "Cliente", "Total", "Método", "Fecha"])
        for o in orders:
            writer.writerow([o.id, str(o.customer), o.total_price, o.payment_method, o.created_at])
        writer.writerow([])
        writer.writerow(["TOTAL PEDIDOS", total_orders])
        writer.writerow(["TOTAL VENTAS", total_revenue])

    # Enviar email
    subject = f"📊 Reporte Diario - {today}"
    body = (
        f"Hola 👋\n\n"
        f"Aquí tienes el reporte del día {today}:\n"
        f"🧾 Total de pedidos: {total_orders}\n"
        f"💰 Total de ingresos: ${total_revenue}\n\n"
        f"Se adjunta el CSV con el detalle completo.\n\n"
        f"Saludos,\nTu sistema Cevichería 🍣🦞"
    )

    email = EmailMessage(
        subject,
        body,
        to=["correo_destinatario@tudominio.com"],  # <-- cambia este correo
    )
    email.attach_file(filename)
    email.send(fail_silently=False)

    print(f"📊 Reporte generado y enviado: {filename}")
    return str(filename)
