# EventNotifier Telegram Bot

The EventNotifier Telegram Bot is your personal event assistant, allowing you to effortlessly manage and receive reminders for both one-time and recurring events. With multilingual support, intuitive scheduling options, and even the ability to create events through voice messages, this bot is designed to simplify your planning.

## Features:

1. **Multilingual Support:**
   - Choose your preferred language from Russian, Kazakh, or English upon starting the bot.

2. **Add Weekly Events:**
   - Create weekly events by selecting the day of the week and the desired time. Follow up by entering event details.

3. **Quick One-time Events:**
   - Enter one-time events swiftly by adhering to the format `{Time(HH:MM) Event Text}`. Choose when to be reminded (0, 15, 30, 45, 60 minutes before).

4. **View and Delete Events:**
   - Easily view your events through the "View Schedule" option. Choose between one-time and weekly events.
   - Delete events seamlessly by selecting from a numbered list.

5. **Automatic Cleanup:**
   - One-time events are automatically deleted daily at 23:59.

6. **Voice Message Support:**
   - Create events effortlessly by recording voice messages in Russian. The bot understands and validates the format for both one-time and weekly events.
   - Receive format guidance if needed. Confirm or cancel the event after listening.

7. **Reminder Notifications:**
   - Receive personal reminders twice at the specified time and, if selected, in advance.

## Getting Started:

1. Start the bot and choose your language.
2. Navigate through options: Add Schedule, View Schedule, Delete Schedule.
3. For weekly events, choose the day and time, then enter event details.
4. For one-time events, enter the time and event details, then choose when to be reminded.
5. View or delete events as needed.
6. Record voice messages for quick event creation.
7. Enjoy timely reminders for your events.

## Example Usage:

### Adding a Weekly Event:

1. Choose "Add Schedule."
2. Select the day (Monday to Sunday).
3. Choose the time (0 to 9).
4. Enter event details when prompted.
5. Confirm or cancel event saving.
6. Choose when to be reminded (0, 15, 30, 45, 60 minutes).

### Quick One-time Event:

1. Enter event details in the format `{Time(HH:MM) Event Text}`.
2. Choose when to be reminded (0, 15, 30, 45, 60 minutes).

### Voice Message Event Creation:

1. Record a voice message with the correct format.
2. Confirm or cancel event saving.

## Notes:

- Weekly events are saved until the user deletes them.
- Voice messages must be in Russian and follow the specified format.
- The bot provides guidance for incorrect formats.

## Reminder Notification Format:

- **Example:** `{Reminder - Time - Event Text}`
- Reminders are sent twice: at the specified time and, if selected, in advance.

## Contributions:

Feel free to contribute by reporting issues, suggesting improvements, or submitting pull requests.

## License:

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments:

Special thanks to the Telegram API and the open-source community for their contributions.

Feel free to reach out with any questions or feedback! Enjoy using the EventNotifier Telegram Bot!
