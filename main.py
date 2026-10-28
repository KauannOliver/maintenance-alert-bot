import logging
import sys
from src.config import Config
from src.main_app import OMSentinelApp

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO)
)
logger = logging.getLogger(__name__)

def main():
    try:
        # 1. Validate configuration
        logger.info("Verificando configurações...")
        Config.validate()
        
        # 2. Start App
        logger.info("Iniciando aplicação...")
        app = OMSentinelApp()
        app.run()

    except ValueError as config_err:
        logger.error(f"Config Error: {config_err}")
        print(f"\n❌ ERRO DE CONFIGURAÇÃO: {config_err}")
        print("Certifique-se de que o arquivo .env existe e contém as chaves obrigatórias.")
        print("Veja .env.example para referência.\n")
        sys.exit(1)
        
    except Exception as e:
        logger.critical(f"FATAL ERROR: {e}")
        print(f"\n🚨 ERRO FATAL: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
