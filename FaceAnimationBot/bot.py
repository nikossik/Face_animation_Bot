import telebot
import config
import imageio
import pafy
import sys
import moviepy.editor as mp
import glob, os
import imageio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from skimage.transform import resize
from IPython.display import HTML
sys.path.insert(1, 'first-order-model')
from demo import load_checkpoints
from demo import make_animation
from demo import make_animation
from skimage import img_as_ubyte
from skimage import img_as_ubyte
import warnings

warnings.filterwarnings("ignore")

global streams
streams = 0

def start():
    API = config.API

    bot = telebot.TeleBot(API)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, 'Wassup, bro! Send me your photo with video example and i will animate it. Firstly, send me photo. For more information use /help :)')

    @bot.message_handler(commands=['help'])
    def send_help(message):
        bot.reply_to(message, 'To use this bot, you should crop you photo(only the face). The next step is to upload a video(your video should not be more than 20mb and more than 1 minute). Then wait 2-5 minutes and check the results.')

    @bot.message_handler(content_types=['photo'])
    def photo(message):
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("image.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, 'Your photo was downloaded. And now video :3')

    
    @bot.message_handler(content_types=['text'])
    def video(message):
        global streams
        if message.text[:8] == 'https://':
            v = pafy.new(message.text)
            streams = v.streams
            available_streams = {}
            count = 1
            a = []
            for stream in streams:
                available_streams[count] = stream
                a.append(f"{count} : {stream}")
                count += 1
            for i in a:
                bot.send_message(message.from_user.id, i)
            bot.send_message(message.from_user.id, 'Which resolution you want ?')

        elif message.text == '1' or message.text == '2' or message.text == '3' or message.text == '4' or message.text == '5':
            stream_count = message.text
            streams[int(stream_count) - 1].download()
            bot.send_message(message.from_user.id, "Your video was downloaded. Wait a few minutes and I'll send a final result for you!")
            
            # Preparing video and photo
            try:
                os.remove(os.getcwd() + '\\' + 'video.mp4')
            except:
                pass

            try:
                os.remove(os.getcwd() + '\\' + 'resized.mp4')
            except:
                pass

            try:
                os.remove(os.getcwd() + '\\' + 'generated.mp4')
            except:
                pass

            file_name = ''

            os.chdir(os.getcwd())
            for file in glob.glob("*.mp4"):
                if file == 'resized.mp4':
                    continue
                file_name = file

            os.rename(file_name, 'video.mp4')

            clip = mp.VideoFileClip(os.getcwd() + '\\' + 'video.mp4')
            clip_resized = clip.resize(height=256, width=256)
            clip_resized.write_videofile("resized.mp4")

            # creating
            print('creating')
            source_image = imageio.imread(os.getcwd() + '\\' + 'image.jpg')
            reader = imageio.get_reader(os.getcwd() + '\\' + 'resized.mp4')

            source_image = resize(source_image, (256, 256))[..., :3]
 
            fps = reader.get_meta_data()['fps']
            driving_video = []
            try:
                for im in reader:
                    driving_video.append(im)
            except RuntimeError:
                pass
            reader.close()
            
            driving_video = [resize(frame, (256, 256))[..., :3] for frame in driving_video]

            generator, kp_detector = load_checkpoints(config_path='first-order-model/config/vox-256.yaml', checkpoint_path='vox-cpk.pth.tar')

            predictions = make_animation(source_image, driving_video, generator, kp_detector, relative=True)
            imageio.mimsave('generated.mp4', [img_as_ubyte(frame) for frame in predictions], fps=30)

            video = open('generated.mp4', 'rb')
            bot.send_video(message.chat.id, video)





    print('Bot started!')

    bot.polling()