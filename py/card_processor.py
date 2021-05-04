def reg(loc): # визначаємо номер регіону за повною адресою фірми
    if loc.find('київська обл') != -1:
        return 1
    elif loc.find('дніпропетровська обл') != -1:
        return 2
    elif loc.find('донецька обл') != -1:
        return 3
    elif loc.find('харківська обл') != -1:
        return 4
    elif loc.find('одеська обл') != -1:
        return 5
    elif loc.find('львівська обл') != -1:
        return 6
    elif loc.find('миколаївська обл') != -1:
        return 7
    elif loc.find('запорізька обл') != -1:
        return 8
    elif loc.find('хмельницька обл') != -1:
        return 9
    elif loc.find('полтавська обл') != -1:
        return 10
    elif loc.find('луганська обл') != -1:
        return 11
    elif loc.find('вінницька обл') != -1:
        return 12
    elif loc.find('житомирська обл') != -1:
        return 13
    elif loc.find('черкаська обл') != -1:
        return 14
    elif loc.find('херсонська обл') != -1:
        return 15
    elif loc.find('кіровоградська обл') != -1:
        return 16
    elif loc.find('сумська обл') != -1:
        return 17
    elif loc.find('івано-франківська обл') != -1:
        return 18
    elif loc.find('тернопільська обл') != -1:
        return 19
    elif loc.find('чернігівська обл') != -1:
        return 20
    elif loc.find('волинська обл') != -1:
        return 21
    elif loc.find('рівненська обл') != -1:
        return 22
    elif loc.find('закарпатська обл') != -1:
        return 23
    elif loc.find('чернівецька обл') != -1:
        return 24
    elif (loc.find('республіка крим') != -1) or (loc.find(' арк ') != -1) or (loc.find(' арк,') != -1):
        return 25
    elif (loc.find(' київ ') != -1) or (loc.find(' київ,') != -1):
        return 1
    elif (loc.find(' севастополь ') != -1) or (loc.find(' севастополь,') != -1):
        return 25
    else:
        return 0 # адреса не підходить під жодну з наших масок, тому на неї далі не звертатимемо уваги
    
def find_addr(addresses_cut, records_cut, person): # знаходимо список адрес бенефіціара
    list_addr = []
    for address in addresses_cut:
        for record in records_cut:
            if record.find(person.replace(' ', '').replace('-', '')) != -1 and record.find(address) != -1:
                list_addr.append(address)
    return list(set(list_addr)) # видаляємо дублі, які могли утворитися протягом обробки

class Processor():
    def __init__(self, firm, info=0, list_addr=None):
        self.firm = firm # словник усіх даних із картки фірми, знайденої за певним ЗАПИТОМ 
        self.info = info # назва фірми в ЗАПИТІ (str) або номер області, у якій вона знаходиться (int)
        self.list_addr = list_addr # адреса фізособи, вказаної в ЗАПИТІ (засновника знайденої фірми)
        
    def addCardData(self, dict_find, dict_firm, list_type, list_head, list_temp, list_next, oblast): #обробка картки даних фірми
        next_step = False # за замовчуванням дані про цю фірму не додаємо
        # додаємо фірму до словника знайдених контрагентів
        edrpou = self.firm['full_edrpou']
        name = self.firm['latest_record']['name'].lower().replace('  ', ' ')
        short_name = self.firm['latest_record']['short_name'].lower().replace('  ', ' ')
        status = self.firm['latest_record']['status'].lower().replace('  ', ' ') 
        dict_find[edrpou] = (name, short_name, status) # додаємо інформацію про фірму: назва, повна назва, статус
        dict_firm[name] = edrpou # якщо будуть дублі за повною назвою фірми, то запишеться лише останній ЄДРПОУ!
        if status != 'припинено': # дані про фірми зі статусом 'припинено' не додаємо
            try: # якщо фірма функціонує, виконуємо три перевірки
                records = self.firm['raw_records'] # тут міститься інформація про частки участі засновників (у грн.)
                location = self.firm['latest_record']['location'].lower().replace('  ', ' ')
                region = reg(location) # знаходимо регіон, де розташована фірма
                if type(self.info) == str: # перевірка № 1 -- за співпадінням назв фірм
                    if self.info in [record.split(',')[0].lower().replace('  ', ' ') for record in records]: 
                        next_step = True
                else: # перевірка № 2 -- за співпадінням адрес при спільному П.І.Б. бенефіціарів
                    if self.list_addr != None and len(list([person[0] for person in self.firm['raw_persons'] 
                                                       if person[1] == 'Бенефіціарний власник'])) > 0: # є адреса і бенефіціари
                        for addr in self.list_addr: # перебираємо список адрес (можуть відрізнятися незначним чином)
                            if not next_step:
                                for record in records: # для кожного запису про частку участі засновника
                                    if record.lower().replace(' ', '').replace('-', '').find(addr) != -1: # адреси співпали
                                        next_step = True
                                        break
                    else: # перевірка № 3 -- за співпадінням регіонів фірм при спільному П.І.Б. засновників
                        if (not oblast) or (self.info == 0) or (self.info == region): # фірми з іншої області не розглядаємо
                            next_step = True
            except:
                print('Warning: Detail information about firm {0} is absend, status = {1}.'.format(edrpou, status))
        if next_step:
            # якщо ця фірма ще не включена до списку пошуку (поточного або наступного)
            if (name not in [x[0] for x in list_temp]) and (name not in [x[0] for x in list_next]): 
                list_next.append((name, -1)) # на наступному рівні шукатимемо засновані цією фірмою фірми
                # додаємо інформацію про засновників фірми
                list_all = list(set([person[0].lower().replace('  ', ' ') for person in self.firm['raw_persons']])) # фізособи
                list_master = list(set([person[0].lower().replace('  ', ' ') for person in self.firm['raw_persons'] 
                                        if person[1] == 'Голова'])) # список голів фірми (голова тільки один?)
                list_founder = list(set([person[0].lower().replace('  ', ' ') for person in self.firm['raw_persons'] 
                                         if person[1] == 'Засновник'])) # список засновників (вносили кошти)
                list_benef = list(set([person[0].lower().replace('  ', ' ') for person in self.firm['raw_persons'] 
                                       if person[1] == 'Бенефіціарний власник'])) # список бенефіціарів
                if len(list_benef) > 0: # адреси засновників вказуються зазвичай тільки для бенефіціарів
                    addresses = self.firm['addresses']
                    addresses = [address.lower().replace(' ', '').replace('-', '') for address in addresses if 
                                 len(address.split(',')) > 1] # вилучаємо всі пробіли й дефіси та адреси з одного слова
                    records_new = [record.lower().replace(' ', '').replace('-', '') for record in records]
                    addresses_cut = []
                    for address in addresses: # лишаємо ті адреси, які є в записах про частку участі засновників
                        if sum([False if record.find(address) == -1 else True for record in records_new]) > 0:
                            addresses_cut.append(address)
                    addresses_cut = list(set(addresses_cut)) # видаляємо дублі, які могли утворитися протягом обробки
                    records_cut = []
                    for record in records_new: # лишаємо тільки ті записи про частку участі, у яких є адреси
                        if sum([False if record.find(address) == -1 else True for address in addresses_cut]) > 0:
                            records_cut.append(record)
                for person in list_all:
                    if person not in set(dict_find.keys()): # якщо ця особа ще не засвітилася раніше
                        dict_find[person] = () # додаємо її П.І.Б. до словника знайдених контрагентів
                        # і якщо ця особа не включена до списку пошуку (поточного або наступного)
                        if (person not in [x[0] for x in list_temp]) and (person not in [x[0] for x in list_next]): 
                            if person not in list_benef: # список бенефіціарів може бути порожнім
                                list_next.append((person, region)) # на наступному рівні шукатимемо засновані цією особою фірми
                            else: # якщо ми маємо справу з бенефіціаром, додаємо також його адресу
                                list_next.append((person, region, find_addr(addresses_cut, records_cut, person)))
                for head in list_master: # додаємо інформацію про голів фірм, вони можуть не бути засновниками
                    list_head.append([head, edrpou])
                part = dict()
                for record in records: # відбираємо інформацію тільки про ненульові внески
                    if (record.find(' грн.') != -1) and (record.find(' 0.00 грн.') == -1) and (record.find(' 0,00 грн.') == -1):
                        part[record.split(',')[0].lower().replace('  ', ' ')] = float(
                            record.split('-')[-1].split('грн')[0].strip().replace(',', '.')) # засновник і його внесок
                if len(part) > 0: # якщо є інформація хоча б про один ненульовий внесок до статутного капіталу
                    capital = sum(part.values())
                    for founder in list(part):
                        capital_part = part[founder]/capital if capital != 0 else 0
                        if founder in list_all: # засновник -- фізична особа
                            if founder in list_benef: # засновник є бенефіціаром
                                list_type.append([founder, edrpou, capital_part, 1])
                            else: # засновник не є бенефіціаром
                                list_type.append([founder, edrpou, capital_part, 0])
                        else: # засновник -- юридична особа (фірма)
                            if founder in list(dict_firm): # і для цієї фірми ми вже маємо інформації про її ЄДРПОУ
                                list_type.append([dict_firm[founder], edrpou, capital_part, 0])
                            else: # інакше записуємо просто назву фірми
                                list_type.append([founder, edrpou, capital_part, 0])
                # якщо бенефіціар не вносив кошти до статутного капіталу, додаємо інформацію про нього
                zero_benef = list(set(list_benef) - set(list(part)))
                if len(zero_benef) > 0:
                    for founder in zero_benef:
                        list_type.append([founder, edrpou, 0, 1])
                # якщо засновник не є бенефіціаром і не вносив кошти до статутного капіталу, додаємо інформацію про нього
                zero_founder = list(set(list_founder) - set(list_benef) - set(list(part)))
                if len(zero_founder) > 0:
                    for founder in zero_founder:
                        list_type.append([founder, edrpou, 0, 0])
        return dict_find, dict_firm, list_type, list_head, list_next
    
    
# testing
if __name__ == '__main__':
    from ring_parser import Parser # for testing only 
    start = '36492837' # "Бон Буассон"
    parser = Parser(start)
    processor = Processor(parser.getData()[1][0]) # для прикладу беремо першу зі списку знайдених фірм
    # на вхід подаємо dict_find, dict_firm, list_type, list_head, list_temp, list_next
    result = processor.addCardData(dict(), dict(), [], [], [(start, 0)], [], False)
    print('Dict_find: ', result[0])
    print('Dict_firm: ', result[1])
    print('List_type: ', result[2])
    print('List_head: ', result[3])
    print('List_next: ', result[4])