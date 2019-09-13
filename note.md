# Optional Environment Variables
### `LOGGER`
Logger(s) to be used and printed in the console. Log level can be specified.

**Options:**

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

**Example Value:**

(w/o log level)

> LINE,LINE_INTERNAL

or

(w/ log level)

> LINE|40,DISCORD

**Default Value:**
> N/A

**Notes:**
- If `DEBUG` in environment variable is set to `1`, this setting will be ignored, except that the log level is specified.

<hr>

### `LOG_LEVEL`
Default numeric value of the level to be logged. This will be overrided if a level is specified in [`LOGGER`](#logger).

**Options:**
> Refer to <https://docs.python.org/3/library/logging.html#levels>

**Example Value:**
> 50

**Default Value:**
> `logging.ERROR` (40)

**Notes:**
- If `DEBUG` in environment variable is set to 1, this setting will be ignored.
