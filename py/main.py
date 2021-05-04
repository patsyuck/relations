from ring_parser import Parser
from card_processor import Processor
from graph_creator import Graph

def main(start, level, oblast=False): 
    # oblast -- чи треба здійснювати пошук заснованих фірм при спільному П.І.Б. лише в межах однієї області
    # задаємо початкові значення словників та списків
    dict_find = dict() # словник знайдених контрагентів
    dict_firm = dict() # словник назва фірми --> ЄДРПОУ
    list_type = [] # список зв'язків між знайденими контрагентами
    list_head = [] # список голів фірм
    list_temp = [] # список контрагентів на поточному рівні
    list_next = [] # список контрагентів наступного рівня -- кортежі: назва фірми або П.І.Б., регіон (-1 для фірми)
    i = 0 # лічильник (номер рівня відносно початкового об'єкта)
    
    # запускаємо процес (цикл із передумовою, обмеження за кількістю рівнів)
    list_next.append((start, 0)) # 0 -- для вказівки на те, що нам не важливо, з якого регіону дана фірма
    while (i < level) and (len(list_next) > 0):
        list_temp = list_next.copy()
        list_next = []
        for obj in list_temp:
            parser = Parser(obj[0]) # ініціюємо парсер
            resp = parser.getData() # витягуємо з сайту ring.org.ua дані по даному об'єкту
            num = resp[0] # кількість знайдених фірм, пов'язаних із даним об'єктом (ЄДРПОУ, назва фірми, П.І.Б.)
            if num != 0:
                list_obj = resp[1] # список даних по знайдених фірмах
                for n in range(num):
                    edrpou = list_obj[n]['full_edrpou'] # підтягуємо ЄДРПОУ фірми (що робити, якщо його немає?)
                    if edrpou not in set(dict_find.keys()): # якщо ми ще не обробляли інформацію про дану фірму
                        if obj[1] == -1: # додаємо інформацію про засновників фірми та нові об'єкти для пошуку
                            # тут передаємо другим аргументом для перевірки рядок -- назву фірми
                            processor = Processor(list_obj[n], obj[0]) # ініціюємо обробник картки фірми
                        elif len(obj) == 2: # додаємо те ж саме, тільки для фірм із певної області
                            # тут передаємо другим аргументом ціле число -- номер регіону (або 0)
                            processor = Processor(list_obj[n], obj[1]) # ініціюємо обробник картки фірми
                        else: # а тут додаємо третім аргументом ще й адресу засновника
                            processor = Processor(list_obj[n], obj[1], obj[2]) # ініціюємо обробник картки фірми
                        dict_find, dict_firm, list_type, list_head, list_next = processor.addCardData(
                            dict_find, dict_firm, list_type, list_head, list_temp, list_next, oblast) # обробляємо картку
            else:
                if resp[1] == ['error']:
                    print('Error request for object = ', obj[0])
        i += 1
        
    # після формування словників та списків здійснюємо їх обробку, формуємо граф і записуємо його до json-файлу
    graph = Graph(list_type, list_head, dict_find)
    graph.addNodes()
    graph.addLinks()
    graph.createJson()
    
    
# testing
if __name__ == '__main__':
    main('36492837', 2)