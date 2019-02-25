import asyncio
import random
import time
from pyppeteer import launch
from chaojiying import Chaojiying_Client
from retrying import retry

async def main(username, pwd):
    url = 'https://weibo.com/'
    browser = await launch({'headless': True,
                            'dumpio': True,
                            })
    page = await browser.newPage()
    page.setDefaultNavigationTimeout(80000)
    await page.setUserAgent('Mozilla / 5.0(WindowsNT10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 69.0.3494.0Safari / 537.36')
    await page.goto(url)
    await page.waitFor('#loginname')
    await page.Jeval('#loginname', "input => input.value = ''")
    time.sleep(2)
    await page.type('#loginname', username, {'delay': input_time_random() - 50})
    time.sleep(2)
    await page.type('.info_list.password div input', pwd, {'delay': input_time_random() - 60})
    time.sleep(1)
    await page.Jeval('.W_btn_a.btn_32px', 'node => node.click()')
    await page.waitFor(1000)
    try:
        Error = await page.Jeval('span[node-type="text"]', 'node => node.textContent')
        '''判断验证码账号密码是否错误'''
    except Exception as e:
        print('验证码和账号密码正确')
        cookies = await get_cookie(page)
        print(cookies)
        await page.close()
        await browser.close()
        return cookies
    else:
        print('出现异常')
        if Error == '用户名或密码错误。查看帮助':
            print('账号user:{0}出错'.format(username))
            '''后续加个从redis中删除'''
            await page.close()
            await browser.close()
        else:
            print(Error + ',破解验证码')
            '''调用破解程序'''
            flag = await Captcha_Crack(page=page)
            if flag == 1:
                cookies = await get_cookie(page)
                print(cookies)
                await page.close()
                await browser.close()
                return cookies
            else:
                await page.close()
                await browser.close()

def retry_if_result_none(result):
    return result is None
@retry(stop_max_attempt_number=3)
async def Captcha_Crack(page=None):
    await asyncio.sleep(2)
    """img_url = await page.Jeval('.code.W_fl img', 'node => node.src')
    获取图片地址，图片地址每次请求的图片都是不一样的
    改用获取元素的截图来处理,找到验证码所在位置
    注意要用无头，界面情况下，验证码截取不到"""
    img = await page.J('.code.W_fl')
    await img.screenshot({'path': './captcha.png'})
    time.sleep(2)
    chaojiying = Chaojiying_Client('？？？', '？？？', '？？？')
    img_url = 'E:/DongXuXiang/PycharmProjects/interview/weibocookie/CookiesPool/weibocaptcha.png'
    im = open(img_url, 'rb').read()
    time.sleep(5)
    '''{'err_no': 0, 'err_str': 'OK', 'pic_id': '8059523242134500006', 'pic_str': 'zq6q4','md5': 'b8602e2653ddd0930ecd772f842a4bf9'}'''
    CAPTCHA = chaojiying.PostPic(im, 1902)['pic_str']
    print(CAPTCHA)
    time.sleep(1)
    await page.type('.input_wrap.W_fl input', CAPTCHA, {'delay': input_time_random() - 60})
    time.sleep(2)
    await page.Jeval('.W_btn_a.btn_32px', 'node => node.click()')
    await page.waitFor(1000)
    '''判断验证码账号密码是否错误'''
    ErrorElement = await page.J('span[node-type="text"]')
    if ErrorElement == None:
        print('验证码和账号密码正确，正常登录')
        return 1
    else:
        print('账号密码或者验证码出错')
        error = await page.Jeval('span[node-type="text"]', 'node => node.textContent')
        if error == '输入的验证码不正确':
            print()
            print('验证码出错，需要重新破解')
            return None
        else:
            print('账号user:{0}出错'.format(username))
            '''删除这条数据'''
            await page.close()
            await browser.close()
            return 2

def input_time_random():
    return random.randint(150, 201)

async def get_cookie(page):
    cookies_list = await page.cookies()
    cookies = ''
    for cookie in cookies_list:
        str_cookie = '{0}={1};'
        str_cookie = str_cookie.format(cookie.get('name'), cookie.get('value'))
        cookies += str_cookie
    return cookies


if __name__ == '__main__':
    username = '？？？？'  # 账号
    pwd = '？？？？'  # 密码
    loop = asyncio.get_event_loop()  # 事件循环，开启个无限循环的程序流程，把一些函数注册到事件循环上。当满足事件发生的时候，调用相应的协程函数。
    result = loop.run_until_complete(main(username, pwd))


'''经过崔大的指点，获取图片验证码地址的方法也是行的通的，同样的网址，虽然图片改变了，但是验证码也是随之改变的，意思是第二次请求时，服务器上的图片也改变了'''
