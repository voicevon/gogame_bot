
from datetime import datetime
import cv2


class app_config:
    class mainloop:
        class at_demo_mover:
            do_vision_check = True

    class game_rule:
        class board_size:
            row = 19
            col = 19
        class cell_color:
            blank = 0
            white = 3
            black = 8
            died_white = 103
            died_black = 108


        class state_machine:
            class state:
                begin = 1
                computer_playing = 2
                withdraw_white = 3
                comparing_layout = 4
                user_playing = 5
                withdraw_black =6
                game_over = 7

    class server:
        class AI:
            ip = '192.168.123.123'
            port = 50007

        class mqtt:
            broker_addr = 'voicevon.vicp.io'
            port = 1883
            username = 'von'
            password = 'von1970'

    class robot_arm:
        name = 'GO_SCARA'

    class robot_eye:
        camera_index = 0
        show_origin = True

        class board_scanner:
            show_board_image = True

            class cropping:
                crop_width_on_x = 428
                crop_height_on_y = 428
        class cell_scanner:
            class dimension:
                cell_space_x = 22
                cell_space_y = 22
                cell_detector_range = 1.6

        class layout_scanner:
            stable_depth = 6
            show_scan_image = True 
            
            class inspecting:
                cell_name = 'T14'
                counter = 100
        class mark_scanner:
            stable_depth = 5

    class current_game:
        lastest_move_cell_name = None


class CvDebugger():
    def __init__(self):
        pass
    
    @staticmethod
    def show_debug_image( window_name, soure_img, debug_text):
        if app_config.robot_eye.board_scanner.show_board_image:
            cp = soure_img.copy()
            debug_text += '  ' + datetime.now().strftime('%s')
            cv2.putText(cp, debug_text, (10,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1)
            cv2.imshow(window_name, cp)
            cv2.waitKey(1)


if __name__ == "__main__":
    # global_config = app_config
    # s1 = global_config.robot_arm.name
    app_config.robot_eye.layout_scanner.inspecting.cell_name = 'A1'
    print(app_config.robot_eye.layout_scanner.inspecting.cell_name)