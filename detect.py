import cv2
import numpy as np

def nothing(x):
    pass

# Abrindo o vídeo
cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Gravacao do video
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('resultado.avi', fourcc, 30.0, (640, 480))
# /Gravacao do video

# Inicializando sliders com valores padrão
lower_bound = [0, 0, 180]
upper_bound = [255, 255, 255]

anteriorBrancos = 0
placas = 0

def check_position(mask, l1, l2, l3, l4):
    recorte = mask[l2:l2 + l4, l1: l1 + l3]
    brancos = cv2.countNonZero(recorte)
    return brancos != 0, brancos

def draw_inclined_line(frame, start_point, length, angle, color, thickness, point_number):
    angle_rad = np.radians(angle)
    end_point = (
        int(start_point[0] + length * np.cos(angle_rad)),
        int(start_point[1] - length * np.sin(angle_rad))
    )
    #cv2.line(frame, start_point, end_point, color, thickness)
    #cv2.putText(frame, f'{point_number}', start_point, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)
    #cv2.putText(frame, f'{point_number+1}', end_point, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)
    return end_point


while True:
    ret, frame = cap.read()
    

    if not ret:
        cap.release()
        cap = cv2.VideoCapture(2)
        continue

    height, width = frame.shape[:2]
    
    # Coordenadas da região de interesse (ROI)
    linha_y = int(height * 0.2)
    linha_y2 = int(height * 0.48)
    coluna_x = int(width // 7)
    
    end_point1 = draw_inclined_line(frame, (0, 200), width - 50, 15, (0, 0, 255), 2, 1)  # Linha superior
    end_point2 = draw_inclined_line(frame, (0, 295), width - 50 , 17, (0, 0, 255), 2, 3)  # Linha inferior
    end_point3 = draw_inclined_line(frame, (0, 100), height, -60, (0, 255, 0), 2, 5)  # Linha vertical

    # Desenha linha vertical
    """start_point = (width // 2, 0)
    end_point = (width // 2, height)
    color = (0, 255, 0)  # Verde
    thickness = 2
    cv2.line(frame, start_point, end_point, color, thickness)"""
    # // Desenha linha vertical

    # Define os pontos da ROI inclinada
    roi_points = np.array([[0, 200], [end_point1[0], end_point1[1]], [end_point2[0], end_point2[1]], [0, 295]], dtype=np.int32)

    # Cria uma máscara para a ROI inclinada
    mask = np.zeros_like(frame)
    cv2.fillPoly(mask, [roi_points], (255, 255, 255))

    # Aplica a máscara ao frame para obter a ROI inclinada
    roi = cv2.bitwise_and(frame, mask)
    cv2.imshow('roi', roi)
    
    # Define a região de interesse
    #roi = frame[linha_y:linha_y2, coluna_x:width]
    
    # Converte a ROI para o espaço de cor HSV
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Criando uma máscara usando a faixa de cores especificada
    mascara = cv2.inRange(hsv, np.array(lower_bound), np.array(upper_bound))
    cv2.imshow('mascara', mascara)


    # Encontra os contornos na máscara
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Processando os contornos detectados
    count = 0
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        #print(area)
        if 500< area < 6000:  # Filtro para evitar contornos muito pequenos
            x, y, w, h = cv2.boundingRect(contorno)
            # Desenha o retângulo no frame, ajustando para as coordenadas da ROI
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            count += 1 
            
    # Quadrado para detectar se chegou na posicao
    l1, l2, l3, l4 = 100, 10, 20, 200
    liberado, brancos = check_position(mascara, l1,l2,l3,l4)
    # /Quadrado para detectar se chegou na posicao

    if anteriorBrancos == 0 and brancos != 0:
        cv2.imwrite('salva.png',frame)
        placas += count
        cv2.putText(frame, f'Quantidade: {placas}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    anteriorBrancos = brancos

    cv2.putText(frame, f'Quantidade: {placas}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    out.write(frame)
    cv2.imshow('frame', frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()