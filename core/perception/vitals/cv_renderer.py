import cv2

WHITE = (255, 255, 255)

def draw_pill_badge_aa(img, text, x, y, bg_color, text_color=(255, 255, 255)):
    tw = len(text) * 7 + 16
    r = 8
    cv2.rectangle(img, (x + r, y), (x + tw - r, y + 16), bg_color, -1, cv2.LINE_AA)
    cv2.circle(img, (x + r, y + 8), r, bg_color, -1, cv2.LINE_AA)
    cv2.circle(img, (x + tw - r, y + 8), r, bg_color, -1, cv2.LINE_AA)
    cv2.rectangle(img, (x + r, y), (x + tw - r, y + 16), WHITE, 1, cv2.LINE_AA)
    cv2.circle(img, (x + r, y + 8), r, WHITE, 1, cv2.LINE_AA)
    cv2.circle(img, (x + tw - r, y + 8), r, WHITE, 1, cv2.LINE_AA)
    cv2.putText(img, text, (x + 8, y + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.34, text_color, 1, cv2.LINE_AA)

def draw_corner_brackets_aa(img, x1, y1, x2, y2, color, length=12, thickness=2):
    cv2.line(img, (x1, y1), (x1 + length, y1), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x1, y1), (x1, y1 + length), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x2, y1), (x2 - length, y1), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x2, y1), (x2, y2 - length), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x1, y2), (x1 + length, y2), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x1, y2), (x1, y2 - length), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x2, y2), (x2 - length, y2), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x2, y2), (x2, y2 - length), color, thickness, cv2.LINE_AA)
