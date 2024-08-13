from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image, ImageDraw
import json
from time import sleep
import threading
import os
import requests
import tkinter as tk
import webbrowser as web

file_path = 'configuration.json'
apiJson = {     #默认公共用户的api，可以自己在https://www.apihz.cn/注册更稳定
    "id" : 88888888,
    "key" : 88888888
}
costant = {
    "region": '*请输入当前的省',
    "city": '*请输入当前的市',
    "address": '(选填)请输入详细位置'
}
warnStart = False
weatherRresh = False
settingOpenBool = False
windowOpenBool = False
iconShow = '晴'

#检测初始化
file_exists = os.path.exists(file_path)
if not file_exists:
    with open(file_path, 'w') as file:
        json.dump({'warnStart': False,
                   'weatherRresh': False,
                   'region': costant['region'],
                   'city': costant['city'],
                   'location': costant['address'],
                   'longitude': 104.07274727406208,
                   'latitude': 30.578993724029967,
                   'earthquick': {}
                   }, file)


with open(file_path, 'r') as file:
    fileText = json.load(file)
    warnStart = fileText['warnStart']
    weatherRresh = fileText['weatherRresh']

#创建窗口
def windowCreat():
    global window,addressRegionI,addressCityI,addressMoreI,locationLongituteI,locationLatitudeI,locationT,warnStartB,weatherRefreshB,fileText,warnStart,weatherRresh
    window = tk.Tk()
    window.title('预警控制台')
    window.geometry(windowPlaceValue())
    addressRegionI = tk.StringVar()
    addressCityI = tk.StringVar()
    addressMoreI = tk.StringVar()
    locationLongituteI = tk.StringVar()
    locationLatitudeI = tk.StringVar()
    locationT = tk.StringVar()
    locationT.set('请分别填入经度和纬度')
    with open(file_path, 'r') as file:
        text = json.load(file)
        addressRegionI.set(text['region'])
        addressCityI.set(text['city'])
        addressMoreI.set(text['location'])
        locationLongituteI.set(text['longitude'])
        locationLatitudeI.set(text['latitude'])
    warnStartB = tk.StringVar()
    weatherRefreshB = tk.StringVar()
    with open(file_path, 'r') as file:
        fileText = json.load(file)
        warnStart = fileText['warnStart']
        weatherRresh = fileText['weatherRresh']
        if fileText['warnStart']:
            warnStartB.set('点击 关闭地震预警')
        else:
            warnStartB.set('点击 启动地震预警')
        if fileText['weatherRresh']:
            weatherRefreshB.set('点击 关闭天气预报')
        else:
            weatherRefreshB.set('点击 启动天气预报')
def windowPlaceValue():
    global window
    windowWidth = 400
    windowHeight = 400
    screenWidth = window.winfo_screenwidth() - 50
    screenHeight = window.winfo_screenheight() - 100
    showX = screenWidth - windowWidth
    showY = screenHeight - windowHeight
    return '{}x{}+{}+{}'.format(windowWidth,windowHeight,showX,showY)
#########################引用###################################
def autoWriteLocation():
    response = getLocationRequest('all',addressMoreI.get())
    if response == False:
        print("状态码出错")
        locationT.set("错误：无法连接至服务器")
        return None
    if not response['code'] == 200:
        print("返回代码：{}\t信息：{}".format(response['code'],response['msg']))
        locationT.set("错误：{}".format(response['msg']))
        return None
    locationLongituteI.set(response['lng'])
    locationLatitudeI.set(response['lat'])
    locationT.set("定位等级：{}".format(response['precise']))
def saveForm():
    with open(file_path, 'r') as file:
        text = json.load(file)
    with open(file_path, 'w') as file:
        if addressRegionI.get() == '':
            addressRegionI.set(costant['region'])
        if addressCityI.get() == '':
            addressCityI.set(costant['city'])
        if addressMoreI.get() == '':
            addressMoreI.set(costant['address'])
        text['region'] = addressRegionI.get()
        text['city'] = addressCityI.get()
        text['location'] = addressMoreI.get()
        text['longitude'] = locationLongituteI.get()
        text['latitude'] = locationLatitudeI.get()
        json.dump(text, file)
    stateRefresh()
def warnStartClick():
    with open(file_path, 'r') as file:
        text = json.load(file)
    with open(file_path, 'w') as file:
        if text['warnStart']:
            warnStartB.set('【已关闭】地震预警')
            text['warnStart'] = False
        else:
            warnStartB.set('【已开启】地震预警')
            text['warnStart'] = True
        json.dump(text, file)
    stateRefresh()
def weatherRefreshtClick():
    with open(file_path, 'r') as file:
        text = json.load(file)
    with open(file_path, 'w') as file:
        if text['weatherRresh']:
            weatherRefreshB.set('【已关闭】天气预报')
            text['weatherRresh'] = False
        else:
            weatherRefreshB.set('【已开启】天气预报')
            text['weatherRresh'] = True
        json.dump(text, file)
    stateRefresh()
def stateRefresh():
    global warnStart
    global weatherRresh
    with open(file_path, 'r') as file:
        text = json.load(file)
        warnStart = text['warnStart']
        weatherRresh = text['weatherRresh']
def getLocationRequest(type,address):
    url = 'https://cn.apihz.cn/api/other/jwbaidu.php?id={}&key={}&address={}'.format(apiJson['id'],apiJson['key'],address)
    response = requests.get(url=url)
    getJson = json.loads(response.text)
    match response.status_code:
        case 200:
            if not getJson['code'] == 200:
                return getJson
            match type:
                case 'longitude':
                    return getJson['lng']
                case 'latitude':
                    return getJson['lat']
                case 'class':
                    return getJson['precise']
                case _:
                    return getJson
        case _:
            return False
############################################################

#布置组件
def windowMoudulePlace():
    title = tk.Label(window, text='天气和地震预警警报启动器', width=50, height=2)
    title.pack()
    warnStartButton = tk.Button(window, text='启动地震预警', width=15, height=1, command=warnStartClick,
                                textvariable=warnStartB)
    warnStartButton.pack()
    weatherRefreshButton = tk.Button(window, text='启动天气预报', width=15, height=1, command=weatherRefreshtClick,
                                     textvariable=weatherRefreshB)
    weatherRefreshButton.pack()
    #输入地址
    addressText = tk.Label(window, text='请输入城市或地区', width=70, height=2)
    addressText.pack(side='top')
    addressRegionInput = tk.Entry(window, textvariable=addressRegionI)
    addressRegionInput.pack(side='top')
    addressRegionInput.bind('<FocusIn>',addressRegionIClick)
    addressRegionInput.bind('<FocusOut>',addressRegionIClick)
    addressCityInput = tk.Entry(window, textvariable=addressCityI)
    addressCityInput.pack(side='top')
    addressCityInput.bind('<FocusIn>', addressCityIClick)
    addressCityInput.bind('<FocusOut>', addressCityIClick)
    addressInput = tk.Entry(window, textvariable=addressMoreI)
    addressInput.pack(side='top')
    addressInput.bind('<FocusIn>', addressMoreIClick)
    addressInput.bind('<FocusOut>', addressMoreIClick)
    getLocationButton = tk.Button(window, text='自动填写经纬度', width=15, height=1,
                                  command=lambda: autoWriteLocation())
    getLocationButton.pack(side='top')
    LocationText = tk.Label(window, text='请分别填入经度和纬度', width=50, height=2, textvariable=locationT)
    LocationText.pack(side='top')
    LocationLongituteInput = tk.Entry(window, textvariable=locationLongituteI)
    LocationLongituteInput.pack(side='top')
    LocationLatitudeInput = tk.Entry(window, textvariable=locationLatitudeI)
    LocationLatitudeInput.pack(side='top')
    #功能按钮
    saveButton = tk.Button(window, text='保存', width=15, height=1, command=saveForm)
    saveButton.pack(side='top')
    informationButton = tk.Button(window, text='信息', width=15, height=1, command=openInformation)
    informationButton.pack(side='left')
    exitButton = tk.Button(window, text='退出', width=15, height=1, command=closeSetting)
    exitButton.pack(side='right')
    '''旧布局
    title = tk.Label(window, text='天气和地震预警警报启动器',width=50,height=2)
    title.pack()
    warnStartButton = tk.Button(window, text='启动地震预警',width=15,height=1,command=warnStartClick,textvariable=warnStartB)
    warnStartButton.pack()
    weatherRefreshButton = tk.Button(window, text='启动天气预报',width=15,height=1,command=weatherRefreshtClick,textvariable=weatherRefreshB)
    weatherRefreshButton.pack()
    addressText = tk.Label(window, text='请输入城市或地区',width=70,height=2)
    addressText.pack(side='top')
    addressInput = tk.Entry(window,textvariable=addressI)
    addressInput.pack(side='top')
    getLocationButton = tk.Button(window, text='自动填写经纬度',width=15,height=1,command=lambda : autoWriteLocation())
    getLocationButton.pack(side='top')
    LocationText = tk.Label(window, text='请分别填入经度和纬度',width=50,height=2,textvariable=locationT)
    LocationText.pack(side='top')
    LocationLongituteInput = tk.Entry(window,textvariable=locationLongituteI)
    LocationLongituteInput.pack(side='top')
    LocationLatitudeInput = tk.Entry(window,textvariable=locationLatitudeI)
    LocationLatitudeInput.pack(side='top')
    saveButton = tk.Button(window, text='保存',width=15,height=1,command=saveForm)
    saveButton.pack(side='top')
    informationButton = tk.Button(window, text='信息',width=15,height=1)
    informationButton.pack(side='left')
    exitButton = tk.Button(window, text='退出', width=15, height=1, command=closeSetting)
    exitButton.pack(side='right')
'''
def openInformation():
    web.open('https://github.com/Ordinary-awa/Nature-Disaster-warning/tree/main')
def iconReady(name):
    match name:
        case 'icon':
            return Image.open('icon.png')
        case '晴':
            return Image.open('icon/sun.png')
        case '小雨':
            return Image.open('icon/sprinkle.png')
        case '中雨':
            return Image.open('icon/rain.png')
        case '阵雨':
            return Image.open('icon/shower.png')
        case '多云':
            return Image.open('icon/cloudySun.png')
        case '阴':
            return Image.open('icon/cloudy.png')
        case '雷阵雨':
            return Image.open('icon/thunderRain.png')
        case _:
            return Image.open('icon/other.png')
def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)
    return image
# 更新图标
def iconUpdate(iconImg, iconGet):
    iconGet.icon = iconImg
    iconGet._update_icon()
def warnRequest():
    url = 'https://api.wolfx.jp/sc_eew.json'
    response = requests.get(url=url)
    match response.status_code:
        case 200:
            return response.json()
        case _:
            return False
def weatherRequest():
    with open(file_path, 'r') as file:
        fileJson = json.load(file)
        region = fileJson['region']
        city = fileJson['city']
    url = 'https://cn.apihz.cn/api/tianqi/tqyb.php'
    requestsJson = apiJson
    requestsJson['sheng'] = region
    requestsJson['place'] = city
    response = requests.get(url=url, params=requestsJson)
    if response.status_code != 200:
        return False
    responseJson = json.loads(response.text)
    if responseJson['code'] != 200:
        return False
    return responseJson
def weatherThread(iconGet):
    while 1:
        if weatherRresh == False:
            sleep(0.1)
            continue
        weatherJson = weatherRequest()
        if weatherJson == False:
            sleep(5)
            continue
        iconUpdate(iconReady(weatherJson['weather1']), iconGet)
        sleep(5)
def openSetting():
    global windowOpenBool
    if not windowOpenBool:
        windowOpenBool = True
        windowCreat()
        windowMoudulePlace()
        window.protocol("WM_DELETE_WINDOW", closeSetting)
        window.mainloop()
        #window.focus_force()
    else:
        window.deiconify()
        window.focus_force()
        print('already open window')

def closeSetting():
    global windowOpenBool
    windowOpenBool = False
    window.destroy()
def warnThread():
    while 1:
        if warnStart == False:
            sleep(0.1)
            continue
        with open(file_path, 'r') as file:
            text = json.load(file)
        response = warnRequest()
        if not response == False:
            if not text['earthquick'] == response:
                noticCreat("【{}】发生地震●{}级地震".format(response['HypoCenter'], response['Magunitude']),"{}\n经度:{}\n纬度:{}".format(response['ReportTime'], response['Latitude'], response['Longitude']))
                text['earthquick'] = response
                with open(file_path, 'w') as file:
                    json.dump(text, file)
                #print(response)
            sleep(5 - 0.2)
        sleep(0.2)

def warnStart_clicked(icon, item):
    global warnStart
    warnStart = not item.checked
    with open(file_path, 'r') as file:
        text = json.load(file)
    with open(file_path, 'w') as file:
        if text['warnStart']:
            text['warnStart'] = False
        else:
            text['warnStart'] = True
        json.dump(text, file)
def weatherRresh_clicked(icon, item):
    global weatherRresh
    weatherRresh = not item.checked
    with open(file_path, 'r') as file:
        text = json.load(file)
    with open(file_path, 'w') as file:
        if text['weatherRresh']:
            text['weatherRresh'] = False
        else:
            text['weatherRresh'] = True
        json.dump(text, file)
def iconClick():
    print('ok')
def inputFocus(tab,type):
    #print('click')
    global addressMoreI, addressRegionI, addressCityI
    match tab:
        case 'address':
            if type == 'in':
                if addressMoreI.get() == costant['address']:
                    if addressRegionI.get() != costant['region'] and addressCityI.get() != costant['city']:
                        addressMoreI.set('{}省{}市'.format(addressRegionI.get(), addressCityI.get()))
                    else:
                        addressMoreI.set('')
            else:
                if addressMoreI.get() == '':
                    addressMoreI.set(costant['address'])
            return 0
        case 'region':
            if type == 'in':
                if addressRegionI.get() == costant['region']:
                    addressRegionI.set('')
            else:
                if addressRegionI.get() == '':
                    addressRegionI.set(costant['region'])
            return 0
        case 'city':
            if type == 'in':
                if addressCityI.get() == costant['city']:
                    addressCityI.set('')
            else:
                if addressCityI.get() == '':
                    addressCityI.set(costant['city'])
def addressMoreIClick(event):
    if event.type == tk.EventType.FocusIn:
        inputFocus('address', 'in')
    else:
        inputFocus('address', 'out')
def addressRegionIClick(event):
    if event.type == tk.EventType.FocusIn:
        inputFocus('region', 'in')
    else:
        inputFocus('region', 'out')
def addressCityIClick(event):
    if event.type == tk.EventType.FocusIn:
        inputFocus('city', 'in')
    else:
        inputFocus('city', 'out')
def noticCreat(title,msg):
    icon.notify(msg,title)
#启动预警线程
warnThread = threading.Thread(target=warnThread, name='warnThread')
warnThread.daemon = True
warnThread.start()

#iconChangeThread = threading.Thread(target=iconChangeThread, name='weatherThread', args=(icon, ))
#iconChangeThread.daemon = True
#iconChangeThread.start()

menu = menu(
    item(
        '启动地震预警',
        warnStart_clicked,
        checked=lambda item: warnStart),
    item(
        '启动天气预报',
        weatherRresh_clicked,
        checked=lambda item: weatherRresh),
    item(
        '配置',
        openSetting,
        checked=lambda item: settingOpenBool)
)
#icon = icon('command', create_image(64, 64, 'black', 'white'), menu=menu).run()
icon = icon('command', icon=iconReady('雷阵雨'), menu=menu)

#启动预警线程
weatherThread = threading.Thread(target=weatherThread, name='weatherThread', args=(icon, ))
weatherThread.daemon = True
weatherThread.start()

icon.run()