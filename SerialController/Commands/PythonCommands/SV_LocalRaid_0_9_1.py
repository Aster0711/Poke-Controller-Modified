#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.Keys import KeyPress, Button, Direction, Stick, Hat
import datetime
import os
import shutil
import glob
import enum


class Type(enum.Enum):
    NORMAL = "ノーマルタイプ"
    FIRE = "ほのおタイプ"
    WATER = "みずタイプ"
    GRASS = "くさタイプ"
    ELECTRIC = "でんきタイプ"
    ICE = "こおりタイプ"
    FIGHTING = "かくとうタイプ"
    POISON = "どくタイプ"
    GROUND = "じめんタイプ"
    FLYING = "ひこうタイプ"
    PSYCHIC = "エスパータイプ"
    BUG = "むしタイプ"
    ROCK = "いわタイプ"
    GHOST = "ゴーストタイプ"
    DRAGON = "ドラゴンタイプ"
    DARK = "あくタイプ"
    STEEL = "はがねタイプ"
    FAIRY = "フェアリータイプ"


class AutoEncount(ImageProcPythonCommand):
    NAME = 'SV_Local自動レイド_v.0.9.1'

    def __init__(self,cam):
        super().__init__(cam)

    def do(self):
        print("-------------------------------")
        print("SV Local自動レイド_v.0.9.1")
        print("Developed by.じゃんきー")
        print("Special Thanks:はんぺんさん、特にさん、minahokuさん")
        print("-------------------------------")
        self.wait(0.5)
        count = 0
        menu_while_num = 0
        raid_while_num = 0
        result_while_num = 0
        loop_num = 0
        lose_counts = []
        # 開始時間を取得（画像ファイル名に用いる）
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        start_time = datetime.datetime.now(JST)
        start_time_yyyymmddHHMMSS = start_time.strftime('%Y%m%d%H%M%S')
        print("Start", " ", start_time)

        #事前設定

        #手持ち：1匹目眼鏡ニンフィア(1番目の技：はかいこうせん)
        #ボックス：星5以上のとき使用するポケモンをdecide_myPokemonで設定した順番通りにボックスの左上からに配置
        # 1  2  3  4  5  6
        # 7  8  9  10 11 12
        # ...

        #ニックネーム設定：OFF
        #ボックスは自動で送る設定
        #オートセーブ：ON

        #初回は巣穴の北側正面に立って実施。場所がわかってればその場でOK
        #南方向に目的地を設定
        #ボール変更の処理は入れてません
        #メタモン表示があったら止める設定もできます。デフォルトはコメントアウトしてます。
        #注意事項！！！
        #ボールがなくなった時の処理は入れてません。ご注意ください。
        #ボールの変更処理も入れてません。A連打でボールを投げます
        

        while True:
            self.wait(0.5)
            #メニュー認識

            while not self.isContainTemplate('SV_suana/menu_R.png', threshold=0.8, use_gray=True, show_value=False):
                menu_while_num += 1
                print("メニューのwhile")
                # 待機時間が約5分を越えたとき再起動
                if menu_while_num >= 200:
                    self.recover_error()
                    self.do()
                if menu_while_num % 15 == 0:
                    print("指定時間以上待機しました。Aボタンをクリックします。")
                    self.press(Button.A, wait=1.0)
                # メニュー展開
                self.press(Button.X, wait=1.0)

            print("メニュー画面を認識しました")
            menu_while_num = 0
            self.press(Button.B, wait=2.0)
            self.press(Button.Y, wait=5.0)
            self.press(Button.Y, wait=4.0)
            self.press(Button.A, wait=3.0)
            loop_num = 0
            while not self.isContainTemplate('SV_suana/V_raid.png', threshold=0.7, use_gray=True, show_value=False):
                print("巣穴のwhile")
                print("巣穴がないため日付変更をします。",loop_num,"回目です。")
                self.dayprogress()
                self.wait(4.0) #巣穴沸き待機
                self.press(Button.A, wait=1.5)
                loop_num += 1
                # 30回連続で見つからなかった場合再起動→再帰的に処理を呼び出す
                if loop_num >= 25:
                    self.recover_error()
                    self.do()
                

            # 捕まえるか否かの判定
            is_capture = self.is_capture_pokemon()
            print("巣穴発見。", "倒せた場合は捕まえます。" if is_capture else "このポケモンは捕まえません。")
            #レイド参加
            count += 1
            self.camera.saveCapture(filename=f"{start_time_yyyymmddHHMMSS}/{count}")

            # ここにcapture画像を、そのままcapturepokemonsに投げ込めるようなサイズに変更する処理を入れる

            print("------------レイド開始-------------")
            print("         ",count,"回目のレイドです")
            print("----------------------------------")

            # レイドポケモンのタイプを判定する
            raidPokemon_type = self.judge_raidPokemon_type() 

            # レイドポケモンのレベルを判定する
            # 星5以上であればボックスから有利相性のポケモンを選択する
            if self.isContainTemplate('SV_suana/S_Lv5.png', threshold=0.9, use_gray=True, show_value=False) \
            or self.isContainTemplate('SV_suana/Lv6.png', threshold=0.8, use_gray=False, show_value=False):
                print("星5以上のレイドです。ボックスから有利タイプのポケモンを選択します。")

                # レイドポケモンのタイプに応じて使用するポケモンを決定する
                myPokemon_num = self.decide_myPokemon(raidPokemon_type)
                # 必要に応じて使用するポケモンを変更する
                self.change_pokemon_from_box(myPokemon_num)

            # 星4以下の場合はタイプに関わらず1番目の眼鏡ニンフィアではかいこうせんを打つ
            else:
                print("星4以下なので先頭のポケモンで戦います")
                self.press(Direction.DOWN, wait=1.0)

            self.press(Button.A, wait=1.0)
            self.press(Button.A, wait=1.0) #入力抜け防止

            #つかまえたが出るまで
            print("倒すまでの処理を実施します")
            turn = 0
            while not self.isContainTemplate('SV_suana/raid_catch.png', threshold=0.95, use_gray=False, show_value=False):
                print("レイドのwhile")
                raid_while_num += 1
                # 待機時間が約5分を越えたとき再起動→再帰的に処理を呼び出す
                if raid_while_num >= 200:
                    self.recover_error()
                    self.do()
                
                self.wait(1.0)
                if self.isContainTemplate("SV_Suana/raid_keepon_Y.png", threshold=0.8, use_gray=False, show_value=False) \
                or self.isContainTemplate("SV_suana/raid_keepon_m.png", threshold=0.8, use_gray=False, show_value=False) \
                or self.isContainTemplate("SV_suana/raid_keepon_f.png", threshold=0.8, use_gray=False, show_value=False):
                    print("レイド継続中")
                    if(raid_while_num < 5):
                        turn -= 1
                    raid_while_num = 0
                    self.wait(0.5)#0.5にする
                    self.press(Button.A, wait=1.0)
                    if 3 <= turn and turn <= 6:
                        print("多分テラスタルオーブが溜まりました。テラスタルを発動します。")
                        self.press(Button.R, wait=0.5)
                    self.press(Button.A, wait=1.0)
                    self.press(Button.A, wait=1.0)
                    self.press(Button.A, wait=1.0)
                    self.press(Button.A, wait=1.0)
                    turn += 1

                if self.isContainTemplate('SV_suana/raid_lose.png', threshold=0.95, use_gray=True, show_value=False):
                    break
            if self.isContainTemplate('SV_suana/raid_lose.png', threshold=0.9, use_gray=True, show_value=False):
                print("負けたため、次のレイドを行います。")
                lose_counts.append(count)
                self.wait(4.0) #巣穴沸き待機
                self.press(Button.A, wait=1.0)
                self.dayprogress()
                self.wait(1.0)
                try: 
                    SCREENSHOT_DIR = r"C:\PokeCon\Poke-Controller-Modified\SerialController\Captures"
                    image_path = os.path.join(SCREENSHOT_DIR, start_time_yyyymmddHHMMSS)
                    print('image_path: ', image_path)
                    src_path = os.path.join(image_path, f"{count}.png")
                    print('src_path: ', src_path)
                    dst_path = os.path.join(image_path, f"lose_{count}.png")
                    print('dst_path: ', dst_path)
                    shutil.copyfile(src_path, dst_path)
                except BaseException as e:
                    print(e)
                    pass
                continue
            print("ポケモンを倒しました。")
            self.wait(2.0)
            if is_capture:
                print("捕獲対象ポケモンなので捕獲します。")
                self.press(Button.A, wait=1.0)
            else:
                print("捕獲せずに処理を進めます。")
                self.press(Direction.DOWN, wait=1.0)
        
            self.press(Button.A, wait=1.0)
            #ボール選ぶ処理を入れるならここ
            #つぎへのAボタン認識するまで待機
            result_while_num = 0
            while not self.isContainTemplate('SV_suana/raid_A.png', threshold=0.8, use_gray=False, show_value=False):
                print("結果待ちのwhile")
                self.wait(0.5)
                result_while_num += 0.5
                # 待機時間が約5分を越えたとき再起動
                if result_while_num >= 300:
                    self.recover_error()
                    self.do()

            self.wait(2.0)
            self.press(Button.A, wait=1.0)
            print("------------レイド終了-------------")
            print("周回数 → ",count,"回")
            print("敗北数 → ",len(lose_counts),"回")
            for lose in lose_counts:
                print("敗北画像 → ",lose,".png")
            print("----------------------------------")

    def dayprogress(self):
        print("< 日付を1日進めます >")
        # ホーム画面⇒日時と時刻の画面
        self.press(Button.HOME, wait=1)
        self.press(Direction.DOWN)
        self.press(Direction.RIGHT)
        self.press(Direction.RIGHT)
        self.press(Direction.RIGHT)
        self.press(Direction.RIGHT)
        self.press(Direction.RIGHT)
        self.press(Button.A, wait=1.5)  
        self.press(Direction.DOWN, duration=2, wait=0.5)
        self.press(Button.A, wait=0.3)  
        for j in range(20):
            if self.isContainTemplate("SV_Suana/select_date_change_white.png", threshold=0.83, use_gray=False, show_value=False) \
            or self.isContainTemplate("SV_suana/select_date_change_dark.png", threshold=0.83, use_gray=False, show_value=False):
                self.press(Button.A, wait=1.0)
                self.press(Direction.DOWN)
                self.press(Direction.DOWN)
                self.press(Button.A, wait=1.0)
                self.press(Direction.RIGHT)
                self.press(Direction.RIGHT)
                self.press(Direction.UP)
                self.press(Button.A)
                self.press(Button.A)
                self.press(Button.A)
                self.press(Button.A)
                self.wait(0.5)
                self.press(Button.HOME, wait=0.5)
                self.press(Button.HOME, wait=1)
                break
            else:
                self.press(Direction.DOWN, wait=0.13)

    def judge_raidPokemon_type(self):
        for x in Type:
            if self.isContainTemplate('SV_Raid/raid_S/raid_' + x.name + '.png', threshold=0.95, use_gray=True,
                                      show_value=False) \
                    or self.isContainTemplate('SV_Raid/raid_6/raid_6_' + x.name + '.png', threshold=0.95, use_gray=True,
                                              show_value=False):
                print(x.value + "のレイドです。")
                return x
        # 合致するものがいなかった場合水として返す(デフォルトはハラバリーを使用する)
        print("合致するタイプがないので水タイプとして処理します。")
        return Type.WATER

    def is_capture_pokemon(self):
        POKEMON_DIR = r"C:\PokeCon\Poke-Controller-Modified\SerialController\Template\SV_Suana\capture_pokemons"
        capture_pokemons = glob.glob(os.path.join(POKEMON_DIR,'*.png'))
        for pokemon_image_full_path in capture_pokemons:
            image_name = os.path.basename(pokemon_image_full_path)
            path = f'SV_suana/capture_pokemons/{image_name}'
            if self.isContainTemplate(path, threshold=0.85, use_gray=True, show_value=False):
                return True
        return False

    def softreset(self):
        self.wait(0.5)
        self.press(Button.HOME, wait=0.5)
        self.wait(0.5)
        self.press(Button.X, wait=0.5)
        self.wait(0.5)
        self.press(Button.A, wait=5.0) 
        self.press(Button.A, wait=5.0) 
        self.press(Button.A, wait=10.0) 
        while not self.isContainTemplate('SV_suana/S_TOP.png', threshold=0.5, use_gray=True, show_value=False):
            self.wait(0.5)
        print("TOP画面を認識しました。")
        self.wait(3.0)
        self.press(Button.A, wait=1.0)

    # def change_pokemon(self, num):
    #     self.press(Direction.UP, wait=0.5)
    #     self.press(Button.A, wait=5.0)
    #     # ボックス操作
    #     print(f"手持ちから{num}匹目を選択。")
    #     self.press(Direction.LEFT, wait=1.0)

    #     for _ in range(1, num):
    #         self.press(Direction.DOWN, wait=1.0)

    #     self.press(Button.A, wait=0.5)
    #     self.press(Button.A, wait=2.0)
    #     self.press(Direction.DOWN, wait=0.5)

    def change_pokemon_from_box(self, num: int):
        self.wait(1.0)
        self.press(Direction.UP, wait=1.0)  # オンラインとオフラインで「ポケモンをいれかえる」の場所が違うので注意
        self.press(Button.A, wait=3.0)

        # ボックス操作
        while not self.isContainTemplate('SV_Raid/raid_box.png', threshold=0.9, use_gray=True, show_value=False):
            self.wait(0.5)
        print(f"ボックスから{num}匹目を選択。")
        self.wait(1.0)
        for _ in range(0, num // 6):
            self.press(Direction.DOWN, wait=1.0)
        for _ in range(1, num % 6):
            self.press(Direction.RIGHT, wait=1.0)

        self.press(Button.A, wait=1)
        self.press(Button.A, wait=5.0)
        self.press(Direction.UP, wait=1)
        
    def decide_myPokemon(self, raidPokemon_type: Type):
        # ニンフィア(1番目)を使うタイプ
        NINFIA = [Type.DRAGON]
        # テツノカイナ(2番目を使うタイプ)
        TETUNOKAINA = [Type.NORMAL, Type.ICE, Type.ROCK, Type.STEEL, Type.DARK]
        # ハラバリー(3番目を使うタイプ)
        HARABARI = [Type.WATER, Type.FLYING]
        # クエスパトラ(4番目を使うタイプ)
        KUESUPATORA = [Type.POISON, Type.FIGHTING]
        # ラウドボーン(5番目を使うタイプ)
        RAUDOBON = [Type.GRASS, Type.BUG]
        # マリルリ(6番目を使うタイプ)
        MARIRURI = [Type.FIRE, Type.GROUND]
        # ハバタクカミ(7番目を使うタイプ)
        HABATAKUKAMI= [Type.PSYCHIC, Type.GHOST] 
        # ドドゲザン(8番目を使うタイプ)
        DODOGEZAN = [Type.FAIRY]
        # ガブリアス(9番目を使うタイプ)
        GABURIASU = [Type.ELECTRIC]

        if raidPokemon_type in NINFIA:
            print('ニンフィアを使用します。')
            return 1
        elif raidPokemon_type in TETUNOKAINA:
            print('テツノカイナを使用します。')
            return 2
        elif raidPokemon_type in HARABARI:
            print('ハラバリーを使用します。')
            return 3
        elif raidPokemon_type in KUESUPATORA:
            print('クエスパトラを使用します。')
            return 4
        elif raidPokemon_type in RAUDOBON:
            print('ラウドボーンを使用します。')
            return 5
        elif raidPokemon_type in MARIRURI:
            print('マリルリを使用します。')
            return 6
        elif raidPokemon_type in HABATAKUKAMI:
            print('ハバタクカミを使用します。')
            return 7
        elif raidPokemon_type in DODOGEZAN:
            print('ドドゲザンを使用します。')
            return 8
        elif raidPokemon_type in GABURIASU:
            print('ガブリアスを使用します。')
            return 9
        # デフォルトではニンフィア(1番目)を使用する
        else:
            print('ニンフィアを使用します。')
            return 3

    def recover_error(self):
        print("エラー状況と判定。再起動します。")
        self.press(Button.HOME, wait=3.0)
        self.press(Button.X, wait=5.0)
        self.press(Button.A, wait=5.0) # ゲーム終了
        self.press(Button.A, wait=5.0)
        self.press(Button.A, wait=35.0) # ゲーム起動中
        self.press(Button.A, wait=40.0) # ゲーム起動

