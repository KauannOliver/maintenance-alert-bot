from telegram import Update
from telegram.ext import ContextTypes
from src.services.formatter import Formatter
from src.db.sqlite_store import SQLiteStore
from src.config import Config
import logging

logger = logging.getLogger(__name__)

class CommandHandlers:
    def __init__(self, store: SQLiteStore):
        self.store = store

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /start command."""
        user_id = str(update.effective_user.id)
        if user_id not in Config.TELEGRAM_ALLOWED_USERS:
            await update.message.reply_text("Usuário não autorizado para este bot.")
            return

        msg = """👋 <b>Olá! Eu sou o OMSentinel.</b>

Sou um assistente especializado em detectar anomalias em Ordens de Manutenção (OMs).

<b>Comandos disponíveis:</b>
/status - Ver estado atual do monitoramento
/help - Explicar as regras de detecção
/ultimas - Ver os últimos alertas enviados
/pause - Pausar o envio de alertas
/resume - Retomar o envio de alertas
/testalert - Enviar um alerta de teste (sintético)
"""
        await update.message.reply_html(msg)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /help command."""
        user_id = str(update.effective_user.id)
        if user_id not in Config.TELEGRAM_ALLOWED_USERS:
            return

        msg = """📖 <b>Regras de Detecção do OMSentinel</b>

<b>1. Conclusão em até 120s</b>
Detecta OMs que foram criadas e concluídas em um intervalo de até 2 minutos. Isso pode indicar registros puramente administrativos ou inconsistências no processo real.

<b>2. Criação da OM 2h+ após início da parada</b>
Detecta casos onde o veículo entrou em parada (manutenção) mas a OM só foi aberta mais de 2 horas depois. Isso pode indicar atraso no registro do processo.

<b>Dúvidas?</b>
Entre em contato com o administrador do sistema.
"""
        await update.message.reply_html(msg)

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /status command."""
        user_id = str(update.effective_user.id)
        if user_id not in Config.TELEGRAM_ALLOWED_USERS:
            return

        status_data = {
            'running': True, # In a job queue, it's always running if responsive
            'paused': self.store.is_paused(),
            'interval': Config.POLL_INTERVAL_SECONDS,
            'last_poll': self.store.get_last_successful_poll_at(),
            'total_alerts': self.store.count_sent_alerts()
        }
        
        await update.message.reply_html(Formatter.format_status(status_data))

    async def ultimas(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /ultimas command."""
        user_id = str(update.effective_user.id)
        if user_id not in Config.TELEGRAM_ALLOWED_USERS:
            return

        recent = self.store.get_recent_alerts(limit=10)
        await update.message.reply_html(Formatter.format_recent_list(recent))

    async def pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /pause command."""
        user_id = str(update.effective_user.id)
        if user_id not in Config.TELEGRAM_ALLOWED_USERS:
            return

        self.store.set_paused(True)
        await update.message.reply_text("⏸ Monitoramento de alertas pausado.")

    async def resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /resume command."""
        user_id = str(update.effective_user.id)
        if user_id not in Config.TELEGRAM_ALLOWED_USERS:
            return

        self.store.set_paused(False)
        await update.message.reply_text("▶️ Monitoramento de alertas retomado.")

    async def testalert(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /testalert command."""
        user_id = str(update.effective_user.id)
        if user_id not in Config.TELEGRAM_ALLOWED_USERS:
            return

        # Synthetic finding for testing
        test_finding = {
            "cod_om": "999999",
            "rules_triggered": ["fast_closure_120s"],
            "rule_labels": ["Conclusão em até 120s"],
            "metrics": {"closure_seconds": 45},
            "context": {
                "placa": "TEST-123",
                "familia": "TESTE",
                "operacao": "OP_TESTE",
                "filial": "FILIAL_TESTE",
                "status": "Teste",
                "responsavel": "Agente AI",
                "servico": "Manutenção Preventiva de Teste"
            },
            "timestamps": {
                "inicio_parada": "24/03/2026 08:00",
                "criacao_om": "24/03/2026 09:00",
                "conclusao_om": "24/03/2026 09:00"
            }
        }
        
        await update.message.reply_html(Formatter.format_alert(test_finding))
