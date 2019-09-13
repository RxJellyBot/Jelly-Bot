# Optional Environment Variables
### `LOGGER`
Logger(s) to be used and printed in the console.

Options
> `LINE`: System's logger on `linebot` wrapper
>
> `LINE_INTERNAL`: `linebot`'s logger
>
> `DISCORD`: `discord.py`'s logger
>
> `DISCORD_INTERNAL`: System's logger on `discord.py`'s wrapper
>
> `TIME_EXEC`: Function execution timing logs
>
> `MODEL_CHECK`: MongoDB model checker's logger
>
> `MONGO_UTILS`: MongoDB utility's logger

Example Value
> LINE,LINE_INTERNAL

Default Value
> N/A

<hr>

### `LOG_LEVEL`
Numeric value of the level to be logged.

Options
> Refer to <https://docs.python.org/3/library/logging.html#levels>

Example Value
> 50

Default Value
> `logging.ERROR` (40)
