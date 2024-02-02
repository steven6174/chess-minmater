from mm_enums import Player_Color
from mm_sounds import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
import timeit
import chess


def get_chrome_driver(url='https://www.chess.com/play/computer', is_win=False) -> webdriver:
    import undetected_chromedriver as webdriver2
    chrome_options = webdriver2.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-features=RendererCodeIntegrity")
    # chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if is_win:
        # chrome_options.add_argument("user-data-dir=/Users/Steven/PycharmProjects/MinMater++/userdata")
        # chrome_driver = webdriver.Chrome(options=chrome_options)
        chrome_driver = webdriver2.Chrome(options=chrome_options, user_data_dir="/Users/Steven/PycharmProjects/MinMater++/userdata")
    else:
        chrome_options.add_argument("user-data-dir=/home/steven/PycharmProjects/MinMater++/userdata")
        chrome_driver = webdriver2.Chrome("/home/steven/PycharmProjects/MinMater++/venv/bin/chromedriver",
                                         options=chrome_options)
    chrome_driver.get(url)


    return chrome_driver





# noinspection PyUnusedLocal
def close_chrome_driver(driver: webdriver, is_win=False) -> None:
    if is_win:
        try:
            driver.quit()
            driver = None
            return
        except:
            raise Exception('There was a problem closing Chrome')
    try:
        driver.close()
        driver.quit()
        driver = None
    except:
        raise Exception('There was a problem closing Chrome')


def is_user_on_top(driver: webdriver) -> bool:
    # I noticed that the html for both the user and the bot is very similar except the user has an <a> element within
    # while the bot does not. It has to do with flair icons, which bots don't have. This won't work if the user
    # chooses to not have flair.
    # If necessary, can also look at the images. I think the bots all have PNG files as source while humans have
    # JPEG files. And I think the bots all have 200x200 source images versus 50x50 for humans.

    # for now, assume user (me) has flair
    try:
        # the following element should exist if user is on bottom
        driver.find_element(By.XPATH, f"//div[@id='board-layout-player-bottom']/div/div/div/div/div[1]/div/a")
    except NoSuchElementException:
        return True
    return False


def is_white_on_top(driver: webdriver) -> bool:
    # idea is to get the coordinates of the divs for square-11 (white's queen side rook)
    # and square-18 (black's queen side rook) and compare
    white_queenside_rook = driver.find_element(By.XPATH,
                                               f"//div[contains(@class, 'piece') and contains(@class, 'square-11')]")
    black_queenside_rook = driver.find_element(By.XPATH,
                                               f"//div[contains(@class, 'piece') and contains(@class, 'square-18')]")
    # if white's on top then black's y offset minus white's y offset will be positive
    # recall that y increases as you go down the screen
    white_y = white_queenside_rook.location['y']
    black_y = black_queenside_rook.location['y']
    return black_y > white_y


def determine_user_color(driver: webdriver) -> Player_Color:
    white_on_top = is_white_on_top(driver)
    user_on_top = is_user_on_top(driver)
    if white_on_top and user_on_top:
        return Player_Color.WHITE
    if white_on_top and not user_on_top:
        return Player_Color.BLACK
    if not white_on_top and user_on_top:
        return Player_Color.BLACK
    return Player_Color.WHITE


def click_back_button(driver: webdriver) -> None:
    time.sleep(0.5)
    try:
        back_button = driver.find_element(By.XPATH, f"//button[contains(@data-cy,'Move Back')]")
    except NoSuchElementException:
        time.sleep(0.5)
        try:
            back_button = driver.find_element(By.XPATH, f"//button[contains(@data-cy,'Move Back')]")
        except NoSuchElementException:
            time.sleep(3.0)
            try:
                back_button = driver.find_element(By.XPATH, f"//button[contains(@data-cy,'Move Back')]")
            except NoSuchElementException:
                time.sleep(15.0)
                back_button = driver.find_element(By.XPATH, f"//button[contains(@data-cy,'Move Back')]")
    time.sleep(0.2)
    back_button.click()
    # time.sleep(2.0)
    # try:
    #     print('trying to find confirm button')
    #     # confirm_button = driver.find_element(By.XPATH, f"//button[contains(@data-cy,'confirm-popover-yes-button')]")
    #     confirm_button = driver.find_element(By.XPATH, f"//button[contains(.,'Take Back')]")
    #     print('button found')
    #     time.sleep(0.5)
    #     confirm_button.click()
    #     print('button clicked')
    # except NoSuchElementException:
    #     print('NoSuchElementException')
    # except ElementNotInteractableException:
    #     print('ElementNotInteractableException')


def get_square_size(driver: webdriver) -> float:
    return driver.find_element(By.TAG_NAME, 'wc-chess-board').size['height'] / 8


def make_move_and_promote(driver: webdriver, square_size: float, move: str, white_on_top: bool,
                          user_color: Player_Color) -> None:
    # the move passed in is something like 'e7e6' playing as black
    # a, b, c, ..., h     unicode for 'a' is 97
    source_square_x = str(ord(move[0]) - 96)
    # 1, 2, 3,   , 8      unicode for '1' is 49
    source_square_y = str(ord(move[1]) - 48)
    target_square_x = str(ord(move[2]) - 96)
    target_square_y = str(ord(move[3]) - 48)
    offset_x = (int(target_square_x) - int(source_square_x)) * square_size
    offset_y = (int(target_square_y) - int(source_square_y)) * square_size
    if white_on_top:
        offset_x *= -1
    else:
        offset_y *= -1
    source_element = driver.find_element(By.XPATH,
                                         f"//div[contains(@class, 'piece') and contains(@class, 'square-{source_square_x}{source_square_y}')]")
    action_chains = ActionChains(driver)
    action_chains.drag_and_drop_by_offset(source_element, offset_x, offset_y).perform()
    if len(str(move)) == 5:
        color_char = 'b'
        if user_color == Player_Color.WHITE:
            color_char = 'w'
        try:
            promotion = driver.find_element(By.CSS_SELECTOR, "div.promotion-piece." + color_char + str(move)[-1].lower())
            promotion.click()
        except NoSuchElementException:
            pass
    try:
        # print('trying to find confirm button')
        #        # confirm_button = driver.find_element(By.XPATH, f"//button[contains(@data-cy,'confirm-popover-yes-button')]")
        confirm_button = driver.find_element(By.XPATH, f"//button[contains(.,'Take Back')]")
        # print('button found')
        #     time.sleep(0.5)
        confirm_button.click()
        # print('button clicked')
    except NoSuchElementException:
        #print('NoSuchElementException')
        pass


def get_opening_name(driver: webdriver) -> str:
    try:
        opening = driver.find_element(By.CLASS_NAME, 'eco-opening-name')
        opening_as_list = opening.text.split('\n')
        opening_name = opening_as_list[0]
        return opening_name
    except:
        return ''


def save_game(driver: webdriver) -> None:
    try:
        time.sleep(0.5)
        add_to_archive_span = driver.find_element(By.CLASS_NAME, 'add-to-archive-label')
        add_to_archive_span.click()
    except:
        play_losing_sound()
        raise


def find_and_click_button(driver: webdriver, match_text: str):
    time.sleep(0.1)
    iterations = 0
    while iterations < 20:
        try:
            time.sleep(0.1)
            button = driver.find_element(By.XPATH, match_text)
            time.sleep(0.1)
            button.click()
            break
        except:
            iterations += 1
        finally:
            time.sleep(0.1)
    if iterations >= 20:
        raise NoSuchElementException("button not found!")


def click_new_game_button(driver: webdriver) -> None:
    try:
        time.sleep(0.5)
        find_and_click_button(driver, f"//button[contains(.,'New Game')]")
    except:
        play_losing_sound()
        raise


def start_new_game(driver: webdriver) -> None:
    try:
        time.sleep(0.1)
        find_and_click_button(driver, f"//button[contains(.,'New Game')]")
        find_and_click_button(driver, f"//button[contains(.,'Choose')]")
        find_and_click_button(driver, f"//button[contains(.,'Play')]")
    except:
        play_losing_sound()
        raise


def resign_and_start_new_game(driver: webdriver) -> None:
    try:
        time.sleep(0.1)
        find_and_click_button(driver, f"//span[contains(@class,'icon-font-chess ui_v5-button-icon plus')]")
        find_and_click_button(driver, f"//button[contains(.,'Yes')]")
    except:
        play_losing_sound()
        raise
    finally:
        start_new_game(driver)


def go_to_main_bot_selection_screen(driver: webdriver) -> None:
    # after navigating to chess.com/play/computer, we are either at the main bot selection screen
    # or are in the middle of an existing game
    # if we can find the resign button then it is the latter and we can resign and start new game
    try:
        time.sleep(0.5)
        resign_button = driver.find_element(By.XPATH, f"//a[contains(@data-cy,'Resign')]")
        resign_button.click()
        time.sleep(0.5)
        new_game_button = driver.find_element(By.XPATH, f"//button[contains(@data-cy,'Game Over - New Game')]")
        new_game_button.click()
        time.sleep(0.5)
        # find_and_click_button(driver, f"//span[contains(@class,'icon-font-chess ui_v5-button-icon plus')]")
        #find_and_click_button(driver, f"//a[contains(@data-cy,'Resign')]")
        # resign_game(driver)
    except NoSuchElementException:
        # we must already be there
        pass


def choose_opponent_1(driver: webdriver, html_section_name: str, html_bot_name: str) -> None:
    top_players_section = driver.find_element(By.XPATH, f"//div[contains(@data-cy,'{html_section_name}')]")
    try:
        top_players_location = top_players_section.location_once_scrolled_into_view()
        time.sleep(0.5)
    except:
        try:
            top_players_location = top_players_section.location_once_scrolled_into_view()
            time.sleep(0.5)
        except:
            pass
    bot_img = driver.find_element(By.XPATH, f"//img[contains(@alt,'{html_bot_name}')]")
    try:
        bot_img.click()
        time.sleep(0.5)
    except ElementClickInterceptedException:
        # must already be selected
        pass
    choose_button = driver.find_element(By.XPATH, f"//button[contains(@title,'Choose')]")
    choose_button.click()
    time.sleep(0.5)


def choose_opponent_2(driver: webdriver, player_color: Player_Color) -> None:
    color_text = 'white' if player_color == Player_Color.WHITE else 'black'
    color_button = driver.find_element(By.XPATH, f"//div[contains(@data-cy,'{color_text}')]")
    try:
        color_button.click()
        time.sleep(0.5)
    except ElementClickInterceptedException:
        # must already be selected
        pass
    play_button = driver.find_element(By.XPATH, f"//button[contains(@title,'Play')]")
    play_button.click()
    time.sleep(0.5)


def get_full_move_list(driver: webdriver) -> str:
    try:
        move_list = driver.find_element(By.TAG_NAME, "wc-vertical-move-list")
    except NoSuchElementException:
        return ""
    except:
        return ""
    move_as_list = move_list.text.split("\n")
    return move_as_list


def wait_for_then_get_latest_move(driver: webdriver, player_color_to_get: Player_Color, move_number: int) -> str:
    moves_as_list = get_full_move_list(driver)
    # print(f'moves_as_list == {moves_as_list}, player_color == {player_color}, move_number == {move_number}')
    list_length = len(moves_as_list)
    # print(f'initial list_length == {list_length}')
    # print(f'while list_length < {move_number * 3 - (1 if player_color == Player_Color.BLACK else 0)}')
    while list_length < (move_number * 3 - (1 if player_color_to_get == Player_Color.WHITE else 0)):
        time.sleep(0.1)
        moves_as_list = get_full_move_list(driver)
        list_length = len(moves_as_list)
        # print(f'new list_length == {list_length}')
    # print(f'moves_as_list = {moves_as_list}')
    last_element = moves_as_list.pop()
    # print(f'last_element == {last_element}')
    cleaned_element = last_element.removesuffix('+')
    # print(f'cleaned_element == {cleaned_element}')
    return cleaned_element


def wait_for_then_get_black_latest_move(driver: webdriver, board: chess.Board, move_number: int) -> chess.Move:
    moves_as_list = get_full_move_list(driver)
    list_length = len(moves_as_list)
    loop_start_time = time.time()
    while list_length < (move_number * 3):
        time.sleep(0.1)
        loop_elapsed = time.time() - loop_start_time
        if loop_elapsed > 10 and move_number == 1:
            raise ElementNotInteractableException("timed out waiting to read black's responding move")
        time.sleep(0.1)
        moves_as_list = get_full_move_list(driver)
        list_length = len(moves_as_list)
    last_element = moves_as_list[list_length - 1]
    cleaned_element = last_element.removesuffix("+")
    black_latest_move = board.parse_san(cleaned_element)
    return black_latest_move


def wait_for_then_get_white_latest_move(driver: webdriver, board: chess.Board, move_number: int) -> chess.Move:
    moves_as_list = get_full_move_list(driver)
    list_length = len(moves_as_list)
    loop_start_time = time.time()
    while list_length < (move_number * 3 - 1):
        loop_elapsed = time.time() - loop_start_time
        if loop_elapsed > 10:
            try:
                driver.get('https://www.chess.com/play/computer')
                time.sleep(1.0)
                find_and_click_button(driver, f"//button[contains(.,'Choose')]")
                time.sleep(1.0)
                find_and_click_button(driver, f"//button[contains(.,'Play')]")
                time.sleep(1.0)
            except:
                play_losing_sound()
        time.sleep(0.1)
        moves_as_list = get_full_move_list(driver)
        list_length = len(moves_as_list)
    last_element = moves_as_list[list_length - 1]
    cleaned_element = last_element.removesuffix("+")
    white_latest_move = board.parse_san(cleaned_element)
    return white_latest_move
