#!/usr/bin/env python3
"""
俄罗斯方块游戏 - Windows版本（不使用pygame）
作者: AI Assistant
基于终端的俄罗斯方块游戏
"""

import os
import sys
import time
import random
import msvcrt  # Windows特有的模块

# 游戏配置
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
GAME_SPEED = 0.5  # 方块下落速度（秒）

# 方块形状定义（坐标相对于中心点）
SHAPES = {
    'I': [
        [(-1, 0), (0, 0), (1, 0), (2, 0)],  # 水平
        [(0, -1), (0, 0), (0, 1), (0, 2)],  # 垂直
    ],
    'O': [
        [(0, 0), (1, 0), (0, 1), (1, 1)]  # 只有旋转
    ],
    'T': [
        [(-1, 0), (0, 0), (1, 0), (0, -1)],  # T形
        [(0, -1), (0, 0), (0, 1), (-1, 0)],
        [(-1, 0), (0, 0), (1, 0), (0, 1)],
        [(0, -1), (0, 0), (0, 1), (1, 0)],
    ],
    'S': [
        [(-1, 0), (0, 0), (0, 1), (1, 1)],  # S形
        [(0, -1), (0, 0), (1, 0), (1, 1)],
    ],
    'Z': [
        [(-1, 1), (0, 1), (0, 0), (1, 0)],  # Z形
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'J': [
        [(-1, 0), (-1, 1), (0, 1), (1, 1)],  # J形
        [(-1, -1), (-1, 0), (-1, 1), (0, 1)],
        [(-1, 0), (0, 0), (1, 0), (1, 1)],
        [(1, -1), (1, 0), (1, 1), (0, 1)],
    ],
    'L': [
        [(1, 0), (1, 1), (-1, 1), (0, 1)],  # L形
        [(-1, -1), (-1, 0), (-1, 1), (0, -1)],
        [(-1, 0), (0, 0), (1, 0), (-1, 1)],
        [(1, -1), (1, 0), (1, 1), (0, -1)],
    ],
}

class TetrisBlock:
    """方块类"""
    def __init__(self, board_width, board_height):
        self.board_width = board_width
        self.board_height = board_height
        self.shape_type = random.choice(list(SHAPES.keys()))
        self.rotation = 0
        self.x = board_width // 2
        self.y = 0
        
    def get_blocks(self):
        """获取当前方块的坐标列表"""
        blocks = []
        shape_data = SHAPES[self.shape_type][self.rotation]
        for dx, dy in shape_data:
            blocks.append((self.x + dx, self.y + dy))
        return blocks
    
    def can_move(self, dx, dy, board):
        """检查是否可以移动"""
        for x, y in self.get_blocks():
            new_x = x + dx
            new_y = y + dy
            if new_x < 0 or new_x >= self.board_width:
                return False
            if new_y < 0 or new_y >= self.board_height:
                return False
            if board[new_y][new_x] != 0:
                return False
        return True
    
    def move(self, dx, dy):
        """移动方块"""
        self.x += dx
        self.y += dy
    
    def can_rotate(self, board):
        """检查是否可以旋转"""
        new_rotation = (self.rotation + 1) % len(SHAPES[self.shape_type])
        shape_data = SHAPES[self.shape_type][new_rotation]
        for dx, dy in shape_data:
            new_x = self.x + dx
            new_y = self.y + dy
            if new_x < 0 or new_x >= self.board_width:
                return False
            if new_y < 0 or new_y >= self.board_height:
                return False
            if board[new_y][new_x] != 0:
                return False
        return True
    
    def rotate(self):
        """旋转方块"""
        self.rotation = (self.rotation + 1) % len(SHAPES[self.shape_type])

class TetrisGame:
    """俄罗斯方块游戏主类"""
    def __init__(self):
        self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.current_block = None
        self.next_block = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.last_move = time.time()
        
        # 初始化第一个方块
        self.spawn_new_block()
    
    def spawn_new_block(self):
        """生成新方块"""
        if self.next_block is None:
            self.next_block = TetrisBlock(BOARD_WIDTH, BOARD_HEIGHT)
        
        self.current_block = self.next_block
        self.next_block = TetrisBlock(BOARD_WIDTH, BOARD_HEIGHT)
        
        # 检查是否能在顶部生成方块
        if not self.current_block.can_move(0, 0, self.board):
            self.game_over = True
    
    def clear_lines(self):
        """消除完整的行"""
        lines_to_clear = []
        
        for y in range(BOARD_HEIGHT):
            if all(cell != 0 for cell in self.board[y]):
                lines_to_clear.append(y)
        
        if lines_to_clear:
            # 移除完整的行
            for y in lines_to_clear:
                del self.board[y]
                self.board.insert(0, [0] * BOARD_WIDTH)
            
            # 更新分数
            lines_count = len(lines_to_clear)
            self.lines_cleared += lines_count
            self.score += lines_count * 100 * self.level
            
            # 升级检查
            if self.lines_cleared >= self.level * 10:
                self.level += 1
                return True
        
        return False
    
    def place_block(self):
        """放置方块到游戏板上"""
        for x, y in self.current_block.get_blocks():
            if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
                self.board[y][x] = self.current_block.shape_type
    
    def update(self):
        """游戏更新逻辑"""
        if self.game_over:
            return
        
        current_time = time.time()
        if current_time - self.last_move >= GAME_SPEED:
            if self.current_block.can_move(0, 1, self.board):
                self.current_block.move(0, 1)
            else:
                # 放置方块
                self.place_block()
                self.clear_lines()
                self.spawn_new_block()
            self.last_move = current_time
    
    def handle_input(self, key):
        """处理用户输入"""
        if self.game_over:
            return
        
        if key == 'q' or key == 'Q':
            self.game_over = True
        elif key == 'a' or key == 'A':
            # 左移
            if self.current_block.can_move(-1, 0, self.board):
                self.current_block.move(-1, 0)
        elif key == 'd' or key == 'D':
            # 右移
            if self.current_block.can_move(1, 0, self.board):
                self.current_block.move(1, 0)
        elif key == 's' or key == 'S':
            # 快速下降
            if self.current_block.can_move(0, 1, self.board):
                self.current_block.move(0, 1)
                self.score += 1
        elif key == 'w' or key == 'W':
            # 旋转
            if self.current_block.can_rotate(self.board):
                self.current_block.rotate()
        elif key == ' ':
            # 瞬间下降
            while self.current_block.can_move(0, 1, self.board):
                self.current_block.move(0, 1)
                self.score += 2
    
    def get_display_char(self, value):
        """获取显示字符"""
        chars = {
            0: ' ',
            'I': '█',
            'O': '█',
            'T': '█',
            'S': '█',
            'Z': '█',
            'J': '█',
            'L': '█'
        }
        return chars.get(value, ' ')
    
    def render(self):
        """渲染游戏画面"""
        # 清屏
        os.system('cls')  # Windows清屏命令
        
        # 创建显示的临时板子
        display_board = [row[:] for row in self.board]
        
        # 添加当前方块到显示板
        if self.current_block and not self.game_over:
            for x, y in self.current_block.get_blocks():
                if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
                    display_board[y][x] = self.current_block.shape_type
        
        # 显示游戏信息
        print("╔════════════════════════════════╗")
        print("║     俄罗斯方块 Tetris          ║")
        print("╠════════════════════════════════╣")
        print(f"║ 分数: {self.score:6d}                 ║")
        print(f"║ 等级: {self.level:2d}                  ║")
        print(f"║ 消除行数: {self.lines_cleared:4d}          ║")
        print("╠════════════════════════════════╣")
        print("║ 操作:                          ║")
        print("║  A/D - 左/右移动              ║")
        print("║  W - 旋转                     ║")
        print("║  S - 快速下降                 ║")
        print("║  空格 - 瞬间下降              ║")
        print("║  Q - 退出游戏                 ║")
        print("╚════════════════════════════════╝")
        print()
        
        # 显示游戏区域
        print("┌" + "─" * (BOARD_WIDTH * 2) + "┐")
        for y in range(BOARD_HEIGHT):
            print("│", end="")
            for x in range(BOARD_WIDTH):
                char = self.get_display_char(display_board[y][x])
                print(char * 2, end="")
            print("│")
        print("└" + "─" * (BOARD_WIDTH * 2) + "┘")
        
        # 显示下一个方块
        print("\n下一个方块:")
        if self.next_block:
            next_display = []
            shape_data = SHAPES[self.next_block.shape_type][0]
            min_x = min(cell[0] for cell in shape_data)
            max_x = max(cell[0] for cell in shape_data)
            min_y = min(cell[1] for cell in shape_data)
            max_y = max(cell[1] for cell in shape_data)
            
            for y in range(min_y, max_y + 1):
                line = ""
                for x in range(min_x, max_x + 1):
                    if (x, y) in shape_data:
                        line += "██"
                    else:
                        line += "  "
                next_display.append(line)
            
            for line in next_display:
                print("    " + line)
        
        if self.game_over:
            print("\n████████╗ 游戏结束 ════════")
            print("请按 Q 退出游戏")

def get_key():
    """获取键盘输入 - Windows版本"""
    if msvcrt.kbhit():
        return msvcrt.getch().decode('utf-8', errors='ignore')
    return None

def main():
    """主函数"""
    try:
        # 创建游戏实例
        game = TetrisGame()
        
        # 渲染初始画面
        game.render()
        
        # 游戏主循环
        while not game.game_over:
            # 处理用户输入
            key = get_key()
            if key:
                game.handle_input(key)
                game.render()
            
            # 更新游戏状态
            game.update()
            if key:  # 如果有输入，立即重新渲染
                game.render()
            
            # 短暂延时，避免CPU占用过高
            time.sleep(0.01)
        
        # 游戏结束后的清理
        game.render()
        while game.game_over:
            key = get_key()
            if key and (key.lower() == 'q'):
                break
            time.sleep(0.01)
        
    except KeyboardInterrupt:
        pass
    finally:
        # 清屏并显示结束信息
        os.system('cls')
        print("感谢您玩俄罗斯方块！")
        print("再见！")
        input("按任意键退出...")

if __name__ == "__main__":
    main()