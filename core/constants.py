"""Constantes de negocio: listas para formularios y nombres de tablas en MySQL."""

# Tipos de servicio logístico (selectores en formularios)
TIPOS_SERVICIO = [
    "Fletes Nacionales",
    "Fletes Internacionales",
    "Almacenaje",
    "Distribucion Local",
    "Gestion Aduanera",
    "Transporte Refrigerado",
    "Logistica de Ultima Milla",
    "Consolidacion de Carga",
    "Seguros de Mercancia",
    "Servicios Express",
]

ESTADOS = ["Completado", "Pendiente", "Cancelado"]

METODOS_PAGO = ["Transferencia", "Efectivo", "Tarjeta", "Credito", "Deposito"]

# Columnas mínimas para importar CSV al dashboard
CSV_REQUIRED_COLUMNS = ["monto_total", "estado", "tipo_servicio"]

DB_TABLE_TRANSACTIONS = "transacciones_logistik"
DB_TABLE_USERS = "usuarios"
