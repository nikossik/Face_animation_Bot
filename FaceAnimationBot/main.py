import os
if not os.path.exists('model-detection'):
    os.system('pip install -r requirements.txt')
    os.mkdir('model-detection')

if not os.path.exists('first-order-model'):
    print('Preparing files:')
    os.system('git clone https://github.com/AliaksandrSiarohin/first-order-model')

config = open('config.py').read()

if config == '':
    API = input('Please, write your API: \n> ')
    open('config.py', 'w').write('API = "' + API + '"')
    print('Done!')
else:
    import bot
    bot.start()