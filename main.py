import telebot
import requests
from tokens import TG_API as BOT_TOKEN, OWHL_API as OPENWEATHER_API_KEY

bot = telebot.TeleBot(BOT_TOKEN)
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


def get_weather(city): #получение погоды
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code == 200: #если все хорошо, то получаем данные
            data = response.json()

            city_name = data['name'] #название города
            temp = round(data['main']['temp']) #температура в градусах по Цельсию
            feels_like = round(data['main']['feels_like']) #округление температуры, ощущения
            description = data['weather'][0]['description'].capitalize() #описание погоды
            pressure = data['main']['pressure'] #давление в гектоПаскалях
            humidity = data['main']['humidity'] #влажность в процентах
            wind_speed = round(data['wind']['speed']) #скорость ветра
            
            result = [
                f"**Погода в городе {city_name} сейчас:**",
                "",
                f"🌡️ **Температура:** {temp}°C (Ощущается как: {feels_like}°C)",
                f"☁️ **Состояние:** {description}",
                f"💨 **Скорость ветра:** {wind_speed} м/с",
                f"💧 **Влажность:** {humidity}%",
                f"🧭 **Давление:** {pressure} гПа" 
            ]
            
            return "\n".join(result)#ответ
        
        elif response.status_code == 404: #если браток фигня получилась
            return f"Город **{city}** не найден."
        
        else:
            return f"Не удалось получить данные. Код ошибки: {response.status_code}."
            
    except requests.exceptions.RequestException:
        return "❌ Ошибка при выполнении сетевого запроса." #нифига не получилось
    except Exception as e:
        print(f"Ошибка: {e}") 
        return "❌ Произошла внутренняя ошибка при обработке данных."#тоже самое, неизвестная ошибка


@bot.message_handler(commands=['start']) #абрабочек start
def start(message):
    welcome_message = (
        "👋 Привет! Я бот для погоды.\n"
        "Чтобы узнать погоду, просто напиши: \n"
        "**/weather город** (например, /weather Владимир)"
    )
    bot.send_message(message.chat.id, welcome_message, parse_mode='Markdown') #отправка приветствия

@bot.message_handler(commands=['weather']) #обработчик weather
def weather(message):
    sent_message_id = None
    
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2: #если этот дебил отправил только команду
            bot.send_message(
                message.chat.id, 
                "Пользуйся: **/weather город**",
                parse_mode='Markdown'
            )
            return
            
        city = parts[1].strip()
        
        #временное сообщение
        sent_message = bot.send_message(message.chat.id, f"Ищу погоду в городе **{city}**...", parse_mode='Markdown')
        sent_message_id = sent_message.message_id
        
        #але нам дадут результат?
        result = get_weather(city)

        #удаление временного сообщения
        try:
            bot.delete_message(message.chat.id, sent_message_id)
        except Exception:
            pass
            
        bot.send_message(
            chat_id=message.chat.id, 
            text=result, 
            parse_mode='Markdown' 
        ) #отправка результата
        
    except Exception:
        error_text = "❌ Извини, произошла внутренняя ошибка при обработке команды." #если какая-то ошибка
        bot.send_message(message.chat.id, error_text)

@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, "Погодник 1.1, использую OpenWeatherMap API.", parse_mode="Markdown")

@bot.message_handler(commands=['help', 'commands'])
def help(message):
    bot.send_message(message.chat.id, """
Список команд:

**/help**, **/commands** - список комманд
**/start** - приветствие
**/weather** - погода
**/info** - информация о боте
""", parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def other(message):
    bot.send_message(message.chat.id, "Неуч, ты че пишешь? Я знаю только **/weather** и **/start**", parse_mode='Markdown')


bot.infinity_polling()