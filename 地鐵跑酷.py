"""
地鐵跑酷 (Subway Surfers 風格的無盡跑酷)

安裝:  pip install pygame
執行:  python 地鐵跑酷.py

操作:
  ← → (或 A D)        換跑道
  ↑ (或 W / 空白鍵)   跳起來, 跳過矮柵欄
  ↓ (或 S)            滑行, 鑽過上面的橫桿 (在空中按會快速落地)
  空白鍵 / Enter      開始 / 重新開始
  ESC                 離開

障礙物:
  火車       -> 一定要換跑道閃開 (撞到車頭就結束)
  矮柵欄     -> 跳過去
  高橫桿     -> 滑行鑽過去
"""
import math
import random
import sys
from array import array

import pygame

# ======================== 基本設定 ========================
W, H = 480, 720
FPS = 60

# 世界座標: x=左右, y=高度, z=往前 (玩家固定站在 z=0, 世界往後退)
LANE_W = 1.6                    # 一條跑道的寬度
TRACK_HALF = LANE_W * 1.5       # 整片鐵軌的半寬
CAM_H = 4.2                     # 鏡頭高度
CAM_BACK = 6.0                  # 鏡頭在玩家後面多遠
FOCAL = 500                     # 焦距 (越大畫面越"近")
HORIZON = int(H * 0.30)         # 地平線在螢幕上的 y 座標
NEAR_Z = 1.0 - CAM_BACK         # 比這更近的東西不畫 (已經貼到鏡頭了)
FAR = 80.0                      # 看得到的最遠距離, 再遠就是霧

# 玩家與障礙物的數值
LANE_SPEED = 10.0               # 換跑道的速度 (每秒幾條跑道)
GRAVITY = 34.0
JUMP_V = 12.5
ROLL_TIME = 0.65                # 滑行持續時間
STAND_H, ROLL_H = 1.9, 0.8      # 站著 / 滑行時的身高
LOW_H = 0.9                     # 矮柵欄高度
HIGH_BOTTOM, HIGH_TOP = 1.15, 2.5   # 高橫桿的下緣 / 上緣
START_SPEED, MAX_SPEED, ACCEL = 14.0, 34.0, 0.25

# 顏色
SKY_TOP = (64, 128, 214)
FOG_COLOR = (255, 222, 178)     # 地平線的顏色, 遠處的東西會漸漸變成這個顏色
ROAD = (112, 112, 120)
WALK = (176, 168, 158)
BED = (132, 116, 100)
SLEEPER = (88, 66, 50)
RAIL = (190, 190, 200)
SHADOW = (96, 84, 72)
GOLD, GOLD_DARK = (255, 213, 74), (214, 150, 20)
HOODIE, PANTS, CAP, BAG, SKIN = (236, 92, 70), (52, 70, 120), (60, 140, 230), (250, 200, 60), (240, 190, 150)
TRAIN_COLORS = [(46, 110, 190), (200, 64, 56), (52, 150, 92), (226, 170, 40)]
BUILD_COLORS = [(176, 120, 96), (150, 150, 165), (200, 180, 150), (120, 140, 170), (170, 100, 90), (130, 120, 140)]

# 路邊大樓: 事先用固定種子產生 64 棟, 繞圈圈重複使用
SLOT = 9.0
_rng = random.Random(7)
BUILDINGS = [[(_rng.uniform(4, 7), _rng.uniform(6, 20), _rng.choice(BUILD_COLORS)) for _ in range(64)]
             for _ in range(2)]


# ======================== 3D 小工具 ========================
def project(x, y, z):
    """把 3D 世界座標變成螢幕座標. 越遠 (d 越大) 縮得越小, 都往中間的地平線靠過去."""
    d = max(z + CAM_BACK, 0.6)
    k = FOCAL / d
    return (W / 2 + x * k, HORIZON + (CAM_H - y) * k)


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(color, k):
    return tuple(min(255, int(c * k)) for c in color)


def fog(color, z):
    """離越遠, 顏色越接近地平線的顏色"""
    t = min(max(z / FAR, 0.0), 1.0) ** 1.5
    return lerp_color(color, FOG_COLOR, t)


GROUND_Z = [0.6 - CAM_BACK, 0, 6, 12, 20, 30, 42, 55, 70, 90, 140, 4000]


def ground_strip(s, x0, x1, color):
    """畫一條貼在地上的長條 (切成很多段, 每段有各自的霧色)"""
    for za, zb in zip(GROUND_Z, GROUND_Z[1:]):
        pts = [project(x0, 0, za), project(x1, 0, za), project(x1, 0, zb), project(x0, 0, zb)]
        pygame.draw.polygon(s, fog(color, (za + zb) / 2), pts)


def side_face(s, xs, y0, y1, z0, z1, color):
    """畫一個站在 x=xs 的垂直牆面 (箱子的側面)"""
    z0 = max(z0, NEAR_Z)
    z = z0
    while z < z1:
        zb = min(z + 6.0, z1)
        pts = [project(xs, y0, z), project(xs, y0, zb + 0.1), project(xs, y1, zb + 0.1), project(xs, y1, z)]
        pygame.draw.polygon(s, fog(color, z), pts)
        z = zb


def top_face(s, x0, x1, y, z0, z1, color):
    """畫一個水平的頂面"""
    z0 = max(z0, NEAR_Z)
    z = z0
    while z < z1:
        zb = min(z + 6.0, z1)
        pts = [project(x0, y, z), project(x1, y, z), project(x1, y, zb + 0.1), project(x0, y, zb + 0.1)]
        pygame.draw.polygon(s, fog(color, z), pts)
        z = zb


def front_face(s, x0, x1, y0, y1, z, color):
    """畫面對鏡頭的那一面"""
    pts = [project(x0, y0, z), project(x1, y0, z), project(x1, y1, z), project(x0, y1, z)]
    pygame.draw.polygon(s, fog(color, z), pts)


def draw_box(s, x0, x1, y0, y1, z0, z1, color):
    """畫一個立體箱子: 頂面 + 看得到的那個側面 + 正面"""
    clipped = z0 < NEAR_Z
    if z1 <= max(z0, NEAR_Z):
        return
    if CAM_H > y1:
        top_face(s, x0, x1, y1, z0, z1, shade(color, 1.25))
    if x1 < 0:
        side_face(s, x1, y0, y1, z0, z1, shade(color, 0.7))
    elif x0 > 0:
        side_face(s, x0, y0, y1, z0, z1, shade(color, 0.7))
    if not clipped:
        front_face(s, x0, x1, y0, y1, z0, color)


def stripe_face(s, x0, x1, y0, y1, z, c1, c2, n=6):
    """正面畫上一條一條的警示色"""
    w = (x1 - x0) / n
    for i in range(n):
        xa = x0 + i * w
        pts = [project(xa, y0, z), project(xa + w, y0, z), project(xa + w, y1, z), project(xa, y1, z)]
        pygame.draw.polygon(s, fog(c1 if i % 2 == 0 else c2, z), pts)


# ======================== 字型與音效 ========================
CJK_FONTS = ['microsoftjhenghei', 'microsoftyahei', 'pingfangtc', 'heititc', 'notosanscjktc',
             'notosanscjksc', 'notosanscjk', 'wenquanyizenhei', 'wenquanyimicrohei',
             'droidsansfallback', 'simhei', 'arialunicodems']


def load_fonts():
    """找得到中文字型就用中文介面, 找不到就退回英文 (避免出現一堆方塊)"""
    path = pygame.font.match_font(CJK_FONTS)
    fonts = {name: pygame.font.Font(path, size) for name, size in
             (('xl', 66), ('l', 40), ('m', 26), ('s', 19))}
    return fonts, path is not None


def make_sound(fn, seconds):
    """用數學公式合成音效, 不需要任何音檔. fn(t) 回傳 -1 ~ 1 的波形"""
    rate, _, channels = pygame.mixer.get_init()
    samples = array('h')
    for i in range(int(rate * seconds)):
        v = int(max(-1.0, min(1.0, fn(i / rate))) * 32767 * 0.35)
        samples.extend([v] * channels)
    return pygame.mixer.Sound(buffer=samples.tobytes())


def load_sounds():
    try:
        pygame.mixer.init()
        if pygame.mixer.get_init()[1] != -16:
            return {}
        tau = 2 * math.pi
        return {
            'coin': make_sound(lambda t: math.sin(tau * (988 if t < 0.06 else 1319) * t) * math.exp(-t * 14), 0.25),
            'jump': make_sound(lambda t: math.sin(tau * (300 + 900 * t) * t) * (1 - t / 0.18), 0.18),
            'bump': make_sound(lambda t: math.sin(tau * 140 * t) * math.exp(-t * 25), 0.15),
            'crash': make_sound(lambda t: (random.uniform(-1, 1) * 0.7 + math.sin(tau * 90 * t) * 0.6) * math.exp(-t * 7), 0.6),
        }
    except pygame.error:
        return {}


# ======================== 遊戲物件 ========================
class Obstacle:
    """kind: 'train' 火車 / 'low' 矮柵欄 / 'high' 高橫桿"""

    def __init__(self, kind, lane, wz, length=0.8):
        self.kind = kind
        self.lane = lane            # -1 左, 0 中, 1 右
        self.wz = wz                # 在世界裡的絕對位置 (前緣)
        self.length = length
        self.color = random.choice(TRAIN_COLORS) if kind == 'train' else None


class Coin:
    def __init__(self, lane, wz, y):
        self.lane = lane
        self.wz = wz
        self.y = y


class Game:
    def __init__(self):
        self.fonts, self.has_cjk = load_fonts()
        self.sounds = load_sounds()
        self.canvas = pygame.Surface((W, H))
        self.sky = pygame.Surface((W, HORIZON + 1))
        for y in range(HORIZON + 1):
            pygame.draw.line(self.sky, lerp_color(SKY_TOP, FOG_COLOR, y / HORIZON), (0, y), (W, y))
        self.dim = pygame.Surface((W, H), pygame.SRCALPHA)
        self.best = 0
        self.t = 0.0                # 動畫用的時間
        self.reset()
        self.state = 'title'        # title 標題 / play 遊玩中 / over 結束

    # ---------- 文字 ----------
    def txt(self, zh, en):
        return zh if self.has_cjk else en

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    # ---------- 遊戲狀態 ----------
    def reset(self):
        self.dist = 0.0             # 跑了多遠
        self.speed = START_SPEED
        self.coins_got = 0
        self.lane = 0               # 目標跑道
        self.px = 0.0               # 畫面上實際的位置 (會滑順地追向目標跑道)
        self.y = 0.0
        self.vy = 0.0
        self.roll_t = 0.0
        self.fast_fall = False
        self.obstacles = []
        self.coins = []
        self.safe = 0               # 目前這一排一定過得去的跑道
        self.next_row_z = 45.0      # 下一排障礙物要放的位置
        self.shake = 0.0
        self.flash = 0.0
        self.over_t = 0.0

    def start(self):
        self.reset()
        self.state = 'play'

    @property
    def score(self):
        return int(self.dist) + self.coins_got * 10

    @property
    def rolling(self):
        return self.roll_t > 0 and self.y <= 0

    @property
    def height(self):
        return ROLL_H if self.rolling else STAND_H

    # ---------- 操作 ----------
    def handle_key(self, key):
        if self.state == 'play':
            if key in (pygame.K_LEFT, pygame.K_a):
                self.move(-1)
            elif key in (pygame.K_RIGHT, pygame.K_d):
                self.move(1)
            elif key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                self.jump()
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.roll()
        elif key in (pygame.K_SPACE, pygame.K_RETURN):
            if self.state == 'title' or self.over_t > 0.6:      # 避免狂按時手滑直接重來
                self.start()

    def move(self, d):
        new = self.lane + d
        if not -1 <= new <= 1:
            return
        if self.lane_blocked(new):
            self.px += d * 0.25     # 撞到火車側面: 彈回來, 不會死
            self.shake = 0.15
            self.play('bump')
            return
        self.lane = new

    def lane_blocked(self, lane):
        """換過去會不會直接擦撞到火車?"""
        for ob in self.obstacles:
            if ob.kind == 'train' and ob.lane == lane:
                z0 = ob.wz - self.dist
                if z0 < 0.4 + self.speed * 0.08 and z0 + ob.length > -0.4:
                    return True
        return False

    def jump(self):
        if self.y <= 0:
            self.vy = JUMP_V
            self.y = 0.001
            self.roll_t = 0
            self.play('jump')

    def roll(self):
        if self.y > 0:
            self.vy = -22.0         # 在空中按下: 快速落地, 落地後直接滑行
            self.fast_fall = True
        else:
            self.roll_t = ROLL_TIME

    # ---------- 產生障礙物 ----------
    def spawn_row(self):
        z = self.next_row_z
        self.safe = max(-1, min(1, self.safe + random.choice((-1, 0, 0, 1))))
        hard = min(self.dist / 4000, 1.0)           # 難度 0 -> 1, 跑越遠火車越多
        row_len = 0.8
        safe_kind = None
        for lane in (-1, 0, 1):
            r = random.random()
            kind = None
            if lane == self.safe:                   # 安全跑道: 沒有火車, 偶爾有柵欄
                if r < 0.3:
                    kind = random.choice(('low', 'high'))
                safe_kind = kind
            elif r < 0.30 + 0.2 * hard:
                kind = 'train'
            elif r < 0.50 + 0.2 * hard:
                kind = 'low'
            elif r < 0.65 + 0.2 * hard:
                kind = 'high'
            if kind == 'train':
                ob = Obstacle('train', lane, z, random.uniform(10, 22))
                row_len = max(row_len, ob.length)
                self.obstacles.append(ob)
            elif kind:
                self.obstacles.append(Obstacle(kind, lane, z))
        gap = 14 + self.speed * 0.65                # 越快, 兩排之間留越長
        # 安全跑道上排一串金幣, 遇到矮柵欄就排成拱形, 引導玩家跳起來吃
        zc = z - 2
        while zc < z + row_len + gap * 0.5:
            y = 0.8
            if safe_kind == 'low':
                u = (zc - (z + 0.4)) / 3.5
                if abs(u) < 1:
                    y = 0.8 + 1.9 * (1 - u * u)
            self.coins.append(Coin(self.safe, zc, y))
            zc += 2.5
        self.next_row_z = z + row_len + gap

    # ---------- 更新 ----------
    def update(self, dt):
        self.t += dt
        self.shake = max(0.0, self.shake - dt)
        self.flash = max(0.0, self.flash - dt)
        if self.state == 'title':
            self.dist += 10 * dt                    # 標題畫面: 背景慢慢往前跑
            return
        if self.state == 'over':
            self.over_t += dt
            return

        self.speed = min(MAX_SPEED, self.speed + ACCEL * dt)
        self.dist += self.speed * dt

        # 左右: 慢慢滑向目標跑道
        step = LANE_SPEED * dt
        if abs(self.lane - self.px) <= step:
            self.px = self.lane
        else:
            self.px += step if self.lane > self.px else -step

        # 上下: 重力
        if self.y > 0:
            self.vy -= GRAVITY * dt
            self.y += self.vy * dt
            if self.y <= 0:
                self.y, self.vy = 0.0, 0.0
                if self.fast_fall:
                    self.fast_fall = False
                    self.roll_t = ROLL_TIME
        self.roll_t = max(0.0, self.roll_t - dt)

        while self.next_row_z - self.dist < FAR:
            self.spawn_row()
        self.check_hits()
        self.obstacles = [o for o in self.obstacles if o.wz + o.length - self.dist > -4.5]
        self.coins = [c for c in self.coins if c.wz - self.dist > -4.5]

    def check_hits(self):
        for ob in self.obstacles:
            z0 = ob.wz - self.dist
            if z0 > 0.4 or z0 + ob.length < -0.4:           # 前後沒碰到
                continue
            if abs(self.px - ob.lane) > 0.62:               # 左右沒碰到
                continue
            if ob.kind == 'train':
                return self.crash()
            if ob.kind == 'low' and self.y < LOW_H - 0.1:
                return self.crash()
            if ob.kind == 'high' and not self.rolling:
                return self.crash()

        mid = self.y + self.height / 2
        for c in self.coins[:]:
            if abs(c.wz - self.dist) < 0.8 and abs(self.px - c.lane) < 0.5 and abs(c.y - mid) < 1.1:
                self.coins.remove(c)
                self.coins_got += 1
                self.play('coin')

    def crash(self):
        self.state = 'over'
        self.over_t = 0.0
        self.shake = 0.4
        self.flash = 0.35
        self.best = max(self.best, self.score)
        self.play('crash')

    # ======================== 畫面 ========================
    def draw(self, screen):
        self.draw_scene(self.canvas)
        screen.fill((0, 0, 0))
        ox = oy = 0
        if self.shake > 0:
            m = int(self.shake * 30)
            ox, oy = random.randint(-m, m), random.randint(-m, m)
        screen.blit(self.canvas, (ox, oy))
        if self.flash > 0:
            self.dim.fill((255, 40, 40, int(150 * self.flash / 0.35)))
            screen.blit(self.dim, (0, 0))
        if self.state == 'title':
            self.draw_title(screen)
        else:
            self.draw_hud(screen)
            if self.state == 'over':
                self.draw_over(screen)

    def draw_scene(self, s):
        s.blit(self.sky, (0, 0))
        s.fill(FOG_COLOR, (0, HORIZON + 1, W, H - HORIZON))

        # 地面: 馬路 -> 人行道 -> 鐵軌床
        ground_strip(s, -60, 60, ROAD)
        ground_strip(s, -TRACK_HALF - 1.4, TRACK_HALF + 1.4, WALK)
        ground_strip(s, -TRACK_HALF, TRACK_HALF, BED)

        # 枕木 (跟著跑的距離移動, 才會有往前衝的感覺)
        gap = 1.4
        z = -(self.dist % gap) - gap * 3
        while z < FAR:
            if z + 0.3 > NEAR_Z:
                top_face(s, -TRACK_HALF, TRACK_HALF, 0.0, max(z, NEAR_Z), z + 0.3, SLEEPER)
            z += gap
        # 鐵軌
        for lane in (-1, 0, 1):
            for off in (-0.45, 0.45):
                x = lane * LANE_W + off
                top_face(s, x - 0.04, x + 0.04, 0.03, NEAR_Z, FAR + 10, RAIL)

        self.draw_buildings(s)

        # 障礙物 / 金幣 / 玩家 一起排序: 遠的先畫, 近的蓋在上面
        items = [(o.wz - self.dist, 'ob', o) for o in self.obstacles if o.wz - self.dist < FAR]
        items += [(c.wz - self.dist, 'coin', c) for c in self.coins if c.wz - self.dist < FAR]
        items.append((0.0, 'player', None))
        items.sort(key=lambda it: -it[0])
        for _, kind, obj in items:
            if kind == 'coin':
                self.draw_coin(s, obj)
            elif kind == 'player':
                self.draw_player(s)
            elif obj.kind == 'train':
                self.draw_train(s, obj)
            elif obj.kind == 'low':
                self.draw_low(s, obj)
            else:
                self.draw_high(s, obj)

    def draw_buildings(self, s):
        base = int(self.dist // SLOT)
        for idx in range(base + int(FAR // SLOT) + 1, base - 2, -1):    # 由遠到近
            z0 = idx * SLOT - self.dist
            for side in (0, 1):
                w, h, color = BUILDINGS[side][idx % 64]
                if side == 0:
                    x0, x1, xs = -3.8 - w, -3.8, -3.8
                else:
                    x0, x1, xs = 3.8, 3.8 + w, 3.8
                draw_box(s, x0, x1, 0, h, z0, z0 + 7.0, color)
                if z0 > FAR * 0.75:
                    continue
                for j in range(int(h // 2.2)):              # 窗戶, 有些有開燈
                    for i in range(3):
                        lit = (idx * 5 + i * 3 + j * 7 + side) % 4 == 0
                        za = z0 + 0.6 + i * 2.1
                        side_face(s, xs, 1.0 + j * 2.2, 2.2 + j * 2.2, za, za + 1.2,
                                  (255, 232, 140) if lit else shade(color, 0.45))

    def draw_train(self, s, ob):
        z0 = ob.wz - self.dist
        z1 = z0 + ob.length
        x = ob.lane * LANE_W
        hw = 0.62
        draw_box(s, x - hw, x + hw, 0.3, 2.7, z0, z1, ob.color)
        # 側面的窗戶
        xs = x + hw if x < 0 else x - hw if x > 0 else None
        if xs is not None:
            zw = z0 + 1.0
            while zw + 2.0 < z1:
                side_face(s, xs, 1.5, 2.3, zw, zw + 2.0, (28, 38, 58))
                zw += 3.2
        if z0 < NEAR_Z:
            return
        # 車頭: 底盤, 白色橫條, 擋風玻璃, 車燈
        front_face(s, x - hw, x + hw, 0.3, 0.95, z0, (50, 50, 60))
        front_face(s, x - hw, x + hw, 1.0, 1.2, z0, (240, 240, 240))
        front_face(s, x - 0.5, x + 0.5, 1.45, 2.45, z0, (28, 38, 58))
        front_face(s, x - 0.5, x + 0.5, 2.05, 2.45, z0, (70, 95, 130))
        r = max(2, int(0.13 * FOCAL / (z0 + CAM_BACK)))
        for sx in (-0.42, 0.42):
            cx, cy = project(x + sx, 0.65, z0)
            pygame.draw.circle(s, fog((255, 240, 150), z0), (int(cx), int(cy)), r)

    def draw_low(self, s, ob):
        z0 = ob.wz - self.dist
        x = ob.lane * LANE_W
        draw_box(s, x - 0.7, x + 0.7, 0, LOW_H, z0, z0 + ob.length, (236, 236, 236))
        if z0 >= NEAR_Z:
            stripe_face(s, x - 0.7, x + 0.7, 0.4, LOW_H, z0, (240, 120, 30), (245, 245, 245))

    def draw_high(self, s, ob):
        z0 = ob.wz - self.dist
        x = ob.lane * LANE_W
        for sx in (-0.62, 0.62):
            draw_box(s, x + sx - 0.07, x + sx + 0.07, 0, HIGH_TOP, z0, z0 + ob.length, (90, 90, 100))
        draw_box(s, x - 0.7, x + 0.7, HIGH_BOTTOM, HIGH_TOP, z0, z0 + ob.length, (236, 236, 236))
        if z0 >= NEAR_Z:
            stripe_face(s, x - 0.7, x + 0.7, HIGH_BOTTOM, HIGH_TOP, z0, (210, 50, 50), (245, 245, 245))

    def draw_coin(self, s, c):
        z = c.wz - self.dist
        if z < -2.0:                            # 跑過去的金幣太靠近鏡頭, 不畫
            return
        x = c.lane * LANE_W
        cx, cy = project(x, c.y, z)
        r = 0.34 * FOCAL / (z + CAM_BACK)
        w = max(1.5, r * abs(math.cos(self.t * 5 + c.wz)))      # 左右寬度會變, 看起來像在旋轉
        gx, gy = project(x, 0, z)
        pygame.draw.ellipse(s, fog(SHADOW, z), (gx - r * 0.6, gy - r * 0.2, r * 1.2, r * 0.4))
        pygame.draw.ellipse(s, fog(GOLD_DARK, z), (cx - w, cy - r, w * 2, r * 2))
        pygame.draw.ellipse(s, fog(GOLD, z), (cx - w * 0.7, cy - r * 0.8, w * 1.4, r * 1.6))

    def draw_player(self, s):
        k = FOCAL / CAM_BACK                    # 玩家這個距離下, 1 個世界單位 = k 像素
        cx = W / 2 + self.px * LANE_W * k
        gy = HORIZON + CAM_H * k                # 地面 (腳下) 的 y
        foot = gy - self.y * k
        lean = (self.lane - self.px) * 0.25 * k     # 換跑道時身體往那邊傾斜

        sw = 0.9 * k * max(0.4, 1 - self.y / 4)     # 影子: 跳越高越小
        pygame.draw.ellipse(s, SHADOW, (cx - sw / 2, gy - 0.1 * k, sw, 0.24 * k))

        if self.state == 'over' or self.rolling:    # 滑行 (或撞倒): 縮成一團滾動
            cy = foot - 0.45 * k
            pygame.draw.circle(s, HOODIE, (cx, cy), 0.45 * k)
            ang = self.t * 20 if self.state == 'play' else 2.4
            pygame.draw.circle(s, BAG, (cx + math.cos(ang + 2) * 0.2 * k, cy + math.sin(ang + 2) * 0.2 * k), 0.17 * k)
            pygame.draw.circle(s, CAP, (cx + math.cos(ang) * 0.3 * k, cy + math.sin(ang) * 0.3 * k), 0.21 * k)
            if self.state == 'over':                # 頭上轉圈圈的星星
                for i in range(3):
                    a = self.t * 6 + i * 2.1
                    pygame.draw.circle(s, GOLD, (cx + math.cos(a) * 0.55 * k, cy - 0.7 * k + math.sin(a) * 0.12 * k), max(2, int(0.07 * k)))
            return

        air = self.y > 0.05
        phase = self.dist * 0.9
        hip = foot - 0.95 * k
        shoulder = hip - 0.7 * k
        lw = int(0.27 * k)

        for i, sgn in enumerate((-1, 1)):           # 腿
            swing = math.sin(phase + i * math.pi)
            if air:
                fx, fy = cx + sgn * 0.3 * k, hip + 0.5 * k
            else:
                fx, fy = cx + sgn * 0.17 * k, foot - max(0, swing) * 0.32 * k
            pygame.draw.line(s, PANTS, (cx + sgn * 0.17 * k, hip), (fx, fy), lw)
            pygame.draw.circle(s, (245, 245, 245), (fx, fy), 0.15 * k)

        for i, sgn in enumerate((-1, 1)):           # 手
            swing = -math.sin(phase + i * math.pi)
            if air:
                hx, hy = cx + sgn * 0.62 * k, shoulder - 0.05 * k
            else:
                hx, hy = cx + sgn * 0.5 * k, shoulder + 0.5 * k + swing * 0.25 * k
            pygame.draw.line(s, HOODIE, (cx + sgn * 0.38 * k, shoulder + 0.1 * k), (hx, hy), int(0.2 * k))
            pygame.draw.circle(s, SKIN, (hx, hy), 0.1 * k)

        body = pygame.Rect(0, 0, 0.76 * k, 0.8 * k)         # 身體 + 背包
        body.midtop = (cx + lean * 0.5, shoulder)
        pygame.draw.rect(s, HOODIE, body, border_radius=int(0.2 * k))
        bag = pygame.Rect(0, 0, 0.5 * k, 0.5 * k)
        bag.midtop = (cx + lean * 0.5, shoulder + 0.1 * k)
        pygame.draw.rect(s, BAG, bag, border_radius=int(0.1 * k))
        head = (cx + lean, shoulder - 0.25 * k)             # 頭 (背面, 看到的是帽子)
        pygame.draw.ellipse(s, SKIN, (head[0] - 0.1 * k, head[1] + 0.1 * k, 0.2 * k, 0.25 * k))
        pygame.draw.circle(s, CAP, head, 0.26 * k)
        pygame.draw.rect(s, shade(CAP, 1.3), (head[0] - 0.12 * k, head[1] + 0.12 * k, 0.24 * k, 0.07 * k))

    # ---------- 文字與介面 ----------
    def text(self, s, msg, font, color, pos, anchor='center'):
        shadow = self.fonts[font].render(msg, True, (30, 30, 50))
        img = self.fonts[font].render(msg, True, color)
        s.blit(shadow, shadow.get_rect(**{anchor: (pos[0] + 2, pos[1] + 3)}))
        s.blit(img, img.get_rect(**{anchor: pos}))

    def draw_hud(self, s):
        self.text(s, str(self.score), 'l', (255, 255, 255), (16, 10), 'topleft')
        self.text(s, self.txt('最高 ', 'BEST ') + str(max(self.best, self.score)), 's', (255, 240, 200), (18, 56), 'topleft')
        count = str(self.coins_got)
        self.text(s, count, 'm', GOLD, (W - 16, 14), 'topright')
        icon_x = W - 16 - self.fonts['m'].size(count)[0] - 20      # 金幣圖示貼在數字左邊
        pygame.draw.circle(s, GOLD_DARK, (icon_x, 29), 13)
        pygame.draw.circle(s, GOLD, (icon_x, 29), 9)

    def draw_title(self, s):
        self.dim.fill((0, 0, 30, 90))
        s.blit(self.dim, (0, 0))
        self.text(s, self.txt('地鐵跑酷', 'SUBWAY RUN'), 'xl', GOLD, (W / 2, 150))
        if int(self.t * 2) % 2 == 0:
            self.text(s, self.txt('按 空白鍵 開始', 'Press SPACE to start'), 'm', (255, 255, 255), (W / 2, 250))
        lines = [self.txt('← →  換跑道', 'LEFT / RIGHT : change lane'),
                 self.txt('↑  跳過矮柵欄', 'UP : jump over low fences'),
                 self.txt('↓  滑行鑽過橫桿', 'DOWN : slide under bars'),
                 self.txt('火車要閃開!', 'Dodge the trains!')]
        for i, line in enumerate(lines):
            self.text(s, line, 's', (255, 255, 255), (W / 2, 614 + i * 27))

    def draw_over(self, s):
        self.dim.fill((0, 0, 0, 140))
        s.blit(self.dim, (0, 0))
        self.text(s, self.txt('撞到了!', 'CRASHED!'), 'xl', (255, 110, 90), (W / 2, 190))
        self.text(s, self.txt('分數  ', 'SCORE  ') + str(self.score), 'l', (255, 255, 255), (W / 2, 300))
        self.text(s, self.txt('金幣  ', 'COINS  ') + str(self.coins_got), 'm', GOLD, (W / 2, 360))
        self.text(s, self.txt('最高分  ', 'BEST  ') + str(self.best), 'm', (255, 240, 200), (W / 2, 405))
        if self.over_t > 0.6 and int(self.t * 2) % 2 == 0:
            self.text(s, self.txt('按 空白鍵 再玩一次', 'Press SPACE to retry'), 'm', (255, 255, 255), (W / 2, 520))


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption('Subway Run 地鐵跑酷')
    clock = pygame.time.Clock()
    game = Game()
    while True:
        dt = min(clock.tick(FPS) / 1000, 0.05)      # 限制單次最長 0.05 秒, 視窗卡一下也不會瞬間衝過頭
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                game.handle_key(event.key)
        game.update(dt)
        game.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
