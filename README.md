# 🏓 Hand Pong - AI Powered Game

Um jogo de Pong clássico reimaginado, onde você controla as raquetes usando os movimentos das suas mãos através da webcam. Utiliza Visão Computacional de última geração para uma experiência fluida e interativa.

---

## ✨ Funcionalidades

- **Controle por Gestos**: Utilize a posição vertical das suas mãos para mover as raquetes em tempo real.
- **Threading de IA**: Processamento assíncrono do MediaPipe, garantindo que o jogo rode a 60 FPS constantes enquanto a IA trabalha em segundo plano.
- **Sistema de Calibração**: Ajuste a área de movimento das mãos para o seu conforto pessoal através de uma calibração rápida de 5 segundos.
- **Efeitos Visuais Dinâmicos**: Partículas, trepidação de tela (screen shake) e efeitos de "fogo/raio" conforme a intensidade do jogo aumenta.
- **Interface Moderna**: UI estilo holográfico com placar neon e indicadores de status dos jogadores.

---

## 🚀 Tecnologias Utilizadas

- **Python 3.9+**
- **Pygame**: Engine para renderização e lógica de jogo.
- **OpenCV**: Captura e processamento de frames da câmera.
- **MediaPipe (Google)**: Landmarker de mãos para rastreamento de alta precisão.
- **NumPy**: Processamento de matrizes de imagem.

---

## 📦 Instalação e Execução

### 1. Pré-requisitos
Certifique-se de ter o Python instalado. Recomenda-se o uso de um ambiente virtual.

### 2. Clonar o Repositório
```bash
git clone https://github.com/gleissondouglas/pong-hand-control.git
cd pong-hand-control
```

### 3. Configurar Ambiente
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Mac/Linux)
source venv/bin/activate

# Ativar (Windows)
# venv\Scripts\activate
```

### 4. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 5. Rodar o Jogo
```bash
python main.py
```

---

## 🎮 Como Jogar

1. Ao iniciar, você estará no **Menu Principal**.
2. Pressione **'C'** para iniciar a **Calibração**:
   - Mova as mãos para cima e para baixo para definir sua área de conforto.
3. Pressione **ESPAÇO** para começar a partida.
4. O objetivo é marcar **5 pontos** para vencer.
5. Pressione **'Q'** a qualquer momento para sair.

---

## 🛠️ Estrutura do Projeto

- `main.py`: Ponto de entrada e gerenciador do estado do jogo.
- `src/`: Módulos do sistema (Câmera, IA, Física, UI).
- `assets/`: Sons, modelos de IA e recursos gráficos.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
Desenvolvido com ❤️ por [Douglas Oliveira](https://github.com/gleissondouglas)
