import ggg
# ggg = None
btc = ggg.Token['BTC']
# btc.id = 'USD'
btc.papa = '1111'

def save():
    print('actually do not save')

btc.save = save
btc.save()