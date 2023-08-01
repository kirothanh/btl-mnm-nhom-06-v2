
import time,webbrowser, pyautogui
import cv2
from myPose import myPose
from datetime import datetime
import myHand as handlib

class myGame():
    def __init__(self):
        self.pose = myPose()
        self.game_started = False
        self.x_position = 1 # 0: Ray ben trai, 1: Ray giua, 2: Ray ben phai
        self.y_position = 1 # 0: Down, 1: Stand, 2: jump
        self.clap_duration = 0 # So frame ma ng dung vo tay
        self.fist_duration = 0 # Số frame mà người dùng nắm bàn tay lại
        self.game_ended = False
        self.score = self.load_score_from_file()  # Load the previous score from file        
        self.app = 0
        self.destroywindow = 0
        self.detector = handlib.handDetector()

    def load_score_from_file(self, filename="score.txt"):
        try:
            with open(filename, "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 0
        except Exception as e:
            print("Error loading the score:", str(e))
            return 0

    def move_LRC(self, LRC):
        if LRC=="L":
            for _ in range(self.x_position):
                pyautogui.press('left')
            self.x_position = 0
        elif LRC=="R":
            for _ in range(2, self.x_position, -1):
                pyautogui.press('right')
            self.x_position = 2
        else:
            if self.x_position ==0:
                pyautogui.press('right')
            elif self.x_position == 2:
                pyautogui.press('left')

            self.x_position = 1
        return

    def move_JSD(self, JSD):
        if (JSD=="J") and (self.y_position == 1):
            pyautogui.press('up')
            self.y_position = 2
        elif (JSD=="D") and (self.y_position ==1):
            pyautogui.press('down')
            self.y_position = 0
        elif (JSD=="S") and (self.y_position !=1):
            self.y_position = 1
        return

    def play(self):

        # Khoi tao camera
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280)
        cap.set(4, 960)

        while True:
            ret, image = cap.read()
            if ret:

                image = cv2.flip(image, 1)
                image_height, image_width, _ = image.shape
                image, results = self.pose.detectPose(image)
                img, hand_lms = self.detector.findHands(image)
                n_fingers = self.detector.count_finger(hand_lms)

                # Mo game bang cach xoe tay
                if n_fingers == 5:  # n_fingers = 5 la xoe tay
                    self.app += 1
                    if self.app == 10:
                        print(self.app)
                        webbrowser.open_new("https://poki.com/en/g/subway-surfers")
                        time.sleep(2)

                #Choi game
                if results.pose_landmarks:
                    # Kiem tra game da bat dau chua
                    if self.game_started:
                          # Kiem tra trai phai
                        image, LRC = self.pose.checkPose_LRC(image, results)
                        self.move_LRC(LRC)

                         # Kiem tra len xuong
                        image, JSD = self.pose.checkPose_JSD(image, results)
                        self.move_JSD(JSD)
                        #cv2.putText(img,n_fingers, (100, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 3)
                        cv2.putText(image, "Nam tay de ket thuc!!!", (100, image_height - 10), cv2.FONT_HERSHEY_PLAIN,
                                    2, (255, 255, 0), 3)
                    else:
                        if self.app < 10:
                           cv2.putText(image, "Xoe tay de mo game!!!", (5, image_height-10), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,0), 3)
                        else:
                           cv2.putText(image, "Vo tay de bat dau!!!", (5, image_height - 10), cv2.FONT_HERSHEY_PLAIN,
                                        2, (255, 255, 0), 3)

                    #Bat dau game
                    image, CLAP = self.pose.checkPose_Clap(image, results)
                    if CLAP == "C":
                        self.clap_duration +=1
                        if self.clap_duration == 5: #5 frame
                            if self.game_started:
                                # Reset
                                self.x_position  = 1
                                self.y_position  = 1
                                self.pose.save_shoulder_line_y(image, results)
                                pyautogui.press('space')
                            else:
                                self.game_started  = True
                                self.pose.save_shoulder_line_y(image, results)
                                pyautogui.click(x=500, y = 300, button = "left")
                                self.score += 1  # Increase the score by 1 each time the game starts

                            self.clap_duration = 0

                    else:
                        self.clap_duration = 0

                # Nam ban tay de dong game
                if n_fingers == 0:  # n_finger = 0 nam tay
                    self.fist_duration += 1
                    if self.fist_duration == 15:
                        pyautogui.hotkey('alt', 'f4')
                        self.game_ended = True


                cv2.imshow("Game", image)
                cv2.waitKey(1)

            if  self.game_ended == True :
                break

        self.save_score_to_file()  # Save the player's score when the game ends
        cv2.destroyAllWindows()
        cap.release()

    def save_score_to_file(self, filename="score.txt"):
        try:
            with open(filename, "a") as file:  # Use "a" (append) mode to add scores to a new line
                print("\n")
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current date and time
                score_data = f"{current_time}: {self.score}\n"  # Format the score data
                file.write(score_data)  # Write the s  core data to the file
            print("Score saved s                     uc            cessful   ly.")
        except Exception as e:   
            print("Error saving the score:", str(e))



myGame = myGame()
myGame.play()