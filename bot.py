import os
import logging
import asyncpg
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

# ================= CONFIGURACIÓN =================
TOKEN = os.getenv('TELEGRAM_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
WHATSAPP_NUMERO = os.getenv('WHATSAPP_NUMERO', '+59387757446')
ADMIN_IDS = os.getenv('ADMIN_IDS', '').split(',')
UBICACION = "📍 Martínez-Sucre, Ecuador"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================= FUNCIÓN DE NOTIFICACIONES =================
async def notificar_admins(context, mensaje):
    """Enviar notificación a TODOS los administradores"""
    for admin_id in ADMIN_IDS:
        if admin_id.strip():
            try:
                await context.bot.send_message(
                    chat_id=int(admin_id.strip()),
                    text=mensaje,
                    parse_mode='Markdown'
                )
                logger.info(f"✅ Notificación enviada a admin {admin_id}")
            except Exception as e:
                logger.error(f"❌ Error notificando a {admin_id}: {e}")

# ================= BASE DE DATOS =================
async def get_db_connection():
    """Conectar a Supabase"""
    return await asyncpg.connect(DATABASE_URL)

# ================= COMANDOS PRINCIPALES =================
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("💅 Agendar cita", callback_data='agendar')],
        [InlineKeyboardButton("❌ Cancelar cita", callback_data='cancelar')],
        [InlineKeyboardButton("📱 Contactar por WhatsApp", callback_data='whatsapp')],
        [InlineKeyboardButton("📍 Ver ubicación", callback_data='ubicacion')],
        [InlineKeyboardButton("💎 Nuestros servicios", callback_data='servicios')],
        [InlineKeyboardButton("📋 Mis citas agendadas", callback_data='ver_citas')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✨ *Hola {user.first_name}!* ✨\n\n"
        f"Bienvenida al *Veronica Guerra Studio* 💅\n\n"
        f"{UBICACION}\n"
        f"📞 *WhatsApp:* {WHATSAPP_NUMERO}\n\n"
        f"*¿Qué te gustaría hacer hoy?*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ================= SERVICIOS =================
async def servicios(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    servicios_text = (
        "💎 *NUESTROS SERVICIOS:*\n\n"
        "• *Manicure Tradicional*\n"
        "• *Uñas Esculpidas*\n"
        "• *Kapping Gel*\n"
        "• *Esmaltado Semipermanente*\n"
        "• *Pedicure Spa*\n"
        "• *Diseños Especiales*\n"
        "• *Retiro de Acrílico*\n\n"
        "💅 *También realizamos:*\n"
        "• Decoraciones personalizadas\n"
        "• Cristales y strass\n"
        "• French y reverso\n"
        "• Diseños a pedido\n\n"
        "📅 *Agenda tu cita ahora mismo!*"
    )
    
    await query.edit_message_text(
        servicios_text,
        parse_mode='Markdown'
    )

# ================= UBICACIÓN =================
async def ubicacion(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    ubicacion_text = (
        f"{UBICACION}\n\n"
        "📍 *Dirección:*\n"
        "Martínez-Sucre, Ecuador\n\n"
        "🚗 *Cómo llegar:*\n"
        "• Zona residencial\n"
        "• Estacionamiento disponible\n"
        "• Fácil acceso\n\n"
        "⏰ *Horarios:*\n"
        "Lunes a Viernes: 9:00 - 19:00\n"
        "Sábados: 9:00 - 17:00\n"
        "Domingos: Con cita previa\n\n"
        "¡Te esperamos! 💕"
    )
    
    await query.edit_message_text(
        ubicacion_text,
        parse_mode='Markdown'
    )

# ================= AGENDAR CITAS =================
async def agendar_cita_start(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "💅 *AGENDAR CITA - PASO 1/4*\n\n"
        "Por favor, escribe tu *nombre completo*:\n"
        "(Ej: María González)",
        parse_mode='Markdown'
    )
    context.user_data['agendando'] = True
    context.user_data['paso'] = 'nombre'

async def procesar_nombre(update: Update, context: CallbackContext):
    nombre = update.message.text
    if len(nombre) < 3:
        await update.message.reply_text("❌ El nombre debe tener al menos 3 caracteres. Escribe tu nombre:")
        return
    
    context.user_data['nombre'] = nombre
    
    await update.message.reply_text(
        f"✅ *Nombre registrado:* {nombre}\n\n"
        f"💅 *PASO 2/4*\n"
        f"Escribe tu *número de teléfono*:\n"
        f"(Ej: 0987654321)",
        parse_mode='Markdown'
    )
    context.user_data['paso'] = 'telefono'

async def procesar_telefono(update: Update, context: CallbackContext):
    telefono = update.message.text
    context.user_data['telefono'] = telefono
    
    await update.message.reply_text(
        f"✅ *Teléfono:* {telefono}\n\n"
        f"💅 *PASO 3/4*\n"
        f"Selecciona el *servicio* que deseas:\n\n"
        f"1. 💅 Manicure Tradicional\n"
        f"2. ✨ Uñas Esculpidas\n"
        f"3. 🌟 Kapping Gel\n"
        f"4. 💎 Semipermante\n"
        f"5. 🦶 Pedicure Spa\n"
        f"6. 🎨 Diseño Especial\n"
        f"7. 🔄 Retiro de Acrílico\n\n"
        f"*Escribe solo el número:*",
        parse_mode='Markdown'
    )
    context.user_data['paso'] = 'servicio'

async def procesar_servicio(update: Update, context: CallbackContext):
    opcion = update.message.text
    servicios = {
        '1': 'Manicure Tradicional',
        '2': 'Uñas Esculpidas',
        '3': 'Kapping Gel',
        '4': 'Semipermante',
        '5': 'Pedicure Spa',
        '6': 'Diseño Especial',
        '7': 'Retiro de Acrílico'
    }
    
    if opcion not in servicios:
        await update.message.reply_text("❌ Opción inválida. Escribe solo el número (1-7):")
        return
    
    servicio = servicios[opcion]
    context.user_data['servicio'] = servicio
    
    await update.message.reply_text(
        f"✅ *Servicio:* {servicio}\n\n"
        f"💅 *PASO 4/4*\n"
        f"Escribe la *fecha* de tu cita:\n"
        f"*Formato:* DD/MM/AAAA\n"
        f"*Ejemplo:* 25/12/2023",
        parse_mode='Markdown'
    )
    context.user_data['paso'] = 'fecha'

async def procesar_fecha(update: Update, context: CallbackContext):
    fecha = update.message.text
    try:
        datetime.strptime(fecha, '%d/%m/%Y')
    except ValueError:
        await update.message.reply_text("❌ Formato incorrecto. Usa DD/MM/AAAA:")
        return
    
    context.user_data['fecha'] = fecha
    
    await update.message.reply_text(
        f"✅ *Fecha:* {fecha}\n\n"
        f"💅 *PASO 5/5*\n"
        f"Escribe la *hora* de tu cita:\n"
        f"*Formato:* HH:MM (24 horas)\n"
        f"*Ejemplo:* 14:30",
        parse_mode='Markdown'
    )
    context.user_data['paso'] = 'hora'

async def procesar_hora(update: Update, context: CallbackContext):
    hora = update.message.text
    try:
        datetime.strptime(hora, '%H:%M')
    except ValueError:
        await update.message.reply_text("❌ Formato incorrecto. Usa HH:MM (ej: 14:30):")
        return
    
    user_id = update.effective_user.id
    nombre = context.user_data.get('nombre', '')
    telefono = context.user_data.get('telefono', '')
    servicio = context.user_data.get('servicio', '')
    fecha = context.user_data.get('fecha', '')
    
    try:
        conn = await get_db_connection()
        await conn.execute('''
            INSERT INTO citas (user_id, cliente_nombre, telefono, servicio, fecha, hora, estado)
            VALUES ($1, $2, $3, $4, $5, $6, 'activa')
        ''', user_id, nombre, telefono, servicio, fecha, hora)
        await conn.close()
        
        # Confirmación al cliente
        await update.message.reply_text(
            f"🎉 *¡CITA CONFIRMADA!* 🎉\n\n"
            f"✨ *Resumen de tu cita:*\n\n"
            f"👤 *Nombre:* {nombre}\n"
            f"📞 *Teléfono:* {telefono}\n"
            f"💅 *Servicio:* {servicio}\n"
            f"📅 *Fecha:* {fecha}\n"
            f"⏰ *Hora:* {hora}\n"
            f"📍 *Ubicación:* {UBICACION}\n\n"
            f"✅ *Tu cita ha sido registrada exitosamente.*\n"
            f"📱 *WhatsApp:* {WHATSAPP_NUMERO}\n\n"
            f"*Importante:*\n"
            f"• Llega 5 minutos antes\n"
            f"• Trae tu mascarilla\n"
            f"• Cancelación con 24h de anticipación\n\n"
            f"¡Te esperamos! 💕",
            parse_mode='Markdown'
        )
        
        # 🔔 NOTIFICAR A AMBOS ADMINISTRADORES
        notificacion = (
            f"📥 *NUEVA CITA AGENDADA*\n\n"
            f"👤 *Cliente:* {nombre}\n"
            f"📞 *Teléfono:* {telefono}\n"
            f"💅 *Servicio:* {servicio}\n"
            f"📅 *Fecha:* {fecha}\n"
            f"⏰ *Hora:* {hora}\n"
            f"🆔 *User ID:* {user_id}\n"
            f"🕐 *Hora registro:* {datetime.now().strftime('%H:%M')}\n\n"
            f"📍 *Ubicación:* {UBICACION}"
        )
        await notificar_admins(context, notificacion)
        
    except Exception as e:
        logger.error(f"Error al guardar cita: {e}")
        await update.message.reply_text(
            "❌ *Ocurrió un error al guardar tu cita.*\n"
            "Por favor, intenta nuevamente o contáctanos por WhatsApp."
        )
    
    # Limpiar datos temporales
    context.user_data.clear()

# ================= VER CITAS =================
async def ver_citas(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    try:
        conn = await get_db_connection()
        citas = await conn.fetch('''
            SELECT id, cliente_nombre, servicio, fecha, hora, estado
            FROM citas 
            WHERE user_id = $1 AND estado = 'activa'
            ORDER BY fecha, hora
        ''', user_id)
        await conn.close()
        
        if citas:
            texto = "📋 *TUS CITAS ACTIVAS:*\n\n"
            for cita in citas:
                texto += f"🆔 *ID:* {cita['id']}\n"
                texto += f"👤 *Cliente:* {cita['cliente_nombre']}\n"
                texto += f"💅 *Servicio:* {cita['servicio']}\n"
                texto += f"📅 *Fecha:* {cita['fecha']}\n"
                texto += f"⏰ *Hora:* {cita['hora']}\n"
                texto += "────────────\n"
            
            texto += "\n*Para cancelar una cita:*\n"
            texto += "1. Selecciona '❌ Cancelar cita'\n"
            texto += "2. Escribe el *ID* de la cita\n\n"
            texto += f"📞 *Dudas:* {WHATSAPP_NUMERO}"
        else:
            texto = (
                "📭 *No tienes citas agendadas.*\n\n"
                "¿Te gustaría agendar una cita ahora? 💅\n\n"
                f"📍 *Ubicación:* {UBICACION}\n"
                f"📞 *WhatsApp:* {WHATSAPP_NUMERO}"
            )
        
        await query.edit_message_text(texto, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error al obtener citas: {e}")
        await query.edit_message_text(
            "❌ *Error al obtener tus citas.*\n"
            "Intenta más tarde o contáctanos por WhatsApp."
        )

# ================= CANCELAR CITAS =================
async def cancelar_cita_start(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    try:
        conn = await get_db_connection()
        citas = await conn.fetch('''
            SELECT id, cliente_nombre, servicio, fecha, hora
            FROM citas 
            WHERE user_id = $1 AND estado = 'activa'
            ORDER BY fecha, hora
        ''', user_id)
        await conn.close()
        
        if citas:
            texto = "❌ *CANCELAR CITA*\n\n"
            texto += "*Tus citas activas:*\n\n"
            
            for cita in citas:
                texto += f"🆔 *ID:* {cita['id']}\n"
                texto += f"👤 {cita['cliente_nombre']}\n"
                texto += f"💅 {cita['servicio']}\n"
                texto += f"📅 {cita['fecha']} - ⏰ {cita['hora']}\n"
                texto += "──────\n"
            
            texto += "\n✍️ *Escribe el ID de la cita que deseas cancelar:*\n\n"
            texto += f"📍 *Ubicación:* {UBICACION}"
            
            await query.edit_message_text(texto, parse_mode='Markdown')
            context.user_data['cancelando'] = True
        else:
            await query.edit_message_text(
                "📭 *No tienes citas activas para cancelar.*\n\n"
                f"📍 *Ubicación:* {UBICACION}"
            )
            
    except Exception as e:
        logger.error(f"Error al obtener citas para cancelar: {e}")
        await query.edit_message_text("❌ *Error.* Intenta más tarde.")

async def procesar_cancelacion(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    cita_id = update.message.text.strip()
    
    try:
        cita_id_int = int(cita_id)
        
        conn = await get_db_connection()
        cita = await conn.fetchrow('''
            SELECT id, cliente_nombre, servicio, fecha, hora 
            FROM citas 
            WHERE id = $1 AND user_id = $2 AND estado = 'activa'
        ''', cita_id_int, user_id)
        
        if cita:
            await conn.execute('''
                UPDATE citas SET estado = 'cancelada' 
                WHERE id = $1 AND user_id = $2
            ''', cita_id_int, user_id)
            
            await conn.close()
            
            await update.message.reply_text(
                f"✅ *CITA CANCELADA EXITOSAMENTE*\n\n"
                f"*Detalles cancelados:*\n"
                f"🆔 *ID:* {cita_id}\n"
                f"👤 *Cliente:* {cita['cliente_nombre']}\n"
                f"💅 *Servicio:* {cita['servicio']}\n"
                f"📅 *Fecha:* {cita['fecha']}\n"
                f"⏰ *Hora:* {cita['hora']}\n\n"
                f"*Si deseas reagendar:*\n"
                f"Usa '💅 Agendar cita'\n\n"
                f"📞 *WhatsApp:* {WHATSAPP_NUMERO}\n"
                f"{UBICACION}",
                parse_mode='Markdown'
            )
            
            # 🔔 NOTIFICAR A AMBOS ADMINISTRADORES
            notificacion = (
                f"❌ *CITA CANCELADA*\n\n"
                f"🆔 *ID Cita:* {cita_id}\n"
                f"👤 *Cliente:* {cita['cliente_nombre']}\n"
                f"💅 *Servicio:* {cita['servicio']}\n"
                f"📅 *Fecha:* {cita['fecha']}\n"
                f"⏰ *Hora:* {cita['hora']}\n"
                f"🆔 *User ID:* {user_id}\n"
                f"🕐 *Hora cancelación:* {datetime.now().strftime('%H:%M')}\n\n"
                f"{UBICACION}"
            )
            await notificar_admins(context, notificacion)
        else:
            await update.message.reply_text(
                "❌ *No se encontró una cita activa con ese ID.*\n"
                "Verifica el ID y vuelve a intentar.\n\n"
                f"📍 *Ubicación:* {UBICACION}"
            )
            
    except ValueError:
        await update.message.reply_text(
            "❌ *ID inválido.* Escribe solo el número (ej: 1, 2, 3).\n\n"
            f"📍 *Ubicación:* {UBICACION}"
        )
    except Exception as e:
        logger.error(f"Error al cancelar cita: {e}")
        await update.message.reply_text(
            "❌ *Error al cancelar la cita.*\n"
            "Intenta más tarde o contáctanos por WhatsApp.\n\n"
            f"📍 *Ubicación:* {UBICACION}"
        )
    
    if 'cancelando' in context.user_data:
        del context.user_data['cancelando']

# ================= WHATSAPP =================
async def contactar_whatsapp(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    whatsapp_text = (
        f"📱 *CONTACTO DIRECTO POR WHATSAPP*\n\n"
        f"👉 *Número:* `+593 87757446`\n\n"
        f"📲 *Enlace directo:*\n"
        f"https://wa.me/59387757446\n\n"
        f"*Horario de atención:*\n"
        f"• Lunes a Viernes: 9:00 - 19:00\n"
        f"• Sábados: 9:00 - 17:00\n"
        f"• Domingos: Con cita previa\n\n"
        f"📍 *Ubicación:*\n"
        f"{UBICACION}\n\n"
        f"¡Estaremos encantadas de atenderte! 💕"
    )
    
    await query.edit_message_text(
        whatsapp_text,
        parse_mode='Markdown',
        disable_web_page_preview=False
    )

# ================= MANEJAR BOTONES =================
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    
    if data == 'agendar':
        await agendar_cita_start(update, context)
    elif data == 'cancelar':
        await cancelar_cita_start(update, context)
    elif data == 'whatsapp':
        await contactar_whatsapp(update, context)
    elif data == 'ubicacion':
        await ubicacion(update, context)
    elif data == 'servicios':
        await servicios(update, context)
    elif data == 'ver_citas':
        await ver_citas(update, context)

# ================= MANEJAR MENSAJES =================
async def manejar_mensajes(update: Update, context: CallbackContext):
    texto = update.message.text.lower()
    
    # Procesar agendamiento
    if context.user_data.get('agendando'):
        paso = context.user_data.get('paso', '')
        
        if paso == 'nombre':
            await procesar_nombre(update, context)
        elif paso == 'telefono':
            await procesar_telefono(update, context)
        elif paso == 'servicio':
            await procesar_servicio(update, context)
        elif paso == 'fecha':
            await procesar_fecha(update, context)
        elif paso == 'hora':
            await procesar_hora(update, context)
            del context.user_data['agendando']
            del context.user_data['paso']
        return
    
    # Procesar cancelación
    if context.user_data.get('cancelando'):
        await procesar_cancelacion(update, context)
        return
    
    # Respuestas automáticas
    if any(palabra in texto for palabra in ['hola', 'buenas', 'hi', 'hello']):
        await update.message.reply_text(
            f"¡Hola! 👋\n\n"
            f"Bienvenida al *Veronica Guerra Studio* 💅\n\n"
            f"📍 {UBICACION}\n"
            f"📞 WhatsApp: {WHATSAPP_NUMERO}\n\n"
            f"Escribe /start para ver todas las opciones.",
            parse_mode='Markdown'
        )
    elif any(palabra in texto for palabra in ['gracias', 'thank you', 'thanks']):
        await update.message.reply_text(
            "¡De nada! 💕\n"
            "Es un placer atenderte.\n\n"
            "¡Te esperamos en el estudio! ✨"
        )
    elif any(palabra in texto for palabra in ['adiós', 'chao', 'bye', 'hasta luego']):
        await update.message.reply_text(
            "¡Hasta luego! 💕\n"
            "Que tengas un lindo día.\n\n"
            f"📍 {UBICACION}"
        )
    else:
        await update.message.reply_text(
            "🤔 *No estoy segura de qué necesitas.*\n\n"
            "Usa /start para ver el menú principal o selecciona una opción:\n\n"
            f"📍 *Ubicación:* {UBICACION}\n"
            f"📞 *WhatsApp:* {WHATSAPP_NUMERO}",
            parse_mode='Markdown'
        )

# ================= COMANDOS DE ADMINISTRADOR =================
async def admin_citas(update: Update, context: CallbackContext):
    """Ver todas las citas (solo admin)"""
    user_id = str(update.effective_user.id)
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ No autorizado.")
        return
    
    try:
        conn = await get_db_connection()
        citas = await conn.fetch('''
            SELECT id, user_id, cliente_nombre, telefono, servicio, fecha, hora, estado
            FROM citas 
            ORDER BY fecha, hora
        ''')
        await conn.close()
        
        if citas:
            texto = "📊 *TODAS LAS CITAS REGISTRADAS:*\n\n"
            for cita in citas:
                estado_emoji = "✅" if cita['estado'] == 'activa' else "❌"
                texto += f"{estado_emoji} *ID:* {cita['id']}\n"
                texto += f"👤 *Cliente:* {cita['cliente_nombre']}\n"
                texto += f"📞 *Teléfono:* {cita['telefono']}\n"
                texto += f"💅 *Servicio:* {cita['servicio']}\n"
                texto += f"📅 *Fecha:* {cita['fecha']}\n"
                texto += f"⏰ *Hora:* {cita['hora']}\n"
                texto += f"🆔 *User ID:* `{cita['user_id']}`\n"
                texto += f"📊 *Estado:* {cita['estado']}\n"
                texto += "────────────\n"
            
            texto += f"\n📈 *Total:* {len(citas)} citas\n"
            activas = sum(1 for c in citas if c['estado'] == 'activa')
            texto += f"✅ *Activas:* {activas}\n"
            texto += f"❌ *Canceladas:* {len(citas) - activas}"
        else:
            texto = "📭 *No hay citas registradas.*"
        
        await update.message.reply_text(texto, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error admin_citas: {e}")
        await update.message.reply_text("❌ Error al obtener citas.")

async def admin_estadisticas(update: Update, context: CallbackContext):
    """Estadísticas (solo admin)"""
    user_id = str(update.effective_user.id)
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ No autorizado.")
        return
    
    try:
        conn = await get_db_connection()
        
        total = await conn.fetchval('SELECT COUNT(*) FROM citas')
        activas = await conn.fetchval('SELECT COUNT(*) FROM citas WHERE estado = $1', 'activa')
        canceladas = await conn.fetchval('SELECT COUNT(*) FROM citas WHERE estado = $1', 'cancelada')
        hoy = await conn.fetchval('''
            SELECT COUNT(*) FROM citas 
            WHERE creado_en::date = CURRENT_DATE
        ''')
        
        await conn.close()
        
        texto = (
            "📊 *ESTADÍSTICAS DEL ESTUDIO*\n\n"
            f"📈 *Total citas:* {total}\n"
            f"✅ *Citas activas:* {activas}\n"
            f"❌ *Citas canceladas:* {canceladas}\n"
            f"📅 *Citas hoy:* {hoy}\n\n"
            f"📍 *Ubicación:* {UBICACION}\n"
            f"📞 *WhatsApp:* {WHATSAPP_NUMERO}"
        )
        
        await update.message.reply_text(texto, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error admin_estadisticas: {e}")
        await update.message.reply_text("❌ Error al obtener estadísticas.")

# ================= INICIALIZAR BOT =================
def main():
    if not TOKEN:
        logger.error("❌ Faltan credenciales")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin_citas", admin_citas))
    app.add_handler(CommandHandler("admin_estadisticas", admin_estadisticas))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensajes))
    
    logger.info("🤖 Veronica Guerra Studio Bot iniciado...")
    app.run_polling()

if __name__ == '__main__':
    main()
