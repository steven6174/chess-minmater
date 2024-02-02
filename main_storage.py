
from selenium import webdriver
import time


def main():
    driver = webdriver.Chrome()
    url = 'https://www.chess.com'
    driver.get(url)
    time.sleep(5)
    # scriptArray = """localStorage.setItem("key1", 'new item');
    #                  localStorage.setItem("key2", 'second item');
    #                  return Array.apply(0, new Array(localStorage.length)).map(function (o, i) { return localStorage.getItem(localStorage.key(i)); }
    #                 )"""
    scriptArray = """for ( var i = 0, len = localStorage.length; i < len; ++i ) {
                        console.log( localStorage.getItem( localStorage.key( i ) ) );
                     }"""
    scriptArray2 = """return Object.keys(sessionStorage)
                   ;"""
    result = driver.execute_script(scriptArray2)
    print(result)


if __name__ == '__main__':
    main()
