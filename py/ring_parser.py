import requests

class Parser():
    def __init__(self, obj):
        self.obj = obj
        
    def getData(self):
        url = 'https://ring.org.ua/search?q=' + self.obj + '&datasources=edrdr&format=json'
        response = requests.get(url) # надсилаємо get-запит на сервер ring.org.ua
        #response = requests.get(url, verify=False) # якщо матюкається на SSL-сертифікат
        if response.status_code == 200:
            dict_resp = response.json()
            items = dict_resp['search_results']['paginator']['count'] # кількість пов'язаних фірм
            pages = dict_resp['search_results']['paginator']['num_pages'] # кількість сторінок у результаті
            result = dict_resp['search_results']['object_list'] # формуємо список даних про фірми
            if pages > 1: # якщо результати запиту не вмістилися на одну сторінку (не віддасть більше 1000 сторінок?)
                for i in range(2, pages+1): # повторюємо запит для всіх сторінок, починаючи з другої
                    url = 'https://ring.org.ua/search?q=' + self.obj + '&datasources=edrdr&format=json&page=' + str(i)
                    response = requests.get(url) # надсилаємо get-запит на сервер ring.org.ua
                    #response = requests.get(url, verify=False) # якщо матюкається на SSL-сертифікат
                    if response.status_code == 200:
                        dict_resp = response.json()
                        result += dict_resp['search_results']['object_list'] # поповнюємо список даних про фірми
                    else:
                        print('Error: requested url ' + url + ' is not available!')
            if len(result) == items: # перевіряємо, чи нам вдалося отримати інформацію про всі пов'язані фірми
                return (items, result)
            else:
                print('Warning: parsed url ' + url.split('&page=')[0] + ' is not full!')
                return (len(result), result)
        else:
            print('Error: requested url ' + url + ' is not available!')
            return (0, ['error'])
        

# testing
if __name__ == '__main__':
    parser = Parser('41133715') # "Бон Буассон"
    #parser = Parser('31382665') # "Сигарний Дім 'Фортуна'"
    print(parser.getData())