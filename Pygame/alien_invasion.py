import sys
import pygame
from pygame.sprite import Group
from settings import Settings
from ship import Ship
from alien import Alien
from button import Button
from game_stats import GameStats
from scoreboard import Scoreboard
import game_functions as gf
def run_game():
    #初始化游戏 创建屏幕对象
    pygame.init()
    ai_settings=Settings()
    screen=pygame.display.set_mode((ai_settings.screen_width,ai_settings.screen_height))
    pygame.display.set_caption("Alien Invasion")
    #创建Play按钮
    play_button=Button(ai_settings,screen,"PLAY")
    #创建一艘飞船
    ship=Ship(ai_settings,screen)
    #创建一个用于储存子弹的编组(类似于列表但是提供了有助于开发游戏的额外功能)
    bullets=Group()
    aliens=Group()
    #创建一个外星人
    gf.create_fleet(ai_settings,screen,ship,aliens)
    #创建一个储存游戏统计信息的实例
    stats=GameStats(ai_settings)
    sb=Scoreboard(ai_settings,screen,stats)

    #开始游戏的主循环
    while True:
        #监视键盘和鼠标
        gf.check_events(ai_settings,screen,stats,
                        sb,play_button,ship,aliens,bullets)
        if stats.game_activate:

            ship.update()
            gf.update_bullets(ai_settings,screen,
                              stats,sb,ship,aliens,bullets)
            gf.update_aliens(ai_settings,stats,screen,
                             sb,ship,aliens,bullets)
            #每次循环重绘屏幕

        gf.update_screen(ai_settings,screen,stats,sb,ship,aliens,bullets,play_button)


run_game()