import html
import json
from datetime import datetime

class Formatter:
    @staticmethod
    def format_alert(finding):
        """
        Builds a Telegram-friendly HTML message for an alert finding.
        """
        cod_om = finding["cod_om"]
        context = finding["context"]
        timestamps = finding["timestamps"]
        rules = finding["rule_labels"]
        
        # Determine title
        if len(rules) > 1:
            title = "🚨 <b>OM com múltiplos indícios de problema</b>"
        else:
            title = "🚨 <b>OM com indício de problema</b>"

        # Escape context fields for HTML safety
        safe_context = {k: html.escape(str(v or '')) for k, v in context.items()}
        
        # Rule list
        rules_text = "\n".join([f"- {r}" for r in rules])
        
        # Formatting evidence
        evidence_lines = []
        evidence_lines.append(f"- Início da parada: {timestamps.get('inicio_parada') or 'N/I'}")
        evidence_lines.append(f"- Criação da OM: {timestamps['criacao_om']}")
        if timestamps.get("conclusao_om"):
            evidence_lines.append(f"- Conclusão da OM: {timestamps['conclusao_om']}")
            
        # Specific metrics
        metrics = finding.get("metrics", {})
        if "closure_seconds" in metrics:
            evidence_lines.append(f"- <b>Tempo de execução:</b> {metrics['closure_seconds']} segundos")
        if "late_creation_seconds" in metrics:
            late_h = metrics["late_creation_seconds"] // 3600
            late_m = (metrics["late_creation_seconds"] % 3600) // 60
            evidence_lines.append(f"- <b>Atraso na abertura:</b> {late_h}h{late_m:02d}")

        # Suggested actions
        if "fast_closure_120s" in finding["rules_triggered"] and "late_creation_after_stop_2h" in finding["rules_triggered"]:
            action = "Validar a cronologia completa da OM, pois há mais de um indício de inconsistência operacional."
        elif "fast_closure_120s" in finding["rules_triggered"]:
            action = "Validar se a abertura e conclusão quase imediatas refletem execução real ou apenas registro administrativo."
        else:
            action = "Realizar a abertura da OM Digital o mais breve da parada do equipamento para manutenção."

        evidence_text = "\n".join(evidence_lines)
        msg = f"""{title}

<b>OM:</b> <code>{cod_om}</code>
<b>Placa:</b> <code>{safe_context['placa']}</code>
<b>Família:</b> {safe_context['familia']}
<b>Operação:</b> {safe_context['operacao']}
<b>Filial:</b> {safe_context['filial']}
<b>Serviço:</b> {safe_context['servico']}
<b>Status:</b> {safe_context['status']}
<b>Responsável:</b> {safe_context['responsavel']}

<b>Regras acionadas:</b>
{rules_text}

<b>Evidências:</b>
{evidence_text}

<b>Ação sugerida:</b>
{action}"""
        return msg

    @staticmethod
    def format_status(status_data):
        """
        Formats /status command output.
        """
        active_str = "ativo" if status_data['running'] else "pausado"
        pause_str = "sim" if status_data['paused'] else "não"
        
        return f"""🤖 <b>Status do OMSentinel</b>

<b>Monitoramento:</b> {active_str}
<b>Intervalo:</b> {status_data['interval']} segundos
<b>Último polling com sucesso:</b> {status_data['last_poll'] or 'nunca'}
<b>Total de alertas enviados:</b> {status_data['total_alerts']}
<b>Modo pausa:</b> {pause_str}"""

    @staticmethod
    def format_recent_list(alerts_list):
        """
        Formats /ultimas command output.
        """
        if not alerts_list:
            return "🕘 <b>Lista de alertas vazia.</b>"
            
        lines = ["🕘 <b>Últimos alertas enviados</b>"]
        for row in alerts_list:
            # row: (cod_om, rules_json, sent_at)
            cod_om = row[0]
            rules = json.loads(row[1])
            # Parse iso format for cleaner display
            try:
                dt = datetime.fromisoformat(row[2])
                dt_str = dt.strftime("%d/%m %H:%M")
            except:
                dt_str = row[2]
                
            rule_summary = "Múltiplas regras" if len(rules) > 1 else rules[0].replace("_", " ")
            lines.append(f"- OM <code>{cod_om}</code> — {rule_summary} — {dt_str}")
            
        return "\n".join(lines)
