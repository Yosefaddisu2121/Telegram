import telebot 
import random
import time
import json

TOKEN = "7474182345:AAEym4DfLAGXUlGYQiaD6Z-F2-NDQK5mLVw"
bot = telebot.TeleBot(TOKEN)

USER_DB = "users.json"
chosen_numbers = {}
payment_received = {}
waiting_for_verification = {}
YOUR_USER_ID = 474803674

# Load users
def load_users():
    try:
        with open(USER_DB, "r") as file:
            data = json.load(file)
            return data if isinstance(data, list) else [] 
    except FileNotFoundError:
        return []

# Save users
def save_users(users):
    with open(USER_DB, "w") as file:
        json.dump(users, file)

@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.chat.id
    users = load_users()
    
    if user_id not in users:
        users.append(user_id)
        save_users(users)
    
    bot.send_message(user_id, "\t💰💰 እንኳን ደህና መጡ 💰💰 \n💰ይህ እየተዝናኑ እድሎን የሚሞክሩበት ሺህ ብሮችን የሚያፍሱበት ቦታ ነው!\n 💷💷 የሚከተሉትን ትዕዛዞች ይጠቀሙ💷💷\n \t\t ቁጥር ለመምረጥ :- /p <ቁጥር>ን    eg(/p 1)\n \t\tያልተያዙ ቁጥሮችን ለማየት :- /a \n \t\t   ")

@bot.message_handler(commands=['a'])
def available_numbers(message):
    available = [str(num) for num in range(1, 6) if num not in chosen_numbers]
    bot.send_message(message.chat.id, f"📋 የሚገኙ ቁጥሮች: {', '.join(available) if available else 'None'}")

@bot.message_handler(commands=['p'])
def pick_number(message):
    try:
        num = int(message.text.split()[1])
        if num < 1 or num > 5:
            bot.send_message(message.chat.id, "⚠️ በ1 እና 5 መካከል ቁጥር ይምረጡ")
        elif num in chosen_numbers:
            bot.send_message(message.chat.id, "❌ ይህ ቁጥር አስቀድሞ ተወስዷል።")
OBOBOBOBOBOBOBOBOBOB        else:
            username = message.from_user.username or str(message.from_user.id) 
OB            chosen_numbers[num] = username
            bot.send_message(message.chat.id, f"✅ ቁጥር {num} ይዘዋል! የክፍያ ቅጽበታዊ ገጽ Screenshot ይላኩ።\n⚠️ ማረጋገጫ በመጠባበቅ ላይ...")
    except:
        bot.send_message(message.chat.id, "⚠️ ቁጥር ለመምረጥ /p <ቁጥር>ን ተጠቀም/ሚ።")

@bot.message_handler(content_types=['photo'])
def receive_screenshot(message):
    bot.forward_message(YOUR_USER_ID, message.chat.id, message.message_id)
    username = message.from_user.username or str(message.from_user.id)
    
    reserved_numbers = [num for num, user in chosen_numbers.items() if user == username]
    
    if reserved_numbers:
        bot.send_message(message.chat.id, "✅ የክፍያ Screenshot ደርሷል። የአስተዳዳሪውን ማረጋገጫ በመጠበቅ ላይ...")
        waiting_for_verification[username] = {num: message.from_user.id for num in reserved_numbers}
        bot.send_message(YOUR_USER_ID, f"💰 የክፍያ Screenshot ከ @{username}.\nየተያዘ ቁጥር: {', '.join(map(str, reserved_numbers))}\n ለ ማረጋገጥ /confirm @{username} <number> approve/deny ተጠቀም")

@bot.message_handler(commands=['confirm'])
def confirm_payment(message):
    if message.chat.id != YOUR_USER_ID:
        bot.send_message(message.chat.id, "❌ ክፍያዎችን የማረጋገጥ ፍቃድ የለዎትም።")
        return
    try:
        parts = message.text.split()
        username = parts[1].strip("@")
        num = int(parts[2])
        decision = parts[3].lower()
        if decision not in ['approve', 'deny']:
            bot.send_message(message.chat.id, "⚠️ ልክ ያልሆነ ውሳኔ።  'approve' or 'deny'ተጠቀም")
            return
    except:
        bot.send_message(message.chat.id, "⚠️ ለ ማረጋገጥ /confirm @username <number> approve/deny ተጠቀም")
        return

    if username in waiting_for_verification and num in waiting_for_verification[username]:
        user_id = waiting_for_verification[username][num]
        if decision == 'approve':
            payment_received.setdefault(username, []).append(num)
            bot.send_message(user_id, f"✅ የቁጥር ክፍያዎ  {num} ** ጸድቋል**። \n✔️ **ተረጋግጠዋል!**\n  ********መልካም ዕድል********")
        elif decision == 'deny':
            del chosen_numbers[num]
            bot.send_message(user_id, f"❌ የቁጥር ክፍያዎ {num} ** ተከልክሏል**።\n⚠️ **አልተረጋገጠም።**")
        del waiting_for_verification[username][num]
        if not waiting_for_verification[username]:
            del waiting_for_verification[username]
    else:
        bot.send_message(message.chat.id, f"⚠️ ምንም በመጠባበቅ ላይ ያለ ማረጋገጫ አልተገኘም ከ @{username}  በ ቁጥር {num} ላይ")

@bot.message_handler(commands=['draw'])
def draw_winners(message):
    if message.chat.id != YOUR_USER_ID:
        bot.send_message(message.chat.id, "❌ እጣውን መጀመር የሚችለው አስተዳዳሪው ብቻ ነው።")
        return

    verified_numbers = [num for nums in payment_received.values() for num in nums]
    if len(verified_numbers) < 2:
        bot.send_message(message.chat.id, "⏳ በቂ የተረጋገጡ ተጫዋቾች የሉም ! draw  ከ ማረግዎ በፊት ቢያንስ 2 የተረጋገጡ ቁጥሮች ያስፈልጋሉ።")
        return

    users = load_users()  # Load all registered users
    
    # Broadcast the start message to all users
    start_message = "🎉 **የሎተሪ ዕጣው እየተጀመረ ነው!** 🎟\n🔄 ቁጥሮቹን በማዋሃድ ላይ........."
    for user in users:
        try:
            bot.send_message(user, start_message)
        except Exception as e:
            print(f"መልእክት መላክ አልተሳካም። {user}: {e}")

    # Countdown
    for i in range(30, 0, -1):
        countdown_message = f"⏳ {i} ሰከንዶች ይቀራል... "
        for user in users:
            try:
                bot.send_message(user, countdown_message)
            except Exception as e:
                print(f"መልእክት መላክ አልተሳካም!! {user}: {e}")
        time.sleep(2)  # Delay for effect

    # Select winners
    winners = random.sample(verified_numbers, 2)
    winner_user1 = next(user for user, nums in payment_received.items() if winners[0] in nums)
    winner_user2 = next(user for user, nums in payment_received.items() if winners[1] in nums)

    # Final announcement
    result_message = (
        f"🎊🎊🎊 **የሎተሪ ውጤቶች!** 🎊🎊🎊\n"
        f"*******🏆🏆🏆🏆እንኳን ደስ አላችሁ🏆🏆🏆🏆*******\n"
        f"🏆 ** አሸናፊዎች: ***@{winner_user1} (Number {winners[0]}) & @{winner_user2} (Number {winners[1]}) 🏆\n"
        f"💰 አስተዳዳሪው ለሽልማቱ አሸናፊዎቹን ያነጋግራል!"
    )
    for user in users:
        try:
            bot.send_message(user, result_message)
        except Exception as e:
            print(f"❌መልእክት መላክ አልተሳካም!!! {user}: {e}")

    bot.send_message(message.chat.id, "✅ Draw ውጤቶች ለሁሉም ተጠቃሚዎች ተልከዋል!!")

@bot.message_handler(commands=['close'])
def close_lottery(message):
    if message.chat.id != YOUR_USER_ID:
        bot.send_message(message.chat.id, "❌ ሎተሪውን መዝጋት የሚችለው አስተዳዳሪው ብቻ ነው።")
        return
    global chosen_numbers, payment_received, waiting_for_verification
    chosen_numbers.clear()
    payment_received.clear()
    waiting_for_verification.clear()
    bot.send_message(message.chat.id, "🚫 ሎተሪው ተዘግቷል። ሁሉም ቁጥሮች አሁን እንደገና ይገኛሉ!")

bot.polling()

