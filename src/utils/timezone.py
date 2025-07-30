from datetime import datetime
import pytz

def convert_to_brasilia_timezone(utc_dt: datetime) -> datetime:
    """
    Converte um datetime em UTC para o fuso horário de Brasília.
    
    Args:
        utc_dt: datetime em UTC
        
    Returns:
        datetime convertido para o fuso horário de Brasília
    """
    if utc_dt is None:
        return None
        
    # Se o datetime não tem timezone info, assume que é UTC
    if utc_dt.tzinfo is None:
        utc_dt = pytz.UTC.localize(utc_dt)
    
    # Converte para o fuso horário de Brasília
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    return utc_dt.astimezone(brasilia_tz)