# Комнатный термостат или терморегулятор на ESP8266 (NodeMCU)
Проект комнатного термостата или терморегулятора (контроль температуры) с управлением насосами на ESP8266 (NodeMCU) с использованием управления через Telegram.

## Цели
1. Автоматизация работы газового котла взагородном доме;
2. Удаленный котроль за состоянием отопления;
3. Удаленное управление режимом отопления.
4. Управление насосами отопления.


# Room thermostat or the thermostat on the ESP8266 (NodeMCU)
Project room thermostat or the thermostat (temperature control) with pump control at ESP8266 (NodeMCU) with the use of control via Telegram.

## Goals
1. Automation of gas boiler in home;
2. Remote monitor the state of heating;
3. Remote control of heating.
4. Pump control heating.

## Решения (Solution)
1. Аппаратные (Hardware)
   1. NodeMCU https://ru.aliexpress.com/item/New-Wireless-module-NodeMcu-Lua-WIFI-Internet-of-Things-development-board-based-ESP8266-with-pcb-Antenna/32453920794.html?spm=a2g0s.8937460.0.0.JigHr0
   2. DALLAS DS18B20 (https://ru.aliexpress.com/item/5pcs-DALLAS-DS18B20-18B20-18S20-TO-92-IC-CHIP-Thermometer-Temperature-Sensor/32236763433.html)
   3. Four Channel Relay Module interface Board Shield 5V (https://ru.aliexpress.com/item/1pcs-lot-4-channel-relay-module-4-channel-relay-control-board-with-optocoupler-Relay-Output-4/32340914033.html?spm=a2g0s.9042311.0.0.8Ihmg6)
2. Программные решения (Software)
   1. MicroPython http://micropython.org/download#esp8266

   
## Установка
1. На OrangePI или аналоги устаннавливается MQTT Broker (mosquito) который слушает события и Telegram бот для управления.

    1.1. Используя Docker Compose
    * Обновляем прошивку до версии ядра Linux не ниже 4.х (Мainline kernel) https://www.armbian.com/orange-pi-pc-plus/
    * Устанавливаем Docker c учетом архитектуры **armhf** (https://docs.docker.com/install/linux/docker-ce/ubuntu/#set-up-the-repository)
    * Устанавливаем Docker Compose `pip install docker-compose`
    * Запускаем `sudo docker-compose up -d ` в директории с `docker-compose.yml`
    
    1.2. В ручную
    * Обновляем пакеты `sudo apt-get update`
    * Устанавливаем MQTT Broker Mosquitto (http://mosquitto.org/) `apt-get install mosquitto`
    * Устанавливаем telepot  `pip3 install telepot`
    * Устанавливаем paho.mqtt `pip3 install paho-mqtt`
    * Запускаем Python скрипт для уведомлений и управления посредством Telegram бота (Telepot) `python3 ./telegrambot.py`
2. Заливается в плату NodeMCU прошивка MicroPython http://micropython.org/download#esp8266
3. На плату NodeMCU записываются скрипты из папки ESP8266

##Настройка
1. Настройка NodeMCU `\src\esp8266\config.py` (настройка управлющих пинов и MQTT)
2. Настройка Telegram Bot `\src\OrangePI\telegram_bot\app-files\telegrambot.py` (BOT API TOKEN и MQTT)
