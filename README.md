# Kensa Discord Bot

Kensa is a Discord bot designed to expedite the process of searching various logs on the Dnd World Discord, which you can join [here](https://discord.gg/6uSV7Whgss).

## Syntax
Below, you will find detailed instructions on how to use the bot to perform various different kinds of audits. Please note the bot is still a work-in-progress, and command names can change at any time.

### /audit-full:
This is the command that you will be using most frequently. The syntax is as follows:
- `year`: The year of the first message you wish to audit.
- `month`: The month of the first message you wish to audit.
- `day`: The day of the first message you wish to audit

Additionally, there are several optional filters that you can apply to the result as follows:
- `char_name`: The name of the character you wish to audit.
- `user_id`: The id of the player you wish to audit. *Note: If you are performing an audit that take place before July 1, 2023, this option does not work properly. Instead use the `char_name` option listed above.*
- `dtd_type`: The type of DTD you are looking for. *Note: At present, only `!guild` dtds support this option. Support for other DTDs is planned for a future update*

### /audit get_message
This command fetches the raw text of a message. The syntax is as follows:
- `channel_id`: The id of the channel you wish to audit. *Note: Only a select few channels are supported at this time. Support for additional channels is planned for a future update.*
- `message_id`: The id of the message you wish to audit.
- `content_type`: The type of text you are trying to get from the message. This can either be `message` for raw text, or `embed` for embed contents.

### /database reset_latest_audit_info (Trusted Users Only)
This command resets caching information for the bot. Useful if the database is missing a message from official logging channels after performing an audit.
