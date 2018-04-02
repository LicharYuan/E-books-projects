# 避免alien_invasion过长

import sys
from time import  sleep
import pygame
from bullet import Bullet
from alien import Alien

def check_keydown_events(event,ai_settings,screen,ship,bullets):
    """响应按键"""
    if event.key==pygame.K_RIGHT:
        ship.moving_right=True
    elif event.key==pygame.K_LEFT:
        ship.moving_left=True
        # print('Left is OK')
    elif event.key==pygame.K_SPACE:
        fire_bullet(ai_settings,screen,ship,bullets)
    elif event.key==pygame.K_q:
        sys.exit()

def check_keyup_events(event,ship):
    """响应松开"""
    if event.key==pygame.K_RIGHT:
        ship.moving_right=False
    elif event.key==pygame.K_LEFT:
        ship.moving_left=False
def check_events(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets):
    """响应按键和鼠标事件"""
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            sys.exit()
        elif event.type==pygame.MOUSEBUTTONDOWN:
            mouse_x,mouse_y=pygame.mouse.get_pos()
            check_play_button(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets,mouse_x,mouse_y)
        elif event.type==pygame.KEYDOWN:
            check_keydown_events(event,ai_settings,screen,ship,bullets)
        elif event.type==pygame.KEYUP:
            check_keyup_events(event,ship)

def check_play_button(ai_settings,screen,stats,sb,play_button,
                      ship,aliens,bullets,mouse_x,mouse_y):
    """玩家单击PLAY按钮开始新游戏"""
    button_clicked=play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_activate:
        ai_settings.initialize_dynamic_settings()
        #隐藏光标
        pygame.mouse.set_visible(False)
        #重置游戏统计信息
        stats.reset_stats()
        stats.game_activate=True
        #重置记分牌
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()

        #清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()
        #创建一群新的外星人并让飞船居中
        create_fleet(ai_settings,screen,ship,aliens)
        ship.center_ship()


def update_screen(ai_seetings,screen,stats,sb,ship,aliens,bullets,play_button):
    screen.fill(ai_seetings.bg_color)
    #在飞船和外星人后面重绘所有子弹
    for bullet in bullets.sprites():
        #方法bullets.sprites()返回一个列表,包含bullets所有精灵
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)
    #如果游戏处于非活动状态，就绘制Play按钮
    sb.show_score()
    if not stats.game_activate:
        play_button.draw_button()

    pygame.display.flip()


def ship_hit(ai_settings, screen,stats,sb, ship, aliens, bullets):
    """方法响应外星人撞倒飞船的情况：1.余下飞船-1 2.创建新的外星人并把飞船重新放置在底端"""
    if stats.ships_left>0:
        stats.ships_left -= 1
        sb.prep_ships()




    else:
        stats.game_activate=False
        pygame.mouse.set_visible(True)

    aliens.empty()
    bullets.empty()
    create_fleet(ai_settings, screen, ship, aliens)
    ship.center_ship()
    sleep(0.5)

def check_bullet_alien_collisions(ai_settings,screen,stats,sb,ship,aliens,bullets):
    """响应子弹和外星人的碰撞"""
    # 用sprite.groupcollide()检测两个编组成员之间的碰撞
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
    # 这行代码遍历bullets中每颗子弹，再遍历编组aliens每个外星人，发现重叠时，就在它返回的字典中添加一个键值对
    # 两个True告诉Pygame删除碰撞的子弹和外星人，如果子弹不消失，则为False，True
    if collisions:
        for aliens in collisions.values():
            stats.score+=ai_settings.alien_points*len(aliens)
            sb.prep_score()
        check_high_score(stats,sb)
    if len(aliens) == 0:
        # del 现有的子弹并创建一群外星人
        bullets.empty()
        ai_settings.increase_speed()
        #如果外星人都消灭提高一个等级
        stats.level+=1
        sb.prep_level()

        create_fleet(ai_settings, screen, ship, aliens)
def check_aliens_bottom(ai_settings,screen,stats,sb,ship,aliens,bullets):
    """检查是否有外星人到达了屏幕底部"""
    screen_rect=screen.get_rect()
    for alien in  aliens:
        if alien.rect.bottom>=screen_rect.bottom:
            ship_hit(ai_settings, screen,stats,sb, ship, aliens, bullets)
            break


#让主程序尽量简单，建新方法
def update_bullets(ai_settings,screen,stats,sb,ship,aliens,bullets):
    bullets.update()

    # 删除已消失的子弹
    for bullet in bullets.copy():
        # 不应从列表或者编组中删除条目，因此必须遍历编组的副本，用copy()方法来设置for循环
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
            # print(len(bullets)) #打印实时的子弹数
    check_bullet_alien_collisions(ai_settings,screen,stats,sb,ship,aliens,bullets)


def fire_bullet(ai_settings,screen,ship,bullets):
    if len(bullets) < ai_settings.bullets_allowed:
        # print('SPACE is OK') #按键可能会与输入法冲突
        # 创建一个子弹并把它加入到编组bullets中
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)
def create_fleet(ai_settings,screen,ship,aliens):
    """创建外星人群"""
    #创建外星人，并计算一行可以容纳多少个外星人
    #外星人间距为外星人宽度
    alien=Alien(ai_settings,screen)
    number_aliens_x=get_number_aliens_x(ai_settings,alien.rect.width)
    number_rows=get_number_rows(ai_settings,ship.rect.height,alien.rect.height)
    for row_number in range(number_rows):
        #创建一行外星人
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings,screen,aliens,alien_number,row_number)
def get_number_aliens_x(ai_settings,alien_width):
    """计算每行可以容纳多少外星人"""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x
def get_number_rows(ai_settings,ship_height,alien_height):
    """计算屏幕可容纳多少行外星人"""
    available_space_y=(ai_settings.screen_height-(3*alien_height)-ship_height)
    number_rows=int(available_space_y/(2*alien_height))
    return number_rows
def create_alien(ai_settings,screen,aliens,alien_number,row_number):
    """创建外星人并把它放在当前行"""
    alien=Alien(ai_settings,screen)
    alien_width=alien.rect.width
    alien.x=alien_width+2*alien_width*alien_number
    alien.rect.x=alien.x
    alien.rect.y=alien.rect.height+2*alien.rect.height*row_number
    aliens.add(alien)


def check_fleet_edges(ai_settings,aliens):
    """到达边缘采取相应措施"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings,aliens)
            break
def change_fleet_direction(ai_settings,aliens):
    """整体外星人下移，并改变他们的方向"""
    for alien in aliens.sprites():
        alien.rect.y+=ai_settings.fleet_drop_speed
    ai_settings.fleet_direction*=-1

def update_aliens(ai_settings,stats,screen,sb,ship,aliens,bullets):
    """检查是否有外星人位于屏幕边缘，并更新整群的位置"""
    check_fleet_edges(ai_settings,aliens)
    aliens.update()
    #检测外星人和飞船之间的碰撞
    if pygame.sprite.spritecollideany(ship,aliens):
        #pygame.sprite.spritecollideany()接受两个实参，一个精灵和一个编组，
        # 检测编组是否有成员与精灵发生碰撞，有就停止遍历编组并返回第一个与飞船碰撞的外星人
        ship_hit(ai_settings,screen,stats,sb,ship,aliens,bullets)
    check_aliens_bottom(ai_settings,screen, stats,sb,ship, aliens, bullets)

def check_high_score(stats,sb):
    """检查是否诞生了新的最高分"""
    if stats.score>stats.high_score:
        stats.high_score=stats.score
        sb.prep_high_score()
