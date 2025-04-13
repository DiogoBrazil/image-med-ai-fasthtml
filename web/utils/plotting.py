# web/utils/plotting.py
import matplotlib
matplotlib.use('Agg') # Usa backend não interativo, essencial para servidor web
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, List

def generate_probability_chart(probabilities: Dict[str, float], title: str = "Prediction Probabilities") -> str:
    """
    Gera um gráfico de barras horizontais a partir de um dicionário de probabilidades
    e retorna a imagem como uma string base64 PNG.
    """
    if not probabilities:
        return ""

    labels = list(probabilities.keys())
    values = list(probabilities.values())

    # Cores (opcional, pode definir um conjunto de cores)
    colors = plt.cm.viridis_r([v / 100. for v in values]) # Exemplo de cores baseadas no valor

    # Criar a figura e os eixos
    fig, ax = plt.subplots(figsize=(7, max(3, len(labels) * 0.6))) # Ajusta altura com base no nº de labels

    # Criar barras horizontais
    bars = ax.barh(labels, values, color=colors, height=0.6)

    # Adicionar rótulos de porcentagem nas barras
    ax.bar_label(bars, fmt='%.1f%%', padding=3, fontsize=9, color='dimgray')

    # Configurações do gráfico
    ax.set_xlabel("Probability (%)", fontsize=10)
    ax.set_title(title, fontsize=12, pad=15)
    ax.set_xlim(0, 105) # Limite um pouco maior que 100% para espaço
    ax.tick_params(axis='y', labelsize=10) # Tamanho da fonte dos labels Y
    ax.tick_params(axis='x', labelsize=9)
    ax.spines['top'].set_visible(False) # Remove bordas superior/direita
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#dddddd') # Cor mais suave para borda esquerda
    ax.spines['bottom'].set_color('#dddddd') # Cor mais suave para borda inferior

    # Inverte a ordem dos labels (opcional, para mais importantes em cima)
    # ax.invert_yaxis()

    plt.tight_layout() # Ajusta layout para evitar sobreposição

    # Salva o gráfico em um buffer de memória
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=90) # Salva como PNG
    buf.seek(0)

    # Codifica para base64
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig) # Fecha a figura para liberar memória

    return image_base64


def generate_confidence_histogram(detections: List[Dict], title: str = "Detection Confidence Distribution") -> str:
    """
    Gera um histograma das confianças de detecção.
    Espera uma lista de dicionários, cada um com 'confidence'.
    Retorna imagem base64 PNG.
    """
    if not detections:
        return ""

    confidences = [d.get('confidence', 0) * 100 for d in detections] # Confianças em %
    if not confidences: return ""

    fig, ax = plt.subplots(figsize=(7, 4)) # Tamanho fixo para histograma

    # Define os bins (faixas) para o histograma, por exemplo, de 70% a 100%
    bins = [70, 75, 80, 85, 90, 95, 100] # Ajuste os bins conforme necessário

    # Cria o histograma
    n, bins, patches = ax.hist(confidences, bins=bins, color='skyblue', edgecolor='black', rwidth=0.85)

    # Adiciona contagem acima das barras (opcional)
    for count, patch in zip(n, patches):
        if count > 0:
            height = patch.get_height()
            ax.text(patch.get_x() + patch.get_width() / 2., height + 0.1,
                    f'{int(count)}', ha='center', va='bottom', fontsize=9)

    ax.set_xlabel("Confidence Score (%)", fontsize=10)
    ax.set_ylabel("Number of Detections", fontsize=10)
    ax.set_title(title, fontsize=12, pad=15)
    # ax.set_xticks(bins) # Define ticks nos limites dos bins
    ax.tick_params(axis='both', labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Ajusta o limite Y para dar espaço às contagens
    if n.any(): # Verifica se n não está vazio ou só com zeros
      ax.set_ylim(0, n.max() * 1.15 if n.max() > 0 else 1)


    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=90)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return image_base64