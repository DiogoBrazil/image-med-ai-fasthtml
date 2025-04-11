from ..utils.logger import get_logger

logger = get_logger(__name__)

def load_file_to_dictionary(file_path):
    """
    Carrega um arquivo de texto contendo resultados de predição para um dicionário.
    Cada linha do arquivo deve ter o formato: "valor doença".
    
    Args:
        file_path: Caminho para o arquivo de resultados
        
    Returns:
        dict: Dicionário com doença como chave e valor normalizado (0-100) como valor
    """
    try:
        result_dict = {}

        with open(file_path, 'r') as file:
            for line in file:
                try:
                    line = line.strip()
                    if not line:
                        continue
                        
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        value, disease = parts
                        result_dict[disease] = float(value) * 100
                except ValueError as e:
                    logger.warning(f"Erro ao processar linha '{line}' do arquivo {file_path}: {str(e)}")
                    continue
                
        logger.info(f"Arquivo {file_path} carregado com sucesso: {len(result_dict)} entradas")
        return result_dict
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo {file_path}: {str(e)}")
        return {}