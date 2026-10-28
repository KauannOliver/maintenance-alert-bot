from datetime import datetime
import hashlib
import json

class RuleEngine:
    @staticmethod
    def classify_row(row):
        """
        Processes a raw SQL row and returns a finding if any rule is triggered.
        """
        rules_triggered = []
        rule_labels = []
        metrics = {}

        # Rule A - Extremely Fast Closure
        criacao_dt = row.get('CRIACAO_OM_DT')
        conclusao_dt = row.get('CONCLUSAO_OM_DT')
        
        if criacao_dt and conclusao_dt:
            closure_seconds = (conclusao_dt - criacao_dt).total_seconds()
            if 0 <= closure_seconds <= 120:
                rules_triggered.append("fast_closure_120s")
                rule_labels.append("Conclusão em até 120s")
                metrics["closure_seconds"] = int(closure_seconds)

        # Rule B - Late creation after stop
        inicio_parada_dt = row.get('INICIO_PARADA_DT')
        if inicio_parada_dt and criacao_dt:
            late_seconds = (criacao_dt - inicio_parada_dt).total_seconds()
            if late_seconds >= 7200:
                rules_triggered.append("late_creation_after_stop_2h")
                rule_labels.append("Criação da OM 2h+ após início da parada")
                metrics["late_creation_seconds"] = int(late_seconds)

        if not rules_triggered:
            return None

        # Filter out pending orders older than 5 days
        status = row.get("STATUS", "")
        if status and "pendente" in status.lower():
            if criacao_dt:
                age_days = (datetime.now() - criacao_dt).total_seconds() / 86400.0
                if age_days > 5:
                    return None

        # Build normalized finding
        finding = {
            "cod_om": str(row.get("COD_OM")),
            "rules_triggered": rules_triggered,
            "rule_labels": rule_labels,
            "metrics": metrics,
            "context": {
                "placa": row.get("PLACA"),
                "familia": row.get("FAMILIA"),
                "operacao": row.get("NOME_OPERACAO"),
                "filial": row.get("NOME_FILIAL"),
                "status": row.get("STATUS"),
                "responsavel": row.get("RESPONSAVEL"),
                "servico": row.get("DESC_SERVICO")
            },
            "timestamps": {
                "inicio_parada": row.get("INICIO_PARADA"),
                "criacao_om": row.get("CRIACAO_OM"),
                "conclusao_om": row.get("CONCLUSAO_OM")
            }
        }
        
        # Add fingerprint
        finding["fingerprint"] = RuleEngine.generate_fingerprint(finding)
        
        return finding

    @staticmethod
    def generate_fingerprint(finding):
        """
        sha256(f"{COD_OM}|{rule_list}|{CRIACAO_OM}")
        """
        rules_str = "|".join(sorted(finding["rules_triggered"]))
        base = f"{finding['cod_om']}|{rules_str}|{finding['timestamps']['criacao_om']}"
        return hashlib.sha256(base.encode()).hexdigest()
