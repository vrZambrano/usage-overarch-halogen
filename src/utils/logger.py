import logging
import sys
from datetime import datetime
from typing import Optional

# Formato padrão para logs
LOG_FORMAT = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'

# Níveis de log
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def setup_logger(
    name: str = "bitcoin_app",
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configura e retorna um logger com formatação estruturada
    
    Args:
        name: Nome do logger
        level: Nível de log
        log_file: Caminho para arquivo de log (opcional)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evita duplicação de handlers em caso de múltiplas chamadas
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Formato do log
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Handler para stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo (se especificado)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Logger centralizado para a aplicação
app_logger = setup_logger("bitcoin_app")

def log_operation(operation: str, status: str, details: dict = None):
    """
    Função auxiliar para logar operações com estrutura
    
    Args:
        operation: Nome da operação
        status: Status da operação (success, error, warning)
        details: Dados adicionais para o log
    """
    log_data = {
        'operation': operation,
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'details': details or {}
    }
    
    if status == 'success':
        app_logger.info(f"OPERATION: {log_data}")
    elif status == 'error':
        app_logger.error(f"OPERATION: {log_data}")
    elif status == 'warning':
        app_logger.warning(f"OPERATION: {log_data}")
    else:
        app_logger.debug(f"OPERATION: {log_data}")