from enum import Enum
from io import BytesIO
import os
from typing import List, Optional, Tuple
from PIL import Image, ImageDraw
from PIL.Image import Image as IMG

from .utils import legal_word, load_font, save_png

class GuessResult(Enum):
    WIN = 0  # 猜出正确单词
    LOSS = 1  # 达到最大可猜次数，未猜出正确单词

class Hangman():
    def __init__(self, word: str, meaning: str):
        self.word: str = word  # 单词
        self.meaning: str = meaning  # 单词释义
        self.result = f"【单词】：{self.word}\n【释义】：{self.meaning}"
        self.wordLower: str = self.word.lower()
        self.length: int = len(word)  # 单词长度
        self.chance: int = 6  # 可猜次数
        self.wordsState: List[str] = []  # 记录单词状态
        for i in range(len(self.word)):
            self.wordsState.append(0)

        self.block_size = (40, 40)  # 文字块尺寸
        self.block_padding = (10, 10)  # 文字块之间间距
        self.padding = (20, 20)  # 边界间距
        self.border_width = 2  # 边框宽度
        self.font_size = 20  # 字体大小
        self.font = load_font("KarnakPro-Bold.ttf", self.font_size)

        self.correct_color = (134, 163, 115)  # 存在且位置正确时的颜色
        self.border_color = (123, 123, 124)  # 边框颜色
        self.bg_color = (255, 255, 255)  # 背景颜色
        self.font_color = (255, 255, 255)  # 文字颜色

    def guess(self, letterOrWord: str) -> Optional[GuessResult]:
        if len(letterOrWord)==1:
            letter = letterOrWord.lower()
            if letter in self.word:
                for i in range(len(self.word)):
                    if letter==self.word[i]:self.wordsState[i]=1
        else:
            word=letterOrWord.lower()
            if word==self.word:return GuessResult.WIN
        if all(w==1 for w in self.wordsState):return GuessResult.WIN
        self.chance-=1
        if self.chance==0:return GuessResult.LOSS


    def draw_block(self, color: Tuple[int, int, int], letter: str) -> IMG:
        block = Image.new("RGB", self.block_size, self.border_color)
        inner_w = self.block_size[0] - self.border_width * 2
        inner_h = self.block_size[1] - self.border_width * 2
        inner = Image.new("RGB", (inner_w, inner_h), color)
        block.paste(inner, (self.border_width, self.border_width))
        if letter:
            letter = letter.upper()
            draw = ImageDraw.Draw(block)
            bbox = self.font.getbbox(letter)
            x = (self.block_size[0] - bbox[2]) / 2
            y = (self.block_size[1] - bbox[3]) / 2
            draw.text((x, y), letter, font=self.font, fill=self.font_color)
        return block

    def draw(self) -> BytesIO:
        board_w = self.length * self.block_size[0]
        board_w += (self.length - 1) * self.block_padding[0] + 2 * self.padding[0]
        board_h = 3 * self.block_size[1]
        hangman = Image.open(os.path.dirname(__file__)+f"/resources/hangman{6-self.chance}.png")
        hangman = hangman.resize((hangman.size[0]*self.length,hangman.size[1]*self.length))
        board_h += hangman.size[1]-10*self.length
        board_size = (board_w, board_h)
        board = Image.new("RGB", board_size, self.bg_color)
        board.paste(hangman,(int(board_w/2)-40*self.length,0))

        blocks: List[IMG] = []
        for i in range(len(self.wordsState)):
            color = self.correct_color if self.wordsState[i]==1 else self.bg_color
            letter = self.word[i] if self.wordsState[i]==1 else ''
            blocks.append(self.draw_block(color, letter))

        for col, block in enumerate(blocks):
            x = self.padding[0] + (self.block_size[0] + self.block_padding[0]) * col
            y = self.padding[1] + (self.block_size[1] + self.block_padding[1]) + hangman.size[1]-10*self.length
            board.paste(block, (x, y))
        return save_png(board)

# a = Hangman('fuckyou','pip')
# a.guess('p')
# a.guess('f')
# Image.open(a.draw()).show()