"""
Yandex Transport Webdriver API. Continuous Monitoring tests.

NOTE: These are designed to run indefinitely and check current YandexTransportAPI status.
      Tests are working with Live Data, with several random delays between them.
      They take a lot of time as a result.

NOTE: Tests require running YandexTransportProxy server

UPD:  These are kinda questionable, they made sence in the era of YandexTransportMonitor,
      but now they kinda... don't.
"""

import pytest
import random
import time
import json
from yandex_transport_webdriver_api import YandexTransportProxy

# Working server settings
SERVER_HOST = '172.17.0.1'
SERVER_PORT = 25555

# Station URLs used in tests.
# Template: {"": ""}
mini_set = \
    {"Москва/Метро Сокол": "https://yandex.ru/maps/213/moscow/?ll=37.511152%2C55.804204&masstransit%5BstopId%5D=stop__9647423&mode=stop&z=17",
     "Москва/Улица Станиславского": "https://yandex.ru/maps/213/moscow/?ll=37.664542%2C55.744704&masstransit%5BstopId%5D=stop__9647379&mode=stop&z=17"
    }

# These are working stations, they should return getStopInfo and getLayerRegions.
station_urls = \
    {"Москва/Метро Сокол": "https://yandex.ru/maps/213/moscow/?ll=37.511152%2C55.804204&masstransit%5BstopId%5D=stop__9647423&mode=stop&z=17",
     "Москва/Улица Станиславского": "https://yandex.ru/maps/213/moscow/?ll=37.664542%2C55.744704&masstransit%5BstopId%5D=stop__9647379&mode=stop&z=17",
     "Москва/Платформа Тестовская": "https://yandex.ru/maps/213/moscow/?ll=37.535037%2C55.752682&masstransit%5BstopId%5D=stop__9649559&mode=stop&z=17",
     "Москва/Тишинская площадь": "https://yandex.ru/maps/213/moscow/?ll=37.587580%2C55.770117&masstransit%5BstopId%5D=stop__9648355&mode=stop&z=17",
     "Москва/Метро Китай-город": "https://yandex.ru/maps/213/moscow/?ll=37.634151%2C55.754175&masstransit%5BstopId%5D=stop__10187976&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D37.633884%252C55.754364%26spn%3D0.001000%252C0.001000%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%259C%25D0%25BE%25D1%2581%25D0%25BA%25D0%25B2%25D0%25B0%252C%2520%25D0%25A2%25D0%25B0%25D0%25B3%25D0%25B0%25D0%25BD%25D1%2581%25D0%25BA%25D0%25BE-%25D0%259A%25D1%2580%25D0%25B0%25D1%2581%25D0%25BD%25D0%25BE%25D0%25BF%25D1%2580%25D0%25B5%25D1%2581%25D0%25BD%25D0%25B5%25D0%25BD%25D1%2581%25D0%25BA%25D0%25B0%25D1%258F%2520%25D0%25BB%25D0%25B8%25D0%25BD%25D0%25B8%25D1%258F%252C%2520%25D0%25BC%25D0%25B5%25D1%2582%25D1%2580%25D0%25BE%2520%25D0%259A%25D0%25B8%25D1%2582%25D0%25B0%25D0%25B9-%25D0%25B3%25D0%25BE%25D1%2580%25D0%25BE%25D0%25B4%2520&z=19",
     "Петропавловск-Камчатский/Советская улица": "https://yandex.ru/maps/78/petropavlovsk/?ll=158.650965%2C53.015840&masstransit%5BstopId%5D=1543338149&mode=stop&z=17",
     "Магадан/Телевышка": "https://yandex.ru/maps/79/magadan/?ll=150.800171%2C59.560040&masstransit%5BstopId%5D=1941449091&mode=stop&z=16",
     "Владивосток/Центр": "https://yandex.ru/maps/75/vladivostok/?ll=131.886671%2C43.115497&masstransit%5BstopId%5D=stop__9980150&mode=stop&sll=37.540794%2C55.925019&sspn=0.145741%2C0.050022&z=17",
     "Якутск/Крестьянский рынок": "https://yandex.ru/maps/74/yakutsk/?ll=129.728396%2C62.035988&masstransit%5BstopId%5D=2040377980&mode=stop&z=16",
     "Иркутск/Железнодорожный вокзал": "https://yandex.ru/maps/63/irkutsk/?ll=104.259650%2C52.282821&masstransit%5BstopId%5D=stop__9795272&mode=stop&sctx=ZAAAAAgBEAAaKAoSCWnCm9o%2BElpAEVnd6jlpJUpAEhIJE7%2Ft%2F5%2Bnwj8RVFOjSVz4qz8iBAABAgQoCjAAOKqiz7joupHNA0DVzQZIAFXNzMw%2BWABqAnJ1cACdAc3MzD2gAQCoAQA%3D&sll=104.259650%2C52.282821&sspn=0.004554%2C0.001708&text=%D0%98%D1%80%D0%BA%D1%83%D1%82%D1%81%D0%BA%20cnfywbz&z=18",
     "Красноярск/Железнодорожный вокзал": "https://yandex.ru/maps/62/krasnoyarsk/?ll=92.832626%2C56.006039&masstransit%5BstopId%5D=stop__9901229&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D92.852577%252C56.010567%26spn%3D0.541885%252C0.222061%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%259A%25D1%2580%25D0%25B0%25D1%2581%25D0%25BD%25D0%25BE%25D1%258F%25D1%2580%25D1%2581%25D0%25BA%2520&z=17",
     "Омск/Железнодорожный вокзал": "https://yandex.ru/maps/66/omsk/?ll=73.386035%2C54.939776&masstransit%5BstopId%5D=stop__9727412&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D73.368217%252C54.989346%26spn%3D0.563622%252C0.594631%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%259E%25D0%25BC%25D1%2581%25D0%25BA%2520&z=17",
     "Екатеринбург/1-й километр": "https://yandex.ru/maps/54/yekaterinburg/?ll=60.611944%2C56.863058&masstransit%5BstopId%5D=stop__9810370&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D60.597473%252C56.838013%26spn%3D0.679832%252C0.389126%26&z=18",
     "Самара/Некрасовская улица": "https://yandex.ru/maps/51/samara/?ll=50.102397%2C53.189701&masstransit%5BstopId%5D=stop__10097748&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D50.101788%252C53.195541%26spn%3D0.659111%252C0.459122%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%25A1%25D0%25B0%25D0%25BC%25D0%25B0%25D1%2580%25D0%25B0%2520&z=17",
     "Санкт-Петербург/Станция метро Невский проспект": "https://yandex.ru/maps/2/saint-petersburg/?ll=30.326364%2C59.935241&masstransit%5BstopId%5D=stop__10075220&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D30.315639%252C59.938953%26spn%3D1.334415%252C0.611099%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%25A1%25D0%25B0%25D0%25BD%25D0%25BA%25D1%2582-%25D0%259F%25D0%25B5%25D1%2582%25D0%25B5%25D1%2580%25D0%25B1%25D1%2583%25D1%2580%25D0%25B3%2520&z=18",
     "Калининград/Гостиница Калининград": "https://yandex.ru/maps/22/kaliningrad/?ll=20.509223%2C54.712040&masstransit%5BstopId%5D=3313917805&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D20.507313%252C54.707394%26spn%3D0.359865%252C0.148655%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%259A%25D0%25B0%25D0%25BB%25D0%25B8%25D0%25BD%25D0%25B8%25D0%25BD%25D0%25B3%25D1%2580%25D0%25B0%25D0%25B4%2520&z=18",
     "Москва/Метро Марьино (южная)": "https://yandex.ru/maps/213/moscow/?ll=37.744035%2C55.649321&masstransit%5BstopId%5D=stop__9647488&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D37.743473%252C55.650028%26spn%3D0.001000%252C0.001000%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%259C%25D0%25BE%25D1%2581%25D0%25BA%25D0%25B2%25D0%25B0%252C%2520%25D0%25BC%25D0%25B5%25D1%2582%25D1%2580%25D0%25BE%2520%25D0%259C%25D0%25B0%25D1%2580%25D1%258C%25D0%25B8%25D0%25BD%25D0%25BE%2520&z=17"
}

# This is an empty station, it should return nothing.
# There was a small period when it returned getLayerRegions.
station_empty = {"Якутск/Школа №7": "https://yandex.ru/maps/74/yakutsk/?ll=129.725800%2C62.037399&mode=poi&poi%5Bpoint%5D=129.728085%2C62.036624&poi%5Buri%5D=ymapsbm1%3A%2F%2Forg%3Foid%3D179807288972&sll=37.586616%2C55.802258&sspn=0.036435%2C0.012545&text=%D1%8F%D0%BA%D1%83%D1%82%D1%81%D0%BA&z=16"}

# These are working routes, they should return getRouteInfo, getVehiclesInfo, getVehiclesInfoWithRegion, getLayerRegions
routes_urls = {"Москва/Автобус 105": "https://yandex.ru/maps/213/moscow/?ll=37.517402%2C55.804455&masstransit%5BlineId%5D=213_105_bus_mosgortrans&masstransit%5BstopId%5D=stop__9647423&masstransit%5BthreadId%5D=213A_105_bus_mosgortrans&mode=stop&z=14",
               "Москва/Троллейбус 53": "https://yandex.ru/maps/213/moscow/?ll=37.746753%2C55.737977&masstransit%5BlineId%5D=2036926340&masstransit%5BstopId%5D=stop__9647379&masstransit%5BthreadId%5D=213A_53_trolleybus_mosgortrans&mode=stop&z=13",
               "Москва/Автобус 12": "https://yandex.ru/maps/213/moscow/?ll=37.546941%2C55.755232&masstransit%5BlineId%5D=213_12_bus_mosgortrans&masstransit%5BstopId%5D=stop__9649559&masstransit%5BthreadId%5D=213A_12_bus_mosgortrans&mode=stop&z=15",
               "Москва/Троллейбус 54": "https://yandex.ru/maps/213/moscow/?ll=37.587580%2C55.770117&masstransit%5BlineId%5D=213_54_trolleybus_mosgortrans&masstransit%5BstopId%5D=stop__9648355&masstransit%5BthreadId%5D=2036927249&mode=stop&z=17",
               "Москва/Автобус Н1": "https://yandex.ru/maps/213/moscow/?ll=37.634151%2C55.754175&masstransit%5BlineId%5D=N1_bus_default&masstransit%5BstopId%5D=stop__10187976&masstransit%5BthreadId%5D=2036926069&mode=stop&z=19",
               "Петропавловск-Камчатский/Автобус 1": "https://yandex.ru/maps/78/petropavlovsk/?ll=158.650258%2C53.016359&masstransit%5BlineId%5D=1704841626&masstransit%5BthreadId%5D=2163257102&mode=stop&z=17",
               "Магадан/Автобус 1": "https://yandex.ru/maps/79/magadan/?ll=150.800171%2C59.560040&masstransit%5BlineId%5D=1704917872&masstransit%5BthreadId%5D=1952775971&mode=stop&z=16",
               "Владивосток/Маршрутка 24": "https://yandex.ru/maps/75/vladivostok/?ll=131.886671%2C43.115497&masstransit%5BlineId%5D=2468209792&masstransit%5BthreadId%5D=2468209966&mode=stop&z=17",
               "Якутск/Автобус 104": "https://yandex.ru/maps/74/yakutsk/?ll=129.723504%2C62.037152&masstransit%5BlineId%5D=1704844454&masstransit%5BthreadId%5D=3442738945&mode=stop&z=16",
               "Иркутск/Трамвай 4А": "https://yandex.ru/maps/63/irkutsk/?ll=104.259354%2C52.282396&masstransit%5BlineId%5D=1962955244&masstransit%5BthreadId%5D=1962955369&mode=stop&z=18",
               "Красноярск/Маршрутка 130": "https://yandex.ru/maps/62/krasnoyarsk/?ll=92.831247%2C56.005319&masstransit%5BlineId%5D=2611970500&masstransit%5BthreadId%5D=2611970606&mode=stop&z=17",
               "Омск/Троллейбус 12": "https://yandex.ru/maps/66/omsk/?ll=73.386035%2C54.939776&masstransit%5BlineId%5D=2012848234&masstransit%5BthreadId%5D=2012848632&mode=stop&z=17",
               "Екатеринбург/Трамвай 5": "https://yandex.ru/maps/54/yekaterinburg/?ll=60.614978%2C56.863073&masstransit%5BlineId%5D=2107048890&masstransit%5BthreadId%5D=2107049173&mode=stop&z=16",
               "Самара/Трамвай 5": "https://yandex.ru/maps/51/samara/?ll=50.099858%2C53.188705&masstransit%5BlineId%5D=2193179444&masstransit%5BthreadId%5D=2193179903&mode=stop&z=17",
               "Санкт-Петербург/Троллейбус 22": "https://yandex.ru/maps/2/saint-petersburg/?ll=30.324825%2C59.935390&masstransit%5BlineId%5D=22_trolleybus_discus&masstransit%5BthreadId%5D=22B_trolleybus_discus&mode=stop&z=18",
               "Калининград/Автобус 593": "https://yandex.ru/maps/22/kaliningrad/?ll=20.508255%2C54.712590&masstransit%5BlineId%5D=3181656187&masstransit%5BthreadId%5D=3181656277&mode=stop&z=18",
               "Москва/Маршрутка 937к": "https://yandex.ru/maps/213/moscow/?ll=37.465495%2C55.878790&masstransit%5BlineId%5D=937_minibus_default&masstransit%5BthreadId%5D=937A_minibus_default&mode=stop&z=13",
               "Москва/Трамвай А": "https://yandex.ru/maps/213/moscow/?ll=37.638675%2C55.764634&masstransit%5BlineId%5D=213_A_tramway_mosgortrans&masstransit%5BthreadId%5D=2036927519&mode=stop&z=18"
              }

# Accumulated results. Good idea is to actually SAVE accumulated data results.
query_results = []
json_data = []

# NOTE: It seems sometimes getting ALL services (get_stop_info, getLayerRegions etc) might fail.
#       It may be a browser issue, or problem may be on Yandex side.
#       In tests this sometimes appears near the end of strain of get_all_info queries while checking stops.
#       For now we're increasing random period from 15-45 to 40-90
def wait_random_time():
    value = random.randint(40, 90)
    print("Waiting " + str(value) + " seconds.")
    time.sleep(value)

# -----                                        DATA COLLECTION                                                   ----- #
do_data_collection = True
do_stations_collection = True
do_routes_collection = True

data_collection_passed = False
def perform_data_collection():
    """
    Data collection test, every single request should return valid JSON object.
    This test can be switched off, and data can be loaded from files instead during development.
    This takes a huge amount of time to process, by the way, due to wait times between queries
    (We don't want Yandex to get angry due to frequent queries, so we're playing safe here).
    Expect about 40-60 minutes of data collection.
    """
    global query_results

    global do_data_collection
    global do_stations_collection
    global do_routes_collection

    global data_collection_passed

    if not do_data_collection:
        return

    if data_collection_passed:
        return

    print()

    proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    if do_stations_collection:
        for station, url in station_urls.items():
            print("Collecting station: " + station + "... ", end='')
            result=''
            try:
                result = proxy.get_all_info(url)
                for entry in result:
                    query_results.append({"success": True,
                                          "station": station,
                                          "url": url,
                                          "method": entry['method'],
                                          "data": entry['data']})
                    print(entry['method'], end=' ')
                print("[OK]")
            except Exception as e:
                query_results.append({"success": False,
                                      "station": station,
                                      "url": url,
                                      "method": "getAllInfo (failed)",
                                      "data": ""
                                      }
                                     )
                print("[FAILED]")
                print("Exception (station): ",str(e))
            f = open('tests/testdata/output/station_' + station.replace('/', '-') + '.json.pretty', 'w', encoding='utf-8')
            f.write(json.dumps(result, ensure_ascii=False, indent=4, separators=(',', ': ')))
            f.close()
            f = open('tests/testdata/output/station_' + station.replace('/', '-') + '.json', 'w', encoding='utf-8')
            f.write(json.dumps(result, ensure_ascii=False))
            f.close()
            wait_random_time()

    if do_routes_collection:
        for route, url in routes_urls.items():
            print("Collecting route: " + route + "... ", end='')
            result = ''
            try:
                result = proxy.get_all_info(url)
                for entry in result:
                    query_results.append({"success": True,
                                          "route": route,
                                          "url": url,
                                          "method": entry['method'],
                                          "data": entry['data']})
                    print(entry['method'], end=' ')
                print("[OK]")
            except Exception as e:
                query_results.append({"success": False,
                                      "route": route,
                                      "url": url,
                                      "method": "getAllInfo (failed)",
                                      "data": ""
                                      })
                print("[FAILED]")
                print("Exception (route): ", str(e))
            f = open('tests/testdata/output/route_' + route.replace('/', '-') + '.json.pretty', 'w', encoding='utf-8')
            f.write(json.dumps(result, ensure_ascii=False, indent=4, separators=(',', ': ')))
            f.close()
            f = open('tests/testdata/output/route_' + route.replace('/', '-') + '.json', 'w', encoding='utf-8')
            f.write(json.dumps(result, ensure_ascii=False))
            f.close()
            wait_random_time()

    # Saving data to files
    f = open('test_data.json', 'w', encoding='utf-8')
    f.write(json.dumps(query_results, ensure_ascii=False))
    f.close()

    # Setting "data collection passed" flag.
    data_collection_passed = True

    # Basically, always succeeds
    assert True == True

def load_data_from_file():
    global json_data
    print()
    f = open('test_data.json', 'r', encoding='utf-8')
    data = f.readline()
    f.close()
    json_data = json.loads(data)
    for entry in json_data:
        if 'station' in entry:
            print('Station : ', entry["station"], ",", entry["success"], ",", end=' ')
            if 'method' in entry:
                print(entry["method"])
            else:
                print("")
        if 'route' in entry:
            print('Route   : ', entry["route"], ",", entry["success"], ",", end=' ')
            if 'method' in entry:
                print(entry["method"])
            else:
                print("")

@pytest.fixture(scope="session", autouse=True)
def prepare_data():
    # Collect data from Yandex Maps, save it to a file
    perform_data_collection()
    # Load data from file for tests.
    load_data_from_file()

# -----                                          TESTS                                                           ----- #
@pytest.mark.timeout(3600)
def test_data_load_stage():
    """Needed to call perform_data_collection and load_data_from_file functions"""
    print()
    assert True == True

@pytest.mark.timeout(120)
def test_initial():
    """Most basic test.py to ensure pytest DEFINITELY works"""
    assert True == True

# -----                                       CONTINUOUS TESTS                                                   ----- #
# With "getting the JSON" approach, checking if JSON contains the required data (stopInfo, routeInfo etc)
# is too difficult. Instead, continuous tests just check integrity of obtained JSONS, and which methods were called.
# Testing of actual data should be performed for particular API functions instead, if implemented,
# like getVehiclesInfo should count vehicles on several routes, or getStopCoordinates should get stop coordinated,
# accordingly.
# -------------------------------------------------------------------------------------------------------------------- #

def test_check_if_failure():
    """ Test if there was no failures"""
    failure_found = False
    for entry in json_data:
        if not entry["success"]:
            failure_found = True
            if 'station' in entry:
                print("Data for stop ", entry['station'], "collection failed.")
            if 'route' in entry:
                print("Data for route ", entry['route'], "collection failed.")
    assert not failure_found

def test_check_if_json():
    """ Test is every record is JSON"""
    failure_found = False
    for entry in json_data:
        try:
            record = json.dumps(entry['data'])
        except Exception as e:
            print("Exception:", str(e))
            failure_found = True
            if 'station' in entry:
                print("Data for stop ", entry['station'], "is not JSON.")
            if 'route' in entry:
                print("Data for route ", entry['route'], "is not JSON.")
    assert not failure_found

def test_check_if_no_error():
    """ Check that there is no 'error' field in json"""
    failure_found = False
    for entry in json_data:
        if 'error' in entry['data']:
            failure_found = True
            if 'station' in entry:
                print("Data for stop ", entry['station'], "has an 'error'.")
            if 'route' in entry:
                print("Data for route ", entry['route'], "has an 'error'.")
    assert not failure_found

def test_encountered_methods():
    """
    Test that each method was encountered at least once.
    Pretty "forgiving" test, "strict" would be expect every valid stop return getStopInfo and getLayerRegions,
    ane every route return getLayerRegions, getVehiclesInfo, getVehiclesInfoWithRegion and getRouteInfo.
    This may not happen due to network conditions.
    """
    print()
    print("Counting methods:")
    result = {'getStopInfo': 0,
              'getRouteInfo': 0,
              'getLine': 0,
              'getVehiclesInfo': 0,
              'getVehiclesInfoWithRegion': 0,
              'getLayerRegions': 0,
              'getAllInfo (failed)': 0}
    for entry in json_data:
        result[entry['method']] += 1

    for key, value in result.items():
        print(key, ':', value)

    assert result['getStopInfo'] > 0
    assert result['getVehiclesInfo'] > 0
    assert result['getLayerRegions'] > 0
    assert result['getLine'] > 0
    assert result['getVehiclesInfoWithRegion'] > 0
    assert result['getAllInfo (failed)'] == 0

def test_no_data_returned():
    """
    Test if there is a stop/route with no data returned
    """
    print()
    data_stations = {}
    data_routes = {}
    failure_found = False
    for entry in json_data:
        if 'station' in entry:
            data_stations[entry['station']] = 1
        if 'route' in entry:
            data_routes[entry['route']] = 1

    for key, value in station_urls.items():
        if key not in data_stations:
            failure_found = True
            print("No data for station", key)

    for key, value in routes_urls.items():
        if key not in data_routes:
            failure_found = True
            print("No data for route", key)

    assert not failure_found

# -------------------------------------------------------------------------------------------------------------------- #
