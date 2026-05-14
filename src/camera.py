import cv2
import threading
import time
from .config import WIDTH, HEIGHT

class Camera:
    def __init__(self, camera_index=0):
        # O diagnóstico confirmou que o índice 0 e 1 funcionam com AVFOUNDATION
        print(f"Inicializando câmera no índice {camera_index}...")
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_AVFOUNDATION)
        
        if not self.cap.isOpened():
            print("Tentando índice alternativo 1...")
            self.cap = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)

        if not self.cap.isOpened():
            print("Erro Crítico: Não foi possível abrir a câmera.")
            return

        # "Warm-up" mais agressivo: lê e descarta frames iniciais
        for i in range(10):
            success, frame = self.cap.read()
            if success and frame is not None:
                print(f"Câmera pronta e enviando frames (Warm-up {i+1}/10)")
            else:
                print("Aguardando sinal da câmera...")
            cv2.waitKey(50) 
        
    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None
        
        # Inverte o frame horizontalmente para efeito de espelho (melhor para jogos)
        frame = cv2.flip(frame, 1)
        return frame
    
    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

class CameraStream:
    """Gerencia a captura da câmera e o processamento de IA em uma thread separada."""
    def __init__(self, camera, tracker):
        self.camera = camera
        self.tracker = tracker
        self.frame = None
        self.hands = {"left": None, "right": None}
        self.stopped = False
        self.lock = threading.Lock()
        
    def start(self):
        t = threading.Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        while not self.stopped:
            frame = self.camera.get_frame()
            if frame is not None:
                # 1. Processa a IA no frame original (melhor precisão)
                frame, hands = self.tracker.find_hands(frame)
                
                # 2. OTIMIZAÇÃO: Prepara o frame para o Pygame aqui na thread de background
                # Redimensiona, converte para RGB e transpõe
                frame_resized = cv2.resize(frame, (WIDTH, HEIGHT))
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                frame_pygame_ready = cv2.transpose(frame_rgb)
                
                # Atualiza os dados de forma segura para a thread principal
                with self.lock:
                    self.frame = frame_pygame_ready
                    self.hands = hands
            
            # Pequena pausa para não sobrecarregar a CPU
            time.sleep(0.001)

    def read(self):
        with self.lock:
            return self.frame, self.hands

    def stop(self):
        self.stopped = True

if __name__ == "__main__":
    # Teste rápido do módulo (pode falhar se rodado fora do contexto do pacote src)
    try:
        from config import WIDTH, HEIGHT
    except ImportError:
        WIDTH, HEIGHT = 800, 600

    cam = Camera()
    print("Pressione 'q' ou 'ESC' para sair.")
    while True:
        frame = cam.get_frame()
        if frame is not None:
            cv2.imshow("Teste Webcam", frame)
            
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
    cam.release()
